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
        self.name="TaskGoToMain"
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
            self.parent.Push(taskdetect.TaskDetect())
            return
        if gbscreen.is_black_screen():
            print("black screen")
            # do nothing and wait
            self.parent.Push(taskdetect.TaskDetect())
            return
        if gbscreen.is_color_bars(): # my capture device shows color bars for no signal
            # NOTE: this doesn't work :(
            print("color bars")
            # Try to wake up the device with the Home button.
            # Push these onto the stack in reverse order.
            self.parent.Push(taskdetect.TaskDetect())
            # Press Home and wait down 3 seconds, totaling 5 seconds.
            self.parent.Push(taskpress.TaskPress('HOME',5.0,3000))
            return
        if gbscreen.is_start_continue_screen():
            print("start continue")
            # Push these onto the stack in reverse order.
            self.parent.Push(taskdetect.TaskDetect())
            self.parent.Push(taskpress.TaskPress('A',5.0))
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
            self.parent.Push(taskpress.TaskPress('B',5.0))
            return
        if gbscreen.is_continue_triangle():
            # maybe announcements
            print("continue triangle")
            self.parent.Push(taskdetect.TaskDetect())
            # press B to continue
            self.parent.Push(taskpress.TaskPress('B',5.0))
            return
        if gbscreen.is_selection_screen():
            print("selection screen")
            self.parent.Push(taskdetect.TaskDetect())
            # press A to continue
            self.parent.Push(taskpress.TaskPress('A',5.0))
            return
        if gbscreen.is_selection_screen_no_ACNH():
            print("selection screen, no ACNH")
            self.parent.Push(taskdetect.TaskDetect())
            # press hat_LEFT to try to get to the ACNH tile
            self.parent.Push(taskpress.TaskPress('hat_LEFT',5.0))
            return
        if gbscreen.is_user_selection_screen():
            print("user selection screen")
            self.parent.Push(taskdetect.TaskDetect())
            # press A to select default user
            self.parent.Push(taskpress.TaskPress('A',5.0))
            return
        if gbscreen.is_main_logo_screen():
            print("main logo screen")
            self.parent.Push(taskdetect.TaskDetect())
            # press A to continue
            self.parent.Push(taskpress.TaskPress('A',5.0))
            return
        if gbscreen.is_inventory_screen():
            print("inventory screen")
            self.parent.Push(taskdetect.TaskDetect())
            # press B to close inventory
            self.parent.Push(taskpress.TaskPress('B',5.0))
            return
        if gbscreen.is_accept_controller_screen():
            print("accept controller screen")
            self.parent.Push(taskdetect.TaskDetect())
            # press A to accept
            self.parent.Push(taskpress.TaskPress('A',5.0))
            return

        # purturb the game to see if it was screen dimmed or something
        self.parent.Push(taskdetect.TaskDetect())
        self.parent.Push(taskpress.TaskPress('right_joy_left',5.0))
        self.parent.Push(taskpress.TaskPress('right_joy_right',5.0))

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

    def NameRecursive(self):
        gbstate.task_stack_names.append(self.name)
        myname="TaskGoToMain"
        return myname
