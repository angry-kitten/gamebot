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
import tasktree
import taskdig

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
                print("no digested")
                return False
            localdigested=gbstate.digested
        if gbstate.center_mx < 0:
            print("no center")
            return
        target_list=gbdata.gatherable_items.copy()
        if gbstate.inventory_has_net:
            target_list.extend(gbdata.treeable_items)
        if gbstate.inventory_has_shovel:
            target_list.extend(gbdata.digable_items)

        found_list=gbdisplay.find_detect(target_list,gbstate.player_mx,gbstate.player_my,self.close,10,0.30)

        if found_list is None:
            print("empty found_list 1")
            return

        print("found_list",found_list)
        l=len(found_list)
        if l < 1:
            print("empty found_list 2")
            return

        pick=random.randint(0,l-1)
        best_thing=found_list[pick]

        print("best_thing",best_thing)

        if gbdata.treeable_items.count(best_thing[0]) > 0:
            (mx,my)=gbdisplay.convert_pixel_to_map(best_thing[4],best_thing[5])
        else:
            (mx,my)=gbdisplay.convert_pixel_to_map(best_thing[2],best_thing[3])
        if mx < 0:
            print("bad position")
            return
        print("target thing mx",mx,"my",my)

        self.target_mx=mx
        self.target_my=my

        if gbdata.gatherable_items.count(best_thing[0]) > 0:
            print("gatherable")
            print(gbdata.gatherable_items)
            self.parent.Push(taskgather.TaskGather(gbdata.gatherable_items))
            return

        if gbdata.treeable_items.count(best_thing[0]) > 0:
            print("treeable")
            self.parent.Push(tasktree.TaskTree(gbdata.treeable_items))
            return

        if gbdata.digable_items.count(best_thing[0]) > 0:
            print("digable")
            self.parent.Push(taskdig.TaskDig(gbdata.digable_items))
            return

        print("nothing")
        return
