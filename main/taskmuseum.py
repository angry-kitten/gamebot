#
# Copyright 2021 by angry-kitten
# Go the the museum and evaluate fossils and donate items.
#

import gbdata, gbstate
import gbscreen
import gbocr
import cv2
import taskobject
import taskpress
import tasksay
import taskdetect
import taskgotomain
import taskupdatemini
import taskpathplangoto
import taskheadinggoto
import tasktrackturn
import taskocr

class TaskMuseum(taskobject.Task):
    """TaskMuseum Object"""

    def __init__(self):
        super().__init__()
        self.name="TaskMuseum"
        print("new",self.name,"object")
        self.step=0
        self.within=1
        self.ratio=0.30
        self.name_within=30
        self.ocr_name=None
        self.ocr_menu=None
        self.target_slot=0
        self.assessed=False
        self.donated=False
        self.select_count=0

    def Poll(self):
        """check if any action can be taken"""
        print(self.name,"Poll")
        if not self.started:
            self.Start()
            return
        if self.taskdone:
            return
        if gbstate.frame is None:
            return

        print(self.name,"step=",self.step)

        if self.step == 0:
            # Verify that player character is in front of the museum.
            mx=gbstate.building_info_museum[3]
            my=gbstate.building_info_museum[4]
            if not (gbscreen.match_within(gbstate.player_mx,mx,self.within) and gbscreen.match_within(gbstate.player_my,my,self.within)):
                self.step=99
                return

            # Do a detect to get ready for is_inside_building_screen
            self.parent.Push(taskdetect.TaskDetect())

            self.parent.Push(taskobject.TaskTimed(12.0)) # wait for interior of museum

            # When the museum is still a tent, need to press 'A' to go inside.
            # this shouldn't do anything once the museum is a building.
            self.parent.Push(taskpress.TaskPress('A'))

            # Walk to the center of the museum, mapless. This should cause the player
            # character to enter.
            self.parent.Push(taskheadinggoto.TaskHeadingGoTo(0,3))
            self.step=1
            return

        if self.step == 1: # player character should be inside
            if not gbscreen.is_inside_building_screen():
                print("not inside")
                self.step=99
                return

            # Wait for Blathers to wake
            self.parent.Push(taskobject.TaskTimed(10.0))

            # Wake Blathers
            self.parent.Push(taskpress.TaskPress('A'))

            #self.parent.Push(taskobject.TaskTimed(1.0))

            # face Blathers
            self.parent.Push(tasktrackturn.TaskTrackTurn(45))

            # Walk forward.
            self.parent.Push(taskheadinggoto.TaskHeadingGoTo(0,3))

            self.step=2
            return

        if self.step == 2: # continue until menu
            if gbscreen.is_continue_triangle():
                # press continue and wait for animation
                self.parent.Push(taskobject.TaskTimed(8.0))
                self.parent.Push(taskpress.TaskPress('B'))
                return
            self.step=3
            return

        if self.step == 3: # select assess
            # OCR the menu
            self.parent.Push(taskocr.TaskOCR())
            self.step=4
            return

        if self.step == 4:
            self.digest_menu1()
            print("ocr menu",self.ocr_menu)
            if self.ocr_menu is None:
                self.step=90 # exit the museum
                return
            if len(self.ocr_menu) < 1:
                self.step=90 # exit the museum
                return
