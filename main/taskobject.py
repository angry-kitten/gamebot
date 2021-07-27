#
# Copyright 2021 by angry-kitten
# Parse labels from labeled images and create a list for gamebot.
#

class Task:
    """Task Object"""
    taskdone=False
    indent_increment=4

    def __init__(self):
        print("new Task object")

    def Poll(self):
        """check if any action can be taken"""

    def Start(self):
        """Cause the task to begin doing whatever."""

    def Abort(self):
        """Stop the task without completing it."""
        self.taskdone=True

    def IsDone(self):
        return self.taskdone

    def DebugPrint(self,text,indent=0):
        sp=''
        for i in range(indent):
            sp=sp+' '
        print(sp+text)

    def DebugRecursive(self,indent=0):
        self.DebugPrint("Task",indent)


class TaskThreads(Task):
    """This contains a list of tasks that can run independently"""
    threadlist=[]

    def __init__(self):
        print("new TaskThreads object")

    def Poll(self):
        """check if any action can be taken"""

        # copy the list so we can iterate safely
        # and still remove items from the original
        # list.
        tmplist=self.threadlist
        for t in tmplist:
            if t.IsDone():
                self.threadlist.remove(t)
            else:
                t.Poll()
                if t.IsDone():
                    self.threadlist.remove(t)

    def Start(self):
        """Cause the task to begin doing whatever."""

    def Abort(self):
        """Stop the task without completing it."""
        self.taskdone=True
        for t in self.threadlist:
            t.Abort()
        self.threadlist=[]

    def DebugRecursive(self,indent=0):
        self.DebugPrint("TaskThreads",indent)
        indent=indent+self.indent_increment

        for t in self.threadlist:
            t.DebugRecursive(indent)

    def AddThread(self,atask):
        self.threadlist.append(atask)
