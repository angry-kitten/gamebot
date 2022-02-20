#
# Copyright 2021-2022 by angry-kitten
# Open up nook miles on the phone and accept points.
#

import time
import numpy
import cv2
import gbdata, gbstate, gbscreen, gbdisplay
import gbtrack
import gbmap
import taskobject
import taskpress
import tasksay
import taskdetect
import taskgotomain
import taskopenphone

class TaskAcceptNookMiles(taskobject.Task):
    """TaskAcceptNookMiles Object"""

    def __init__(self):
        super().__init__()
        self.name="TaskAcceptNookMiles"
        print("new",self.name,"object")
        self.step=0 # pop up phone
        self.icons=[]
        self.active_plus=None

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
            l=len(gbdata.nook_miles_plus_blue_locations)
            self.active_plus=None
            gbstate.debug_window=True
            for i in range(l):
                (sx,sy)=gbdata.nook_miles_plus_blue_locations[i]
                if gbscreen.color_match_array_list(sx,sy,gbdata.nook_miles_plus_blue_list,5):
                    self.active_plus=i
                    break
            gbstate.debug_window=False
            if self.active_plus is None:
                self.step=10
                return

            # Let the animation play out.
            self.parent.Push(taskobject.TaskTimed(2.0))

            # Open the nook miles + screen.
            self.parent.Push(taskpress.TaskPress('+'))

            self.step=2
            return

        if self.step == 2:
            # We don't know where the hand will be. It saves location state
            # between invocations.
            print("find hand for nook miles plus")
            l=len(gbdata.nook_miles_plus_hand_locations)
            found=None
            for i in range(l):
                (sx,sy)=gbdata.nook_miles_plus_hand_locations[i]
                if gbscreen.color_match_array(sx,sy,gbdata.phone_hand_color,2):
                    found=i
                    break
            if found is None:
                self.step=3
                return

            # Let the animation play out.
            self.parent.Push(taskobject.TaskTimed(2.0))

            # Press 'B' to close the circle.
            self.parent.Push(taskpress.TaskPress('B'))

            # Let the animation play out.
            self.parent.Push(taskobject.TaskTimed(3.0))

            # Accept the active circle.
            self.parent.Push(taskpress.TaskPress('A'))

            # Let the animation play out.
            self.parent.Push(taskobject.TaskTimed(1.0))

            # Select the active circle.
            self.parent.Push(taskpress.TaskPress('A'))

            while found < self.active_plus:
                # Let the animation play out.
                self.parent.Push(taskobject.TaskTimed(1.0))
                # move hand right
                self.parent.Push(taskpress.TaskPress('hat_RIGHT'))
                found+=1
            while found > self.active_plus:
                # Let the animation play out.
                self.parent.Push(taskobject.TaskTimed(1.0))
                # move hand left
                self.parent.Push(taskpress.TaskPress('hat_LEFT'))
                found-=1

            self.step=3
            return

        if self.step == 3:
            print("close nook miles plus")

            # Let the animation play out.
            self.parent.Push(taskobject.TaskTimed(2.0))

            # Close the nook miles + screen.
            self.parent.Push(taskpress.TaskPress('B'))

            self.step=20
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

            # Press 'A' to accept the card.
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
