#
# Copyright 2021 by angry-kitten
# Look at the video at startup and see what the current screen is.
# Move to the main playing screen.
#

import taskobject
import gbdata
import gbstate
import cv2
import taskpress
import tasksay
import taskdetect
import taskgotomain

class TaskTakeStock(taskobject.Task):
    """TaskTakeStock Object"""

    def __init__(self):
        super().__init__()
        print("new TaskTakeStock object")

    def Poll(self):
        """check if any action can be taken"""
        print("TaskTakeStock Poll")
        if not self.started:
            self.Start()
            return
        if self.taskdone:
            return
        if gbstate.frame is None:
            return

        print("TaskTakeStock done")
        self.taskdone=True
        return

    def Start(self):
        """Cause the task to begin doing whatever."""
        print("TaskTakeStock Start")
        if self.started:
            return # already started
        self.started=True
        # push tasks in reverse order
        #self.parent.Push(tasksay.TaskSay(gbstate.ps,"gamebot"))
        self.parent.Push(taskgotomain.TaskGoToMain())

    def DebugRecursive(self,indent=0):
        self.DebugPrint("TaskTakeStock",indent)
