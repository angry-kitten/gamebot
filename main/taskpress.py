#
# Copyright 2021 by angry-kitten
# A task to press a controller button
#

import taskobject
import gbdata

class TaskPress(taskobject.TaskTimed):
    """TaskPress Object"""

    def __init__(self,ps,pressthis,total_sec=0.120,press_msec=60):
        super().__init__()
        print("new TaskPress object")
        self.ps=ps
        self.pressthis=pressthis
        self.step=0
        self.press_msec=press_msec
        self.total_sec=total_sec

        # set the parent TaskTimed duration
        self.duration_sec=self.total_sec

    def Poll(self):
        """check if any action can be taken"""
        print("TaskPress Poll")
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
        print("TaskPress Start")
        super().Start()
        if self.started:
            return # already started

    def DebugRecursive(self,indent=0):
        self.DebugPrint("TaskPress",indent)

    def TriggerPress(self):
        if 'A' == self.pressthis:
            self.ps.press_A(self.press_msec)
            return
        if 'B' == self.pressthis:
            self.ps.press_B(self.press_msec)
            return
        if 'X' == self.pressthis:
            self.ps.press_X(self.press_msec)
            return
        if 'Y' == self.pressthis:
            self.ps.press_Y(self.press_msec)
            return
        if 'L' == self.pressthis:
            self.ps.press_L(self.press_msec)
            return
        if 'R' == self.pressthis:
            self.ps.press_R(self.press_msec)
            return
        if 'ZL' == self.pressthis:
            self.ps.press_ZL(self.press_msec)
            return
        if 'ZR' == self.pressthis:
            self.ps.press_ZR(self.press_msec)
            return
        if '+' == self.pressthis:
            self.ps.press_PLUS(self.press_msec)
            return
        if '-' == self.pressthis:
            self.ps.press_MINUS(self.press_msec)
            return
        if 'LCLICK' == self.pressthis:
            self.ps.press_LCLICK(self.press_msec)
            return
        if 'RCLICK' == self.pressthis:
            self.ps.press_RCLICK(self.press_msec)
            return
        if 'HOME' == self.pressthis:
            self.ps.press_HOME(self.press_msec)
            return
        if 'CAPTURE' == self.pressthis:
            self.ps.press_CAPTURE(self.press_msec)
            return
        if 'hat_TOP' == self.pressthis:
            self.ps.press_hat_TOP(self.press_msec)
            return
        if 'hat_TOP_RIGHT' == self.pressthis:
            self.ps.press_hat_TOP_RIGHT(self.press_msec)
            return
        if 'hat_RIGHT' == self.pressthis:
            self.ps.press_hat_RIGHT(self.press_msec)
            return
        if 'hat_BOTTOM_RIGHT' == self.pressthis:
            self.ps.press_hat_BOTTOM_RIGHT(self.press_msec)
            return
        if 'hat_BOTTOM' == self.pressthis:
            self.ps.press_hat_BOTTOM(self.press_msec)
            return
        if 'hat_BOTTOM_LEFT' == self.pressthis:
            self.ps.press_hat_BOTTOM_LEFT(self.press_msec)
            return
        if 'hat_LEFT' == self.pressthis:
            self.ps.press_hat_LEFT(self.press_msec)
            return
        if 'hat_TOP_LEFT' == self.pressthis:
            self.ps.press_hat_TOP_LEFT(self.press_msec)
            return
        if 'hat_CENTER' == self.pressthis:
            self.ps.press_hat_CENTER(self.press_msec)
            return
        if 'left_joy_right' == self.pressthis:
            self.ps.move_left_joy_right(self.press_msec)
            return
        if 'left_joy_left' == self.pressthis:
            self.ps.move_left_joy_left(self.press_msec)
            return
        if 'left_joy_down' == self.pressthis:
            self.ps.move_left_joy_down(self.press_msec)
            return
        if 'left_joy_up' == self.pressthis:
            self.ps.move_left_joy_up(self.press_msec)
            return
        if 'right_joy_right' == self.pressthis:
            self.ps.move_right_joy_right(self.press_msec)
            return
        if 'right_joy_left' == self.pressthis:
            self.ps.move_right_joy_left(self.press_msec)
            return
        if 'right_joy_down' == self.pressthis:
            self.ps.move_right_joy_down(self.press_msec)
            return
        if 'right_joy_up' == self.pressthis:
            self.ps.move_right_joy_up(self.press_msec)
            return
