#
# Copyright 2021 by angry-kitten
# Pick something for the character to do.
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
import taskrandomwalk
import taskweed

class TaskDoSomething(taskobject.Task):
    """TaskDoSomething Object"""

    def __init__(self):
        super().__init__()
        print("new TaskDoSomething object")

    def Poll(self):
        """check if any action can be taken"""
        print("TaskDoSomething Poll")
        if not self.started:
            self.Start()
            return
        if self.taskdone:
            return
        if gbstate.frame is None:
            return

        self.parent.Push(taskrandomwalk.TaskRandomWalk())
        self.parent.Push(taskweed.TaskWeed())
        return

    def Start(self):
        """Cause the task to begin doing whatever."""
        print("TaskDoSomething Start")
        if self.started:
            return # already started
        self.started=True

    def DebugRecursive(self,indent=0):
        self.DebugPrint("TaskDoSomething",indent)
