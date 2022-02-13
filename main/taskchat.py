#
# Copyright 2021-2022 by angry-kitten
# Look at the video and see if there is a resident to chat with.
#

import cv2
import gbdata
import gbstate
import gbscreen
import taskobject
import taskpress
import tasksay
import taskdetect
import taskgotomain
import taskupdatemini

class TaskChat(taskobject.Task):
    """TaskChat Object"""

    def __init__(self):
        super().__init__()
        self.name="TaskChat"
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

    def DebugRecursive(self,indent=0):
        self.DebugPrint(self.name,indent)

    def NameRecursive(self):
        gbstate.task_stack_names.append(self.name)
        return self.name
