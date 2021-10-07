#
# Copyright 2021 by angry-kitten
# Look at the current screen for weeds and pick them.
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

class TaskWeed(taskobject.Task):
    """TaskWeed Object"""

    def __init__(self):
        super().__init__()
        print("new TaskWeed object")
        self.target_mx=-1
        self.target_my=-1
        self.close=5

    def Poll(self):
        """check if any action can be taken"""
        print("TaskWeed Poll")
        if not self.started:
            self.Start()
            return
        if self.taskdone:
            return
        if gbstate.frame is None:
            return
        # Find a weed

        if self.target_mx < 0:
            self.find_a_weed()
            if self.target_mx < 0:
                print("no target found")
                print("TaskWeed done")
                self.taskdone=True
            return

        gbstate.object_target_mx=-1
        gbstate.object_target_my=-1
        print("TaskWeed done")
        self.taskdone=True
        return

    def Start(self):
        """Cause the task to begin doing whatever."""
        print("TaskWeed Start")
        if self.started:
            return # already started
        self.started=True
        # push tasks in reverse order
        self.parent.Push(taskupdatemini.TaskUpdateMini())
        self.parent.Push(taskobject.TaskTimed()) # default 1 second delay
        self.parent.Push(taskdetect.TaskDetect())

    def DebugRecursive(self,indent=0):
        self.DebugPrint("TaskWeed",indent)

    def find_a_weed(self):
        print("find a weed")
        with gbstate.detection_lock:
            if gbstate.digested is None:
                return False
            localdigested=gbstate.digested
        if gbstate.center_mx < 0:
            return
        weeds=[]
        for det in localdigested:
            print(det)
            # det is [name,score,cx,cy,bx,by]
            if det[0] == "Weeds":
                weeds.append(det)
        print("weeds",weeds)
        l=len(weeds)
        if l < 1:
            print("empty weeds list")
            return

        close_weeds=[]
        for weed in weeds:
            print(weed)
            (mx,my)=gbdisplay.convert_pixel_to_map(weed[2],weed[3]) # use cx cy
            d=gbdisplay.calculate_distance(mx,my,gbstate.center_mx,gbstate.center_my)
            if d < self.close:
                close_weeds.append(weed)

        print("close_weeds",close_weeds)
        l=len(close_weeds)
        if l < 1:
            print("empty close weeds list")
            return

        best_weed=None # Insert pot jokes here.
        for weed in close_weeds:
            if best_weed is None:
                best_weed=weed
            elif best_weed[1] < weed[1]:
                best_weed=weed

        print("best_weed",best_weed)

        print("found weed",best_weed)

        (mx,my)=gbdisplay.convert_pixel_to_map(best_weed[4],best_weed[5])
        if mx < 0:
            print("bad position")
            return
        print("target weed mx",mx,"my",my)

        self.target_mx=mx
        self.target_my=my
        gbstate.object_target_mx=mx
        gbstate.object_target_my=my

        # push tasks in reverse order
        self.parent.Push(taskupdatemini.TaskUpdateMini())
        self.parent.Push(taskobject.TaskTimed()) # default 1 second delay
        self.parent.Push(taskdetect.TaskDetect())
        #self.parent.Push(taskrandomwalk.TaskRandomWalk())
        self.parent.Push(taskpress.TaskPress('Y'))
        self.parent.Push(tasksimplegoto.TaskSimpleGoTo(mx,my))
