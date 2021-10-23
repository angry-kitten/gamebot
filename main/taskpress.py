#
# Copyright 2021 by angry-kitten
# A task to press a controller button
#

import taskobject
import gbdata
import gbstate

class TaskPress(taskobject.TaskTimed):
    """TaskPress Object"""

    def __init__(self,pressthis,total_sec=0.120,press_msec=60):
        super().__init__()
        self.name="TaskPress"
        print("new",self.name,"object")
        self.pressthis=pressthis
        self.step=0
        self.press_msec=press_msec
        self.total_sec=total_sec

        # set the parent TaskTimed duration
        self.duration_sec=self.total_sec

    def Poll(self):
        """check if any action can be taken"""
        print(self.name,"Poll")
        super().Poll()
        if not self.started:
            return
        if self.taskdone:
            return
        if 0 == self.step:
            self.TriggerPress()
            self.step=1
            return

    def Start(self):
        """Cause the task to begin doing whatever."""
        print(self.name,"Start")
        super().Start()
        if self.started:
            return # already started

    def DebugRecursive(self,indent=0):
        self.DebugPrint(self.name,indent)

    def NameRecursive(self):
        gbstate.task_stack_names.append(self.name)
        return self.name

    def TriggerPress(self):
        if 'A' == self.pressthis:
            gbstate.ps.press_A(self.press_msec)
            return
        if 'B' == self.pressthis:
            gbstate.ps.press_B(self.press_msec)
            return
        if 'X' == self.pressthis:
            gbstate.ps.press_X(self.press_msec)
            return
        if 'Y' == self.pressthis:
            gbstate.ps.press_Y(self.press_msec)
            return
        if 'L' == self.pressthis:
            gbstate.ps.press_L(self.press_msec)
            return
        if 'R' == self.pressthis:
            gbstate.ps.press_R(self.press_msec)
            return
        if 'ZL' == self.pressthis:
            gbstate.ps.press_ZL(self.press_msec)
            return
        if 'ZR' == self.pressthis:
            gbstate.ps.press_ZR(self.press_msec)
            return
        if '+' == self.pressthis:
            gbstate.ps.press_PLUS(self.press_msec)
            return
        if '-' == self.pressthis:
            gbstate.ps.press_MINUS(self.press_msec)
            return
        if 'LCLICK' == self.pressthis:
            gbstate.ps.press_LCLICK(self.press_msec)
            return
        if 'RCLICK' == self.pressthis:
            gbstate.ps.press_RCLICK(self.press_msec)
            return
        if 'HOME' == self.pressthis:
            gbstate.ps.press_HOME(self.press_msec)
            return
        if 'CAPTURE' == self.pressthis:
            gbstate.ps.press_CAPTURE(self.press_msec)
            return
        if 'hat_TOP' == self.pressthis:
            gbstate.ps.press_hat_TOP(self.press_msec)
            return
        if 'hat_TOP_RIGHT' == self.pressthis:
            gbstate.ps.press_hat_TOP_RIGHT(self.press_msec)
            return
        if 'hat_RIGHT' == self.pressthis:
            gbstate.ps.press_hat_RIGHT(self.press_msec)
            return
        if 'hat_BOTTOM_RIGHT' == self.pressthis:
            gbstate.ps.press_hat_BOTTOM_RIGHT(self.press_msec)
            return
        if 'hat_BOTTOM' == self.pressthis:
            gbstate.ps.press_hat_BOTTOM(self.press_msec)
            return
        if 'hat_BOTTOM_LEFT' == self.pressthis:
            gbstate.ps.press_hat_BOTTOM_LEFT(self.press_msec)
            return
        if 'hat_LEFT' == self.pressthis:
            gbstate.ps.press_hat_LEFT(self.press_msec)
            return
        if 'hat_TOP_LEFT' == self.pressthis:
            gbstate.ps.press_hat_TOP_LEFT(self.press_msec)
            return
        if 'hat_CENTER' == self.pressthis:
            gbstate.ps.press_hat_CENTER(self.press_msec)
            return
        if 'left_joy_right' == self.pressthis:
            gbstate.ps.move_left_joy_right(self.press_msec)
            return
        if 'left_joy_left' == self.pressthis:
            gbstate.ps.move_left_joy_left(self.press_msec)
            return
        if 'left_joy_down' == self.pressthis:
            gbstate.ps.move_left_joy_down(self.press_msec)
            return
        if 'left_joy_up' == self.pressthis:
            gbstate.ps.move_left_joy_up(self.press_msec)
            return
        if 'right_joy_right' == self.pressthis:
            gbstate.ps.move_right_joy_right(self.press_msec)
            return
        if 'right_joy_left' == self.pressthis:
            gbstate.ps.move_right_joy_left(self.press_msec)
            return
        if 'right_joy_down' == self.pressthis:
            gbstate.ps.move_right_joy_down(self.press_msec)
            return
        if 'right_joy_up' == self.pressthis:
            gbstate.ps.move_right_joy_up(self.press_msec)
            return
