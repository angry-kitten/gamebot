#
# Copyright 2021 by angry-kitten
# Move the player character in a random direction for a random distance.
#

import random

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

class TaskRandomWalk(taskobject.Task):
    """TaskRandomWalk Object"""

    def __init__(self):
        super().__init__()
        print("new TaskRandomWalk object")

    def Poll(self):
        """check if any action can be taken"""
        print("TaskRandomWalk Poll")
        if not self.started:
            self.Start()
            return
        if self.taskdone:
            return
        if gbstate.frame is None:
            return

        print("TaskRandomWalk done")
        self.taskdone=True
        return

    def Start(self):
        """Cause the task to begin doing whatever."""
        print("TaskRandomWalk Start")
        if self.started:
            return # already started
        self.started=True
        # TODO expand this later
        #direction=random.randint(0,3)
        #if 0 == direction:
        #    press='left_joy_right'
        #elif 1 == direction:
        #    press='left_joy_left'
        #elif 2 == direction:
        #    press='left_joy_up'
        #else:
        #    press='left_joy_down'
        #self.parent.Push(taskpress.TaskPress(press,5.0,500))
        heading=random.randint(0,360)
        extent=random.randint(0,100)/100
        print(heading,extent)
        # move for 2 seconds over a total of 3 seconds
        self.parent.Push(taskjoy.TaskJoyLeft(heading,extent,3.0,2000))
        self.taskdone=True

    def DebugRecursive(self,indent=0):
        self.DebugPrint("TaskRandomWalk",indent)
