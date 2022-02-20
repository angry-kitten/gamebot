#
# Copyright 2021-2022 by angry-kitten
# Open the player inventory and process items that can be broken down
# like presents, message bottles, and recipes.
#

import gbdata
import gbstate
import gbscreen
import gbdisplay
import gbocr
import taskobject
import taskpress
import taskdetect
import taskocr

class TaskProcInv(taskobject.Task):
    """TaskProcInv Object"""

    def __init__(self):
        super().__init__()
        self.name="TaskProcInv"
        print("new",self.name,"object")
        self.step=0
        self.target_slot=0
        self.ratio=0.30

    def Poll(self):
        """check if any action can be taken"""
        print(self.name,"Poll")
        if not self.started:
            self.Start()
            return
        if self.taskdone:
            return

        if self.step == 0:
            hand_slot=locate_inventory_hand()
            if hand_slot is None:
                self.step=90 # close the inventory
                return
            self.target_slot=0
            self.step=10
            return

        if self.step == 10:
            # Select each slot in turn
            print("hand_slot",gbstate.hand_slot)
            print("target_slot",self.target_slot)
            print("inventory_size",gbstate.inventory_size)
            if self.target_slot >= gbstate.inventory_size:
                # We are done processing slots
                self.step=90
                return
            gbocr.move_hand_to_slot(self.target_slot,self)
            print("hand_slot",gbstate.hand_slot)
            self.step=11
            return

        if self.step == 11:
            # For a recipe, the name shown is what the recipe
            # makes, not "Recipe". Look at the inventory_name list
            # to see if there is a recipe here.
            if gbstate.inventory_name is not None:
                if self.target_slot < len(gbstate.inventory_name):
                    if 'InvRecipe' == gbstate.inventory_name[self.target_slot]:
                        # Skip directly to handling the recipe.
                        # Select the item
                        self.parent.Push(taskobject.TaskTimed(1.0)) # wait for animation
                        self.parent.Push(taskpress.TaskPress('A'))
                        self.step=40
                        return

            # Do an OCR to see if there is a processable item here.
            self.parent.Push(taskocr.TaskOCR())
            self.step=12
            return

        if self.step == 12:
            # Check the results of the OCR
            gbocr.digest_inv_screen_name()
            print("ocr name",gbstate.ocr_name)
            if gbstate.ocr_name is None:
                # There is no processable item here (that we can tell)
                self.target_slot+=1
                self.step=10
                return

            # convert to inventory name
            inv_name=gbocr.ocr_name_to_inv_name(gbstate.ocr_name)

            print("inv name",inv_name)

            if gbstate.ocr_name not in gbdata.item_activate:
                if inv_name is None:
                    # There is no processable item here
                    self.target_slot+=1
                    self.step=10
                    return
                if inv_name not in gbdata.item_activate:
                    # There is no processable item here
                    self.target_slot+=1
                    self.step=10
                    return

            print("found")

            is_present_like=False
            is_message_bottle_like=False
            is_recipe_like=False

            if 'InvPresent' == inv_name:
                is_present_like=True
            elif 'Present' == gbstate.ocr_name:
                is_present_like=True
            elif 'InvMessageBottle' == inv_name:
                is_message_bottle_like=True
            elif 'Message bottle' == gbstate.ocr_name:
                is_message_bottle_like=True
            elif 'InvRecipe' == inv_name:
                is_recipe_like=True
            elif 'Recipe' == gbstate.ocr_name:
                is_recipe_like=True
            elif 'InvBellBagStar' == inv_name:
                is_bells_like=True
            elif 'bells' == gbstate.ocr_name:
                is_bells_like=True

            # Select the item
            self.parent.Push(taskobject.TaskTimed(1.0)) # wait for animation
            self.parent.Push(taskpress.TaskPress('A'))

            if is_present_like:
                self.step=20
            elif is_message_bottle_like:
                self.step=30
            elif is_recipe_like:
                self.step=40
            elif is_bells_like:
                self.step=50
            else:
                # move on to next slot
                self.target_slot+=1
                self.step=10
            return

        if self.step == 20: # present like
            # Do an OCR to get the menu.
            self.parent.Push(taskocr.TaskOCR())
            self.step=21
            return

        if self.step == 21:
            gbocr.digest_inv_screen_menu()
            if gbstate.ocr_menu is None:
                self.step=22 # close the menu without selecting anything
                return

            # Make sure the menu has an 'open' option.
            if len(gbstate.ocr_menu) < 1:
                self.step=22 # close the menu without selecting anything
                return
            (index,is_last)=gbocr.locate_menu_text(gbstate.ocr_menu,'Open')
            if index is None:
                self.step=22 # close the menu without selecting anything
                return

            # Select 'open'
            self.parent.Push(taskobject.TaskTimed(1.0)) # wait for menu to pop down
            self.parent.Push(taskpress.TaskPress('A'))

            if index != 0:
                print("need to move the pointer hand")
                if is_last:
                    print("move up to wrap around to last item in menu")
                    self.parent.Push(taskobject.TaskTimed(1.0)) # wait for the animation
                    self.parent.Push(taskpress.TaskPress('hat_TOP'))
                else:
                    print("move down by",index)
                    for j in range(index):
                        self.parent.Push(taskobject.TaskTimed(1.0)) # wait for the animation
                        self.parent.Push(taskpress.TaskPress('hat_BOTTOM'))

            # do not move on to next slot in case the present
            # was a recipe or the like
            self.step=10
            return

        if self.step == 22:
            # close the menu without selecting anything
            self.parent.Push(taskobject.TaskTimed(1.0)) # wait for menu to pop down
            self.parent.Push(taskpress.TaskPress('B'))
            # Move to the next slot
            self.target_slot+=1
            self.step=10
            return

        if self.step == 30: # message bottle like
            # Press 'A' to close message window
            # "I got a DIY recipe"
            self.parent.Push(taskobject.TaskTimed(1.0)) # wait for animation
            self.parent.Push(taskpress.TaskPress('A'))

            # Select "open" from the menu
            self.parent.Push(taskobject.TaskTimed(1.0)) # wait for animation
            self.parent.Push(taskpress.TaskPress('A'))

            # do not move on to next slot in case the message bottle
            # was a recipe or the like
            self.step=10
            return

        if self.step == 40: # recipe like
            # Select "learn" from the menu
            self.parent.Push(taskobject.TaskTimed(2.0)) # wait for animation
            self.parent.Push(taskpress.TaskPress('A'))
            self.step=41
            return

        if self.step == 41:
            if gbscreen.is_continue_triangle():
                # "Huh... OK!"

                # Press 'B' to close the chat window
                self.parent.Push(taskobject.TaskTimed(1.0)) # wait for animation
                self.parent.Push(taskpress.TaskPress('B'))

                # look again for more chat
                self.step=41
                return

            self.target_slot+=1
            self.step=10
            return

        if self.step == 50: # bells like
            # Select "put away" from the menu
            self.parent.Push(taskobject.TaskTimed(2.0)) # wait for animation
            self.parent.Push(taskpress.TaskPress('A'))

            self.target_slot+=1
            self.step=10
            return

        if self.step == 90:
            # close the inventory
            self.parent.Push(taskobject.TaskTimed(2.0)) # wait for the inventory to close
            self.parent.Push(taskpress.TaskPress('B'))
            gbstate.draw_inventory_locations=False
            self.step=99
            return

        print(self.name,"done")
        self.taskdone=True

    def Start(self):
        """Cause the task to begin doing whatever."""
        print(self.name,"Start")
        if self.started:
            return # already started
        self.started=True
        self.step=0

        if not can_process_inventory():
            self.step=99
            return

        # open inventory

        self.parent.Push(taskdetect.TaskDetect())

        self.parent.Push(taskobject.TaskTimed(3.0)) # wait for the inventory to open
        self.parent.Push(taskpress.TaskPress('X'))
        gbstate.draw_inventory_locations=True
        return

    def DebugRecursive(self,indent=0):
        self.DebugPrint(self.name,indent)

    def NameRecursive(self):
        myname=self.name
        gbstate.task_stack_names.append(myname)
        return myname

def can_process_inventory():
    iset=set(gbstate.inventory_name)
    #print("iset",iset)
    pset=set(gbdata.item_activate)
    #print("pset",pset)
    i=iset & pset
    #print("i",i)
    l=len(i)
    #print("l",l)
    return l > 0

def locate_inventory_hand():
    # locate the hand
    # find the pointer hand
    hand_match=gbscreen.has_label_in_box('PointerHand',0.30,gbdata.inventory_sx1,gbdata.inventory_sx2,gbdata.inventory_sy1,gbdata.inventory_sy2)
    if hand_match is None:
        print("hand not found")
        return None

    # Find the slot number for the hand.
    x=hand_match[2]
    y=hand_match[3]
    # Estimate the inventory position the hand is pointing at.
    x-=gbdata.inventory_pointer_offset_x
    y-=gbdata.inventory_pointer_offset_y
    hand_slot=gbscreen.find_inventory_slot(x,y)
    print("hand_slot is",hand_slot)
    if hand_slot is None:
        print("hand_slot not found")
        return None
    gbstate.hand_slot=hand_slot
    return hand_slot
