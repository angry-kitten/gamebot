#
# Copyright 2021-2022 by angry-kitten
# Look at the current screen for treeable items and gather wood
# and fruit.
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
import taskcenterplayer
import taskpickup
import taskdetermineposition
import taskholdtool
import tasktrackturn

class TaskDig(taskobject.Task):
    """TaskDig Object"""

    def __init__(self,target_list):
        super().__init__()
        self.name="TaskDig"
        print("new",self.name,"object")
        self.target_list=target_list
        self.target_mx=-1
        self.target_my=-1
        self.close=6
        self.step=0
        (mox,moy)=gbdata.directions_offsets_x_y[random.randint(0,3)]
        self.mox=mox
        self.moy=moy

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
        # Find a crack

        if self.step == 0:
            if self.target_mx < 0:
                # At this point a search for an item hasn't been done yet.
                self.find_an_item()
                if self.target_mx < 0:
                    # At this point no item was found by the search.
                    print("no target found")
                    print(self.name,"done")
                    self.taskdone=True
                # At this point a crack was found by the search and subtasks
                # have been added to the stack.
                self.step=1
                return

        if self.step == 1: # in front of the crack, ready to dig
            print("current_tool",gbstate.current_tool)
            if gbstate.current_tool != "Shovel":
                print("not holding a shovel")
                self.step=99 # done
                return

            # Put away the shovel.
            self.parent.Push(taskholdtool.TaskHoldTool('None'))

            self.parent.Push(taskobject.TaskTimed(2.0)) # wait for the animation

            # close the presentation text with 'B'
            self.parent.Push(taskpress.TaskPress('B'))
            self.parent.Push(taskobject.TaskTimed(9.0)) # wait for the dig and presentation animation
            # Dig with 'A'
            self.parent.Push(taskpress.TaskPress('A'))

            # Face the crack.
            heading=0
            if self.mox == 1:
                # Face left.
                heading=270
            elif self.mox == -1:
                # Face right.
                heading=90
            if self.moy == 1:
                # Face up.
                heading=0
            elif self.moy == -1:
                # Face down.
                heading=180
            self.parent.Push(tasktrackturn.TaskTrackTurn(heading))

            self.step=99 # done
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
        # Hold a shovel. This will also cause the player character to face
        # down/south.
        self.parent.Push(taskholdtool.TaskHoldTool('Shovel'))
        # Go to the position offset by one in one of four directions.
        mx+=self.mox
        my+=self.moy
        self.parent.Push(taskpathplangoto.TaskPathPlanGoTo(mx,my))
        return