# There can be one of several menus at this point
# #1
# Make a donation.
# Assess fossils.
# Tell me about this!
# I'm fine.
# #2
# I'm donating it!
# I'Il take it home.
# #3
#
# busy

            (index,is_last)=gbocr.locate_menu_text(self.ocr_menu,'Assess fossils')
            if index is not None:
                print("menu #1")
                if self.assessed:
                    # We have already assessed and we have come back
                    # around to the menu. Just close it and move on.
                    self.step=80
                    return

                # Move the pointer hand to the
                # menu entry and select it.

                self.parent.Push(taskobject.TaskTimed(6.0)) # wait for animation
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

                self.step=5
                return

            (index,is_last)=gbocr.locate_menu_text(self.ocr_menu,"I'm donating it")
            if index is not None:
                print("menu #2")
                if self.donated:
                    print("already donated. donate again")

                # Move the pointer hand to the
                # menu entry and select it.

                self.parent.Push(taskobject.TaskTimed(6.0)) # wait for animation
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

                self.donated=True
                self.step=2
                return

            (index,is_last)=gbocr.locate_menu_text(self.ocr_menu,'busy')
            if index is not None:
                print("menu #3")
                # Do we want to hear a description of the fossil? Nope.

                # Move the pointer hand to the
                # menu entry and select it.

                self.parent.Push(taskobject.TaskTimed(6.0)) # wait for animation
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

                self.donated=True
                self.step=2
                return

            print("unkown menu, or OCR miss")

            # close the menu, whatever it is
            self.parent.Push(taskobject.TaskTimed(8.0)) # wait for the animation
            self.parent.Push(taskpress.TaskPress('B'))
            self.parent.Push(taskobject.TaskTimed(1.0))
            self.parent.Push(taskpress.TaskPress('B'))
            self.step=2
            return

        if self.step == 5:
            # At this point the chat could be a message saying
            # there are no fossils to assess. Or the chat could
            # lead to the inventory poping up.
            if not gbscreen.is_continue_triangle():
                print("no continue triangle")
                # Assume the inventory is up.
                self.step=8
                return

            # Do an OCR to read the first message.
            self.parent.Push(taskocr.TaskOCR())

            self.step=6
            return

        if self.step == 6:
            # Check the OCR results for:
            # Alas, you have no unknown fossils
            # for me to inspect.

            if gbocr.ocr_results_contain("you have no unknown fossils"):
                self.assessed=True
                self.step=2 # Go back to chat that leads back to the menu.
                return

            if gbocr.ocr_results_contain("Alas"):
                self.assessed=True
                self.step=2 # Go back to chat that leads back to the menu.
                return

            if gbocr.ocr_results_contain("for me to inspect"):
                self.assessed=True
                self.step=2 # Go back to chat that leads back to the menu.
                return

            if gbocr.ocr_results_contain("Alas, you have"):
                self.assessed=True
                self.step=2 # Go back to chat that leads back to the menu.
                return

            if gbocr.ocr_results_contain("no unknown fossils"):
                self.assessed=True
                self.step=2 # Go back to chat that leads back to the menu.
                return

            # Assume this chat will lead to the inventory popping up.
            self.step=7
            return

        if self.step == 7:
            # continue until inventory pops up
            if gbscreen.is_continue_triangle():
                # press continue and wait for animation
                self.parent.Push(taskobject.TaskTimed(8.0))
                self.parent.Push(taskpress.TaskPress('B'))
                return

            self.step=8
            return

        if self.step == 8:
            # Do a detect so we can locate the pointer hand.
            self.parent.Push(taskdetect.TaskDetect())
            self.step=9
            return

        if self.step == 9:
            # locate the hand
            # find the pointer hand
            hand_match=gbscreen.has_label_in_box('PointerHand',self.ratio,gbdata.inventory_sx1,gbdata.inventory_sx2,gbdata.inventory_sy1,gbdata.inventory_sy2)
            if hand_match is None:
                print("hand not found")
                # Assume there are no fossils to assess. We probably
                # have some chat that will go back to the menu.
                self.assessed=True
                self.step=2
                return

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
                self.step=30 # close inventory
                return
            gbstate.hand_slot=hand_slot
            self.target_slot=0
            self.select_count=0

            self.step=10
            return

        if self.step == 10:
            # Select the fossils
            print("hand_slot",gbstate.hand_slot)
            print("target_slot",self.target_slot)
            print("inventory_size",gbstate.inventory_size)
            if self.target_slot >= gbstate.inventory_size:
                # We are done picking fossils
                self.step=20
                return
            gbocr.move_hand_to_slot(self.target_slot,self)
            print("hand_slot",gbstate.hand_slot)
            self.step=11
            return

        if self.step == 11:
            # Do an OCR to see if there is a fossil here.
            self.parent.Push(taskocr.TaskOCR())
            self.step=12
            return

        if self.step == 12:
            # Check the results of the OCR
            self.digest_name()
            print("ocr name",self.ocr_name)
            if self.ocr_name is None:
                # There is no fossil here
                self.target_slot+=1
                self.step=10
                return

            if 'Fossil' != self.ocr_name:
                # There is no fossil here
                self.target_slot+=1
                self.step=10
                return

            # Select the item
            self.parent.Push(taskobject.TaskTimed(1.0)) # wait for animation
            self.parent.Push(taskpress.TaskPress('A'))
            self.select_count+=1

            # Move on to check the next slot
            self.target_slot+=1
            self.step=10
            return

        if self.step == 20:
            if self.select_count < 1:
                # Nothing to confirm
                self.assessed=True
                self.step=30 # close the inventory
                return

            # Confirm the selections
            self.parent.Push(taskobject.TaskTimed(8.0)) # wait for animation
            self.parent.Push(taskpress.TaskPress('+'))

            # Go back around to the menu after some chat.
            self.assessed=True
            self.step=2
            return

        if self.step == 30:
            # close inventory
            self.parent.Push(taskobject.TaskTimed(3.0))
            self.parent.Push(taskpress.TaskPress('B'))
            # This should chat a little and then go back to
            # the first menu.
            self.step=2
            return

        if self.step == 80:
            # close the menu
            self.parent.Push(taskobject.TaskTimed(8.0)) # wait for the animation
            self.parent.Push(taskpress.TaskPress('B'))
            self.parent.Push(taskobject.TaskTimed(1.0))
            self.parent.Push(taskpress.TaskPress('B'))
            self.step=81
            return

        if self.step == 81: # continue until done talking
            if gbscreen.is_continue_triangle():
                # press continue and wait for animation
                self.parent.Push(taskobject.TaskTimed(8.0))
                self.parent.Push(taskpress.TaskPress('B'))
                return
            self.step=90 # exit the museum
            return

        if self.step == 90:
            # Wait for the exit animation.
            self.parent.Push(taskobject.TaskTimed(10.0))
            # Walk out of the museum, mapless.
            self.parent.Push(taskheadinggoto.TaskHeadingGoTo(180,6))
            self.step=99
            return

        print(self.name,"done")
        self.taskdone=True
        return

    def Start(self):
        """Cause the task to begin doing whatever."""
        print(self.name,"Start")
        if self.started:
            return # already started
        self.started=True
        self.step=0

        if gbstate.building_info_museum is None:
            print("no museum location info")
            self.step=99
            return

        doormx=gbstate.building_info_museum[3]
        doormy=gbstate.building_info_museum[4]
        self.parent.Push(taskpathplangoto.TaskPathPlanGoTo(doormx,doormy))
        return

    def DebugRecursive(self,indent=0):
        self.DebugPrint(self.name,indent)

    def NameRecursive(self):
        gbstate.task_stack_names.append(self.name)
        return self.name

    def digest_menu1(self):
        self.ocr_menu=None
        with gbstate.ocr_worker_thread.data_lock:
            dets=gbstate.ocr_detections
        if dets is None:
            return
        menu=[]
        for det in dets:
            print("det",det)
            (box,text,score)=det
            (csx,csy)=gbocr.ocr_box_to_center(box)
            if gbscreen.is_inside_box(gbdata.ocr_museum_menu1_lane_x1,gbdata.ocr_museum_menu1_lane_x2,gbdata.ocr_museum_menu1_lane_y1,gbdata.ocr_museum_menu1_lane_y2,csx,csy):
                print("menu item")
                entry=[csy,text]
                menu.append(entry)
                continue
        menu=gbocr.combine_menu_entries(menu)
        if len(menu) < 1:
            self.ocr_menu=None
        else:
            # Sort the menu by sy
            self.ocr_menu=sorted(menu,key=lambda entry: entry[0])
        return

    def digest_name(self):
        self.ocr_name=None
        with gbstate.ocr_worker_thread.data_lock:
            dets=gbstate.ocr_detections
        if dets is None:
            return
        (slot_sx,slot_sy)=gbstate.inventory_locations[gbstate.hand_slot]
        expect_name_sx=slot_sx
        expect_name_sy=slot_sy+gbdata.ocr_inv_name_offset_y
        for det in dets:
            print("det",det)
            (box,text,score)=det
            (csx,csy)=gbocr.ocr_box_to_center(box)
            if gbscreen.is_near_within(expect_name_sx,expect_name_sy,csx,csy,self.name_within):
                print("item name")
                self.ocr_name=text
                continue
        return
