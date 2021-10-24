#
# Copyright 2021 by angry-kitten
# Run a test (varies over time)  Test turn delay.
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
import tasktrackturn
import taskpause

class TaskTest5(taskobject.Task):
    """TaskTest5 Object"""

    def __init__(self):
        super().__init__()
        self.name="TaskTest5"
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

        # The tasks will be run in reverse order from the loops.
        for heading in range(0,360,45):
            self.parent.Push(taskpause.TaskPause(str(heading),2.0))
            self.parent.Push(tasktrackturn.TaskTrackTurn(heading))

        for heading in range(360,0,-45):
            self.parent.Push(taskpause.TaskPause(str(heading),2.0))
            self.parent.Push(tasktrackturn.TaskTrackTurn(heading))

        self.parent.Push(taskpause.TaskPause(str(heading),2.0))
        self.parent.Push(tasktrackturn.TaskTrackTurn(0))

        self.parent.Push(tasktrackgoto.TaskTrackGoTo(gbstate.player_mx,gbstate.player_my-2))

    def DebugRecursive(self,indent=0):
        self.DebugPrint(self.name,indent)

    def NameRecursive(self):
        gbstate.task_stack_names.append(self.name)
        return self.name
