#
# Copyright 2021 by angry-kitten
# Move the player character to a location with path planning.
#

import random
import math

import cv2
import gbdata, gbstate
import gbmap
import gbscreen
import gbdisplay
import taskobject
import taskpress
import tasksay
import taskdetect
import taskgotomain
import taskupdatemini
import taskjoy
import tasktrackgoto
import tasksimplegoto
import taskpole
import taskdetermineposition

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
        gbmap.waypoints=[]
        print(self.name,"done")
        self.taskdone=True
        return

    def Start(self):
        """Cause the task to begin doing whatever."""
        print(self.name,"Start")
        if self.started:
            return # already started
        self.started=True
        gbmap.waypoints=[]
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

            # In some cases the current position is stale causing
            # path planning to fail.
            self.parent.Push(taskdetermineposition.TaskDeterminePosition())

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
        n=len(gbmap.waypoints)
        for j in range(n):
            wp=gbmap.waypoints[j]
            mx=wp[0]
            my=wp[1]
            movetype=gbstate.mainmap[mx][my].move_type
            print("movetype",movetype)
            cmx=wp[0]+0.5
            cmy=wp[1]+0.5
            if gbmap.MoveStep == movetype:
                self.parent.Push(tasksimplegoto.TaskSimpleGoTo(cmx,cmy,low_precision=True))
            elif gbmap.MovePole == movetype:
                self.parent.Push(taskpole.TaskPole(cmx,cmy))

                # Make sure we have an accurate starting position.
                j2=j+1
                if j2 < n:
                    wp2=gbmap.waypoints[j2]
                    pmx=wp2[0]+0.5
                    pmy=wp2[1]+0.5
                    self.parent.Push(tasksimplegoto.TaskSimpleGoTo(pmx,pmy))

        # Don't clear out the waypoints so that gbdisplay can draw them.
        #gbmap.waypoints=[]

        return

    def DebugRecursive(self,indent=0):
        self.DebugPrint(self.name,indent)

    def NameRecursive(self):
        gbstate.task_stack_names.append(self.name)
        return self.name
