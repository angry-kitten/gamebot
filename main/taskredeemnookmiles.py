#
# Copyright 2021 by angry-kitten
# Look at the current screen and capture the phone map and
# determine player location from the pin.
#

import time
import numpy
import cv2
import taskobject
import gbdata, gbstate, gbscreen, gbdisplay
import gbtrack
import gbmap
import taskpress
import tasksay
import taskdetect
import taskgotomain
import taskopenphone

class TaskRedeemNookMiles(taskobject.Task):
    """TaskRedeemNookMiles Object"""

    def __init__(self):
        super().__init__()
        self.name="TaskRedeemNookMiles"
        print("new",self.name,"object")
        self.step=0 # pop up phone
        self.icons=[]

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

        print("step is",self.step)

        if self.step == 0:
            if not gbscreen.is_nook_miles_screen():
                print("not on nook miles screen")
                self.step=99
                self.parent.Push(taskpress.TaskPress('B',1.0))
                self.parent.Push(taskpress.TaskPress('B',1.0))
                self.parent.Push(taskpress.TaskPress('B',1.0))
                return
            print("yes on nook miles screen")
            # Close the phone so we can test so far.
            self.step=1
            return

        if self.step == 1:
            print("check nook miles plus")
            self.step=10
            return

        if self.step == 10:
            print("check nook miles cards")

            # Press 'B' to close the card.
            self.parent.Push(taskpress.TaskPress('B',1.0))

            # Let the animation play out.
            self.parent.Push(taskobject.TaskTimed(3.0))

            # Press 'A' to acknowledge the redemption level.
            self.parent.Push(taskpress.TaskPress('A',1.0))

            # Let the animation play out.
            self.parent.Push(taskobject.TaskTimed(2.0))

            # Press 'A' to redeem the card.
            self.parent.Push(taskpress.TaskPress('A',1.0))

            # Press 'A' to select the card.
            self.parent.Push(taskpress.TaskPress('A',1.0))

            # Use the right joystick to jump down to an active card.
            self.parent.Push(taskpress.TaskPress('right_joy_down',1.0))
            self.step=11
            return

        if self.step == 11:
            self.step=20
            return

        if self.step == 20:
            # close nook miles
            self.parent.Push(taskpress.TaskPress('B',1.0))
            self.step=30
            return

        if self.step == 30:
            # close phone
            self.parent.Push(taskpress.TaskPress('B',1.0))
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
        self.step=0 # pop up phone

        self.parent.Push(taskdetect.TaskDetect())
        self.parent.Push(taskopenphone.TaskOpenPhone("NookMiles"))
        return

    def DebugRecursive(self,indent=0):
        self.DebugPrint(self.name,indent)

    def NameRecursive(self):
        gbstate.task_stack_names.append(self.name)
        return self.name
