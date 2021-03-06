#
# Copyright 2021-2022 by angry-kitten
# Look at the current screen for gatherable items and pick them.
#

import random
import cv2
import gbdata
import gbstate
import gbscreen
import gbdisplay
import taskobject
import taskpress
import tasksay
import taskdetect
import taskgotomain
import taskupdatemini
import taskrandomwalk
import tasksimplegoto
import taskpathplangoto
import taskcenterplayer
import taskpickup
import taskdetermineposition

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
        gbstate.inventory_needed=True
        # push tasks in reverse order
        self.parent.Push(taskdetect.TaskDetect())
        self.parent.Push(taskdetermineposition.TaskDeterminePosition())

    def DebugRecursive(self,indent=0):
        self.DebugPrint(self.name,indent)

    def NameRecursive(self):
        gbstate.task_stack_names.append(self.name)
        return self.name

    def find_an_item(self):
        print("find an item")
        with gbstate.detection_lock:
            if gbstate.digested is None:
                return
            localdigested=gbstate.digested
        if gbstate.center_mx < 0:
            return

        found_list=gbdisplay.find_detect(self.target_list,gbstate.player_mx,gbstate.player_my,self.close,10,0.30)

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

        (mx,my)=gbdisplay.convert_pixel_to_map(best_thing[2],best_thing[3])
        if mx < 0:
            print("bad position")
            return
        print("target thing mx",mx,"my",my)

        # Assume the object in in the center of a map square. Adjust the
        # location to show that.
        mx=int(mx)+0.5
        my=int(my)+0.5
        print("target thing mx",mx,"my",my)

        self.target_mx=mx
        self.target_my=my

        # push tasks in reverse order
        self.parent.Push(taskdetermineposition.TaskDeterminePosition())
        self.parent.Push(taskdetect.TaskDetect())
        self.parent.Push(taskpickup.TaskPickupSpin())
        self.parent.Push(taskpathplangoto.TaskPathPlanGoTo(mx,my))
        return
