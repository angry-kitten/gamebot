#
# Copyright 2021 by angry-kitten
# Look at the video and see if there is an interrupt with a continue
# triangle that needs to be acknowledged.
#

import taskobject
import gbdata
import gbstate
import cv2
import taskpress
import tasksay
import taskdetect
import taskgotomain
import taskupdatemini
import gbscreen

class TaskCheckForInterrupt(taskobject.Task):
    """TaskCheckForInterrupt Object"""

    def __init__(self):
        super().__init__()
        print("new TaskCheckForInterrupt object")

    def Poll(self):
        """check if any action can be taken"""
        print("TaskCheckForInterrupt Poll")
        if not self.started:
            self.Start()
            return
        if self.taskdone:
            return
        if gbstate.frame is None:
            return

        if gbscreen.is_continue_triangle_detect():
            # maybe announcements
            print("continue triangle detect")
            self.parent.Push(taskdetect.TaskDetect())
            # press B to continue
            self.parent.Push(taskpress.TaskPress('B',5.0))
            return
        if gbscreen.is_continue_triangle():
            # maybe announcements
            print("continue triangle")
            self.parent.Push(taskdetect.TaskDetect())
            # press B to continue
            self.parent.Push(taskpress.TaskPress('B',5.0))
            return

        if gbscreen.is_main_screen():
            print("main screen")
            print("TaskCheckForInterrupt done")
            self.taskdone=True
            return

        self.parent.Push(taskdetect.TaskDetect())
        return

    def Start(self):
        """Cause the task to begin doing whatever."""
        print("TaskCheckForInterrupt Start")
        if self.started:
            return # already started
        self.started=True
        # push tasks in reverse order
        self.parent.Push(taskdetect.TaskDetect())

    def DebugRecursive(self,indent=0):
        self.DebugPrint("TaskCheckForInterrupt",indent)

    def NameRecursive(self):
        myname="TaskCheckForInterrupt"
        return myname
