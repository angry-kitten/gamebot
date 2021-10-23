#
# Copyright 2021 by angry-kitten
# Look at the current screen and pick something to do.
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
import taskweed
import taskgather
import taskdetermineposition

class TaskPickSomething(taskobject.Task):
    """TaskPickSomething Object"""

    def __init__(self):
        super().__init__()
        self.name="TaskPickSomething"
        print("new TaskPickSomething object")
        self.target_mx=-1
        self.target_my=-1
        #self.close=5
        self.close=6

    def Poll(self):
        """check if any action can be taken"""
        print("TaskPickSomething Poll")
        if not self.started:
            self.Start()
            return
        if self.taskdone:
            return
        if gbstate.frame is None:
            return
        # Find a weed

        if self.target_mx < 0:
            # At this point a search hasn't been done yet.
            self.find_something()
            if self.target_mx < 0:
                # At this point no target was found by the search.
                print("no target found")
                print("TaskPickSomething done")
                self.taskdone=True
            # At this point something was found by the search and subtasks
            # have been added to the stack.
            return

        gbstate.object_target_mx=-1
        gbstate.object_target_my=-1
        print("TaskPickSomething done")
        self.taskdone=True
        return

    def Start(self):
        """Cause the task to begin doing whatever."""
        print("TaskPickSomething Start")
        if self.started:
            return # already started
        self.started=True
        # push tasks in reverse order
        self.parent.Push(taskdetermineposition.TaskDeterminePosition())
        self.parent.Push(taskdetect.TaskDetect())

    def DebugRecursive(self,indent=0):
        self.DebugPrint("TaskPickSomething",indent)

    def NameRecursive(self):
        gbstate.task_stack_names.append(self.name)
        myname="TaskPickSomething"
        return myname

    def find_something(self):
        print("find something")
        with gbstate.detection_lock:
            if gbstate.digested is None:
                return False
            localdigested=gbstate.digested
        if gbstate.center_mx < 0:
            return
        things=[]
        for det in localdigested:
            print(det)
            # det is [name,score,cx,cy,bx,by]
            if det[0] == "Weeds":
                things.append(det)
        print("things",things)
        l=len(things)
        if l < 1:
            print("empty things list")
            self.parent.Push(taskgather.TaskGather(gbdata.gatherable_items))
            return

        close_things=[]
        for thing in things:
            print(thing)
            (mx,my)=gbdisplay.convert_pixel_to_map(thing[2],thing[3]) # use cx cy
            d=gbdisplay.calculate_distance(mx,my,gbstate.center_mx,gbstate.center_my)
            if d < self.close:
                close_things.append(thing)

        print("close_things",close_things)
        l=len(close_things)
        if l < 1:
            print("empty close things list")
            self.parent.Push(taskgather.TaskGather(gbdata.gatherable_items))
            return

        best_thing=None
        for thing in close_things:
            if best_thing is None:
                best_thing=thing
            elif best_thing[1] < thing[1]:
                best_thing=thing

        print("best_thing",best_thing)

        print("found thing",best_thing)

        (mx,my)=gbdisplay.convert_pixel_to_map(best_thing[2],best_thing[3])
        if mx < 0:
            print("bad position")
            return
        print("target thing mx",mx,"my",my)

        self.target_mx=mx
        self.target_my=my
        #gbstate.object_target_mx=mx
        #gbstate.object_target_my=my

        if best_thing[0] == "Weeds":
            self.parent.Push(taskweed.TaskWeed())
            return

        self.parent.Push(taskgather.TaskGather(gbdata.gatherable_items))
        return
