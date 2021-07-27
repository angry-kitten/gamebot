#
# Copyright 2021 by angry-kitten
# Parse labels from labeled images and create a list for gamebot.
#

import taskobject

class TaskSay(taskobject.Task):
    """TaskSay Object"""
    taskdone=False
    indent_increment=4

    def __init__(self,saythis):
        print("new Task object")

    def Poll(self):
        """check if any action can be taken"""

    def Start(self):
        """Cause the task to begin doing whatever."""

    def Abort(self):
        """Stop the task without completing it."""
        self.taskdone=True

    def DebugRecursive(self,indent=0):
        self.DebugPrint("TaskSay",indent)
