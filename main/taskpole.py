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
import taskdetermineposition
import taskholdtool
import gbtrack
import tasktrackturn
import taskheadinggoto

class TaskPole(taskobject.Task):
    """TaskPole Object"""

    def __init__(self,mx,my):
        super().__init__()
        self.name="TaskPole"
        print("new",self.name,"object")
        self.target_mx=mx
        self.target_my=my
        print("go to mx",mx,"my",my)
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
            # Check that the pole is held.
            print("current_tool",gbstate.current_tool)
            if gbstate.current_tool != "Pole":
                print("not holding a pole")
                self.step=99 # done
                # Put any tools away just in case.
                self.parent.Push(taskholdtool.TaskHoldTool('None'))
                return

            # Face in the direction to go and press 'A'.
            pmx=gbstate.player_mx
            pmy=gbstate.player_my
            tmx=self.target_mx
            tmy=self.target_my
            dx=tmx-pmx
            dy=tmy-pmy
            heading=gbtrack.calculate_heading(dx,dy)

            self.parent.Push(taskdetermineposition.TaskDeterminePosition())

            self.parent.Push(taskobject.TaskTimed(1.0))

            self.parent.Push(taskholdtool.TaskHoldTool('None'))

            # Wait for pole animation.
            self.parent.Push(taskobject.TaskTimed(5.0))

            self.parent.Push(taskpress.TaskPress('A'))

            self.parent.Push(taskobject.TaskTimed(1.0))

            self.parent.Push(taskheadinggoto.TaskHeadingGoTo(heading,0.5))

            self.parent.Push(taskobject.TaskTimed(1.0))

            self.parent.Push(tasktrackturn.TaskTrackTurn(heading))

            self.step=99 # done
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

        if not gbstate.inventory_has_pole:
            print("no pole")
            # This isn't going to work.
            self.step=99
            return

        # Hold a pole. This will cause the player character to face down/south.
        self.parent.Push(taskholdtool.TaskHoldTool('Pole'))
        return

    def DebugRecursive(self,indent=0):
        self.DebugPrint(self.name,indent)

    def NameRecursive(self):
        gbstate.task_stack_names.append(self.name)
        return self.name
