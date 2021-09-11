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
        self.find_a_weed()
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
        if gbstate.digested is None:
            return
        best_weed=None # Insert pot jokes here.
        weeds=[]
        for det in gbstate.digested:
            print(det)
            # det is [name,score,cx,cy,bx,by]
            if det[0] == "Weeds":
                #if best_weed is None:
                #    best_weed=det
                #elif best_weed[1] < det[1]:
                #    best_weed=det
                weeds.append(det)
        print("weeds",weeds)
        l=len(weeds)
        if l < 1:
            print("empty weeds list")
            return
        best_weed=weeds[random.randint(0,l-1)]
        #if best_weed is None:
        #    return
        print("found weed",best_weed)
        if gbstate.position_minimap_x < 0:
            print("player position not set")
            return
        (mx,my)=gbdisplay.convert_pixel_to_map(best_weed[4],best_weed[5])
        if mx < 0:
            print("bad position")
            return
        print("target weed mx",mx,"my",my)

        gbstate.target_mx=mx
        gbstate.target_my=my

        # push tasks in reverse order
        self.parent.Push(taskupdatemini.TaskUpdateMini())
        self.parent.Push(taskobject.TaskTimed()) # default 1 second delay
        self.parent.Push(taskdetect.TaskDetect())
        #self.parent.Push(taskrandomwalk.TaskRandomWalk())
        self.parent.Push(taskpress.TaskPress('Y'))
        self.parent.Push(tasksimplegoto.TaskSimpleGoTo(mx,my))
