#
# Copyright 2021-2022 by angry-kitten
# Look at the current screen and capture the phone map and
# determine player location from the pin.
#

import time
import cv2
import gbdata
import gbstate
import gbscreen
import gbtrack
import taskobject
import taskpress
import tasksay
import taskdetect
import taskgotomain
import taskupdatemini
import taskupdatephonemap

class TaskDeterminePosition(taskobject.Task):
    """TaskDeterminePosition Object"""

    def __init__(self,low_precision=False):
        super().__init__()
        self.name="TaskDeterminePosition"
        #print("new",self.name,"object")
        self.low_precision=low_precision

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

        gbstate.move_since_determine=False

        #print(self.name,"done")
        self.taskdone=True
        return

    def Start(self):
        """Cause the task to begin doing whatever."""
        #print(self.name,"Start")
        if self.started:
            return # already started
        self.started=True

        if not gbstate.move_since_determine:
            return

        if not self.low_precision:
            self.parent.Push(taskupdatephonemap.TaskUpdatePhoneMap())
        self.parent.Push(taskupdatemini.TaskUpdateMini())

    def DebugRecursive(self,indent=0):
        self.DebugPrint(self.name,indent)

    def NameRecursive(self):
        gbstate.task_stack_names.append(self.name)
        return self.name
