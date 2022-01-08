#
# Copyright 2021-2022 by angry-kitten
# Look at the current screen for weeds and pick them.
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
import tasksimplegoto
import gbscreen
import gbdisplay
import random
import taskweed
import tasksearchpattern

class TaskWeedSearch(taskobject.Task):
    """TaskWeedSearch Object"""

    def __init__(self):
        super().__init__()
        self.name="TaskWeedSearch"
        print("new TaskWeedSearch object")

    def Poll(self):
        """check if any action can be taken"""
        print("TaskWeedSearch Poll")
        if not self.started:
            self.Start()
            return
        if self.taskdone:
            return
        if gbstate.frame is None:
            return

        print("TaskWeedSearch done")
        self.taskdone=True
        return

    def Start(self):
        """Cause the task to begin doing whatever."""
        print("TaskWeedSearch Start")
        if self.started:
            return # already started
        self.started=True

        # push tasks in reverse order
        self.parent.Push(tasksearchpattern.TaskSearchPattern(3,self.weedhere))

    def DebugRecursive(self,indent=0):
        self.DebugPrint("TaskWeedSearch",indent)

    def NameRecursive(self):
        gbstate.task_stack_names.append(self.name)
        myname="TaskWeedSearch"
        return myname

    def weedhere(self):
        print("weedhere")
        self.parent.Push(taskweed.TaskWeed())
        self.parent.Push(taskweed.TaskWeed())
        self.parent.Push(taskweed.TaskWeed())
        self.parent.Push(taskweed.TaskWeed())
        self.parent.Push(taskweed.TaskWeed())
