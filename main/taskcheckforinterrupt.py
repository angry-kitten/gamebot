#
# Copyright 2021 by angry-kitten
# Look at the video and see if there is an interrupt with a continue
# triangle that needs to be acknowledged.
#

import taskobject
import gbdata
import gbstate
import cv2
import taskpress
import tasksay
import taskdetect
import taskgotomain
import taskupdatemini
import gbscreen
import taskchat
import taskmuseum
import tasksell
import taskstore

class TaskCheckForInterrupt(taskobject.Task):
    """TaskCheckForInterrupt Object"""

    def __init__(self):
        super().__init__()
        self.name="TaskCheckForInterrupt"
        print("new",self.name,"object")

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

        if gbscreen.is_continue_triangle_detect():
            # maybe announcements
            print("continue triangle detect")
            self.parent.Push(taskdetect.TaskDetect())
            # press B to continue
            self.parent.Push(taskpress.TaskPress('B',5.0))
            return
        if gbscreen.is_continue_triangle():
            # maybe announcements
            print("continue triangle")
            self.parent.Push(taskdetect.TaskDetect())
            # press B to continue
            self.parent.Push(taskpress.TaskPress('B',5.0))
            return
        if gbscreen.is_accept_controller_screen():
            # power hits cause this
            print("accept controller screen")
            self.parent.Push(taskdetect.TaskDetect())
            # press A to accept
            self.parent.Push(taskpress.TaskPress('A',5.0))
            return

        if gbscreen.is_main_screen():
            print("main screen")

            if gbscreen.is_resident_nearby():
                self.parent.Push(taskchat.TaskChat())
                return

            if gbstate.inventory_slots_full == gbstate.inventory_size:
                self.parent.Push(taskmuseum.TaskMuseum())
                self.parent.Push(tasksell.TaskSell())
                self.parent.Push(taskstore.TaskStore())
                return

            if gbstate.inventory_slots_full > 0 and gbstate.inventory_slots_free == 0:
                self.parent.Push(taskmuseum.TaskMuseum())
                self.parent.Push(tasksell.TaskSell())
                self.parent.Push(taskstore.TaskStore())
                return

            print(self.name,"done")
            self.taskdone=True
            return

        self.parent.Push(taskdetect.TaskDetect())
        return

    def Start(self):
        """Cause the task to begin doing whatever."""
        print(self.name,"Start")
        if self.started:
            return # already started
        self.started=True
        # push tasks in reverse order
        self.parent.Push(taskdetect.TaskDetect())

    def DebugRecursive(self,indent=0):
        self.DebugPrint(self.name,indent)

    def NameRecursive(self):
        gbstate.task_stack_names.append(self.name)
        return self.name
