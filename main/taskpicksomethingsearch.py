#
# Copyright 2021 by angry-kitten
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
import taskpicksomething

class TaskPickSomethingSearch(taskobject.Task):
    """TaskPickSomethingSearch Object"""

    def __init__(self):
        super().__init__()
        self.name="TaskPickSomethingSearch"
        print("new TaskPickSomethingSearch object")

    def Poll(self):
        """check if any action can be taken"""
        print("TaskPickSomethingSearch Poll")
        if not self.started:
            self.Start()
            return
        if self.taskdone:
            return
        if gbstate.frame is None:
            return

        print("TaskPickSomethingSearch done")
        self.taskdone=True
        return

    def Start(self):
        """Cause the task to begin doing whatever."""
        print("TaskPickSomethingSearch Start")
        if self.started:
            return # already started
        self.started=True

        # push tasks in reverse order
        self.parent.Push(tasksearchpattern.TaskSearchPattern(2,self.picksomething))

    def DebugRecursive(self,indent=0):
        self.DebugPrint("TaskPickSomethingSearch",indent)

    def NameRecursive(self):
        gbstate.task_stack_names.append(self.name)
        myname="TaskPickSomethingSearch"
        return myname

    def picksomething(self):
        print("picksomething")
        self.parent.Push(taskpicksomething.TaskPickSomething())
        self.parent.Push(taskpicksomething.TaskPickSomething())
        self.parent.Push(taskpicksomething.TaskPickSomething())
        self.parent.Push(taskpicksomething.TaskPickSomething())
