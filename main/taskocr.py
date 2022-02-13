#
# Copyright 2021-2022 by angry-kitten
# Trigger an OCR detection by clearing gbstate.ocr_detections and
# waiting for it to be generated.
#

import gbdata, gbstate
import taskobject

class TaskOCR(taskobject.Task):
    """TaskOCR Object"""

    def __init__(self):
        super().__init__()
        self.name="TaskOCR"
        print("new",self.name,"object")
        return

    def Poll(self):
        """check if any action can be taken"""
        #print(self.name,"Poll")
        if not self.started:
            self.Start()
            return
        if self.taskdone:
            return

        with gbstate.ocr_worker_thread.data_lock:
            if gbstate.ocr_detections is None:
                return

        gbstate.pause_message=None
        #print(self.name,"done")
        self.taskdone=True
        return

    def Start(self):
        """Cause the task to begin doing whatever."""
        print(self.name,"Start")
        if self.started:
            return # already started
        self.started=True
        gbstate.pause_message='OCR'
        with gbstate.ocr_worker_thread.data_lock:
            gbstate.ocr_detections=None
        gbstate.ocr_worker_thread.RunOnce()
        return

    def DebugRecursive(self,indent=0):
        self.DebugPrint(self.name,indent)
        return

    def NameRecursive(self):
        gbstate.task_stack_names.append(self.name)
        return self.name
