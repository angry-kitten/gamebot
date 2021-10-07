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
        self.limit=100
        self.counter=0
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
                gbstate.goto_target_mx=-1
                gbstate.goto_target_my=-1
                print("TaskSimpleGoTo done")
                self.taskdone=True
                return

        if self.counter >= self.limit:
            print("over count")
            gbstate.goto_target_mx=-1
            gbstate.goto_target_my=-1
            print("TaskSimpleGoTo done")
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
            seconds=self.distance_to_time(distance)
            if seconds > 2:
                seconds=2
            print("seconds",seconds)
            # move for up to 2 seconds over a total of 3 seconds
            self.parent.Push(taskjoy.TaskJoyLeft(heading,1.0,3.0,int(seconds*1000)))
            return

        gbstate.goto_target_mx=-1
        gbstate.goto_target_my=-1
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

    def DebugRecursive(self,indent=0):
        self.DebugPrint("TaskSimpleGoTo",indent)

    def distance_to_time(self,distance):
        print("distance_to_time",distance)
        ttd=gbdata.time_to_distance
        entries=len(ttd)
        for j in range(entries-1):
            a=ttd[j]
            b=ttd[j+1]
            if distance > a[1]:
                t=a[0]*(distance/a[1])
                print("t",t)
                return t
            if distance == a[1]:
                t=a[0]
                print("t",t)
                return t
            if distance == b[1]:
                t=b[0]
                print("t",t)
                return t
            if a[1] <= distance and distance <= b[1]:
                dt=a[0]-b[0]
                dd=a[1]-b[1]
                pd=distance-b[1]
                t=b[0]+((dt/dd)*pd)
                print("t",t)
                return t
        t=0
        print("t",t)
        return t
