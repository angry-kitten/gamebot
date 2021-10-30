#
# Copyright 2021 by angry-kitten
# Move the player character to a location with path planning.
#

import random
import math

import taskobject
import gbdata
import gbstate
import cv2
import taskpress
import tasksay
import taskdetect
import taskgotomain
import taskupdatemini
import taskjoy
import gbscreen
import gbdisplay
import tasktrackgoto
import tasksimplegoto
import gbmap

class TaskPathPlanGoTo(taskobject.Task):
    """TaskPathPlanGoTo Object"""

    def __init__(self,mx,my):
        super().__init__()
        self.name="TaskPathPlanGoTo"
        print("new",self.name,"object")
        self.target_mx=mx
        self.target_my=my
        print("go to mx",mx,"my",my)
        gbstate.unreachable=False

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

        gbstate.plan_goto_target_mx=-1
        gbstate.plan_goto_target_my=-1
        print(self.name,"done")
        self.taskdone=True
        return

    def Start(self):
        """Cause the task to begin doing whatever."""
        print(self.name,"Start")
        if self.started:
            return # already started
        self.started=True
        gbstate.plan_goto_target_mx=self.target_mx
        gbstate.plan_goto_target_my=self.target_my
        # plan from the current player position
        fmx=int(round(gbstate.player_mx))
        fmy=int(round(gbstate.player_my))
        gbmap.planning_build_distance_grid(fmx,fmy)
        tmx=int(round(self.target_mx))
        tmy=int(round(self.target_my))
        n=gbstate.mainmap[tmx][tmy]
        if n.planning_distance == 0:
            print("unreachable")
            gbstate.unreachable=True
            gbstate.plan_goto_target_mx=-1
            gbstate.plan_goto_target_my=-1
            print(self.name,"done")
            self.taskdone=True
            return
        gbmap.planning_build_waypoints_from_to(fmx,fmy,tmx,tmy)
        l=len(gbmap.waypoints)
        if l < 1:
            print("waypointless")
            self.parent.Push(tasksimplegoto.TaskSimpleGoTo(self.target_mx,self.target_my))
            return

        print("waypoints",gbmap.waypoints)

        # Do a simple goto to get from the integer map location to the
        # floating point map location.
        self.parent.Push(tasksimplegoto.TaskSimpleGoTo(self.target_mx,self.target_my))

        # The waypoints are ordered from the destination to the start. This
        # works well because we have to push the task in reverse order anyway.
        # Add 0.5 to the waypoints to go to the center of the map squares.
        for wp in gbmap.waypoints:
            mx=wp[0]+0.5
            my=wp[1]+0.5
            self.parent.Push(tasksimplegoto.TaskSimpleGoTo(mx,my,low_precision=True))

        gbmap.waypoints=[]

        return

    def DebugRecursive(self,indent=0):
        self.DebugPrint(self.name,indent)

    def NameRecursive(self):
        gbstate.task_stack_names.append(self.name)
        return self.name
