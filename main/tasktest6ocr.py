#
# Copyright 2021 by angry-kitten
# Run a test (varies over time)  Test turn delay.
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
import tasktrackgoto
import gbtrack
import tasktrackturn
import taskpause
import pytesseract

class TaskTest6ocr(taskobject.Task):
    """TaskTest6ocr Object"""

    def __init__(self):
        super().__init__()
        self.name="TaskTest6ocr"
        print("new",self.name,"object")

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

        print(self.name,"done")
        self.taskdone=True
        return

    def Start(self):
        """Cause the task to begin doing whatever."""
        print(self.name,"Start")
        if self.started:
            return # already started
        self.started=True

        frame=gbstate.frame
        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        print(pytesseract.image_to_string(img_rgb))

        return

    def DebugRecursive(self,indent=0):
        self.DebugPrint(self.name,indent)
        return

    def NameRecursive(self):
        gbstate.task_stack_names.append(self.name)
        return self.name
