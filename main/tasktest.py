#
# Copyright 2021 by angry-kitten
# Run a test (varies over time)
#

import random
import math

import taskobject
import gbdata
import gbstate
import cv2
import taskpress
import tasksay
import taskdetect
import taskgotomain
import taskupdatemini
import taskjoy

class TaskTest(taskobject.Task):
    """TaskTest Object"""

    def __init__(self):
        super().__init__()
        print("new TaskTest object")
        self.iterations=10
        self.i=0
        self.seconds=2
        self.start_mx=-1
        self.start_my=-1
        self.dlist=[]

    def Poll(self):
        """check if any action can be taken"""
        print("TaskTest Poll")
        if not self.started:
            self.Start()
            return
        if self.taskdone:
            return
        if gbstate.frame is None:
            return

        if gbstate.position_minimap_x < 0:
            print("bad position")
            print("TaskTest done")
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
            rate=self.dlist[j]/self.seconds
            print("distance per second",rate)
            rate_total+=rate
        distance_average=distance_total/self.iterations
        rate_average=rate_total/self.iterations
        print("average distance",distance_average)
        print("average distance per second",rate_average)

        print("TaskTest done")
        self.taskdone=True
        return

    def Start(self):
        """Cause the task to begin doing whatever."""
        print("TaskTest Start")
        if self.started:
            return # already started
        self.started=True

        self.parent.Push(taskupdatemini.TaskUpdateMini())
        self.parent.Push(taskobject.TaskTimed()) # default 1 second delay

    def DebugRecursive(self,indent=0):
        self.DebugPrint("TaskTest",indent)

    def startmove(self):
        self.start_mx=gbstate.position_minimap_x
        self.start_my=gbstate.position_minimap_y

        self.parent.Push(taskupdatemini.TaskUpdateMini())
        self.parent.Push(taskobject.TaskTimed()) # default 1 second delay

        heading=90
        #if (self.i % 2) == 1:
        #    heading=90
        #else:
        #    heading=270
        self.parent.Push(taskjoy.TaskJoyLeft(heading,1.0,3.0,int(self.seconds*1000)))
        
