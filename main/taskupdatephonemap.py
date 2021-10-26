#
# Copyright 2021 by angry-kitten
# Look at the current screen and capture the phone map and
# determine player location from the pin.
#

import time
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

class TaskUpdatePhoneMap(taskobject.Task):
    """TaskUpdatePhoneMap Object"""

    def __init__(self):
        super().__init__()
        self.name="TaskUpdatePhoneMap"
        print("new",self.name,"object")
        self.step=0 # pop up phone

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
            self.select_map()
            return

        if self.step == 1:
            if not gbscreen.is_phone_map_screen():
                print("not on phone map screen")
                self.step=4
                self.parent.Push(taskpress.TaskPress('B',1.0))
                self.parent.Push(taskpress.TaskPress('B',1.0))
                self.parent.Push(taskpress.TaskPress('B',1.0))
                return
            print("yes on phone map screen")
            self.gather_phonemap()
            self.position_from_phonemap()
            self.step=2
            return

        if self.step == 2:
            # close map
            self.parent.Push(taskpress.TaskPress('B',1.0))
            self.step=3
            return

        if self.step == 3:
            # close phone
            self.parent.Push(taskpress.TaskPress('B',1.0))
            self.step=4
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

        # Move the pointer hand to the lower right so we know
        # where it is.
        #self.parent.Push(taskpress.TaskPress('hat_BOTTOM',1.0))
        #self.parent.Push(taskpress.TaskPress('hat_BOTTOM',1.0))
        #self.parent.Push(taskpress.TaskPress('hat_BOTTOM',1.0))
        #self.parent.Push(taskpress.TaskPress('hat_RIGHT',1.0))
        #self.parent.Push(taskpress.TaskPress('hat_RIGHT',1.0))
        #self.parent.Push(taskpress.TaskPress('hat_RIGHT',1.0))
        self.parent.Push(taskpress.TaskPress('hat_BOTTOM'))
        self.parent.Push(taskpress.TaskPress('hat_BOTTOM'))
        self.parent.Push(taskpress.TaskPress('hat_BOTTOM'))
        self.parent.Push(taskpress.TaskPress('hat_RIGHT'))
        self.parent.Push(taskpress.TaskPress('hat_RIGHT'))
        self.parent.Push(taskpress.TaskPress('hat_RIGHT'))

        # Wait for the phone screen to pop up.
        self.parent.Push(taskobject.TaskTimed(1.0))
        # Pop up the phone with ZL
        self.parent.Push(taskpress.TaskPress('ZL'))

    def DebugRecursive(self,indent=0):
        self.DebugPrint(self.name,indent)

    def NameRecursive(self):
        gbstate.task_stack_names.append(self.name)
        return self.name

    def find_icon_by_color(self):
        l=len(gbdata.phone_locations)
        for i in range(l):
            (sx,sy)=gbdata.phone_locations[i]
            sx2=sx+gbdata.phone_color_offset_x
            sy2=sy
            if gbscreen.color_match_array(sx2,sy2,gbdata.phone_map_color,5):
                return i
        return None

    def select_map(self):
        # Try finding the icon by color.
        best_slot=self.find_icon_by_color()
        if best_slot is None:
            print("no slot found by color")
            self.step=3
            return

        print("slot found",best_slot)
        # Wait for the phone screen to pop up and feature highlight
        # to finish.
        #self.parent.Push(taskobject.TaskTimed(30.0))
        self.parent.Push(taskobject.TaskTimed(4.0))
        # Pop up the map with A
        self.parent.Push(taskpress.TaskPress('A'))

        current_slot=8
        while current_slot > best_slot:
            delta=current_slot-best_slot
            if delta >= 3:
                # go up one
                print("go up one")
                #self.parent.Push(taskpress.TaskPress('hat_TOP',1.0))
                self.parent.Push(taskpress.TaskPress('hat_TOP'))
                current_slot-=3
            else:
                # go left one
                print("go left one")
                #self.parent.Push(taskpress.TaskPress('hat_LEFT',1.0))
                self.parent.Push(taskpress.TaskPress('hat_LEFT'))
                current_slot-=1

        print("set step 1")
        self.step=1

    def process_location(self,data_x,data_y,pixel_x,pixel_y):
        (b,g,r)=gbscreen.get_pixel(pixel_x,pixel_y)
        if gbscreen.color_match_rgb_array(r,g,b,gbdata.phonemap_color_water1,8):
            gbstate.phonemap[data_x][data_y]=gbdata.maptypes['Water'][0]
            return
        if gbscreen.color_match_rgb_array(r,g,b,gbdata.phonemap_color_water2,8):
            gbstate.phonemap[data_x][data_y]=gbdata.maptypes['Water'][0]
            return
        if gbscreen.color_match_rgb_array(r,g,b,gbdata.phonemap_color_rock,8):
            gbstate.phonemap[data_x][data_y]=gbdata.maptypes['Rock'][0]
            return
        if gbscreen.color_match_rgb_array(r,g,b,gbdata.phonemap_color_grass0,8):
            gbstate.phonemap[data_x][data_y]=gbdata.maptypes['Grass0'][0]
            return
        if gbscreen.color_match_rgb_array(r,g,b,gbdata.phonemap_color_grass1,8):
            gbstate.phonemap[data_x][data_y]=gbdata.maptypes['Grass1'][0]
            return
        if gbscreen.color_match_rgb_array(r,g,b,gbdata.phonemap_color_grass2,8):
            gbstate.phonemap[data_x][data_y]=gbdata.maptypes['Grass2'][0]
            return
        if gbscreen.color_match_rgb_array(r,g,b,gbdata.phonemap_color_sand,8):
            gbstate.phonemap[data_x][data_y]=gbdata.maptypes['Sand'][0]
            return
        if gbscreen.color_match_rgb_array(r,g,b,gbdata.phonemap_color_dock,8):
            gbstate.phonemap[data_x][data_y]=gbdata.maptypes['Dock'][0]
            return
        if gbscreen.color_match_rgb_array(r,g,b,gbdata.phonemap_color_dirt,8):
            gbstate.phonemap[data_x][data_y]=gbdata.maptypes['Dirt'][0]
            return
        #gbstate.phonemap[data_x][data_y]=gbdata.maptypes['Unknown'][0]

    def gather_phonemap(self):
        print("l1")
        if gbstate.phonemap is None:
            gbstate.phonemap=[0 for x in range(gbdata.phonemap_width)]
            for data_x in range(gbdata.phonemap_width):
                gbstate.phonemap[data_x]=[0 for y in range(gbdata.phonemap_height)]

        print("l2")
        square_center_offset=gbdata.phonemap_square_spacing/2
        pixel_start_x=gbdata.phonemap_origin_x+square_center_offset
        pixel_start_y=gbdata.phonemap_origin_y+square_center_offset
        for data_x in range(gbdata.phonemap_width):
            pixel_x=int(round((data_x*gbdata.phonemap_square_spacing)+pixel_start_x))
            for data_y in range(gbdata.phonemap_height):
                pixel_y=int(round((data_y*gbdata.phonemap_square_spacing)+pixel_start_y))
                self.process_location(data_x,data_y,pixel_x,pixel_y)
        print("l3")

    def debug_phonemap(self):
        if gbstate.phonemap is None:
            print("no phonemap")
            return
        for y in range(gbdata.phonemap_height):
            line=''
            for x in range(gbdata.phonemap_width):
                line+=gbdata.maptype_rev[gbstate.phonemap[x][y]][1]
            print(line)

    def is_pin_orange(self,pixel_x,pixel_y):
        pixel_x=int(round(pixel_x))
        pixel_y=int(round(pixel_y))
        if gbscreen.color_match_array(pixel_x,pixel_y,gbdata.pin_orange1,5):
            return True
        if gbscreen.color_match_array(pixel_x,pixel_y,gbdata.pin_orange2,5):
            return True
        return False

    def locate_vertical_center_line(self,startx,starty):
        # Now use the white circle to find the vertical center line.
        # Scan left from the previous center line.
        circle_left_x=startx
        circle_right_x=startx
        for j in range(1,gbdata.phonemap_pin_width):
            lx=startx-j
            if self.is_pin_orange(lx,starty):
                circle_left_x=lx
                break
        # Scan right from the previous center line.
        for j in range(1,gbdata.phonemap_pin_width):
            rx=startx+j
            if self.is_pin_orange(rx,starty):
                circle_right_x=rx
                break
        # circle_right_y and circle_left_y are one pixel right and left
        # of the white circle.
        print("circle_left_x=",circle_left_x)
        print("circle_right_x=",circle_right_x)
        circle_center_x=(circle_left_x+circle_right_x)/2
        print("circle_center_x=",circle_center_x)
        return circle_center_x

    def locate_horizontal_center_line(self,startx,starty):
        # Now use the white circle to find the horizontal center line.
        # Scan up from the previous center line.
        circle_top_y=starty
        circle_bottom_y=starty
        for j in range(1,gbdata.phonemap_pin_height):
            ty=starty-j
            if self.is_pin_orange(startx,ty):
                circle_top_y=ty
                break
        # Scan down from the previous center line.
        for j in range(1,gbdata.phonemap_pin_height):
            by=starty+j
            if self.is_pin_orange(startx,by):
                circle_bottom_y=by
                break
        # circle_top_y and circle_bottom_y are one pixel above and below
        # the white circle.
        print("circle_top_y=",circle_top_y)
        print("circle_bottom_y=",circle_bottom_y)
        circle_center_y=(circle_top_y+circle_bottom_y)/2
        print("circle_center_y=",circle_center_y)
        return circle_center_y

    def verify_pin_shape(self,x,y):
        """Verify that there is a pin at this location and
        not some other thing that happens to have the same color"""
        #print("verify_pin_shape")

        # Scan pixels left and right to try to find the vertical center line
        # of the orange part.
        left_x=x
        right_x=x
        for j in range(1,gbdata.phonemap_pin_width):
            lx=x-j
            if self.is_pin_orange(lx,y):
                left_x=lx
            rx=x+j
            if self.is_pin_orange(rx,y):
                right_x=rx
        #print("left_x=",left_x)
        #print("right_x=",right_x)
        cx=(left_x+right_x)/2
        #print("cx=",cx)

        # Scan pixels up and down to try to find vertical extent of the
        # orange part.
        up_y=y
        down_y=y
        for j in range(1,gbdata.phonemap_pin_height):
            uy=y-j
            if self.is_pin_orange(cx,uy):
                up_y=uy
            dy=y+j
            if self.is_pin_orange(cx,dy):
                down_y=dy
        #print("up_y=",up_y)
        #print("down_y=",down_y)
        yextent=(down_y-up_y)+1
        #print("l6")
        if yextent < (gbdata.phonemap_pin_height-10):
            return False
        #print("l7")
        if yextent > (gbdata.phonemap_pin_height+3):
            return False
        #print("l8")

        # Find the white circle in the head of the pin.
        # Scan down from the top.
        circle_top_y=up_y
        circle_bottom_y=down_y
        for j in range(1,gbdata.phonemap_pin_height):
            uy=up_y+j
            if self.is_pin_orange(cx,uy):
                circle_top_y=uy
            else:
                break # it stopped being orange
        # Scan up from the bottom.
        for j in range(1,gbdata.phonemap_pin_height):
            dy=down_y-j
            if self.is_pin_orange(cx,dy):
                circle_bottom_y=dy
            else:
                break # it stopped being orange
        # circle_top_y and circle_bottom_y are one pixel higher and lower
        # than the white circle.
        #print("circle_top_y=",circle_top_y)
        #print("circle_bottom_y=",circle_bottom_y)
        circle_center_y=(circle_bottom_y+circle_top_y)/2
        #print("circle_center_y=",circle_center_y)
        # circle_center_y is the center of the white circle

        # Now use the white circle to find the vertical center line again.
        # The assumption is that it will produce a better value than
        # the one above.
        circle_center_x=self.locate_vertical_center_line(cx,circle_center_y)
        #print("circle_center_x=",circle_center_x)

        # Now use the white circle to find the horizontal center line again.
        # This is an attempt to converge on a good center value.
        circle_center_y=self.locate_horizontal_center_line(circle_center_x,circle_center_y)
        #print("circle_center_y=",circle_center_y)

        # Now we use these new values to scan 5 times and average.

        sumx=0
        tmpx=self.locate_vertical_center_line(circle_center_x,circle_center_y-2)
        #print("tmpx=",tmpx)
        sumx+=tmpx
        tmpx=self.locate_vertical_center_line(circle_center_x,circle_center_y-1)
        #print("tmpx=",tmpx)
        sumx+=tmpx
        tmpx=self.locate_vertical_center_line(circle_center_x,circle_center_y)
        #print("tmpx=",tmpx)
        sumx+=tmpx
        tmpx=self.locate_vertical_center_line(circle_center_x,circle_center_y+1)
        #print("tmpx=",tmpx)
        sumx+=tmpx
        tmpx=self.locate_vertical_center_line(circle_center_x,circle_center_y+2)
        #print("tmpx=",tmpx)
        sumx+=tmpx

        sumy=0
        tmpy=self.locate_horizontal_center_line(circle_center_x-2,circle_center_y)
        #print("tmpy=",tmpy)
        sumy+=tmpy
        tmpy=self.locate_horizontal_center_line(circle_center_x-1,circle_center_y)
        #print("tmpy=",tmpy)
        sumy+=tmpy
        tmpy=self.locate_horizontal_center_line(circle_center_x,circle_center_y)
        #print("tmpy=",tmpy)
        sumy+=tmpy
        tmpy=self.locate_horizontal_center_line(circle_center_x+1,circle_center_y)
        #print("tmpy=",tmpy)
        sumy+=tmpy
        tmpy=self.locate_horizontal_center_line(circle_center_x+2,circle_center_y)
        #print("tmpy=",tmpy)
        sumy+=tmpy

        circle_center_x=sumx/5
        circle_center_y=sumy/5
        #print("circle_center_x=",circle_center_x)
        #print("circle_center_y=",circle_center_y)


        # Calculate a tip location.
        tip_x=circle_center_x
        tip_y=circle_center_y+gbdata.phonemap_pin_center_to_tip
        #print("tip_x=",tip_x)
        #print("tip_y=",tip_y)

        # Calculate the map location from the tip location.
        map_x=(tip_x-gbdata.phonemap_origin_x)/gbdata.phonemap_square_spacing
        map_y=(tip_y-gbdata.phonemap_origin_y)/gbdata.phonemap_square_spacing
        #print("map_x=",map_x)
        #print("map_y=",map_y)
        map_x+=gbdata.phonemap_pin_tune_mx
        map_y+=gbdata.phonemap_pin_tune_my
        #print("map_x=",map_x)
        #print("map_y=",map_y)

        gbstate.position_phonemap_x=map_x
        gbstate.position_phonemap_y=map_y

        gbtrack.set_current_position(map_x,map_y)

        return True

    def position_from_phonemap(self):
        print("position_from_phonemap")
        gbstate.position_phonemap_x=-1
        gbstate.position_phonemap_y=-1
        print("l4")
        """Find the orange pin."""
        search_w=gbdata.phonemap_right-gbdata.phonemap_left
        search_h=gbdata.phonemap_bottom-gbdata.phonemap_top_pin
        for local_y in range(0,search_h,gbdata.phonemap_pin_search_y):
            pixel_y=gbdata.phonemap_top_pin+local_y
            for local_x in range(0,search_w,gbdata.phonemap_pin_search_x):
                pixel_x=gbdata.phonemap_left+local_x
                if self.is_pin_orange(pixel_x,pixel_y):
                    print("found phonemap pin at",pixel_x,pixel_y)
                    if self.verify_pin_shape(pixel_x,pixel_y):
                        return
        print("l5")
        return
