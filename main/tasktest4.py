#
# Copyright 2021-2022 by angry-kitten
# Run a test (varies over time)  Test turn delay.
#

import random
import math
import cv2

import gbdata
import gbstate
import gbtrack
import taskobject
import taskpress
import tasksay
import taskdetect
import taskgotomain
import taskupdatemini
import taskjoy
import tasktrackgoto

class TaskTest4(taskobject.Task):
    """TaskTest4 Object"""

    def __init__(self):
        super().__init__()
        self.name="TaskTest4"
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

        #heading=90+45
        heading=90
        #seconds=0.050
        #seconds=1.0
        #seconds=0.5
        #seconds=0.4
        #seconds=0.3
        seconds=0.2 # 45 degrees

        #extent=0.5
        #extent=0.1
        #extent=0.01 no movement
        #extent=0.05 # too much movement
        #extent=0.03 # too much
        #extent=0.02 # no movement
        extent=0.03
        print("seconds",seconds)
        msec=int(seconds*1000) # how long to activate the joystick in milliseconds
        total_sec=1+seconds # the total time for the joystick task
        self.parent.Push(taskjoy.TaskJoyLeft(heading,extent,total_sec,msec))

    def DebugRecursive(self,indent=0):
        self.DebugPrint(self.name,indent)

    def NameRecursive(self):
        gbstate.task_stack_names.append(self.name)
        return self.name
