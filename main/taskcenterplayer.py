#
# Copyright 2021 by angry-kitten
# Center the player character on the screen.
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
import tasktrackgoto
import gbtrack

class TaskCenterPlayer(taskobject.Task):
    """TaskCenterPlayer Object"""

    def __init__(self):
        super().__init__()
        self.name="TaskCenterPlayer"
        print("new",self.name,"object")
        self.stepsize=7

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

        if gbstate.position_minimap_x < 0:
            print("minimap position not set")
            print(self.name,"done")
            self.taskdone=True
            return

        if self.maybe_go(1,0): # right
            return
        if self.maybe_go(-1,0): # left
            return
        if self.maybe_go(0,1): # down
            return
        if self.maybe_go(0,-1): # up
            return

    def DebugRecursive(self,indent=0):
        self.DebugPrint(self.name,indent)

    def NameRecursive(self):
        gbstate.task_stack_names.append(self.name)
        return self.name

    def maybe_go(self,dmx,dmy):

        start_mx=gbstate.position_minimap_x
        start_my=gbstate.position_minimap_y
        start_mx=int(round(start_mx))
        start_my=int(round(start_my))

        # check for obstructions and water
        for j in range(self.stepsize):
            mx=start_mx
            my=start_my
            mx+=dmx*j
            my+=dmy*j
            v=gbstate.obstructionmap[mx][my]
            if v == gbdata.obstruction_maptype_obstructed:
                return False
            if v == gbdata.obstruction_maptype_standing_on_water:
                return False
            v=gbstate.minimap[mx][my]
            if v == gbdata.maptype_water:
                return False

        # Go right back to start.
        self.parent.Push(tasktrackgoto.TaskTrackGoTo(start_mx,start_my))

        # Go away from start.
        self.parent.Push(tasktrackgoto.TaskTrackGoTo(mx,my))

        return True
