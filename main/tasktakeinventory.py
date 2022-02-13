#
# Copyright 2021-2022 by angry-kitten
# Open the player inventory and record the items and slots used and free.
#

import gbdata
import gbstate
import gbscreen
import gbdisplay
import taskobject
import taskpress
import taskdetect

class TaskTakeInventory(taskobject.Task):
    """TaskTakeInventory Object"""

    def __init__(self):
        super().__init__()
        self.name="TaskTakeInventory"
        print("new",self.name,"object")
        self.step=0
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
            self.determine_slots()
            return

        if self.step == 1: # the number of slots is known
            self.sort_detections_to_slots()
            self.step=99
            return

        # close the inventory
        self.parent.Push(taskobject.TaskTimed(2.0)) # wait for the inventory to close
        self.parent.Push(taskpress.TaskPress('B'))
        gbstate.draw_inventory_locations=False
        print(self.name,"done")
        self.taskdone=True

    def Start(self):
        """Cause the task to begin doing whatever."""
        print(self.name,"Start")
        if self.started:
            return # already started
        self.started=True
        self.step=0

        # open inventory

        self.parent.Push(taskdetect.TaskDetect())

        # Get the pointer hand out of the way by moving it to the clothing
        # "slot".

        # Try to move the pointer hand right and down to snag it in the clothing
        # "slot".
        for i in range(9):
            #self.parent.Push(taskobject.TaskTimed(0.3)) # wait for animation
            self.parent.Push(taskpress.TaskPress('hat_BOTTOM'))
            #self.parent.Push(taskobject.TaskTimed(0.3)) # wait for animation
            self.parent.Push(taskpress.TaskPress('hat_RIGHT'))

        # Try to move the pointer hand down to take into account the
        # largest inventory size, 40.
        for i in range(4):
            #self.parent.Push(taskobject.TaskTimed(0.3)) # wait for animation
            self.parent.Push(taskpress.TaskPress('hat_BOTTOM'))

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

    def determine_slots(self):
        # Find the inventory size.
        gbstate.draw_inventory_locations=True

        determine_slots_bubble()

        self.step=1 # the number of slots is known

    def sort_detections_to_slots(self):
        if gbstate.detection_lock is None:
            return
        with gbstate.detection_lock:
            if gbstate.digested is None:
                print("no digested")
                self.step=99
                return
            localdigested=gbstate.digested

        slot_array=gbstate.inventory_locations

        gbstate.inventory_name=['' for x in range(gbstate.inventory_size)]
        inventory_det=[None for x in range(gbstate.inventory_size)]
        print("inventory_name",gbstate.inventory_name)
        for det in localdigested:
            print(det) # det is [name,score,cx,cy,bx,by]
            slot=gbscreen.find_inventory_slot(det[2],det[3])
            if slot is not None and slot < gbstate.inventory_size:
                (sx,sy)=slot_array[slot]
                d=gbdisplay.calculate_distance(det[2],det[3],sx,sy)
                if d < 20:
                    previous=inventory_det[slot]
                    if previous is None:
                        inventory_det[slot]=det
                    else:
                        if previous[1] < det[1]:
                            inventory_det[slot]=det

        gbstate.inventory_slots_full=0
        gbstate.inventory_slots_unknown=0
        gbstate.inventory_slots_free=0
        slot=0
        for thing in inventory_det:
            if thing is None:
                #print("unknown")
                gbstate.inventory_slots_unknown+=1
            else:
                name=thing[0]
                gbstate.inventory_name[slot]=name
                #print(f"name=[{name}]")
                if name == 'InvEmpty':
                    gbstate.inventory_slots_free+=1
                    #print("free")
                elif name == '':
                    gbstate.inventory_slots_unknown+=1
                    #print("unknown")
                else:
                    gbstate.inventory_slots_full+=1
                    #print("full")
            slot+=1

        print("inventory_name",gbstate.inventory_name)
        print("inventory_slots_full",gbstate.inventory_slots_full)
        print("inventory_slots_unknown",gbstate.inventory_slots_unknown)
        print("inventory_slots_free",gbstate.inventory_slots_free)

        gbstate.inventory_has_net=False
        gbstate.inventory_has_pole=False
        gbstate.inventory_has_ladder=False
        gbstate.inventory_has_shovel=False
        gbstate.inventory_has_wetsuit=False
        gbstate.inventory_has_fishingpole=False
        gbstate.inventory_has_wateringcan=False
        gbstate.inventory_has_slingshot=False
        gbstate.inventory_has_stoneaxe=False
        gbstate.inventory_has_cuttingaxe=False
        gbstate.inventory_has_axe=False
        for name in gbstate.inventory_name:
            if name is not None:
                if name in gbdata.net_tools:
                    gbstate.inventory_has_net=True
                elif name in gbdata.pole_tools:
                    gbstate.inventory_has_pole=True
                elif name in gbdata.ladder_tools:
                    gbstate.inventory_has_ladder=True
                elif name in gbdata.shovel_tools:
                    gbstate.inventory_has_shovel=True
                elif name in gbdata.wetsuit_tools:
                    gbstate.inventory_has_wetsuit=True
                elif name in gbdata.fishingpole_tools:
                    gbstate.inventory_has_fishingpole=True
                elif name in gbdata.wateringcan_tools:
                    gbstate.inventory_has_wateringcan=True
                elif name in gbdata.slingshot_tools:
                    gbstate.inventory_has_slingshot=True
                else:
                    # Some of what is left can be in multiple lists.
                    if name in gbdata.stone_axe_tools:
                        gbstate.inventory_has_stoneaxe=True
                    if name in gbdata.cutting_axe_tools:
                        gbstate.inventory_has_cuttingaxe=True
                    if name in gbdata.axe_tools:
                        gbstate.inventory_has_axe=True

