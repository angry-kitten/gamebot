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
import taskpicksomething

class TaskPickSomethingSearch(taskobject.Task):
    """TaskPickSomethingSearch Object"""

    def __init__(self):
        super().__init__()
        self.name="TaskPickSomethingSearch"
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

        print(self.name,"done")
        self.taskdone=True
        return

    def Start(self):
        """Cause the task to begin doing whatever."""
        print(self.name,"Start")
        if self.started:
            return # already started
        self.started=True

        # push tasks in reverse order
        self.parent.Push(tasksearchpattern.TaskSearchPattern(3,self.picksomething))

    def DebugRecursive(self,indent=0):
        self.DebugPrint(self.name,indent)

    def NameRecursive(self):
        gbstate.task_stack_names.append(self.name)
        return self.name

    def picksomething(self):
        print("picksomething")
        #self.parent.Push(taskpicksomething.TaskPickSomething())
        #self.parent.Push(taskpicksomething.TaskPickSomething())
        #self.parent.Push(taskpicksomething.TaskPickSomething())
        self.parent.Push(taskpicksomething.TaskPickSomething())
