#
# Copyright 2021 by angry-kitten
# Move the player character to a location with path planning.
#

import random
import math

import taskobject
import gbdata
import gbstate
import cv2
import taskpress
import tasksay
import taskdetect
import taskgotomain
import taskupdatemini
import taskjoy
import gbscreen
import gbdisplay
import tasktrackgoto
import tasksimplegoto

class TaskPathPlanGoTo(taskobject.Task):
    """TaskPathPlanGoTo Object"""

    def __init__(self,mx,my):
        super().__init__()
        self.name="TaskPathPlanGoTo"
        print("new",self.name,"object")
        self.target_mx=mx
        self.target_my=my
        print("go to mx",mx,"my",my)
        gbstate.goto_target_mx=mx
        gbstate.goto_target_my=my

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
        self.parent.Push(tasksimplegoto.TaskSimpleGoTo(self.target_mx,self.target_my))

    def DebugRecursive(self,indent=0):
        self.DebugPrint(self.name,indent)

    def NameRecursive(self):
        gbstate.task_stack_names.append(self.name)
        return self.name
