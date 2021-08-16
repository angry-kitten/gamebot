#
# Copyright 2021 by angry-kitten
# Look at the video at startup and see what the current screen is.
# Move to the main playing screen.
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

    def position_from_minimap(self):
        return
