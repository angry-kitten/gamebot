#
# Copyright 2021-2022 by angry-kitten
# Trigger the gathering of the map.
# Wait for it to be generated.
#

import cv2
import gbdata, gbstate
import gbdijkstra
import taskobject

class TaskGatherMap(taskobject.Task):
    """TaskGatherMap Object"""

    def __init__(self):
        super().__init__()
        self.name="TaskGatherMap"
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

        with gbstate.gathermap_worker_thread.data_lock:
            if not gbstate.gathermap_completed:
                return

        gbstate.pause_message=None
        gbstate.map_is_gathered=True

        #cv2.imwrite('gather.png',gbstate.frame)

        #print(self.name,"done")
        self.taskdone=True
        return

    def Start(self):
        """Cause the task to begin doing whatever."""
        print(self.name,"Start")
        if self.started:
            return # already started
        self.started=True
        gbstate.pause_message='GatherMap'
        with gbstate.gathermap_worker_thread.data_lock:
            gbstate.gathermap_completed=False
        gbstate.gathermap_worker_thread.RunOnce()
        return

    def DebugRecursive(self,indent=0):
        self.DebugPrint(self.name,indent)
        return

    def NameRecursive(self):
        gbstate.task_stack_names.append(self.name)
        return self.name
