#
# Copyright 2021 by angry-kitten
# Various functions for drawing status on a frame.
#

import taskobject
import gbdata
import gbstate
import cv2
import taskpress
import taskdetect
import math

def set_current_position(map_x,map_y):
    gbstate.player_mx=map_x
    gbstate.player_my=map_y

    if gbstate.center_mx < 0:
        gbstate.center_mx=gbstate.player_mx
        gbstate.center_my=gbstate.player_my
        gbstate.center_my-=gbstate.tune_fb_offset_my
