#
# Copyright 2021 by angry-kitten
# Walk a search pattern and call a function at each node.
#

import taskobject
import gbdata
import gbstate
import cv2
import taskpress
import tasksay
import taskdetect
import taskgotomain
import taskupdatemini
import taskrandomwalk
import tasksimplegoto
import gbscreen
import gbdisplay
import random
import tasksimplegoto
import taskpathplangoto
import taskcheckforinterrupt

class TaskSearchPattern(taskobject.Task):
    """TaskSearchPattern Object"""

    def __init__(self,pattern_number,callme):
        super().__init__()
        self.name="TaskSearchPattern"
        print("new TaskSearchPattern object")
        self.callme=callme # call this function at every node

        # Set the default pattern.
        self.pattern_init=self.pattern0_init
        self.pattern_start=self.pattern0_start
        self.pattern_poll=self.pattern0_poll

        if pattern_number == 1:
            self.pattern_init=self.pattern1_init
            self.pattern_start=self.pattern1_start
            self.pattern_poll=self.pattern1_poll

        if pattern_number == 2:
            self.pattern_init=self.pattern2_init
            self.pattern_start=self.pattern2_start
            self.pattern_poll=self.pattern2_poll

        self.pattern_init()

    def Poll(self):
        """check if any action can be taken"""
        print("TaskSearchPattern Poll")
        if not self.started:
            self.Start()
            return
        if self.taskdone:
            return
        if gbstate.frame is None:
            return

        print("search at",self.search_mx,self.search_my)
        self.callme()

        self.pattern_poll()

        self.parent.Push(taskcheckforinterrupt.TaskCheckForInterrupt())

        return

    def Start(self):
        """Cause the task to begin doing whatever."""
        print("TaskSearchPattern Start")
        if self.started:
            return # already started
        self.started=True
        self.pattern_start()

    def DebugRecursive(self,indent=0):
        self.DebugPrint("TaskSearchPattern",indent)

    def NameRecursive(self):
        gbstate.task_stack_names.append(self.name)
        myname="TaskSearchPattern"
        return myname

    # pattern 0 is top to bottom, left to right
    def pattern0_init(self):
        self.search_mx=0
        self.search_my=0
        self.search_step=7

    def pattern0_start(self):
        self.parent.Push(taskpathplangoto.TaskPathPlanGoTo(self.search_mx,self.search_my))

    def pattern0_poll(self):
        self.search_mx+=self.search_step
        if self.search_mx >= gbdata.minimap_width:
            self.search_mx=0
            self.search_my+=self.search_step
            if self.search_my >= gbdata.minimap_height:
                self.search_my=0
                print("TaskSearchPattern done")
                self.taskdone=True
                return
        self.parent.Push(taskpathplangoto.TaskPathPlanGoTo(self.search_mx,self.search_my))

    # pattern 1 is the same locations as pattern 0 but selected randomly.
    def pattern1_init(self):
        self.search_mx=0
        self.search_my=0
        self.search_step=7
        self.search_list=[]
        for my in range(0,gbdata.minimap_height,self.search_step):
            for mx in range(0,gbdata.minimap_width,self.search_step):
                self.search_list.append((mx,my))

    def pattern1_start(self):
        l=len(self.search_list)
        if l < 1:
            print("TaskSearchPattern done")
            self.taskdone=True
            return
        j=random.randint(0,l-1)
        (mx,my)=self.search_list[j]
        del self.search_list[j]
        self.search_mx=mx
        self.search_my=my
        self.parent.Push(taskpathplangoto.TaskPathPlanGoTo(mx,my))

    def pattern1_poll(self):
        l=len(self.search_list)
        if l < 1:
            print("TaskSearchPattern done")
            self.taskdone=True
            return
        j=random.randint(0,l-1)
        (mx,my)=self.search_list[j]
        del self.search_list[j]
        self.search_mx=mx
        self.search_my=my
        self.parent.Push(taskpathplangoto.TaskPathPlanGoTo(mx,my))

    # pattern 2 is the same as pattern 1 but selected
    # with smaller steps.
    def pattern2_init(self):
        self.search_mx=0
        self.search_my=0
        self.search_step=4
        self.search_list=[]
        for my in range(0,gbdata.minimap_height,self.search_step):
            for mx in range(0,gbdata.minimap_width,self.search_step):
                self.search_list.append((mx,my))

    def pattern2_start(self):
        l=len(self.search_list)
        if l < 1:
            print("TaskSearchPattern done")
            self.taskdone=True
            return
        j=random.randint(0,l-1)
        (mx,my)=self.search_list[j]
        del self.search_list[j]
        self.search_mx=mx
        self.search_my=my
        self.parent.Push(taskpathplangoto.TaskPathPlanGoTo(mx,my))

    def pattern2_poll(self):
        l=len(self.search_list)
        if l < 1:
            print("TaskSearchPattern done")
            self.taskdone=True
            return
        j=random.randint(0,l-1)
        (mx,my)=self.search_list[j]
        del self.search_list[j]
        self.search_mx=mx
        self.search_my=my
        self.parent.Push(taskpathplangoto.TaskPathPlanGoTo(mx,my))
