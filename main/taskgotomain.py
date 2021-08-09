#
# Copyright 2021 by angry-kitten
# Look at the video at startup and see what the current screen is.
# Move to the main playing screen.
#

import taskobject
import gbdata
import gbstate
import cv2
import taskpress
import taskdetect
import gbscreen

class TaskGoToMain(taskobject.Task):
    """TaskGoToMain Object"""

    def __init__(self):
        super().__init__()
        print("new TaskGoToMain object")

    def Poll(self):
        """check if any action can be taken"""
        print("TaskGoToMain Poll")
        if not self.started:
            self.Start()
            return
        if self.taskdone:
            return
        if gbstate.frame is None:
            return

        if gbscreen.is_loading_screen():
            print("loading screen")
            # do nothing and wait
            return
        if gbscreen.is_black_screen():
            print("black screen")
            # do nothing and wait
            return
        if gbscreen.is_color_bars(): # my capture device shows color bars for no signal
            # NOTE: this doesn't work :(
            print("color bars")
            # Try to wake up the device with the Home button.
            # Push these onto the stack in reverse order.
            self.parent.Push(taskdetect.TaskDetect())
            # Press Home and wait down 3 seconds, totaling 5 seconds.
            self.parent.Push(taskpress.TaskPress(gbstate.ps,'HOME',5.0,3000))
            return
        if gbscreen.is_start_continue_screen():
            print("start continue")
            # Push these onto the stack in reverse order.
            self.parent.Push(taskdetect.TaskDetect())
            self.parent.Push(taskpress.TaskPress(gbstate.ps,'A',5.0))
            return
        if gbscreen.is_main_screen():
            print("main screen")
            print("TaskGoToMain done")
            self.taskdone=True
            return
        if gbscreen.is_continue_triangle_detect():
            # maybe announcements
            print("continue triangle detect")
            self.parent.Push(taskdetect.TaskDetect())
            # press B to continue
            self.parent.Push(taskpress.TaskPress(gbstate.ps,'B',5.0))
            return
        if gbscreen.is_continue_triangle():
            # maybe announcements
            print("continue triangle")
            self.parent.Push(taskdetect.TaskDetect())
            # press B to continue
            self.parent.Push(taskpress.TaskPress(gbstate.ps,'B',5.0))
            return

        # purturb the game to see if it was screen dimmed or something
        self.parent.Push(taskdetect.TaskDetect())
        self.parent.Push(taskpress.TaskPress(gbstate.ps,'right_joy_right',5.0))

    def Start(self):
        """Cause the task to begin doing whatever."""
        print("TaskGoToMain Start")
        if self.started:
            return # already started
        self.started=True
        # trigger a detection
        self.parent.Push(taskdetect.TaskDetect())

    def DebugRecursive(self,indent=0):
        self.DebugPrint("TaskGoToMain",indent)
