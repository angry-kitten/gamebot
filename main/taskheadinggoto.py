#
# Copyright 2021-2022 by angry-kitten
# Move the player character to a location with no pathing or object
# avoidance. Track the feet box.
#

import random
import math
import cv2

import gbdata
import gbstate
import gbscreen
import gbdisplay
import gbtrack
import taskobject
import taskpress
import tasksay
import taskdetect
import taskgotomain
import taskupdatemini
import taskjoy
import taskdetermineposition
import taskpause
import tasktrackturn

class TaskHeadingGoTo(taskobject.Task):
    """TaskHeadingGoTo Object"""

    def __init__(self,heading,distance):
        super().__init__()
        self.name="TaskHeadingGoTo"
        print("new",self.name,"object")
        self.heading=heading
        self.distance=distance

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

        gbstate.move_since_determine=True
        gbstate.move_since_detect=True

        heading=self.heading
        distance=self.distance

        #seconds=gbtrack.heading_change_and_distance_to_time(heading,heading,distance)
        seconds=gbtrack.estimate_distance_to_time(distance)
        print("seconds",seconds)
        msec=int(seconds*1000) # how long to activate the joystick in milliseconds
        total_sec=1+seconds # the total time for the joystick task
        self.parent.Push(taskjoy.TaskJoyLeft(heading,1.0,total_sec,msec))

        # This tracks heading, not position. So, it's ok to
        # use mapless.
        self.parent.Push(tasktrackturn.TaskTrackTurn(self.heading))

    def DebugRecursive(self,indent=0):
        self.DebugPrint(self.name,indent)

    def NameRecursive(self):
        gbstate.task_stack_names.append(self.name)
        return self.name
