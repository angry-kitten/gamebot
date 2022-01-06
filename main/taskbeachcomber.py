#
# Copyright 2021-2022 by angry-kitten
# Walk along the beach and pick up stuff.
#

import random
import cv2
import gbdata, gbstate, gbscreen, gbdisplay
import gbmap
import taskobject
import taskpress
import tasksay
import taskdetect
import taskgotomain
import taskupdatemini
import taskrandomwalk
import tasksimplegoto
import tasksimplegoto
import taskpathplangoto
import taskcheckforinterrupt
import taskpickup

class TaskBeachcomber(taskobject.Task):
    """TaskBeachcomber Object"""

    def __init__(self):
        super().__init__()
        self.name="TaskBeachcomber"
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

        if self.step < len(gbstate.beachcomber_list):
            entry=gbstate.beachcomber_list[self.step]
            self.step+=1

            (mx1,my1,mx2,my2)=entry

            # Try to pick up whatever is there.
            self.parent.Push(taskpickup.TaskPickupSpin())

            # Go to the beach edge, moving perpendicular to the edge.
            self.parent.Push(taskpathplangoto.TaskPathPlanGoTo(mx1,my1))

            # Go to the place two map squares in from the beach edge.
            self.parent.Push(taskpathplangoto.TaskPathPlanGoTo(mx2,my2))

            return

        print(self.name,"done")
        self.taskdone=True
        return

    def Start(self):
        """Cause the task to begin doing whatever."""
        print(self.name,"Start")
        if self.started:
            return # already started
        self.started=True
        if gbstate.beachcomber_list is None:
            self.build_list()
        self.step=0
        return

    def DebugRecursive(self,indent=0):
        self.DebugPrint(self.name,indent)

    def NameRecursive(self):
        gbstate.task_stack_names.append(self.name)
        myname=self.name
        return myname

    def build_list(self):
        if gbstate.beachcomber_list is not None:
            gbstate.beachcomber_list.clear()
        gbstate.beachcomber_list=[]

        # Left/west part of map.
        mx=0
        dx=1
        dy=0
        for my in range(gbdata.map_height):
            self.scan_beach_edge(mx,my,dx,dy)

        # Bottom/south part of map.
        my=gbdata.map_height-1
        dx=0
        dy=-1
        for mx in range(gbdata.map_width):
            self.scan_beach_edge(mx,my,dx,dy)

        # Right/east part of map.
        mx=gbdata.map_width-1
        dx=-1
        dy=0
        for my in range(gbdata.map_height):
            self.scan_beach_edge(mx,my,dx,dy)

        # Top/north part of map.
        my=0
        dx=0
        dy=1
        for mx in range(gbdata.map_width):
            self.scan_beach_edge(mx,my,dx,dy)

        return

    def scan_beach_edge(self,mx,my,dx,dy):
        for j in range(10):
            mx2=mx+j*dx
            my2=my+j*dy
            me=gbstate.mainmap[mx2][my2]
            t=me.phonemap2
            if t == gbmap.MapTypeSand:
                # We found where the beach meets the water.
                # Verify that it is sand two more map squares in.
                for k in range(1,3):
                    mx3=mx+(j+k)*dx
                    my3=my+(j+k)*dy
                    me=gbstate.mainmap[mx3][my3]
                    t=me.phonemap2
                    if t != gbmap.MapTypeSand:
                        # The beach isn't wide enough.
                        return
                entry=(mx2,my2,mx3,my3)
                gbstate.beachcomber_list.append(entry)
                return
            if t != gbmap.MapTypeWater:
                # The water transitioned to something other than sand
                # at this location.
                return
        return
