#
# Copyright 2021 by angry-kitten
# Look at the current screen and capture the minimaps and
# determine player location from the pin.
#

import taskobject
import gbdata
import gbstate
import cv2
import taskpress
import tasksay
import taskdetect
import taskgotomain
import gbscreen

class TaskUpdateMini(taskobject.Task):
    """TaskUpdateMini Object"""

    def __init__(self):
        super().__init__()
        print("new TaskUpdateMini object")

    def Poll(self):
        """check if any action can be taken"""
        print("TaskUpdateMini Poll")
        if not self.started:
            self.Start()
            return
        if self.taskdone:
            return
        if gbstate.frame is None:
            return
        self.gather_minimap()
        self.debug_minimap()
        self.position_from_minimap()
        print("TaskUpdateMini done")
        self.taskdone=True
        return

    def Start(self):
        """Cause the task to begin doing whatever."""
        print("TaskUpdateMini Start")
        if self.started:
            return # already started
        self.started=True

    def DebugRecursive(self,indent=0):
        self.DebugPrint("TaskUpdateMini",indent)

    def process_location(self,data_x,data_y,pixel_x,pixel_y):
        (b,g,r)=gbscreen.get_pixel(pixel_x,pixel_y)
        if gbscreen.color_match_rgb(r,g,b,156,221,186,5):
            gbstate.minimap[data_x][data_y]=gbdata.maptypes['Water'][0]
            return
        if gbscreen.color_match_rgb(r,g,b,121,207,180,5):
            gbstate.minimap[data_x][data_y]=gbdata.maptypes['Water'][0]
            return
        if gbscreen.color_match_rgb(r,g,b,113,116,136,5):
            gbstate.minimap[data_x][data_y]=gbdata.maptypes['Rock'][0]
            return
        if gbscreen.color_match_rgb(r,g,b,71,125,68,5):
            gbstate.minimap[data_x][data_y]=gbdata.maptypes['Grass0'][0]
            return
        if gbscreen.color_match_rgb(r,g,b,70,171,67,5):
            gbstate.minimap[data_x][data_y]=gbdata.maptypes['Grass1'][0]
            return
        if gbscreen.color_match_rgb(r,g,b,99,212,78,5):
            gbstate.minimap[data_x][data_y]=gbdata.maptypes['Grass2'][0]
            return
        if gbscreen.color_match_rgb(r,g,b,245,234,165,5):
            gbstate.minimap[data_x][data_y]=gbdata.maptypes['Sand'][0]
            return
        if gbscreen.color_match_rgb(r,g,b,157,131,97,5):
            gbstate.minimap[data_x][data_y]=gbdata.maptypes['Dock'][0]
            return
        if gbscreen.color_match_rgb(r,g,b,174,159,125,5):
            gbstate.minimap[data_x][data_y]=gbdata.maptypes['Dirt'][0]
            return
        gbstate.minimap[data_x][data_y]=gbdata.maptypes['Unknown'][0]

    def gather_minimap(self):
        gbstate.minimap=[0 for x in range(gbdata.minimap_width)]
        pixel_start_x=gbdata.minimap_dashes_L2R_0-gbdata.minimap_dashes_step
        pixel_start_y=gbdata.minimap_dashes_T2B_0-gbdata.minimap_dashes_step
        for data_x in range(gbdata.minimap_width):
            pixel_x=(data_x*gbdata.minimap_square_spacing)+pixel_start_x
            gbstate.minimap[data_x]=[0 for y in range(gbdata.minimap_height)]
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
        if gbscreen.color_match_array(pixel_x,pixel_y,gbdata.pin_orange1,5):
            return True
        if gbscreen.color_match_array(pixel_x,pixel_y,gbdata.pin_orange2,5):
            return True
        return False

    def verify_pin_shape(self,x,y):
        """Verify that there is a pin at this location and
        not some other thing that happens to have the same color"""

        # Scan pixels left and right to try to find the vertical center line.
        left_x=x
        right_x=x
        for j in range(1,gbdata.pin_width):
            lx=x-j
            if self.is_pin_orange(lx,y):
                left_x=lx
            rx=x+j
            if self.is_pin_orange(rx,y):
                right_x=rx
        print("left_x=",left_x)
        print("right_x=",right_x)
        cx=(left_x+right_x)/2
        print("cx=",cx)

        # Scan pixels up and down to try to find vertical extent.
        up_y=y
        down_y=y
        for j in range(1,gbdata.pin_height):
            uy=y-j
            if self.is_pin_orange(cx,uy):
                up_y=uy
            dy=y+j
            if self.is_pin_orange(cx,dy):
                down_y=dy
        print("up_y=",up_y)
        print("down_y=",down_y)
        yextent=(down_y-up_y)+1
        if yextent < (gbdata.pin_height-5):
            return False
        if yextent > (gbdata.pin_height+3):
            return False

        # Find the circle in the head of the pin.
        # Scan down from the top.
        circle_top_y=up_y
        circle_bottom_y=down_y
        for j in range(1,gbdata.pin_height):
            uy=up_y+j
            if self.is_pin_orange(cx,uy):
                circle_top_y=uy
            else:
                break
        # Scan up from the bottom.
        for j in range(1,gbdata.pin_height):
            dy=down_y-j
            if self.is_pin_orange(cx,dy):
                circle_bottom_y=dy
            else:
                break
        print("circle_top_y=",circle_top_y)
        print("circle_bottom_y=",circle_bottom_y)
        circle_center_y=(circle_bottom_y+circle_top_y)/2
        print("circle_center_y=",circle_center_y)

        # Now use the circle to find the vertical center line again.
        # The assumption is that it will produce a better value than
        # the one above.
        # Scan left from the previous center line.
        circle_left_x=cx
        circle_right_x=cx
        for j in range(1,gbdata.pin_width):
            lx=cx-j
            if self.is_pin_orange(lx,circle_center_y):
                circle_left_x=lx
                break
        # Scan right from the previous center line.
        for j in range(1,gbdata.pin_width):
            rx=cx+j
            if self.is_pin_orange(rx,circle_center_y):
                circle_right_x=rx
                break
        print("circle_left_x=",circle_left_x)
        print("circle_right_x=",circle_right_x)
        circle_center_x=(circle_left_x+circle_right_x)/2
        print("circle_center_x=",circle_center_x)

        # Calculate a tip location.
        tip_x=circle_center_x
        tip_y=circle_center_y+gbdata.pin_center_to_tip
        print("tip_x=",tip_x)
        print("tip_y=",tip_y)

        # Calculate the map location from the tip location.
        map_x=(tip_x-gbdata.minimap_left)/gbdata.minimap_square_spacing
        map_y=(tip_y-gbdata.minimap_top)/gbdata.minimap_square_spacing
        print("map_x=",map_x)
        print("map_y=",map_y)

        gbstate.position_minimap_x=map_x
        gbstate.position_minimap_y=map_y

        return True

    def position_from_minimap(self):
        gbstate.position_minimap_x=-1
        gbstate.position_minimap_y=-1
        """Find the orange pin."""
        search_w=gbdata.minimap_right-gbdata.minimap_left
        search_h=gbdata.minimap_bottom-gbdata.minimap_top_pin
        for local_y in range(0,search_h,gbdata.pin_search_y):
            pixel_y=gbdata.minimap_top_pin+local_y
            for local_x in range(0,search_w,gbdata.pin_search_x):
                pixel_x=gbdata.minimap_left+local_x
                if self.is_pin_orange(pixel_x,pixel_y):
                    print("found pin at",pixel_x,pixel_y)
                    if self.verify_pin_shape(pixel_x,pixel_y):
                        return
        return
