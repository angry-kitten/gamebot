#
# Copyright 2021-2022 by angry-kitten
# Look at the video at startup and see what the current screen is.
# Move to the main playing screen.
#

import cv2
import gbdata, gbstate
import taskobject
import taskpress
import tasksay
import taskdetect
import taskgotomain
import taskupdatemini
import taskupdatephonemap
import tasktakeinventory
import taskcheckforinterrupt
import tasksaverestart

class TaskTakeStock(taskobject.Task):
    """TaskTakeStock Object"""

    def __init__(self):
        super().__init__()
        self.name="TaskTakeStock"
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
        #self.parent.Push(tasksay.TaskSay("gamebot"))
        self.parent.Push(taskcheckforinterrupt.TaskCheckForInterrupt())
        self.parent.Push(tasktakeinventory.TaskTakeInventory())
        self.parent.Push(taskupdatephonemap.TaskUpdatePhoneMap())
        self.parent.Push(taskupdatemini.TaskUpdateMini())
        #self.parent.Push(tasksaverestart.TaskSaveRestart())
        self.parent.Push(taskgotomain.TaskGoToMain())

    def DebugRecursive(self,indent=0):
        self.DebugPrint("TaskTakeStock",indent)

    def NameRecursive(self):
        gbstate.task_stack_names.append(self.name)
        myname="TaskTakeStock"
        return myname
