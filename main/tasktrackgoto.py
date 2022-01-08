#
# Copyright 2021-2022 by angry-kitten
# Move the player character to a location with no pathing or object
# avoidance. Track the feet box.
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
import gbtrack
import taskdetermineposition
import taskpause
import tasktrackturn

class TaskTrackGoTo(taskobject.Task):
    """TaskTrackGoTo Object"""

    def __init__(self,mx,my,low_precision=False):
        super().__init__()
        self.name="TaskTrackGoTo"
        print("new",self.name,"object")
        self.target_mx=mx
        self.target_my=my
        print("go to mx",mx,"my",my)
        self.low_precision=low_precision
        self.within=1.0
        self.within_obstructed=0.2
        self.start_mx=-1
        self.start_my=-1
        self.start_heading=-1
        self.target_heading=-1
        self.target_seconds=-1
        self.end_mx=-1
        self.end_my=-1
        gbstate.move_before_mx=-1
        gbstate.move_before_my=-1
        gbstate.move_after_mx=-1
        gbstate.move_after_my=-1

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

        if gbstate.player_mx < 0:
            print("player position not set")
            gbstate.track_goto_target_mx=-1
            gbstate.track_goto_target_my=-1
            print(self.name,"done")
            self.taskdone=True
            return

        mx=gbstate.player_mx
        my=gbstate.player_my

        if gbstate.move_before_mx >= 0:
            print("second time")
            gbstate.move_after_mx=mx
            gbstate.move_after_my=my
            self.end_mx=gbstate.player_mx
            self.end_my=gbstate.player_my

            use_detect=not self.low_precision
            gbtrack.after_move_processing(self.start_mx,self.start_my,self.start_heading,self.target_mx,self.target_my,self.target_heading,self.target_seconds,self.end_mx,self.end_my,use_detect)

            self.process_move()

            gbstate.track_goto_target_mx=-1
            gbstate.track_goto_target_my=-1

            # pause to allow the results of the move to be evaluated
            #self.parent.Push(taskpause.TaskPause('Paused',30.0))
            #self.parent.Push(taskpause.TaskPause('Paused',5.0))
            #self.parent.Push(taskpause.TaskPause('Paused',2.0))

            print(self.name,"done")
            self.taskdone=True
            return

        # this is the first time here
        print("first time")
        gbstate.move_before_mx=mx
        gbstate.move_before_my=my

        self.start_mx=gbstate.player_mx
        self.start_my=gbstate.player_my
        self.start_heading=gbstate.player_heading

        print("track going from to",mx,my,self.target_mx,self.target_my)

        dx=self.target_mx-mx
        dy=self.target_my-my
        print("dx dy",dx,dy)
        distance=math.sqrt(dx*dx+dy*dy)
        print("distance",distance)
        self.distance=distance

        previous_heading=gbstate.player_heading
        heading=gbtrack.calculate_heading(dx,dy)
        self.target_heading=heading
        #gbstate.player_heading=heading

        if not self.low_precision:
            # This detect is here to get the feet position. Which will
            # be used in gbtrack.after_move_processing
            self.parent.Push(taskdetect.TaskDetect())

        self.parent.Push(taskdetermineposition.TaskDeterminePosition(low_precision=self.low_precision))

        self.parent.Push(taskobject.TaskTimed(1.0))

        #seconds=gbtrack.heading_change_and_distance_to_time(previous_heading,heading,distance)
        #seconds=gbtrack.heading_change_and_distance_to_time(heading,heading,distance)
        seconds=gbtrack.estimate_distance_to_time(distance)
        print("seconds",seconds)
        self.target_seconds=seconds
        msec=int(seconds*1000) # how long to activate the joystick in milliseconds
        total_sec=1+seconds # the total time for the joystick task
        self.parent.Push(taskjoy.TaskJoyLeft(heading,1.0,total_sec,msec))
        gbstate.move_since_determine=True
        gbstate.move_since_detect=True

        #self.parent.Push(taskobject.TaskTimed(1.0))

        self.parent.Push(tasktrackturn.TaskTrackTurn(heading))
        return

    def Start(self):
        """Cause the task to begin doing whatever."""
        print(self.name,"Start")
        if self.started:
            return # already started
        self.started=True
        gbstate.track_goto_target_mx=self.target_mx
        gbstate.track_goto_target_my=self.target_my
        self.parent.Push(taskdetermineposition.TaskDeterminePosition(low_precision=self.low_precision))

    def DebugRecursive(self,indent=0):
        self.DebugPrint(self.name,indent)

    def NameRecursive(self):
        gbstate.task_stack_names.append(self.name)
        return self.name

    def process_move(self):
        # See if we reached the target.
        if gbscreen.match_within(gbstate.move_after_mx,self.target_mx,self.within) and gbscreen.match_within(gbstate.move_after_my,self.target_my,self.within):
            # low and high severity obstruction
            gbstate.move_obstructed_low=False
            gbstate.move_obstructed_high=False
            print("not obstructed")
        else:
            # low severity obstruction
            gbstate.move_obstructed_low=True
            print("obstructed")
            print("wanted",self.target_mx,self.target_my)
            print("got",gbstate.move_after_mx,gbstate.move_after_my)
            # We might have passed an obstruction. Or we might be running
            # into one.
            if self.distance >= 0.70:
                # Don't evaluate short moves because they could trigger the
                # obstruction code by accident.
                if gbscreen.match_within(gbstate.move_before_mx,gbstate.move_after_mx,self.within_obstructed) and gbscreen.match_within(gbstate.move_before_my,gbstate.move_after_my,self.within_obstructed):
                    # We ran into an obstruction.
                    print("small movement")
                    # high severity obstruction
                    gbstate.move_obstructed_high=True
                    if (self.target_heading >= 0 and self.target_heading < 45) or (self.target_heading >= 315 and self.target_heading <= 360):
                        print("obstructed up/north")
                        mx=int(round(gbstate.move_after_mx))
                        my=int(round(gbstate.move_after_my-1))
                        gbtrack.set_obstructed(mx,my)
                    elif self.target_heading >= 45 and self.target_heading < 135:
                        print("obstructed right/east")
                        mx=int(round(gbstate.move_after_mx+1))
                        my=int(round(gbstate.move_after_my))
                        gbtrack.set_obstructed(mx,my)
                    elif self.target_heading >= 135 and self.target_heading < 225:
                        print("obstructed down/south")
                        mx=int(round(gbstate.move_after_mx))
                        my=int(round(gbstate.move_after_my+1))
                        gbtrack.set_obstructed(mx,my)
                    elif self.target_heading >= 225 and self.target_heading < 315:
                        print("obstructed left/west")
                        mx=int(round(gbstate.move_after_mx-1))
                        my=int(round(gbstate.move_after_my))
                        gbtrack.set_obstructed(mx,my)

        gbstate.move_before_mx=-1
        gbstate.move_before_my=-1
        gbstate.move_after_mx=-1
        gbstate.move_after_my=-1
