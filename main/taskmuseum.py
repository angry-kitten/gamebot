#
# Copyright 2021 by angry-kitten
# Go the the museum and evaluate fossils and donate items.
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
import gbscreen
import taskpathplangoto
import taskheadinggoto
import tasktrackturn

class TaskMuseum(taskobject.Task):
    """TaskMuseum Object"""

    def __init__(self):
        super().__init__()
        self.name="TaskMuseum"
        print("new",self.name,"object")
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

        if self.step == 0:
            self.parent.Push(taskobject.TaskTimed(10.0)) # wait for interior of museum

            # When the museum is still a tent, need to press 'A' to go inside.
            # this shouldn't do anything once the museum is a building.
            self.parent.Push(taskpress.TaskPress('A'))

            # Walk to the center of the museum, mapless. This should cause the player
            # character to enter.
            self.parent.Push(taskheadinggoto.TaskHeadingGoTo(0,2))
            self.step=1
            return

        if self.step == 1: # player character should be inside

            # Wait for Blathers to wake
            self.parent.Push(taskobject.TaskTimed(10.0))

            # Wake Blathers
            self.parent.Push(taskpress.TaskPress('A'))

            #self.parent.Push(taskobject.TaskTimed(1.0))

            # face Blathers
            self.parent.Push(tasktrackturn.TaskTrackTurn(45))

            # Walk forward.
            self.parent.Push(taskheadinggoto.TaskHeadingGoTo(0,3))

            self.step=2
            return

        if self.step == 2: # continue until menu
            if gbscreen.is_continue_triangle():
                # press continue and wait for animation
                self.parent.Push(taskobject.TaskTimed(5.0))
                self.parent.Push(taskpress.TaskPress('B'))
                return
            self.step=3
            return

        if self.step == 3: # select assess
            self.parent.Push(taskobject.TaskTimed(5.0))
            self.parent.Push(taskpress.TaskPress('A'))
            self.parent.Push(taskpress.TaskPress('hat_BOTTOM'))
            self.step=4
            return

        if self.step == 4: # continue until menu
            if gbscreen.is_continue_triangle():
                # press continue and wait for animation
                self.parent.Push(taskobject.TaskTimed(10.0))
                self.parent.Push(taskpress.TaskPress('B'))
                return
            self.step=5
            return

        if self.step == 5: # select donate
            self.parent.Push(taskobject.TaskTimed(5.0))
            self.parent.Push(taskpress.TaskPress('A'))
            self.parent.Push(taskobject.TaskTimed(5.0))
            self.step=6
            return

        if self.step == 6: # continue until done talking
            if gbscreen.is_continue_triangle():
                # press continue and wait for animation
                self.parent.Push(taskobject.TaskTimed(5.0))
                self.parent.Push(taskpress.TaskPress('B'))
                return
            self.step=8
            return

        if self.step == 8:
            # Wait for the exit animation.
            self.parent.Push(taskobject.TaskTimed(10.0))
            # Walk out of the museum, mapless.
            self.parent.Push(taskheadinggoto.TaskHeadingGoTo(180,4))
            self.step=99
            return

        # This is for debugging to get clear of the building detection.
        self.parent.Push(taskheadinggoto.TaskHeadingGoTo(90,8))
        self.parent.Push(taskobject.TaskTimed(5.0))

        print(self.name,"done")
        self.taskdone=True
        return

    def Start(self):
        """Cause the task to begin doing whatever."""
        print(self.name,"Start")
        if self.started:
            return # already started
        self.started=True
        self.step=0

        if gbstate.building_info_museum is None:
            print("no museum location info")
            self.step=99
            return

        doormx=gbstate.building_info_museum[3]
        doormy=gbstate.building_info_museum[4]
        self.parent.Push(taskpathplangoto.TaskPathPlanGoTo(doormx,doormy))
        return

    def DebugRecursive(self,indent=0):
        self.DebugPrint(self.name,indent)

    def NameRecursive(self):
        gbstate.task_stack_names.append(self.name)
        return self.name