def determine_slots_bubble():
    # Find the inventory size.
    if gbstate.inventory_size < 10:
        gbstate.inventory_size=20
        gbstate.inventory_locations=gbdata.inventory_locations_20

    w=gbdata.stdscreen_size[0]
    sx=int(round(w/2))

    top_sy=gbscreen.locate_vertical_transition(gbdata.inventory_bubble_color,sx,gbdata.inventory_bubble_40_top_sy-gbdata.inventory_bubble_range,gbdata.inventory_bubble_20_top_sy+gbdata.inventory_bubble_range)
    bottom_sy=gbscreen.locate_vertical_transition(gbdata.inventory_bubble_color,sx,gbdata.inventory_bubble_20_bottom_sy-gbdata.inventory_bubble_range,gbdata.inventory_bubble_40_bottom_sy+gbdata.inventory_bubble_range)

    if gbscreen.match_within(top_sy,gbdata.inventory_bubble_20_top_sy,gbdata.inventory_bubble_range) and gbscreen.match_within(bottom_sy,gbdata.inventory_bubble_20_bottom_sy,gbdata.inventory_bubble_range):
        gbstate.inventory_size=20
        gbstate.inventory_locations=gbdata.inventory_locations_20
    elif gbscreen.match_within(top_sy,gbdata.inventory_bubble_30_top_sy,gbdata.inventory_bubble_range) and gbscreen.match_within(bottom_sy,gbdata.inventory_bubble_30_bottom_sy,gbdata.inventory_bubble_range):
        gbstate.inventory_size=30
        gbstate.inventory_locations=gbdata.inventory_locations_30
    elif gbscreen.match_within(top_sy,gbdata.inventory_bubble_40_top_sy,gbdata.inventory_bubble_range) and gbscreen.match_within(bottom_sy,gbdata.inventory_bubble_40_bottom_sy,gbdata.inventory_bubble_range):
        gbstate.inventory_size=40
        gbstate.inventory_locations=gbdata.inventory_locations_40
    return
