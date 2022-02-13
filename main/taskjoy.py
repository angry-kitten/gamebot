#
# Copyright 2021-2022 by angry-kitten
# A task to move a controller joystick
#

import gbdata
import gbstate
import taskobject

class TaskJoyLeft(taskobject.TaskTimed):
    """TaskJoyLeft Object"""

    def __init__(self,heading,extent,total_sec=1.000,press_msec=500):
        super().__init__()
        self.name="TaskJoyLeft"
        #print("new TaskJoyLeft object")
        self.ps=gbstate.ps
        self.heading=heading
        self.extent=extent
        self.step=0
        self.press_msec=press_msec
        self.total_sec=total_sec

        # set the parent TaskTimed duration
        self.duration_sec=self.total_sec

    def Poll(self):
        """check if any action can be taken"""
        #print("TaskJoyLeft Poll")
        super().Poll()
        if not self.started:
            return
        if self.taskdone:
            return
        if 0 == self.step:
            self.TriggerJoyLeft()
            self.step=1
            return

    def Start(self):
        """Cause the task to begin doing whatever."""
        #print("TaskJoyLeft Start")
        super().Start()
        if self.started:
            return # already started

    def DebugRecursive(self,indent=0):
        self.DebugPrint("TaskJoyLeft",indent)

    def NameRecursive(self):
        gbstate.task_stack_names.append(self.name)
        myname="TaskJoyLeft"
        return myname

    def TriggerJoyLeft(self):
        self.ps.left_joy_heading(self.heading,self.extent,self.press_msec)
