#
# Copyright 2021-2022 by angry-kitten
# Gather an item with 'Y' and check for pockets full.
#

import random
import cv2
import gbdata
import gbstate
import gbscreen
import gbdisplay
import taskobject
import taskpress
import tasksay
import taskdetect
import taskgotomain
import taskupdatemini
import taskrandomwalk
import tasksimplegoto
import taskpathplangoto
import taskcenterplayer
import taskstore
import tasksell
import taskmuseum
import tasktrackturn
import tasktakeinventory

class TaskPickup(taskobject.Task):
    """TaskPickup Object"""

    def __init__(self):
        super().__init__()
        self.name="TaskPickup"
        #print("new",self.name,"object")
        self.target_mx=gbstate.player_mx
        self.target_my=gbstate.player_my

    def Poll(self):
        """check if any action can be taken"""
        #print(self.name,"Poll")
        if not self.started:
            self.Start()
            return
        if self.taskdone:
            return
        if gbstate.frame is None:
            return

        # Look for a continue triangle. If it is present then
        # it is likely a pockets full case.
        #if gbscreen.is_continue_triangle_detect():
        #    print("continue triangle detect")
        #    self.handle_pockets_full()
        if gbscreen.is_continue_triangle():
            #print("continue triangle")
            self.handle_pockets_full()

        #print(self.name,"done")
        self.taskdone=True
        return

    def Start(self):
        """Cause the task to begin doing whatever."""
        #print(self.name,"Start")
        if self.started:
            return # already started
        self.started=True
        self.target_mx=gbstate.player_mx
        self.target_my=gbstate.player_my
        # push tasks in reverse order
        #self.parent.Push(taskdetect.TaskDetect())
        self.parent.Push(taskobject.TaskTimed(2.0)) # wait for the animation
        self.parent.Push(taskpress.TaskPress('Y')) # pick up the item

    def DebugRecursive(self,indent=0):
        self.DebugPrint(self.name,indent)

    def NameRecursive(self):
        gbstate.task_stack_names.append(self.name)
        return self.name

    def handle_pockets_full(self):

        if self.target_mx >= 0:
            # Go back to the original location.
            self.parent.Push(taskpathplangoto.TaskPathPlanGoTo(self.target_mx,self.target_my))

        self.parent.Push(tasktakeinventory.TaskTakeInventory())
        self.parent.Push(tasksell.TaskSell())
        self.parent.Push(tasktakeinventory.TaskTakeInventory())
        self.parent.Push(taskstore.TaskStore())
        self.parent.Push(tasktakeinventory.TaskTakeInventory())
        self.parent.Push(taskmuseum.TaskMuseum())

        self.parent.Push(taskobject.TaskTimed(1.0)) # wait for the animation
        # press A to select 'drop it'
        self.parent.Push(taskpress.TaskPress('A'))
        self.parent.Push(taskobject.TaskTimed(1.0)) # wait for the animation
        # move the pointer hand down to 'drop it'
        self.parent.Push(taskpress.TaskPress('hat_BOTTOM'))
        self.parent.Push(taskobject.TaskTimed(1.0)) # wait for the animation
        # press B to continue
        self.parent.Push(taskpress.TaskPress('B'))

class TaskPickupSpin(taskobject.Task):
    """TaskPickupSpin Object"""

    def __init__(self):
        super().__init__()
        self.name="TaskPickupSpin"
        #print("new",self.name,"object")
        return

    def Poll(self):
        """check if any action can be taken"""
        #print(self.name,"Poll")
        if not self.started:
            self.Start()
            return
        if self.taskdone:
            return
        if gbstate.frame is None:
            return

        #print(self.name,"done")
        self.taskdone=True
        return

    def Start(self):
        """Cause the task to begin doing whatever."""
        #print(self.name,"Start")
        if self.started:
            return # already started
        self.started=True
        # push tasks in reverse order

        for heading in range(0,360,45):
            self.parent.Push(TaskPickup())
            self.parent.Push(tasktrackturn.TaskTrackTurn(heading))
        return

    def DebugRecursive(self,indent=0):
        self.DebugPrint(self.name,indent)
        return

    def NameRecursive(self):
        gbstate.task_stack_names.append(self.name)
        return self.name
