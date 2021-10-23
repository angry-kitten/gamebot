#
# Copyright 2021 by angry-kitten
# Look at the current screen and capture the phone map and
# determine player location from the pin.
#

import time
import taskobject
import gbdata
import gbstate
import cv2
import taskpress
import tasksay
import taskdetect
import taskgotomain
import gbscreen
import gbtrack
import taskupdatemini
import taskupdatephonemap

class TaskDeterminePosition(taskobject.Task):
    """TaskDeterminePosition Object"""

    def __init__(self):
        super().__init__()
        self.name="TaskDeterminePosition"
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

        gbstate.move_since_determine=False

        print(self.name,"done")
        self.taskdone=True
        return

    def Start(self):
        """Cause the task to begin doing whatever."""
        print(self.name,"Start")
        if self.started:
            return # already started
        self.started=True

        if not gbstate.move_since_determine:
            return

        self.parent.Push(taskupdatephonemap.TaskUpdatePhoneMap())
        self.parent.Push(taskupdatemini.TaskUpdateMini())

    def DebugRecursive(self,indent=0):
        self.DebugPrint(self.name,indent)

    def NameRecursive(self):
        gbstate.task_stack_names.append(self.name)
        return self.name
