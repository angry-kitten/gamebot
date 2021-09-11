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

class TaskSimpleGoTo(taskobject.Task):
    """TaskSimpleGoTo Object"""

    def __init__(self,mx,my):
        super().__init__()
        print("new TaskSimpleGoTo object")
        self.target_mx=mx
        self.target_my=my
        print("go to mx",mx,"my",my)
        self.within=0.1
        self.previous_mx=-1
        self.previous_my=-1

    def Poll(self):
        """check if any action can be taken"""
        print("TaskSimpleGoTo Poll")
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
                print("TaskSimpleGoTo done")
                self.taskdone=True
                return

        self.previous_mx=mx
        self.previous_my=my

        if (not gbscreen.match_within(mx,self.target_mx,self.within)) or (not gbscreen.match_within(my,self.target_my,self.within)):
            # Keep going.
            dx=self.target_mx-mx
            dy=self.target_my-my
            print("dx dy",dx,dy)
            distance=math.sqrt(dx*dx+dy*dy)
            print("distance",distance)
            if dy == 0:
                heading=0
            else:
                rawheading=math.degrees(math.atan(dx/dy))
                print("rawheading",rawheading)
                if dx > 0 and dy > 0:
                    heading=180-rawheading
                elif dx > 0 and dy < 0:
                    heading=-rawheading
                elif dx < 0 and dy > 0:
                    heading=180-rawheading
                else:
                    heading=360-rawheading
            print("heading",heading)

            self.parent.Push(taskupdatemini.TaskUpdateMini())
            self.parent.Push(taskobject.TaskTimed()) # default 1 second delay
            self.parent.Push(taskdetect.TaskDetect())
            seconds=distance/10
            if seconds > .5:
                seconds=.5
            print("seconds",seconds)
            # move for up to 2 seconds over a total of 3 seconds
            self.parent.Push(taskjoy.TaskJoyLeft(heading,1.0,3.0,int(seconds*1000)))
            return

        print("TaskSimpleGoTo done")
        self.taskdone=True
        return

    def Start(self):
        """Cause the task to begin doing whatever."""
        print("TaskSimpleGoTo Start")
        if self.started:
            return # already started
        self.started=True
        self.parent.Push(taskupdatemini.TaskUpdateMini())
        self.parent.Push(taskobject.TaskTimed()) # default 1 second delay
        self.parent.Push(taskdetect.TaskDetect())

    def DebugRecursive(self,indent=0):
        self.DebugPrint("TaskSimpleGoTo",indent)
