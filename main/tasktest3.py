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

class TaskTest3(taskobject.Task):
    """TaskTest3 Object"""

    def __init__(self):
        super().__init__()
        self.name="TaskTest3"
        print("new",self.name,"object")
        self.iterations=10
        self.i=0
        self.stepsize=5
        #self.turn_delay=0.5 # seconds
        #self.turn_delay=0.3 # seconds
        #self.turn_delay=0.25 # seconds
        #self.turn_delay=0.275 # seconds
        #self.turn_delay=0.280 # seconds
        self.turn_delay=0.285 # seconds

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

        if gbstate.position_minimap_x < 0:
            print("bad position")
            print(self.name,"done")
            self.taskdone=True
            return

        self.i+=1
        if self.i < self.iterations:
            self.setup_one_round()
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

        self.setup_one_round()

    def DebugRecursive(self,indent=0):
        self.DebugPrint(self.name,indent)

    def NameRecursive(self):
        gbstate.task_stack_names.append(self.name)
        return self.name

    def setup_one_round(self):
        # Go right back to start.
        mx=gbstate.position_minimap_x
        my=gbstate.position_minimap_y
        self.parent.Push(tasktrackgoto.TaskTrackGoTo(mx,my))

        # Time delay to evaluate position.
        self.parent.Push(taskobject.TaskTimed(10.0))

        # Try turn delay.
        seconds=self.turn_delay
        print("seconds",seconds)
        msec=int(seconds*1000) # how long to activate the joystick in milliseconds
        total_sec=1+seconds # the total time for the joystick task
        heading=90 # right
        self.parent.Push(taskjoy.TaskJoyLeft(heading,1.0,total_sec,msec))

        # Time delay to evaluate position.
        self.parent.Push(taskobject.TaskTimed(5.0))

        # Go left.
        mx=gbstate.position_minimap_x
        my=gbstate.position_minimap_y
        mx-=self.stepsize
        self.parent.Push(tasktrackgoto.TaskTrackGoTo(mx,my))
