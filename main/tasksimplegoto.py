#
# Copyright 2021-2022 by angry-kitten
# Move the player character to a location with no pathing or object
# avoidance.
#

import random
import math

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
import taskjoy
import tasktrackgoto
import taskdetermineposition

class TaskSimpleGoTo(taskobject.Task):
    """TaskSimpleGoTo Object"""

    def __init__(self,mx,my,low_precision=False):
        super().__init__()
        self.name="TaskSimpleGoTo"
        #print("new",self.name,"object")
        self.step=0
        #self.limit=100
        self.limit=25
        self.counter=0
        self.step_distance_limit=8
        self.target_mx=mx
        self.target_my=my
        self.low_precision=low_precision
        #print("go to mx",mx,"my",my)
        #self.within=0.1
        self.within=0.2
        self.previous_mx=-1
        self.previous_my=-1
        if self.low_precision:
            self.within=1

    def Poll(self):
        """check if any action can be taken"""
        #print(self.name,"Poll")
        if not self.started:
            self.Start()
            return
        if self.taskdone:
            return
        if gbstate.frame is None:
            return

        print(self.name,f"step={self.step}")

        if self.step == 0:
            mx=gbstate.player_mx
            my=gbstate.player_my

            #print("simple going from to",mx,my,self.target_mx,self.target_my)

            if self.previous_mx >= 0:
                if self.previous_mx == mx and self.previous_my == my:
                    print("stuck")
                    gbstate.goto_target_mx=-1
                    gbstate.goto_target_my=-1
                    #print(self.name,"done")
                    self.taskdone=True
                    return
                if gbscreen.match_within(self.previous_mx,mx,self.within) and gbscreen.match_within(self.previous_my,my,self.within):
                    print("stuck 2")
                    gbstate.goto_target_mx=-1
                    gbstate.goto_target_my=-1
                    #print(self.name,"done")
                    self.taskdone=True
                    return

            if self.counter >= self.limit:
                print("over count")
                gbstate.goto_target_mx=-1
                gbstate.goto_target_my=-1
                #print(self.name,"done")
                self.taskdone=True
                return

            self.counter+=1

            self.previous_mx=mx
            self.previous_my=my

            if (not gbscreen.match_within(mx,self.target_mx,self.within)) or (not gbscreen.match_within(my,self.target_my,self.within)):
                # Keep going.
                dx=self.target_mx-mx
                dy=self.target_my-my
                #print("dx dy",dx,dy)
                distance=math.sqrt(dx*dx+dy*dy)
                #print("distance",distance)
                #if distance > 0:
                #    distance2=random.random()*distance
                #    print("distance2",distance2)
                #    ratio=distance2/distance
                #    dx*=ratio
                #    dy*=ratio
                #    distance=distance2
                #    print("distance",distance)

                if distance > self.step_distance_limit:
                    #distance2=self.step_distance_limit*random.random()
                    distance2=self.step_distance_limit
                    ratio=distance2/distance
                    dx*=ratio
                    dy*=ratio
                    distance=distance2
                    #print("distance",distance)

                if distance > 0.01:
                    if distance < 0.5:
                        distance2=distance*0.70
                        ratio=distance2/distance
                        dx*=ratio
                        dy*=ratio
                        distance=distance2
                        #print("distance",distance)
                    #elif distance < 1:
                    #    distance2=distance*0.80
                    #    ratio=distance2/distance
                    #    dx*=ratio
                    #    dy*=ratio
                    #    distance=distance2
                    #    print("distance",distance)
                    #elif distance < 2:
                    #    distance2=distance*0.90
                    #    ratio=distance2/distance
                    #    dx*=ratio
                    #    dy*=ratio
                    #    distance=distance2
                    #    print("distance",distance)

                step_target_mx=mx+dx
                step_target_my=my+dy

                self.parent.Push(tasktrackgoto.TaskTrackGoTo(step_target_mx,step_target_my,low_precision=self.low_precision))
                self.step=1
                return

        if self.step == 1:
            # Evaluate obstruction
            if gbstate.move_obstructed_high:
                print("maybe evasive maneuver")
                if 0 == random.randint(0,5):
                    print("evasive maneuver")
                    ev_mx=gbstate.player_mx+(random.randint(0,16)-8)
                    ev_my=gbstate.player_my+(random.randint(0,16)-8)
                    self.parent.Push(tasktrackgoto.TaskTrackGoTo(ev_mx,ev_my,low_precision=self.low_precision))
            self.step=0
            return

        gbstate.goto_target_mx=-1
        gbstate.goto_target_my=-1
        #print(self.name,"done")
        self.taskdone=True
        return

    def Start(self):
        """Cause the task to begin doing whatever."""
        #print(self.name,"Start")
        if self.started:
            return # already started
        self.started=True
        self.step=0
        gbstate.goto_target_mx=self.target_mx
        gbstate.goto_target_my=self.target_my
        self.parent.Push(taskdetermineposition.TaskDeterminePosition(low_precision=self.low_precision))
        return

    def DebugRecursive(self,indent=0):
        self.DebugPrint(self.name,indent)

    def NameRecursive(self):
        gbstate.task_stack_names.append(self.name)
        return self.name
