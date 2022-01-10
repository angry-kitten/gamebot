#
# Copyright 2021-2022 by angry-kitten
# Save the game and restart.
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
import tasktrackgoto
import taskdetermineposition
import taskholdtool
import tasktrackturn
import taskheadinggoto
import taskgotomain

class TaskSaveRestart(taskobject.Task):
    """TaskSaveRestart Object"""

    def __init__(self):
        super().__init__()
        self.name="TaskSaveRestart"
        print("new",self.name,"object")
        self.step=0

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

        if self.step == 0:
            if gbscreen.is_continue_triangle():
                self.step=1
                return

            print("no continue triangle 1")
            self.step=99
            return

        if self.step == 1:
            # Press 'A' to continue to the menu.
            self.parent.Push(taskobject.TaskTimed(3.0))
            self.parent.Push(taskpress.TaskPress('A'))
            self.step=2
            return

        if self.step == 2:
            # Press 'A' to select the default item in the menu.
            # "Save and end."
            self.parent.Push(taskobject.TaskTimed(20.0))
            self.parent.Push(taskpress.TaskPress('A'))
            self.step=3
            return

        if self.step == 3:
            if gbscreen.is_continue_triangle():
                # Press 'HOME' to get to the switch game select screen.
                self.parent.Push(taskobject.TaskTimed(10.0))
                self.parent.Push(taskpress.TaskPress('HOME'))
                self.step=4
                return
            print("no continue triangle 2")
            self.step=99
            return

        if self.step == 4:
            # Press 'X' to close the program, ACNH.
            self.parent.Push(taskobject.TaskTimed(10.0))
            self.parent.Push(taskpress.TaskPress('X'))
            self.step=5
            return

        if self.step == 5:
            # Press 'A' to accept at the pop-up menu. "Close"
            self.parent.Push(taskobject.TaskTimed(10.0))
            self.parent.Push(taskpress.TaskPress('A'))
            self.step=6
            return

        if self.step == 6:
            self.parent.Push(taskdetermineposition.TaskDeterminePosition())
            # Let TaskGoToMain handle it from here.
            self.parent.Push(taskgotomain.TaskGoToMain())

            # Press 'A' to start the pogram, ACNH, again.
            self.parent.Push(taskobject.TaskTimed(10.0))
            self.parent.Push(taskpress.TaskPress('A'))
            self.step=99
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
        self.step=0

        # Press '-' to start the save sequence.
        self.parent.Push(taskdetect.TaskDetect())
        self.parent.Push(taskobject.TaskTimed(5.0))
        self.parent.Push(taskpress.TaskPress('-'))
        return

    def DebugRecursive(self,indent=0):
        self.DebugPrint(self.name,indent)

    def NameRecursive(self):
        gbstate.task_stack_names.append(self.name)
        return self.name
