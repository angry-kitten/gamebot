#
# Copyright 2021 by angry-kitten
# Look at the current screen and capture the minimaps and
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

class TaskUpdateMini(taskobject.Task):
    """TaskUpdateMini Object"""

    def __init__(self):
        super().__init__()
        self.name="TaskUpdateMini"
        print("new",self.name,"object")
        self.additional_wait=0.1 # 100 milliseconds
        self.additional_wait_active=False

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

        # Don't hang forever if the minimap is not present or turned
        # off.
        time_now=time.monotonic()
        elapsed=time_now-self.start_time
        if elapsed > 1.0:
            print(self.name,"time elapsed")
            self.taskdone=True
            return

        if not gbscreen.is_minimap():
            #print("minimap not visible yet")
            return

        print("minimap visible")

        if not self.additional_wait_active:
            # Wait an additional time to allow for the minimap to
            # slide fully into position.
            print("activate additional wait")
            self.additional_wait_active=True
            self.additioanl_wait_after=time_now+self.additional_wait
            return
        else:
            if time_now <= self.additioanl_wait_after:
                print("additional wait")
                return

        print("additional wait complete")
        self.gather_minimap()
        #self.debug_minimap()
        self.position_from_minimap()
        print(self.name,"done")
        self.taskdone=True
        return

    def Start(self):
        """Cause the task to begin doing whatever."""
        print(self.name,"Start")
        if self.started:
            return # already started
        self.started=True
        self.start_time=time.monotonic()

    def DebugRecursive(self,indent=0):
        self.DebugPrint(self.name,indent)

    def NameRecursive(self):
        gbstate.task_stack_names.append(self.name)
        return self.name

    def process_location(self,data_x,data_y,pixel_x,pixel_y):
        (b,g,r)=gbscreen.get_pixel(pixel_x,pixel_y)
        if gbscreen.color_match_rgb_array(r,g,b,gbdata.minimap_color_water1,5):
            gbstate.minimap[data_x][data_y]=gbdata.maptypes['Water'][0]
            return
        if gbscreen.color_match_rgb_array(r,g,b,gbdata.minimap_color_water2,5):
            gbstate.minimap[data_x][data_y]=gbdata.maptypes['Water'][0]
            return
        if gbscreen.color_match_rgb_array(r,g,b,gbdata.minimap_color_rock,5):
            gbstate.minimap[data_x][data_y]=gbdata.maptypes['Rock'][0]
            return
        if gbscreen.color_match_rgb_array(r,g,b,gbdata.minimap_color_grass0,5):
            gbstate.minimap[data_x][data_y]=gbdata.maptypes['Grass0'][0]
            return
        if gbscreen.color_match_rgb_array(r,g,b,gbdata.minimap_color_grass1,5):
            gbstate.minimap[data_x][data_y]=gbdata.maptypes['Grass1'][0]
            return
        if gbscreen.color_match_rgb_array(r,g,b,gbdata.minimap_color_grass2,5):
            gbstate.minimap[data_x][data_y]=gbdata.maptypes['Grass2'][0]
            return
        if gbscreen.color_match_rgb_array(r,g,b,gbdata.minimap_color_sand,5):
            gbstate.minimap[data_x][data_y]=gbdata.maptypes['Sand'][0]
            return
        if gbscreen.color_match_rgb_array(r,g,b,gbdata.minimap_color_dock,5):
            gbstate.minimap[data_x][data_y]=gbdata.maptypes['Dock'][0]
            return
        if gbscreen.color_match_rgb_array(r,g,b,gbdata.minimap_color_dirt,5):
            gbstate.minimap[data_x][data_y]=gbdata.maptypes['Dirt'][0]
            return
        #gbstate.minimap[data_x][data_y]=gbdata.maptypes['Unknown'][0]

    def gather_minimap(self):
        if gbstate.minimap is None:
            gbstate.minimap=[0 for x in range(gbdata.minimap_width)]
            for data_x in range(gbdata.minimap_width):
                gbstate.minimap[data_x]=[0 for y in range(gbdata.minimap_height)]

        #pixel_start_x=gbdata.minimap_dashes_L2R_0-gbdata.minimap_dashes_step
        #pixel_start_y=gbdata.minimap_dashes_T2B_0-gbdata.minimap_dashes_step
        pixel_start_x=gbdata.minimap_origin_x
        pixel_start_y=gbdata.minimap_origin_y
        for data_x in range(gbdata.minimap_width):
            pixel_x=(data_x*gbdata.minimap_square_spacing)+pixel_start_x
            for data_y in range(gbdata.minimap_height):
                pixel_y=(data_y*gbdata.minimap_square_spacing)+pixel_start_y
                self.process_location(data_x,data_y,pixel_x,pixel_y)

    def debug_minimap(self):
        if gbstate.minimap is None:
            print("no minimap")
            return
        for y in range(gbdata.minimap_height):
            line=''
            for x in range(gbdata.minimap_width):
                line+=gbdata.maptype_rev[gbstate.minimap[x][y]][1]
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
        for j in range(1,gbdata.minimap_pin_width):
            lx=startx-j
            if self.is_pin_orange(lx,starty):
                circle_left_x=lx
                break
        # Scan right from the previous center line.
        for j in range(1,gbdata.minimap_pin_width):
            rx=startx+j
            if self.is_pin_orange(rx,starty):
                circle_right_x=rx
                break
        # circle_right_y and circle_left_y are one pixel right and left
        # of the white circle.
        #print("circle_left_x=",circle_left_x)
        #print("circle_right_x=",circle_right_x)
        circle_center_x=(circle_left_x+circle_right_x)/2
        #print("circle_center_x=",circle_center_x)
        return circle_center_x

    def locate_horizontal_center_line(self,startx,starty):
        # Now use the white circle to find the horizontal center line.
        # Scan up from the previous center line.
        circle_top_y=starty
        circle_bottom_y=starty
        for j in range(1,gbdata.minimap_pin_height):
            ty=starty-j
            if self.is_pin_orange(startx,ty):
                circle_top_y=ty
                break
        # Scan down from the previous center line.
        for j in range(1,gbdata.minimap_pin_height):
            by=starty+j
            if self.is_pin_orange(startx,by):
                circle_bottom_y=by
                break
        # circle_top_y and circle_bottom_y are one pixel above and below
        # the white circle.
        #print("circle_top_y=",circle_top_y)
        #print("circle_bottom_y=",circle_bottom_y)
        circle_center_y=(circle_top_y+circle_bottom_y)/2
        #print("circle_center_y=",circle_center_y)
        return circle_center_y

    def verify_pin_shape(self,x,y):
        """Verify that there is a pin at this location and
        not some other thing that happens to have the same color"""

        # Scan pixels left and right to try to find the vertical center line
        # of the orange part.
        left_x=x
        right_x=x
        for j in range(1,gbdata.minimap_pin_width):
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
        for j in range(1,gbdata.minimap_pin_height):
            uy=y-j
            if self.is_pin_orange(cx,uy):
                up_y=uy
            dy=y+j
            if self.is_pin_orange(cx,dy):
                down_y=dy
        #print("up_y=",up_y)
        #print("down_y=",down_y)
        yextent=(down_y-up_y)+1
        if yextent < (gbdata.minimap_pin_height-5):
            return False
        if yextent > (gbdata.minimap_pin_height+3):
            return False

        # Find the white circle in the head of the pin.
        # Scan down from the top.
        circle_top_y=up_y
        circle_bottom_y=down_y
        for j in range(1,gbdata.minimap_pin_height):
            uy=up_y+j
            if self.is_pin_orange(cx,uy):
                circle_top_y=uy
            else:
                break # it stopped being orange
        # Scan up from the bottom.
        for j in range(1,gbdata.minimap_pin_height):
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
        print("circle_center_x=",circle_center_x)
        print("circle_center_y=",circle_center_y)


        # Calculate a tip location.
        tip_x=circle_center_x
        tip_y=circle_center_y+gbdata.minimap_pin_center_to_tip
        #print("tip_x=",tip_x)
        #print("tip_y=",tip_y)

        # Calculate the map location from the tip location.
        map_x=(tip_x-gbdata.minimap_origin_x)/gbdata.minimap_square_spacing
        map_y=(tip_y-gbdata.minimap_origin_y)/gbdata.minimap_square_spacing
        #print("map_x=",map_x)
        #print("map_y=",map_y)
        map_x+=gbdata.minimap_pin_tune_mx
        map_y+=gbdata.minimap_pin_tune_my
        #print("map_x=",map_x)
        #print("map_y=",map_y)

        if not gbtrack.in_map_bounds(map_x,map_y):
            return False

        gbstate.position_minimap_x=map_x
        gbstate.position_minimap_y=map_y

        gbtrack.set_current_position(map_x,map_y)

        return True

    def position_from_minimap(self):
        gbstate.position_minimap_x=-1
        gbstate.position_minimap_y=-1
        """Find the orange pin."""
        search_w=gbdata.minimap_right-gbdata.minimap_left
        search_h=gbdata.minimap_bottom-gbdata.minimap_top_pin
        for local_y in range(0,search_h,gbdata.minimap_pin_search_y):
            pixel_y=gbdata.minimap_top_pin+local_y
            for local_x in range(0,search_w,gbdata.minimap_pin_search_x):
                pixel_x=gbdata.minimap_left+local_x
                if self.is_pin_orange(pixel_x,pixel_y):
                    print("found pin at",pixel_x,pixel_y)
                    if self.verify_pin_shape(pixel_x,pixel_y):
                        return
        return
