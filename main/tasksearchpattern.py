#
# Copyright 2021-2022 by angry-kitten
# Walk a search pattern and call a function at each node.
#

import random
import cv2
import gbdata, gbstate, gbscreen, gbdisplay
import taskobject
import taskpress
import tasksay
import taskdetect
import taskgotomain
import taskupdatemini
import taskrandomwalk
import tasksimplegoto
import taskpathplangoto
import taskcheckforinterrupt

class TaskSearchPattern(taskobject.Task):
    """TaskSearchPattern Object"""

    def __init__(self,pattern_number,callme):
        super().__init__()
        self.name="TaskSearchPattern"
        print("new",self.name,"object")
        self.callme=callme # call this function at every node
        self.step_limit=100
        self.search_mx=0
        self.search_my=0
        self.search_step=0
        self.search_list=[]

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

        if pattern_number == 3:
            self.pattern_init=self.pattern3_init
            self.pattern_start=self.pattern3_start
            self.pattern_poll=self.pattern3_poll

        self.pattern_init()

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

        print("search at",self.search_mx,self.search_my)
        if gbstate.unreachable:
            # Skip this one.
            gbstate.unreachable=False
        else:
            self.parent.Push(taskcheckforinterrupt.TaskCheckForInterrupt())
            self.callme()
            self.parent.Push(taskcheckforinterrupt.TaskCheckForInterrupt())

        #self.parent.Push(taskcheckforinterrupt.TaskCheckForInterrupt())

        self.pattern_poll()

        #self.parent.Push(taskcheckforinterrupt.TaskCheckForInterrupt())

        return

    def Start(self):
        """Cause the task to begin doing whatever."""
        print(self.name,"Start")
        if self.started:
            return # already started
        self.started=True
        self.pattern_start()

    def DebugRecursive(self,indent=0):
        self.DebugPrint(self.name,indent)

    def NameRecursive(self):
        gbstate.task_stack_names.append(self.name)
        myname=self.name
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
        if self.search_mx >= gbdata.map_width:
            self.search_mx=0
            self.search_my+=self.search_step
            if self.search_my >= gbdata.map_height:
                self.search_my=0
                print(self.name,"done")
                self.taskdone=True
                return
        self.parent.Push(taskpathplangoto.TaskPathPlanGoTo(self.search_mx,self.search_my))

    # pattern 1 is the same locations as pattern 0 but selected randomly.
    def pattern1_init(self):
        self.search_mx=0
        self.search_my=0
        self.search_step=7
        self.search_list=[]
        for my in range(0,gbdata.map_height,self.search_step):
            for mx in range(0,gbdata.map_width,self.search_step):
                self.search_list.append((mx,my))

    def pattern1_start(self):
        l=len(self.search_list)
        if l < 1:
            print(self.name,"done")
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
            print(self.name,"done")
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
        for my in range(0,gbdata.map_height,self.search_step):
            for mx in range(0,gbdata.map_width,self.search_step):
                self.search_list.append((mx,my))
        #for my in range(0,int(gbdata.map_height/2),self.search_step):
        #    for mx in range(0,int(gbdata.map_width/2),self.search_step):
        #        self.search_list.append((mx,int(gbdata.map_height/2)+my))

    def pattern2_start(self):
        l=len(self.search_list)
        if l < 1:
            print(self.name,"done")
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
            print(self.name,"done")
            self.taskdone=True
            return
        j=random.randint(0,l-1)
        (mx,my)=self.search_list[j]
        del self.search_list[j]
        self.search_mx=mx
        self.search_my=my
        self.parent.Push(taskpathplangoto.TaskPathPlanGoTo(mx,my))

    # pattern 3 is the same as pattern 1 but selected
    # with smaller steps.
    def pattern3_init(self):
        self.search_mx=0
        self.search_my=0
        self.search_step=4
        self.search_list=[]
        for my in range(0,gbdata.map_height,self.search_step):
            for mx in range(0,gbdata.map_width,self.search_step):
                self.search_list.append((mx+0.5,my+0.5))
        l=len(self.search_list)
        if l <= self.step_limit:
            return
        l2=l
        if l2 > self.step_limit:
            l2=self.step_limit
        offset=random.randint(0,l-1)
        max_steps=random.randint(0,l2-1)

        if (offset+max_steps) <= l:
            # the reduced list is a one-part subset of the original list
            reduced_list=self.search_list[offset:(offset+max_steps)]
            self.search_list=reduced_list
            return
        # the reduced list is a two-part subset of the original list

        reduced_part_1=self.search_list[offset:]
        reduced_part_2=self.search_list[0:((offset+max_steps)%l)]
        self.search_list=reduced_part_1
        self.search_list.extend(reduced_part_2)
        return

    def pattern3_start(self):
        self.pattern_poll()
        return

    def pattern3_poll(self):
        l=len(self.search_list)
        if l < 1:
            print(self.name,"done")
            self.taskdone=True
            return
        j=random.randint(0,l-1)
        (mx,my)=self.search_list[j]
        del self.search_list[j]
        self.search_mx=mx
        self.search_my=my
        self.parent.Push(taskpathplangoto.TaskPathPlanGoTo(mx,my))
        return
