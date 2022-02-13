#
# Copyright 2021-2022 by angry-kitten
# Move the player character in a random direction for a random distance.
#

import random
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

class TaskRandomWalk(taskobject.Task):
    """TaskRandomWalk Object"""

    def __init__(self):
        super().__init__()
        self.name="TaskRandomWalk"
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
        heading=random.randint(0,360-1)
        distance=random.randint(0,5)
        print(heading,distance)
        (dmx,dmy)=gbtrack.calculate_dx_dy(heading,distance)
        mx=gbstate.player_mx
        my=gbstate.player_my
        mx+=dmx
        my+=dmy
        self.parent.Push(tasktrackgoto.TaskTrackGoTo(mx,my))
        self.taskdone=True

    def DebugRecursive(self,indent=0):
        self.DebugPrint("TaskRandomWalk",indent)

    def NameRecursive(self):
        gbstate.task_stack_names.append(self.name)
        myname="TaskRandomWalk"
        return myname
