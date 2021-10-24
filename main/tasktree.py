#
# Copyright 2021 by angry-kitten
# Look at the current screen for treeable items and gather wood
# and fruit.
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
import taskpickup
import taskdetermineposition
import taskpause
import taskholdtool
import taskgather

class TaskTree(taskobject.Task):
    """TaskTree Object"""

    def __init__(self,target_list):
        super().__init__()
        self.name="TaskTree"
        print("new",self.name,"object")
        self.target_list=target_list
        self.target_mx=-1
        self.target_my=-1
        self.close=6
        self.step=0

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
        # Find a tree

        if self.step == 0: # initial search
            print("tasktree step 0")
            if self.target_mx < 0:
                # At this point a search for an item hasn't been done yet.
                self.find_an_item()
                if self.target_mx < 0:
                    # At this point no item was found by the search.
                    print("no target found")
                    print(self.name,"done")
                    self.taskdone=True
                    return
                # At this point a tree was found by the search and subtasks
                # have been added to the stack to go to the tree.
                self.step=1
                return

        if self.step == 1: # in front of the tree, ready to shake
            print("tasktree step 1")
            print("current_tool",gbstate.current_tool)
            #if gbdata.net_tools.count(gbstate.current_tool) < 1:
            if gbstate.current_tool != "Net":
                print("not holding a net")
                self.step=99 # done
                # Put any tools away just in case.
                self.parent.Push(taskholdtool.TaskHoldTool('None'))
                return
            # Swing the net just in case a wasp nest was triggered.
            self.parent.Push(taskpress.TaskPress('A'))
            # Wait for a possible wasp nest animation.
            self.parent.Push(taskobject.TaskTimed(3.0))
            # Shake the tree with 'A' and maybe trigger a wasp nest.
            self.parent.Push(taskpress.TaskPress('A'))
            self.step=2 # continue to selecting a stone axe
            return

        if self.step == 2: # select a stone axe
            print("tasktree step 2")
            self.parent.Push(taskholdtool.TaskHoldTool('StoneAxe'))
            self.parent.Push(taskholdtool.TaskHoldTool('None'))
            self.step=3 # continue to verify the axe and then use it
            return

        if self.step == 3: # verify the axe and then use it
            print("tasktree step 3")
            print("current_tool",gbstate.current_tool)
            #if gbdata.stone_axe_tools.count(gbstate.current_tool) < 1:
            if gbstate.current_tool != "StoneAxe":
                print("not holding a stone axe")
                self.step=99 # done
                # Put any tools away just in case.
                self.parent.Push(taskholdtool.TaskHoldTool('None'))
                return

            # Gather up to seven items. 3 wood, 3 fruit, 1 wasp nest
            self.parent.Push(taskgather.TaskGather(gbdata.gatherable_items))
            self.parent.Push(taskgather.TaskGather(gbdata.gatherable_items))
            self.parent.Push(taskgather.TaskGather(gbdata.gatherable_items))
            self.parent.Push(taskgather.TaskGather(gbdata.gatherable_items))
            self.parent.Push(taskgather.TaskGather(gbdata.gatherable_items))
            self.parent.Push(taskgather.TaskGather(gbdata.gatherable_items))
            self.parent.Push(taskgather.TaskGather(gbdata.gatherable_items))
            # Put the axe away.
            self.parent.Push(taskholdtool.TaskHoldTool('None'))
            # Swing the axe three times.
            self.parent.Push(taskobject.TaskTimed(1.0)) # let the animation play out
            # Swing the stone axe
            self.parent.Push(taskpress.TaskPress('A'))
            self.parent.Push(taskobject.TaskTimed(1.0)) # let the animation play out
            # Swing the stone axe
            self.parent.Push(taskpress.TaskPress('A'))
            self.parent.Push(taskobject.TaskTimed(1.0)) # let the animation play out
            # Swing the stone axe
            self.parent.Push(taskpress.TaskPress('A'))

            # Go to the tree facing north.
            self.parent.Push(taskpathplangoto.TaskPathPlanGoTo(self.target_mx,self.target_my))
            # Go to one square in front of the tree.
            self.parent.Push(taskpathplangoto.TaskPathPlanGoTo(self.target_mx,self.target_my+1))

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
                return False
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

        (mx,my)=gbdisplay.convert_pixel_to_map(best_thing[4],best_thing[5])
        if mx < 0:
            print("bad position")
            return
        print("target thing mx",mx,"my",my)

        self.target_mx=mx
        self.target_my=my

        # push tasks in reverse order
        self.parent.Push(taskpause.TaskPause('process tree',2.0))
        # Go to the tree facing north.
        self.parent.Push(taskpathplangoto.TaskPathPlanGoTo(mx,my))
        # Go to one square in front of the tree.
        self.parent.Push(taskpathplangoto.TaskPathPlanGoTo(mx,my+1))
        # Start holding the net now because it causes the player character to
        # face down/south.
        self.parent.Push(taskholdtool.TaskHoldTool('Net'))
        self.parent.Push(taskholdtool.TaskHoldTool('None'))
