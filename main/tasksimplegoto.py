#
# Copyright 2021 by angry-kitten
# Move the player character to a location with no pathing or object
# avoidance.
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

class TaskSimpleGoTo(taskobject.Task):
    """TaskSimpleGoTo Object"""

    def __init__(self,mx,my):
        super().__init__()
        self.name="TaskSimpleGoTo"
        print("new",self.name,"object")
        self.limit=100
        self.counter=0
        self.step_distance_limit=4
        self.target_mx=mx
        self.target_my=my
        print("go to mx",mx,"my",my)
        self.within=0.1
        self.previous_mx=-1
        self.previous_my=-1
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

        mx=gbstate.position_minimap_x
        my=gbstate.position_minimap_y

        if self.previous_mx >= 0:
            if self.previous_mx == mx and self.previous_my == my:
                print("stuck")
                gbstate.goto_target_mx=-1
                gbstate.goto_target_my=-1
                print(self.name,"done")
                self.taskdone=True
                return

        if self.counter >= self.limit:
            print("over count")
            gbstate.goto_target_mx=-1
            gbstate.goto_target_my=-1
            print(self.name,"done")
            self.taskdone=True
            return

        self.counter+=1

        self.previous_mx=mx
        self.previous_my=my

        if (not gbscreen.match_within(mx,self.target_mx,self.within)) or (not gbscreen.match_within(my,self.target_my,self.within)):
            # Keep going.
            dx=self.target_mx-mx
            dy=self.target_my-my
            print("dx dy",dx,dy)
            distance=math.sqrt(dx*dx+dy*dy)
            print("distance",distance)

            if distance > self.step_distance_limit:
                distance2=self.step_distance_limit
                ratio=distance2/distance
                dx*=ratio
                dy*=ratio
                distance=distance2
                print("distance",distance)

            step_target_mx=mx+dx
            step_target_my=my+dy

            self.parent.Push(tasktrackgoto.TaskTrackGoTo(step_target_mx,step_target_my))
            return

        gbstate.goto_target_mx=-1
        gbstate.goto_target_my=-1
        print(self.name,"done")
        self.taskdone=True
        return

    def Start(self):
        """Cause the task to begin doing whatever."""
        print(self.name,"Start")
        if self.started:
            return # already started
        self.started=True
        self.parent.Push(taskupdatemini.TaskUpdateMini())

    def DebugRecursive(self,indent=0):
        self.DebugPrint(self.name,indent)

    def NameRecursive(self):
        gbstate.task_stack_names.append(self.name)
        return self.name
