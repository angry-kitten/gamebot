#
# Copyright 2021 by angry-kitten
# A task for the player character to begin holding a tool if possible.
#

import gbdata, gbstate
import gbscreen
import gbdisplay
import taskobject
import taskpress
import taskdetect
import tasktakeinventory
import taskocr

class TaskHoldTool(taskobject.Task):
    """TaskHoldTool Object"""

    def __init__(self,toolname):
        super().__init__()
        self.name="TaskHoldTool"
        print("new",self.name,"object")
        self.toolname=toolname
        self.step=0
        self.ratio=0.30
        #self.move_wait=0.5 # seconds
        self.move_wait=0.3 # seconds

    def Poll(self):
        """check if any action can be taken"""
        #print(self.name,"Poll")
        if not self.started:
            self.Start()
            return
        if self.taskdone:
            return

        if self.step == 0:
            print("detect was just done")
            self.find_tool_and_pointer()
            return

        if self.step == 1:
            print("tool and hand found, moving pointer hand")
            self.move_pointer_hand()
            return

        if self.step == 2:
            print("select tool")
            #self.parent.Push(taskocr.TaskOCR())
            self.parent.Push(taskdetect.TaskDetect())
            self.parent.Push(taskobject.TaskTimed(1.0)) # wait for menu to pop up
            self.parent.Push(taskpress.TaskPress('A'))
            self.step=3 # process menu
            return

        if self.step == 3:
            print("process menu")
            self.process_menu()
            return

        # close the inventory
        self.parent.Push(taskobject.TaskTimed(2.0)) # wait for the inventory to close
        self.parent.Push(taskpress.TaskPress('B'))
        gbstate.draw_inventory_locations=False
        #print(self.name,"done")
        self.taskdone=True

    def Start(self):
        """Cause the task to begin doing whatever."""
        print(self.name,"Start",self.toolname)
        if self.started:
            return # already started
        self.started=True
        self.step=0

        if self.toolname == 'None':
            self.parent.Push(taskobject.TaskTimed(2.0)) # wait for animation
            self.parent.Push(taskpress.TaskPress('hat_BOTTOM'))
            print(self.name,"done")
            self.taskdone=True
            gbstate.current_tool=None
            gbstate.player_heading=180 # down/south
            return

        # open inventory to check for tools
        self.parent.Push(taskdetect.TaskDetect())
        self.parent.Push(taskobject.TaskTimed(2.0)) # wait for the inventory to open
        self.parent.Push(taskpress.TaskPress('X'))
        gbstate.draw_inventory_locations=True

    def DebugRecursive(self,indent=0):
        self.DebugPrint(self.name,indent)

    def NameRecursive(self):
        myname=self.name+" "+self.toolname
        gbstate.task_stack_names.append(myname)
        return myname

    def find_tool_by_inventory_name(self,inventory_name_list):
        print("find_tool_by_inventory_name",inventory_name_list)
        for name in inventory_name_list:
            print("looking for",name)
            match=gbscreen.has_label_in_box(name,self.ratio,gbdata.inventory_sx1,gbdata.inventory_sx2,gbdata.inventory_sy1,gbdata.inventory_sy2)
            if match is not None:
                self.match=match
                return
            print(name,"not found")

        self.step=4 # close inventory
        return

    def find_tool(self):
        print("find_tool",self.toolname)
        if self.toolname == 'Axe':
            self.find_tool_by_inventory_name(gbdata.cutting_axe_tools)
            return
        if self.toolname == 'StoneAxe':
            self.find_tool_by_inventory_name(gbdata.stone_axe_tools)
            return
        if self.toolname == 'AnyAxe':
            self.find_tool_by_inventory_name(gbdata.axe_tools)
            return
        if self.toolname == 'AnyAxeShovel':
            self.find_tool_by_inventory_name(gbdata.axe_shovel_tools)
            return
        if self.toolname == 'Net':
            self.find_tool_by_inventory_name(gbdata.net_tools)
            return
        if self.toolname == 'Shovel':
            self.find_tool_by_inventory_name(gbdata.shovel_tools)
            return
        if self.toolname == 'WateringCan':
            self.find_tool_by_inventory_name(['InvWateringCan'])
            return
        if self.toolname == 'GoldWateringCan':
            self.find_tool_by_inventory_name(['InvGoldWateringCan'])
            return
        if self.toolname == 'Slingshot':
            self.find_tool_by_inventory_name(['InvSlingshot'])
            return
        if self.toolname == 'FishingPole':
            self.find_tool_by_inventory_name(['InvFishingPole'])
            return
        if self.toolname == 'Pole':
            self.find_tool_by_inventory_name(['InvPole'])
            return
        if self.toolname == 'Ladder':
            self.find_tool_by_inventory_name(['InvLadder'])
            return

        print(name,"not found")
        self.step=4 # close inventory
        return

    def find_tool_and_pointer(self):
        # Find the inventory size.
        gbstate.draw_inventory_locations=True

        tasktakeinventory.determine_slots_bubble()

        # Find the tool
        self.find_tool()
        # If not on step 0 still, then tool was not found.
        if self.step != 0:
            return;
        # Find the slot number for the tool.
        # match is [name,score,cx,cy,bx,by]
        slot=gbscreen.find_inventory_slot(self.match[2],self.match[3])
        print("slot is",slot)
        if slot is None:
            print("slot not found")
            self.step=4 # close inventory
            return
        self.tool_slot=slot

        # find the pointer hand
        hand_match=gbscreen.has_label_in_box('PointerHand',self.ratio,gbdata.inventory_sx1,gbdata.inventory_sx2,gbdata.inventory_sy1,gbdata.inventory_sy2)
        if hand_match is None:
            print("hand not found")
            #self.step=4 # close inventory
            # move the pointer to the right and try again
            self.parent.Push(taskdetect.TaskDetect())
            self.parent.Push(taskobject.TaskTimed(self.move_wait)) # wait for animation
            self.parent.Push(taskpress.TaskPress('hat_RIGHT'))
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
            self.step=4 # close inventory
            return
        self.hand_slot=hand_slot

        self.step=1 # move the pointer hand

    def move_pointer_hand(self):
        if self.tool_slot == self.hand_slot:
            print("pointing at tool")
            self.step=2 # select tool
            return
        if self.tool_slot <= 9:
            if self.hand_slot <= 9:
                if self.hand_slot < self.tool_slot:
                    # move pointer hand right
                    self.hand_slot+=1
                    self.parent.Push(taskobject.TaskTimed(self.move_wait)) # wait for animation
                    self.parent.Push(taskpress.TaskPress('hat_RIGHT'))
                    return
                # move pointer hand left
                self.hand_slot-=1
                self.parent.Push(taskobject.TaskTimed(self.move_wait)) # wait for animation
                self.parent.Push(taskpress.TaskPress('hat_LEFT'))
                return
            # move pointer hand up
            self.hand_slot-=10
            self.parent.Push(taskobject.TaskTimed(self.move_wait)) # wait for animation
            self.parent.Push(taskpress.TaskPress('hat_TOP'))
            return
        if self.tool_slot <= 19:
            if self.hand_slot <= 9:
                # move pointer hand down
                self.hand_slot+=10
                self.parent.Push(taskobject.TaskTimed(self.move_wait)) # wait for animation
                self.parent.Push(taskpress.TaskPress('hat_BOTTOM'))
                return
            if self.hand_slot <= 19:
                if self.hand_slot < self.tool_slot:
                    # move pointer hand right
                    self.hand_slot+=1
                    self.parent.Push(taskobject.TaskTimed(self.move_wait)) # wait for animation
                    self.parent.Push(taskpress.TaskPress('hat_RIGHT'))
                    return
                # move pointer hand left
                self.hand_slot-=1
                self.parent.Push(taskobject.TaskTimed(self.move_wait)) # wait for animation
                self.parent.Push(taskpress.TaskPress('hat_LEFT'))
                return
            # move pointer hand up
            self.hand_slot-=10
            self.parent.Push(taskobject.TaskTimed(self.move_wait)) # wait for animation
            self.parent.Push(taskpress.TaskPress('hat_TOP'))
            return
        if self.tool_slot <= 29:
            if self.hand_slot <= 19:
                # move pointer hand down
                self.hand_slot+=10
                self.parent.Push(taskobject.TaskTimed(self.move_wait)) # wait for animation
                self.parent.Push(taskpress.TaskPress('hat_BOTTOM'))
                return
            if self.hand_slot <= 29:
                if self.hand_slot < self.tool_slot:
                    # move pointer hand right
                    self.hand_slot+=1
                    self.parent.Push(taskobject.TaskTimed(self.move_wait)) # wait for animation
                    self.parent.Push(taskpress.TaskPress('hat_RIGHT'))
                    return
                # move pointer hand left
                self.hand_slot-=1
                self.parent.Push(taskobject.TaskTimed(self.move_wait)) # wait for animation
                self.parent.Push(taskpress.TaskPress('hat_LEFT'))
                return
            # move pointer hand up
            self.hand_slot-=10
            self.parent.Push(taskobject.TaskTimed(self.move_wait)) # wait for animation
            self.parent.Push(taskpress.TaskPress('hat_TOP'))
            return
        if self.tool_slot <= 39:
            if self.hand_slot <= 29:
                # move pointer hand down
                self.hand_slot+=10
                self.parent.Push(taskobject.TaskTimed(self.move_wait)) # wait for animation
                self.parent.Push(taskpress.TaskPress('hat_BOTTOM'))
                return
            if self.hand_slot <= 39:
                if self.hand_slot < self.tool_slot:
                    # move pointer hand right
                    self.hand_slot+=1
                    self.parent.Push(taskobject.TaskTimed(self.move_wait)) # wait for animation
                    self.parent.Push(taskpress.TaskPress('hat_RIGHT'))
                    return
                # move pointer hand left
                self.hand_slot-=1
                self.parent.Push(taskobject.TaskTimed(self.move_wait)) # wait for animation
                self.parent.Push(taskpress.TaskPress('hat_LEFT'))
                return
            # move pointer hand up
            self.hand_slot-=10
            self.parent.Push(taskobject.TaskTimed(self.move_wait)) # wait for animation
            self.parent.Push(taskpress.TaskPress('hat_TOP'))
            return

        print("slot error")
        self.step=4 # close inventory
        return

    def process_menu(self):
        if gbstate.inventory_size == 20:
            if not gbscreen.has_label('PointerHand',0.30,792,347,10):
                print("no menu pointer hand 1")
                # "clear favorite" is present in menu
                if not gbscreen.has_label('PointerHand',0.30,766,306,10):
                    print("no menu pointer hand 2")
                    if not gbscreen.has_label('PointerHand',0.30,792,307,10):
                        print("no menu pointer hand 3")
                        # Assume there is a menu but the hand wasn't detected.
                        self.parent.Push(taskobject.TaskTimed(1.0)) # wait for menu to pop down
                        self.parent.Push(taskpress.TaskPress('B'))
                        self.step=4 # close inventory
                        return
        elif gbstate.inventory_size == 30:
            if not gbscreen.has_label('PointerHand',0.30,gbdata.inventory_hand_30_x,gbdata.inventory_hand_30_y,10):
                print("no menu pointer hand 4")
                if not gbscreen.has_label('PointerHand',0.30,gbdata.inventory_hand_30_2_x,gbdata.inventory_hand_30_2_y,10):
                    print("no menu pointer hand 5")
                    if not gbscreen.has_label('PointerHand',0.30,gbdata.inventory_hand_30_3_x,gbdata.inventory_hand_30_3_y,10):
                        print("no menu pointer hand 6")
                        # Assume there is a menu but the hand wasn't detected.
                        self.parent.Push(taskobject.TaskTimed(1.0)) # wait for menu to pop down
                        self.parent.Push(taskpress.TaskPress('B'))
                        self.step=4 # close inventory
                        return
        # select the first item in the menu. Hopefully this is "Hold". 
        self.parent.Push(taskobject.TaskTimed(1.0)) # wait for menu to pop down
        self.parent.Push(taskpress.TaskPress('A'))
        gbstate.current_tool=self.toolname
        gbstate.player_heading=180 # down/south
        self.step=4 # close inventory
        return
