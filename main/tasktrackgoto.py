#
# Copyright 2021 by angry-kitten
# Move the player character to a location with no pathing or object
# avoidance. Track the feet box.
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
import gbtrack

class TaskTrackGoTo(taskobject.Task):
    """TaskTrackGoTo Object"""

    def __init__(self,mx,my):
        super().__init__()
        print("new TaskTrackGoTo object")
        self.target_mx=mx
        self.target_my=my
        print("go to mx",mx,"my",my)
        self.within=0.1
        gbstate.move_before_mx=-1
        gbstate.move_before_my=-1
        gbstate.move_after_mx=-1
        gbstate.move_after_my=-1
        gbstate.track_goto_target_mx=mx
        gbstate.track_goto_target_my=my

    def Poll(self):
        """check if any action can be taken"""
        print("TaskTrackGoTo Poll")
        if not self.started:
            self.Start()
            return
        if self.taskdone:
            return
        if gbstate.frame is None:
            return

        if gbstate.position_minimap_x < 0:
            print("minimap position not set")
            gbstate.track_goto_target_mx=-1
            gbstate.track_goto_target_my=-1
            print("TaskTrackGoTo done")
            self.taskdone=True
            return

        mx=gbstate.position_minimap_x
        my=gbstate.position_minimap_y

        if gbstate.move_before_mx >= 0:
            print("second time")
            gbstate.move_after_mx=mx
            gbstate.move_after_my=my

            self.process_move()

            gbstate.track_goto_target_mx=-1
            gbstate.track_goto_target_my=-1
            print("TaskTrackGoTo done")
            self.taskdone=True
            return

        # this is the first time here
        print("first time")
        gbstate.move_before_mx=mx
        gbstate.move_before_my=my

        dx=self.target_mx-mx
        dy=self.target_my-my
        print("dx dy",dx,dy)
        distance=math.sqrt(dx*dx+dy*dy)
        print("distance",distance)

        heading=gbtrack.calculate_heading(dx,dy)

        self.parent.Push(taskupdatemini.TaskUpdateMini())
        seconds=self.distance_to_time(distance)
        print("seconds",seconds)
        msec=int(seconds*1000) # how long to activate the joystick in milliseconds
        total_sec=1+seconds # the total time for the joystick task
        self.parent.Push(taskjoy.TaskJoyLeft(heading,1.0,total_sec,msec))
        return

    def Start(self):
        """Cause the task to begin doing whatever."""
        print("TaskTrackGoTo Start")
        if self.started:
            return # already started
        self.started=True
        self.parent.Push(taskupdatemini.TaskUpdateMini())

    def DebugRecursive(self,indent=0):
        self.DebugPrint("TaskTrackGoTo",indent)

    def NameRecursive(self):
        myname="TaskTrackGoTo"
        return myname

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

    def process_move(self):
        # See if we reached the target.
        if gbscreen.match_within(gbstate.move_after_mx,self.target_mx,self.within) and gbscreen.match_within(gbstate.move_after_my,self.target_my,self.within):
            gbstate.move_obstructed=False
        else:
            gbstate.move_obstructed=True

        # set center if not already set
        if gbstate.center_mx < 0:
            gbstate.center_mx=gbstate.move_before_mx
            gbstate.center_my=gbstate.move_before_my
            gbstate.center_my-=gbstate.tune_fb_offset_my

        # set the feet box offset if not already set
        if gbstate.feet_box_offset_mx == -2:
            gbstate.feet_box_offset_mx=0
            gbstate.feet_box_offset_my=0

        # calculate the starting center of the feet box
        fbc_mx=gbstate.center_mx+gbstate.feet_box_offset_mx
        fbc_my=gbstate.center_my+gbstate.tune_fb_offset_my+gbstate.feet_box_offset_my

        # calculate the move deltas
        dx=gbstate.move_after_mx-gbstate.move_before_mx
        dy=gbstate.move_after_my-gbstate.move_before_my

        print("dx dy",dx,dy)

        # calculate the feet box sides
        x1=fbc_mx-0.5 # left
        x2=fbc_mx+0.5 # right
        y1=fbc_my-0.5 # top
        y2=fbc_my+0.5 # bottom

        print(x1,x2,y1,y2)

        past_x=0
        past_y=0
        if gbstate.move_after_mx > x2:
            print("moved past the box to the right")
            past_x=gbstate.move_after_mx-x2
        elif gbstate.move_after_mx < x1:
            print("moved past the box to the left")
            past_x=gbstate.move_after_mx-x1
        if gbstate.move_after_my > y2:
            print("moved past the box to the bottom")
            past_y=gbstate.move_after_my-y2
        elif gbstate.move_after_my < y1:
            print("moved past the box to the top")
            past_y=gbstate.move_after_my-y1

        print("past x y",past_x,past_y)

        # the feet box moves to keep the player position inside or on
        fbc2_mx=fbc_mx+past_x
        fbc2_my=fbc_my+past_y

        # calculate the new feet box offset based on the movement
        # if the movement is past the box to the right, the box moves
        # to the left relative to the center of the screen.
        fb_move_x=-(past_x*gbstate.feet_box_ratio_x)
        fb_move_y=-(past_y*gbstate.feet_box_ratio_y)

        print("fb_move x y",fb_move_x,fb_move_y)

        gbstate.feet_box_offset_mx+=fb_move_x
        gbstate.feet_box_offset_my+=fb_move_y

        # bound the movement of the offset of the feet box
        if gbstate.feet_box_offset_mx > 0.5:
            gbstate.feet_box_offset_mx=0.5
        elif gbstate.feet_box_offset_mx < -0.5:
            gbstate.feet_box_offset_mx=-0.5
        if gbstate.feet_box_offset_my > 0.5:
            gbstate.feet_box_offset_my=0.5
        elif gbstate.feet_box_offset_my < -0.5:
            gbstate.feet_box_offset_my=-0.5

        # calculate the new center
        gbstate.center_mx=fbc2_mx-gbstate.feet_box_offset_mx
        gbstate.center_my=(fbc2_my-gbstate.feet_box_offset_my)-gbstate.tune_fb_offset_my

        print("new center",gbstate.center_mx,gbstate.center_my)

        gbstate.move_before_mx=-1
        gbstate.move_before_my=-1
        gbstate.move_after_mx=-1
        gbstate.move_after_my=-1
