#
# Copyright 2021-2022 by angry-kitten
# Look at the current screen for treeable items and gather wood
# and fruit.
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
import taskpause
import taskholdtool
import taskgather
import tasktrackturn
import taskheadinggoto

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

        print(self.name,f"step={self.step}")

        if self.step == 0: # initial search
            print("tasktree step 0")
            if self.target_mx < 0:
                # At this point a search for an item hasn't been done yet.
                self.find_an_item(False) # False= do not prefer north/up
                if self.target_mx < 0:
                    # At this point no item was found by the search.
                    print("no target found")
                    print(self.name,"done")
                    self.taskdone=True
                    return
                # At this point a tree was found by the search and subtasks
                # have been added to the stack to go to the tree.
                self.step=101
                return
            self.step=99 # done
            return

        if self.step == 101:
            # Go to a spot in front of the target to be
            # able to get a better fix on its location.

            self.parent.Push(taskdetect.TaskDetect())
            self.parent.Push(taskdetermineposition.TaskDeterminePosition())

            self.parent.Push(taskpathplangoto.TaskPathPlanGoTo(self.target_mx,self.target_my+2))
            self.step=102
            return

        if self.step == 102:
            # Search again at this location to try to get a better fix.
            self.find_an_item(True) # True= do prefer north/up
            if self.target_mx < 0:
                # no item was found by the search.
                print("no target found")
                print(self.name,"done")
                self.taskdone=True
                self.step=99 # done
                return

            # Face up/north to face the tree.
            self.parent.Push(tasktrackturn.TaskTrackTurn(0))

            # walk up against the tree
            self.parent.Push(taskheadinggoto.TaskHeadingGoTo(0,0.4))

            # This will cause the player character to face down/south.
            self.parent.Push(taskholdtool.TaskHoldTool('Net'))

            # Go to the tree facing north.
            self.parent.Push(taskpathplangoto.TaskPathPlanGoTo(self.target_mx,self.target_my))
            # Go to one square in front of the tree.
            self.parent.Push(taskpathplangoto.TaskPathPlanGoTo(self.target_mx,self.target_my+1))
            self.step=1
            return

        if self.step == 1: # Verify the net
            print("tasktree step 1")
            print("current_tool",gbstate.current_tool)
            if gbstate.current_tool != "Net":
                print("not holding a net")
                self.step=99 # done
                # Put any tools away just in case.
                self.parent.Push(taskholdtool.TaskHoldTool('None'))
                return

            self.step=2
            return

        if self.step == 2: # in front of the tree, ready to shake
            print("tasktree step 2")

            # Close the presentation, if there is one.
            self.parent.Push(taskpress.TaskPress('B'))

            # Wait for a possible wasp presentation animation.
            self.parent.Push(taskobject.TaskTimed(8))

            # Swing the net just in case a wasp nest was triggered.
            self.parent.Push(taskpress.TaskPress('A'))
            self.parent.Push(taskpress.TaskPress('A'))
            self.parent.Push(taskpress.TaskPress('A'))
            self.parent.Push(taskpress.TaskPress('A'))
            self.parent.Push(taskpress.TaskPress('A'))
            # Wait for a possible wasp nest animation.
            self.parent.Push(taskobject.TaskTimed(2.5))
            # Shake the tree with 'A' and maybe trigger a wasp nest.
            self.parent.Push(taskpress.TaskPress('A'))
            self.step=3 # continue to selecting a stone axe
            return

        if self.step == 3: # select a stone axe
            print("tasktree step 3")
            self.parent.Push(taskholdtool.TaskHoldTool('StoneAxe'))
            self.parent.Push(taskholdtool.TaskHoldTool('None'))
            self.step=4 # continue to verify the axe and then use it
            return

        if self.step == 4: # verify the axe and then use it
            print("tasktree step 4")
            print("current_tool",gbstate.current_tool)
            #if gbdata.stone_axe_tools.count(gbstate.current_tool) < 1:
            if gbstate.current_tool != "StoneAxe":
                print("not holding a stone axe")
                self.step=99 # done
                # Put any tools away just in case.
                self.parent.Push(taskholdtool.TaskHoldTool('None'))
                return

            # Put the axe away.
            self.parent.Push(taskholdtool.TaskHoldTool('None'))
            # Swing the axe three times.
            self.parent.Push(taskobject.TaskTimed(2.0)) # let the animation play out
            # Swing the stone axe
            self.parent.Push(taskpress.TaskPress('A'))
            self.parent.Push(taskobject.TaskTimed(1.0)) # let the animation play out
            # Swing the stone axe
            self.parent.Push(taskpress.TaskPress('A'))
            self.parent.Push(taskobject.TaskTimed(1.0)) # let the animation play out
            # Swing the stone axe
            self.parent.Push(taskpress.TaskPress('A'))

            # Face up/north to face the tree.
            self.parent.Push(tasktrackturn.TaskTrackTurn(0))

            # walk up against the tree
            self.parent.Push(taskheadinggoto.TaskHeadingGoTo(0,0.8))

            self.step=10
            return

        if self.step == 10: # walk around the base of the tree and gather
            print("tasktree step 10")
            # 6 5 4
            # 7 T 3
            # 8 1 2

            gbstate.inventory_needed=True

            # Gather at position 8
            self.parent.Push(taskpickup.TaskPickupSpin())
            # Face down/south and step 1
            self.parent.Push(taskheadinggoto.TaskHeadingGoTo(180,1.3))

            # Gather at position 7
            self.parent.Push(taskpickup.TaskPickupSpin())
            # Face down/south and step 1
            self.parent.Push(taskheadinggoto.TaskHeadingGoTo(180,1.3))

            # Gather at position 6
            self.parent.Push(taskpickup.TaskPickupSpin())
            # Face left/west and step 1
            self.parent.Push(taskheadinggoto.TaskHeadingGoTo(270,1.3))

            # Gather at position 5
            self.parent.Push(taskpickup.TaskPickupSpin())
            # Face left/west and step 1
            self.parent.Push(taskheadinggoto.TaskHeadingGoTo(270,1.3))

            # Gather at position 4
            self.parent.Push(taskpickup.TaskPickupSpin())
            # Face up/north and step 1
            self.parent.Push(taskheadinggoto.TaskHeadingGoTo(0,1.3))

            # Gather at position 3
            self.parent.Push(taskpickup.TaskPickupSpin())
            # Face up/north and step 1
            self.parent.Push(taskheadinggoto.TaskHeadingGoTo(0,1.3))

            # Gather at position 2
            self.parent.Push(taskpickup.TaskPickupSpin())
            # Face right/east and step 1
            self.parent.Push(taskheadinggoto.TaskHeadingGoTo(90,1.3))

            # Gather at position 1
            self.parent.Push(taskpickup.TaskPickupSpin())

            # Face up/north to face the tree.
            self.parent.Push(tasktrackturn.TaskTrackTurn(0))

            ## walk up against the tree
            #self.parent.Push(taskheadinggoto.TaskHeadingGoTo(0,0.4))

            # Go to the tree facing north.
            self.parent.Push(taskpathplangoto.TaskPathPlanGoTo(self.target_mx,self.target_my))
            # Go to one square in front of the tree.
            self.parent.Push(taskpathplangoto.TaskPathPlanGoTo(self.target_mx,self.target_my+1))

            self.step=20
            return

        if self.step == 20: # see if we can get more gathered with TaskGather.
            print("tasktree step 20")
            # Gather up to seven items. 3 wood, 3 fruit, 1 wasp nest
            self.parent.Push(taskgather.TaskGather(gbdata.gatherable_items))
            self.parent.Push(taskgather.TaskGather(gbdata.gatherable_items))
            self.parent.Push(taskgather.TaskGather(gbdata.gatherable_items))
            self.parent.Push(taskgather.TaskGather(gbdata.gatherable_items))
            self.parent.Push(taskgather.TaskGather(gbdata.gatherable_items))
            self.parent.Push(taskgather.TaskGather(gbdata.gatherable_items))
            self.parent.Push(taskgather.TaskGather(gbdata.gatherable_items))

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
        self.parent.Push(taskholdtool.TaskHoldTool('None'))

    def DebugRecursive(self,indent=0):
        self.DebugPrint(self.name,indent)

    def NameRecursive(self):
        gbstate.task_stack_names.append(self.name)
        return self.name

    def find_an_item(self,prefer_north):
        print("find an item")
        self.target_mx=-1
        self.target_my=-1
        if gbstate.detection_lock is None:
            return
        with gbstate.detection_lock:
            if gbstate.digested is None:
                return
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

        if prefer_north:
            # Pick a target that is as close to north of the player
            # character as we can get. This should have a good position
            # fix. It should also be the target picked by the previous
            # call to find_an_item.
            best_thing=None
            best_mx_offset=0
            for thing in found_list:
                (mx,my)=gbdisplay.convert_pixel_to_map(thing[4],thing[5])
                if mx < 0:
                    print("bad position")
                    continue
                if my >= gbstate.player_my:
                    # Only accept items north/up from player character.
                    continue
                dx=gbstate.player_mx-mx
                offset=abs(dx)
                print("offset",offset,thing)
                if best_thing is None:
                    best_thing=thing
                    best_mx_offset=offset
                elif offset < best_mx_offset:
                    best_thing=thing
                    best_mx_offset=offset
            if best_thing is None:
                print("item not found with prefer_north")
                return
        else:
            # Pick a random target from the list.
            pick=random.randint(0,l-1)
            best_thing=found_list[pick]

        print("best_thing",best_thing)

        (mx,my)=gbdisplay.convert_pixel_to_map(best_thing[4],best_thing[5])
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

        return
