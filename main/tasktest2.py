#
# Copyright 2021-2022 by angry-kitten
# Run a test (varies over time)
#

import random
import math
import cv2

import gbdata
import gbstate
import gbtrack
import taskobject
import taskpress
import tasksay
import taskdetect
import taskgotomain
import taskupdatemini
import taskjoy
import tasktrackgoto

class TaskTest2(taskobject.Task):
    """TaskTest2 Object"""

    def __init__(self):
        super().__init__()
        self.name="TaskTest2"
        print("new",self.name,"object")
        self.iterations=10
        self.i=0
        self.stepsize=2
        self.start_mx=-1
        self.start_my=-1
        self.dlist=[]

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

        if gbstate.position_minimap_x < 0:
            print("bad position")
            print(self.name,"done")
            self.taskdone=True
            return

        if self.start_mx < 0:
            self.startmove()
            return

        pmx=gbstate.position_minimap_x
        pmy=gbstate.position_minimap_y

        dx=pmx-self.start_mx
        dy=pmy-self.start_my
        distance=math.sqrt(dx*dx+dy*dy)
        print("i",self.i,"distance",distance)

        self.dlist.append(distance)
        self.i+=1

        if self.i < self.iterations:
            self.startmove()
            return

        distance_total=0
        rate_total=0
        for j in range(self.iterations):
            print("distance",self.dlist[j])
            distance_total+=self.dlist[j]
            rate=self.dlist[j]/1
            print("distance per second",rate)
            rate_total+=rate
        distance_average=distance_total/self.iterations
        rate_average=rate_total/self.iterations
        print("average distance",distance_average)
        print("average distance per second",rate_average)

        print(self.name,"done")
        self.taskdone=True
        return

    def Start(self):
        """Cause the task to begin doing whatever."""
        print(self.name,"Start")
        if self.started:
            return # already started
        self.started=True

        self.parent.Push(taskupdatemini.TaskUpdateMini())

    def DebugRecursive(self,indent=0):
        self.DebugPrint(self.name,indent)

    def NameRecursive(self):
        gbstate.task_stack_names.append(self.name)
        return self.name

    def startmove(self):
        self.start_mx=gbstate.position_minimap_x
        self.start_my=gbstate.position_minimap_y

        self.parent.Push(taskupdatemini.TaskUpdateMini())

        heading=90
        (dmx,dmy)=gbtrack.calculate_dx_dy(heading,self.stepsize)
        mx=gbstate.position_minimap_x
        my=gbstate.position_minimap_y
        mx+=dmx
        my+=dmy
        self.parent.Push(tasktrackgoto.TaskTrackGoTo(mx,my))
