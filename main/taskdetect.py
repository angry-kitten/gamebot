#
# Copyright 2021-2022 by angry-kitten
# Trigger an object detection by clearing gbstate.detections and
# waiting for it to be generated.
#

import gbdata
import gbstate
import gamebot
import taskobject
import taskocr

class TaskDetect(taskobject.Task):
    """TaskDetect Object"""

    def __init__(self):
        super().__init__()
        self.name="TaskDetect"
        print("new TaskDetect object")

    def Poll(self):
        """check if any action can be taken"""
        #print("TaskDetect Poll")
        if not self.started:
            self.Start()
            return
        if self.taskdone:
            return
        with gbstate.detection_lock:
            if gbstate.detections is None:
                #gamebot.object_detection_wakeup()
                return

        gbstate.pause_message=None
        gbstate.move_since_detect=False
        print("TaskDetect done")
        self.taskdone=True

    def Start(self):
        """Cause the task to begin doing whatever."""
        print("TaskDetect Start")
        if self.started:
            return # already started
        self.started=True
        gbstate.pause_message='Detect'
        with gbstate.detection_lock:
            gbstate.detections=None
        gamebot.object_detection_wakeup()

    def DebugRecursive(self,indent=0):
        self.DebugPrint("TaskDetect",indent)

    def NameRecursive(self):
        gbstate.task_stack_names.append(self.name)
        myname="TaskDetect"
        return myname
