#
# Copyright 2021 by angry-kitten
# Trigger an object detection by clearing gbstate.detections and
# waiting for it to be generated.
#

import taskobject
import gbdata
import gbstate

class TaskDetect(taskobject.Task):
    """TaskDetect Object"""

    def __init__(self):
        super().__init__()
        print("new TaskDetect object")

    def Poll(self):
        """check if any action can be taken"""
        print("TaskDetect Poll")
        if not self.started:
            self.Start()
            return
        if self.taskdone:
            return
        with gbstate.detection_lock:
            if gbstate.detections is None:
                return

        print("TaskDetect done")
        self.taskdone=True

    def Start(self):
        """Cause the task to begin doing whatever."""
        print("TaskDetect Start")
        if self.started:
            return # already started
        self.started=True
        with gbstate.detection_lock:
            gbstate.detections=None

    def DebugRecursive(self,indent=0):
        self.DebugPrint("TaskDetect",indent)
