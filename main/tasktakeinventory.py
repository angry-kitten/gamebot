#
# Copyright 2021 by angry-kitten
# Open the player inventory and record the items and slots used and free.
#

import taskobject
import gbdata
import taskpress
import taskdetect
import gbscreen
import gbstate
import gbdisplay

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
            print("detect was just done")
            self.determine_slots()
            return

        if self.step == 1: # pointer hand should be out of the way
            print("pointer hand out of the way")
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
        self.parent.Push(taskobject.TaskTimed(3.0)) # wait for the inventory to open
        self.parent.Push(taskpress.TaskPress('X'))
        gbstate.draw_inventory_locations=True

    def DebugRecursive(self,indent=0):
        self.DebugPrint(self.name,indent)

    def NameRecursive(self):
        myname=self.name
        gbstate.task_stack_names.append(myname)
        return myname

    def determine_slots(self):
        # Find the inventory size.
        gbstate.draw_inventory_locations=True
        if gbstate.inventory_size < 20:
            gbstate.inventory_size=20

        if gbscreen.has_label('BellBagStar',0.50,gbdata.inventory_bag_20_x,gbdata.inventory_bag_20_y,5):
            gbstate.inventory_size=20
        elif gbscreen.has_label('BellBagStar',0.50,gbdata.inventory_bag_30_x,gbdata.inventory_bag_30_y,5):
            gbstate.inventory_size=30

        # Get the pointer hand out of the way by moving it to the clothing
        # "slot".

        # Try to move the pointer hand right and down to snag it in the clothing
        # "slot".
        for i in range(9):
            self.parent.Push(taskobject.TaskTimed(0.3)) # wait for animation
            self.parent.Push(taskpress.TaskPress('hat_BOTTOM'))
            self.parent.Push(taskobject.TaskTimed(0.3)) # wait for animation
            self.parent.Push(taskpress.TaskPress('hat_RIGHT'))

        # Try to move the pointer hand down four to take into account the
        # largest inventory size, 40.
        for i in range(6):
            self.parent.Push(taskobject.TaskTimed(0.3)) # wait for animation
            self.parent.Push(taskpress.TaskPress('hat_BOTTOM'))

        self.step=1 # pointer hand should be out of the way

    def sort_detections_to_slots(self):
        with gbstate.detection_lock:
            if gbstate.digested is None:
                print("no digested")
                self.step=99
            localdigested=gbstate.digested

        if gbstate.inventory_size == 20:
            slot_array=gbdata.inventory_locations_20
        elif gbstate.inventory_size == 30:
            slot_array=gbdata.inventory_locations_30

        gbstate.inventory_name=['' for x in range(gbstate.inventory_size)]
        inventory_det=[None for x in range(gbstate.inventory_size)]
        print("inventory_name",gbstate.inventory_name)
        for det in localdigested:
            print(det) # det is [name,score,cx,cy,bx,by]
            slot=gbscreen.find_inventory_slot(det[2],det[3])
            if slot is not None:
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
            if thing is not None:
                name=thing[0]
                gbstate.inventory_name[slot]=name
                if name == 'InvEmpty':
                    gbstate.inventory_slots_free+=1
                elif name == '':
                    gbstate.inventory_slots_unknown+=1
                else:
                    gbstate.inventory_slots_full+=1
            slot+=1

        print("inventory_name",gbstate.inventory_name)
        print("inventory_slots_full",gbstate.inventory_slots_full)
        print("inventory_slots_unknown",gbstate.inventory_slots_unknown)
        print("inventory_slots_free",gbstate.inventory_slots_free)
