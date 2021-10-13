#
# Copyright 2021 by angry-kitten
# Task objects for implementing the task queues, lists, and threads.
#

import time

class Task:
    """Task Object"""
    id=0

    def __init__(self):
        #print("a Task.id is",Task.id)
        self.myid=Task.id
        Task.id=Task.id+1
        #print("b Task.id is",Task.id)
        print("new Task object",self.myid)
        self.taskdone=False
        self.started=False
        self.parent=None # parent in the task tree, not inheritence
        self.indent_increment=4

    def SetParent(self,p):
        self.parent=p

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
        self.DebugPrint("Task "+str(self.myid),indent)

    def NameRecursive(self):
        myname="Task "+str(self.myid)
        return myname

class TaskStack(Task):
    """This contains a list of tasks that can run in order from the top of the stack."""

    def __init__(self):
        super().__init__()
        print("new TaskStack object",self.myid)
        self.thestack=[]

    def Poll(self):
        """check if any action can be taken"""

        # poll only the task at the top of the stack
        if len(self.thestack) < 1:
            return # nothing to do
        lastone=self.thestack[-1]
        if lastone.IsDone():
            self.thestack.remove(lastone)
            return
        lastone.Poll()
        if lastone.IsDone():
            self.thestack.remove(lastone)
            return

    def Start(self):
        """Cause the task to begin doing whatever."""

    def Abort(self):
        """Stop the task without completing it."""
        self.taskdone=True
        for t in self.thestack:
            t.Abort()
        self.thestack=[]

    def DebugRecursive(self,indent=0):
        self.DebugPrint("TaskStack "+str(self.myid),indent)
        indent=indent+self.indent_increment

        self.DebugPrint("bottom of stack",indent)
        for t in self.thestack:
            t.DebugRecursive(indent)
        self.DebugPrint("top of stack",indent)

    def NameRecursive(self):
        l=len(self.thestack)
        if l < 1:
            myname="TaskStack "+str(self.myid)
            return myname
        return self.thestack[l-1].NameRecursive()

    def Push(self,atask):
        print("Push")
        atask.SetParent(self)
        self.thestack.append(atask)

class TaskThreads(Task):
    """This contains a list of stacks of tasks that can run independently"""
    # threadlist is a list of stacks

    def __init__(self):
        super().__init__()
        print("new TaskThreads object",self.myid)
        self.threadlist=[]

    def Poll(self):
        """check if any action can be taken"""

        # copy the list so we can iterate safely
        # and still remove items from the original
        # list.
        tmplist=self.threadlist.copy()
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
        self.DebugPrint("TaskThreads "+str(self.myid),indent)
        indent=indent+self.indent_increment

        for t in self.threadlist:
            t.DebugRecursive(indent)

    def NameRecursive(self):
        l=len(self.threadlist)
        if l < 1:
            myname="TaskThreads "+str(self.myid)
            return myname
        return self.threadlist[l-1].NameRecursive()

    def AddToThread(self,n,atask):
        """ add a task to the stack at n """
        print("AddThread at",n)
        # threadlist is a list of stacks
        # add the task to the stack at n
        if n < 0:
            # append anywhere
            # this will cause a new stack to be appended
            n=len(self.threadlist)
        print("AddThread at",n)
        l=len(self.threadlist)
        print("threadlist len is",l)
        while l <= n:
            newstack=TaskStack()
            newstack.SetParent(self)
            self.threadlist.append(newstack)
            l=len(self.threadlist)
            print("threadlist len is",l)
        addhere=self.threadlist[n]
        addhere.Push(atask)


class TaskTimed(Task):
    """This is a task that runs for a minimum amount of time."""

    def __init__(self,time_seconds=1.0):
        super().__init__()
        print("new TaskTimed object",self.myid)
        self.starttime_sec=0 # monotonic time value
        self.endtime_sec=0 # when it should end, monotonic time value
        self.duration_sec=time_seconds

    def Poll(self):
        """check if any action can be taken"""
        if not self.started:
            self.Start()
            return
        if self.taskdone:
            return
        tnow=time.monotonic()
        if tnow >= self.endtime_sec:
            self.taskdone=True
            return

    def Start(self):
        """Cause the task to begin doing whatever."""
        if self.started:
            return # already started
        self.starttime_sec=time.monotonic()
        self.endtime_sec=self.starttime_sec+self.duration_sec
        self.started=True

    def Abort(self):
        """Stop the task without completing it."""
        self.taskdone=True

    def DebugRecursive(self,indent=0):
        self.DebugPrint("TaskTimed",indent)

    def NameRecursive(self):
        myname="TaskTimed"
        return myname
