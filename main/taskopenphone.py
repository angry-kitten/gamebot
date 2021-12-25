#
# Copyright 2021 by angry-kitten
# Look at the current screen and capture the phone map and
# determine player location from the pin.
#

import time
import numpy
import taskobject
import gbdata
import gbstate
import cv2
import taskpress
import tasksay
import taskdetect
import taskgotomain
import gbscreen
import gbtrack
import gbdisplay
import gbmap

class TaskOpenPhone(taskobject.Task):
    """TaskOpenPhone Object"""

    def __init__(self,name_to_open):
        super().__init__()
        self.name="TaskOpenPhone"
        print("new",self.name,"object")
        self.step=0 # pop up phone
        self.icons=[]
        self.name_to_open=name_to_open

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

        print("step is",self.step)

        if self.step == 0:
            self.select_name_to_open()
            return

        if self.step == 10:
            # Move the pointer hand to the lower right so we know
            # where it is.
            self.parent.Push(taskpress.TaskPress('hat_BOTTOM'))
            self.parent.Push(taskpress.TaskPress('hat_BOTTOM'))
            self.parent.Push(taskpress.TaskPress('hat_RIGHT'))
            self.parent.Push(taskpress.TaskPress('hat_RIGHT'))

            # Move to the upper left.
            self.parent.Push(taskpress.TaskPress('hat_LEFT'))
            self.parent.Push(taskpress.TaskPress('hat_LEFT'))
            self.parent.Push(taskpress.TaskPress('hat_LEFT'))
            self.parent.Push(taskpress.TaskPress('hat_LEFT'))
            self.parent.Push(taskpress.TaskPress('hat_LEFT'))
            self.parent.Push(taskpress.TaskPress('hat_TOP'))
            self.parent.Push(taskpress.TaskPress('hat_TOP'))
            self.parent.Push(taskpress.TaskPress('hat_TOP'))

            self.current_slot=8
            self.step=20
            return

        if self.step == 20:
            self.move_hand_and_select()
            self.step=99
            return

        if self.step == 30:
            # close phone
            self.parent.Push(taskpress.TaskPress('B',1.0))
            self.step=99
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
        self.step=0 # pop up phone

        # Wait for the phone screen to pop up.
        self.parent.Push(taskobject.TaskTimed(1.0))
        # Pop up the phone with ZL
        self.parent.Push(taskpress.TaskPress('ZL'))
        return

    def DebugRecursive(self,indent=0):
        self.DebugPrint(self.name,indent)

    def NameRecursive(self):
        gbstate.task_stack_names.append(self.name)
        return self.name

    def find_map_icon_by_color(self):
        l=len(gbdata.phone_locations)
        for i in range(l):
            (sx,sy)=gbdata.phone_locations[i]
            sx2=sx+gbdata.phone_map_color_offset_x
            sy2=sy+gbdata.phone_map_color_offset_y
            if gbscreen.color_match_array(sx2,sy2,gbdata.phone_map_color,5):
                return i
        return None

    def find_nook_miles_icon_by_color(self):
        l=len(gbdata.phone_locations)
        for i in range(l):
            (sx,sy)=gbdata.phone_locations[i]
            sx2=sx+gbdata.phone_nook_miles_color_offset_x
            sy2=sy+gbdata.phone_nook_miles_color_offset_y
            if gbscreen.color_match_array(sx2,sy2,gbdata.phone_nook_miles_color,2):
                return i
        return None

    def find_hand_by_color(self):
        l=len(gbdata.phone_locations)
        for i in range(l):
            (sx,sy)=gbdata.phone_locations[i]
            sx2=sx+gbdata.phone_hand_offset_x
            sy2=sy+gbdata.phone_hand_offset_y
            if gbscreen.color_match_array(sx2,sy2,gbdata.phone_hand_color,2):
                return i
        return None

    def select_name_to_open(self):
        # Try finding the icon by color.
        if self.name_to_open == "Map":
            self.name_slot=self.find_map_icon_by_color()
            if self.name_slot is None:
                print("no map slot found by color")
                self.step=30 # close phone
                return
            print("map slot found",self.name_slot)
        elif self.name_to_open == "NookMiles":
            self.name_slot=self.find_nook_miles_icon_by_color()
            if self.name_slot is None:
                print("no nook miles slot found by color")
                self.step=30 # close phone
                return
            print("nook miles slot found",self.name_slot)
        else:
            print("name not recognized",self.name_to_open)
            self.step=30 # close phone
            return

        # Try to find the pointer hand by color.
        hand_slot=self.find_hand_by_color()
        if hand_slot is None:
            print("no hand slot found by color")
            self.step=10 # try it the slow way
            return
        print("hand slot found",hand_slot)

        self.current_slot=hand_slot
        self.step=20 # Move the pointer hand, if needed, and select the map.
        return

    def move_hand_and_select(self):
        # Wait for the phone screen to pop up and feature highlight
        # to finish.
        #self.parent.Push(taskobject.TaskTimed(30.0))
        #self.parent.Push(taskobject.TaskTimed(4.0))
        self.parent.Push(taskobject.TaskTimed(5.0))
        # Pop up the name with A
        self.parent.Push(taskpress.TaskPress('A'))
        #self.parent.Push(taskobject.TaskTimed(1.0))

        while self.current_slot != self.name_slot:
            print(self.name_slot,self.current_slot)

            name_slot_row=int(self.name_slot/3)
            name_slot_column=self.name_slot%3
            print(name_slot_row,name_slot_column)

            hand_slot_row=int(self.current_slot/3)
            hand_slot_column=self.current_slot%3
            print(hand_slot_row,hand_slot_column)

            if hand_slot_row < name_slot_row:
                # map slot is in a higher row number
                print("go down one")
                self.parent.Push(taskpress.TaskPress('hat_BOTTOM'))
                self.current_slot+=3
            elif hand_slot_row > name_slot_row:
                # map slot is in a lower row number
                print("go up one")
                self.parent.Push(taskpress.TaskPress('hat_TOP'))
                self.current_slot-=3

            if hand_slot_column < name_slot_column:
                # map slot is in a higher column number
                print("go right one")
                self.parent.Push(taskpress.TaskPress('hat_RIGHT'))
                self.current_slot+=1
            elif hand_slot_column > name_slot_column:
                # map slot is in a lower column number
                print("go left one")
                self.parent.Push(taskpress.TaskPress('hat_LEFT'))
                self.current_slot-=1

        return
