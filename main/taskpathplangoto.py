#
# Copyright 2021-2022 by angry-kitten
# Move the player character to a location with path planning.
#

import random
import math

import cv2
import gbdata, gbstate
import gbmap
import gbscreen
import gbdisplay
import gbdijkstra
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
import taskladder

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

        gbdijkstra.clear_waypoints()
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
        tmx=int(round(self.target_mx))
        tmy=int(round(self.target_my))

        gbdijkstra.path_plan(fmx,fmy,tmx,tmy)

        # use Dijkstra
        if len(gbstate.dijkstra_waypoints) < 1:
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

        print("waypoints",gbstate.dijkstra_waypoints)

        # Do a simple goto to get from the integer map location to the
        # floating point map location.
        self.parent.Push(tasksimplegoto.TaskSimpleGoTo(self.target_mx,self.target_my))

        # The waypoints are ordered from the destination to the start. This
        # works well because we have to push the task in reverse order anyway.
        # Add 0.5 to the waypoints to go to the center of the map squares.
        n=len(gbstate.dijkstra_waypoints)
        if n < 2:
            print("only one waypoint")
            return
        for j in range(1,n):
            # move from i2 to i1
            (i1,t1)=gbstate.dijkstra_waypoints[j-1]
            (i2,t2)=gbstate.dijkstra_waypoints[j]
            (mx1,my1)=gbdijkstra.index_to_xy(i1)
            (mx2,my2)=gbdijkstra.index_to_xy(i2)
            n1=gbdijkstra.node_from_index(i1)
            cmx1=mx1+0.5
            cmy1=my1+0.5
            cmx2=mx2+0.5
            cmy2=my2+0.5
            if t1 == gbdata.dijkstra_walk_type:
                self.parent.Push(tasksimplegoto.TaskSimpleGoTo(cmx1,cmy1,low_precision=True))
            elif t1 == gbdata.dijkstra_pole_type:
                self.parent.Push(taskpole.TaskPole(cmx1,cmy1))
                # Make sure we have an accurate starting position.
                self.parent.Push(tasksimplegoto.TaskSimpleGoTo(cmx2,cmy2))
            elif t1 == gbdata.dijkstra_ladder_type:
                self.parent.Push(taskladder.TaskLadder(cmx1,cmy1))
                # Make sure we have an accurate starting position.
                self.parent.Push(tasksimplegoto.TaskSimpleGoTo(cmx2,cmy2))
            else:
                print("unknown move type",t)
                break
        return

    def DebugRecursive(self,indent=0):
        self.DebugPrint(self.name,indent)

    def NameRecursive(self):
        gbstate.task_stack_names.append(self.name)
        return self.name
