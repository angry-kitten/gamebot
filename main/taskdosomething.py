#
# Copyright 2021-2022 by angry-kitten
# Pick something for the character to do.
#

import cv2
import gbdata, gbstate
import taskobject
import taskpress
import tasksay
import taskdetect
import taskgotomain
import taskupdatemini
import taskrandomwalk
import taskweed
import taskweedsearch
import tasksearchpattern
import taskcheckforinterrupt
import taskholdtool
import taskpicksomethingsearch
import taskbeachcomber

class TaskDoSomething(taskobject.Task):
    """TaskDoSomething Object"""

    def __init__(self):
        super().__init__()
        self.name="TaskDoSomething"
        print("new TaskDoSomething object")

    def Poll(self):
        """check if any action can be taken"""
        print("TaskDoSomething Poll")
        if not self.started:
            self.Start()
            return
        if self.taskdone:
            return
        if gbstate.frame is None:
            return

        #self.parent.Push(taskrandomwalk.TaskRandomWalk())
        ##self.parent.Push(taskweed.TaskWeed())
        ##self.parent.Push(taskweedsearch.TaskWeedSearch())
        #self.parent.Push(taskholdtool.TaskHoldTool('None'))
        #self.parent.Push(taskholdtool.TaskHoldTool('Pole'))
        #self.parent.Push(taskholdtool.TaskHoldTool('Ladder'))
        #self.parent.Push(taskholdtool.TaskHoldTool('Shovel'))
        #self.parent.Push(taskholdtool.TaskHoldTool('Axe'))
        #self.parent.Push(taskholdtool.TaskHoldTool('Slingshot'))
        #self.parent.Push(taskholdtool.TaskHoldTool('FishingPole'))
        #self.parent.Push(taskholdtool.TaskHoldTool('WateringCan'))
        #self.parent.Push(taskholdtool.TaskHoldTool('Net'))
        #self.parent.Push(taskholdtool.TaskHoldTool('StoneAxe'))
        #self.parent.Push(taskholdtool.TaskHoldTool('None'))

        #self.parent.Push(taskcheckforinterrupt.TaskCheckForInterrupt())

        self.parent.Push(taskbeachcomber.TaskBeachcomber())
        self.parent.Push(taskpicksomethingsearch.TaskPickSomethingSearch())

        return

    def Start(self):
        """Cause the task to begin doing whatever."""
        print("TaskDoSomething Start")
        if self.started:
            return # already started
        self.started=True

    def DebugRecursive(self,indent=0):
        self.DebugPrint("TaskDoSomething",indent)

    def NameRecursive(self):
        gbstate.task_stack_names.append(self.name)
        myname="TaskDoSomething"
        return myname
