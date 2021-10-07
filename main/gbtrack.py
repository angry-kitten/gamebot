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

default_center_offset_my=0.80

def current_position(map_x,map_y):
    gbstate.player_mx=map_x
    gbstate.player_my=map_y
    gbstate.center_mx=gbstate.player_mx
    gbstate.center_my=gbstate.player_my

    gbstate.center_my-=default_center_offset_my
