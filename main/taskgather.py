#
# Copyright 2021 by angry-kitten
# Look at the current screen for gatherable items and pick them.
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
import taskpathplangoto
import gbscreen
import gbdisplay
import random
import taskcenterplayer

class TaskGather(taskobject.Task):
    """TaskGather Object"""

    def __init__(self,target_list):
        super().__init__()
        self.name="TaskGather"
        print("new",self.name,"object")
        self.target_list=target_list
        self.target_mx=-1
        self.target_my=-1
        self.close=6

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
        # Find a weed

        if self.target_mx < 0:
            # At this point a search for an item hasn't been done yet.
            self.find_an_item()
            if self.target_mx < 0:
                # At this point no item was found by the search.
                print("no target found")
                print(self.name,"done")
                self.taskdone=True
            # At this point a weed was found by the search and subtasks
            # have been added to the stack.
            return

        gbstate.object_target_mx=-1
        gbstate.object_target_my=-1
        print(self.name,"done")
        self.taskdone=True
        return

    def Start(self):
        """Cause the task to begin doing whatever."""
        print(self.name,"Start")
        if self.started:
            return # already started
        self.started=True
        # push tasks in reverse order
        self.parent.Push(taskupdatemini.TaskUpdateMini())
        self.parent.Push(taskdetect.TaskDetect())
        self.parent.Push(taskcenterplayer.TaskCenterPlayer())

    def DebugRecursive(self,indent=0):
        self.DebugPrint(self.name,indent)

    def NameRecursive(self):
        gbstate.task_stack_names.append(self.name)
        return self.name

    def find_an_item(self):
        print("find an item")
        with gbstate.detection_lock:
            if gbstate.digested is None:
                return False
            localdigested=gbstate.digested
        if gbstate.center_mx < 0:
            return
        items=[]
        for det in localdigested:
            print(det)
            # det is [name,score,cx,cy,bx,by]
            for t in self.target_list:
                if det[0] == t:
                    items.append(det)
        print("items",items)
        l=len(items)
        if l < 1:
            print("empty items list")
            return

        close_items=[]
        for item in items:
            print(item)
            (mx,my)=gbdisplay.convert_pixel_to_map(item[2],item[3]) # use cx cy
            d=gbdisplay.calculate_distance(mx,my,gbstate.center_mx,gbstate.center_my)
            if d < self.close:
                close_items.append(item)

        print("close_items",close_items)
        l=len(close_items)
        if l < 1:
            print("empty close items list")
            return

        best_item=None
        for item in close_items:
            if best_item is None:
                best_item=item
            elif best_item[1] < item[1]:
                best_item=item

        print("best_item",best_item)

        print("found item",best_item)

        (mx,my)=gbdisplay.convert_pixel_to_map(best_item[2],best_item[3])
        if mx < 0:
            print("bad position")
            return
        print("target item mx",mx,"my",my)

        self.target_mx=mx
        self.target_my=my
        gbstate.object_target_mx=mx
        gbstate.object_target_my=my

        # push tasks in reverse order
        self.parent.Push(taskupdatemini.TaskUpdateMini())
        self.parent.Push(taskdetect.TaskDetect())
        self.parent.Push(taskobject.TaskTimed(0.5)) # wait for the animation
        self.parent.Push(taskpress.TaskPress('Y'))
        self.parent.Push(taskpathplangoto.TaskPathPlanGoTo(mx,my))
