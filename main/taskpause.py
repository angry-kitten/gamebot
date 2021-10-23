#
# Copyright 2021 by angry-kitten
# A task to pause a given amount of time with a message.
#

import taskobject
import gbdata
import gbstate

class TaskPause(taskobject.TaskTimed):
    """TaskPause Object"""

    def __init__(self,message='PAUSE',total_sec=1.0):
        super().__init__(total_sec)
        self.name="TaskPause"
        print("new",self.name,"object")
        self.message=message
        print("message is",self.message)

    def Poll(self):
        """check if any action can be taken"""
        print(self.name,"Poll")
        super().Poll()
        if not self.started:
            return
        if self.taskdone:
            gbstate.pause_message=None
            print("pause_message is cleared",gbstate.pause_message)
            return

    def Start(self):
        """Cause the task to begin doing whatever."""
        print(self.name,"Start")
        gbstate.pause_message=self.message
        print("pause_message is",gbstate.pause_message)
        super().Start()
        if self.started:
            return # already started

    def DebugRecursive(self,indent=0):
        self.DebugPrint(self.name,indent)

    def NameRecursive(self):
        gbstate.task_stack_names.append(self.name)
        return self.name
