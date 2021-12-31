#
# Copyright 2021 by angry-kitten
# Move the player character to turn to face a heading clockwise or counterclockwise.
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
import taskdetermineposition
import taskpause

class TaskTrackTurn(taskobject.Task):
    """TaskTrackTurn Object"""

    def __init__(self,heading,clockwise=False,counterclockwise=False):
        super().__init__()
        self.name="TaskTrackTurn"
        #print("new",self.name,"object")
        self.heading=heading
        self.arg_clockwise=clockwise
        self.arg_counterclockwise=counterclockwise

    def Poll(self):
        """check if any action can be taken"""
        #print(self.name,"Poll")
        if not self.started:
            self.Start()
            return
        if self.taskdone:
            return
        if gbstate.frame is None:
            return

        gbstate.player_heading=self.heading
        #print(self.name,"done")
        self.taskdone=True
        return

    def Start(self):
        """Cause the task to begin doing whatever."""
        #print(self.name,"Start")
        if self.started:
            return # already started
        self.started=True

        previous_heading=gbstate.player_heading

        if self.heading == previous_heading:
            return;

        heading_change=self.heading-previous_heading
        #print("heading_change",heading_change)

        if heading_change >= 360:
            heading_change-=360
            #print("heading_change",heading_change)
        elif heading_change <= -360:
            heading_change+=360
            #print("heading_change",heading_change)

        if heading_change == 0:
            return;

        # Pick the short way around as the default.
        clockwise=True
        if heading_change >= 0:
            if heading_change <= 180:
                clockwise=True
            else:
                clockwise=False
        else:
            hc=-heading_change
            if hc <= 180:
                clockwise=False
            else:
                clockwise=True

        # Override the default if the caller wants a specific direction.
        if self.arg_clockwise:
            clockwise=True
        elif self.arg_counterclockwise:
            clockwise=False

        #if clockwise:
        #    print("clockwise")
        #else:
        #    print("counterclockwise")

        # We need to push the movements in reverse order. Build a list
        # and then run through it in reverse.
        movement_list=[]

        if heading_change > 0:
            # This would be the heading change if going clockwise.
            if clockwise:
                #print("clockwise")
                heading_change_left=heading_change
                head_to=previous_heading
                while heading_change_left > 90:
                    #print("heading_change_left",heading_change_left)
                    head_to+=90
                    if head_to >= 360:
                        head_to-=360
                    movement_list.append([90,head_to])
                    heading_change_left-=90
                #print("heading_change_left",heading_change_left)
                head_to+=heading_change_left
                if head_to >= 360:
                    head_to-=360
                movement_list.append([heading_change_left,head_to])
            else:
                #print("counterclockwise")
                heading_change=360-heading_change
                #print("heading_change",heading_change)
                heading_change_left=heading_change
                head_to=previous_heading
                while heading_change_left > 90:
                    #print("heading_change_left",heading_change_left)
                    head_to-=90
                    if head_to < 0:
                        head_to+=360
                    movement_list.append([90,head_to])
                    heading_change_left-=90
                #print("heading_change_left",heading_change_left)
                head_to-=heading_change_left
                if head_to < 0:
                    head_to+=360
                movement_list.append([heading_change_left,head_to])
        else:
            # This would be the heading change if going counterclockwise.
            heading_change=-heading_change
            #print("heading_change",heading_change)
            if clockwise:
                #print("clockwise")
                heading_change=360-heading_change
                #print("heading_change",heading_change)
                heading_change_left=heading_change
                head_to=previous_heading
                while heading_change_left > 90:
                    #print("heading_change_left",heading_change_left)
                    head_to+=90
                    if head_to >= 360:
                        head_to-=360
                    movement_list.append([90,head_to])
                    heading_change_left-=90
                #print("heading_change_left",heading_change_left)
                head_to+=heading_change_left
                if head_to >= 360:
                    head_to-=360
                movement_list.append([heading_change_left,head_to])
            else:
                #print("counterclockwise")
                heading_change_left=heading_change
                head_to=previous_heading
                while heading_change_left > 90:
                    #print("heading_change_left",heading_change_left)
                    head_to-=90
                    if head_to < 0:
                        head_to+=360
                    movement_list.append([90,head_to])
                    heading_change_left-=90
                #print("heading_change_left",heading_change_left)
                head_to-=heading_change_left
                if head_to < 0:
                    head_to+=360
                movement_list.append([heading_change_left,head_to])

        movement_list.reverse()

        for move in movement_list:
            self.change_amount_to(move[0],move[1])

    def DebugRecursive(self,indent=0):
        self.DebugPrint(self.name,indent)

    def NameRecursive(self):
        gbstate.task_stack_names.append(self.name)
        return self.name

    def change_amount_to(self,heading_change,head_to):
        # 0.2 seconds per 45 degree change
        seconds=(0.2/45)*heading_change
        extent=0.03
        msec=int(seconds*1000) # how long to activate the joystick in milliseconds
        total_sec=1+seconds # the total time for the joystick task
        self.parent.Push(taskjoy.TaskJoyLeft(head_to,extent,total_sec,msec))
