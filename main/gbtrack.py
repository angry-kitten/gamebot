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

def evaluate_position(mx,my):
    mx=int(round(mx))
    my=int(round(my))
    if gbstate.minimap is None:
        return
    v=gbstate.minimap[mx][my]
    if v == gbdata.maptype_water:
        set_standing_on_water(mx,my)

def set_current_position(map_x,map_y):
    gbstate.player_mx=map_x
    gbstate.player_my=map_y
    set_not_obstructed(map_x,map_y)
    evaluate_position(map_x,map_y)

    if gbstate.center_mx < 0:
        gbstate.center_mx=gbstate.player_mx
        gbstate.center_my=gbstate.player_my
        gbstate.center_my-=gbstate.tune_fb_offset_my

def calculate_heading(dx,dy):
    # Heading = 0 for North and clockwise from there.
    # +dx is right/east
    # +dy is down/south
    print("dx=",dx,"dy=",dy)
    if dx == 0 and dy == 0:
        heading=0 # up/north
        print("heading",heading)
        return heading

    if dx == 0:
        if dy > 0:
            heading=180 # down/south
            print("heading",heading)
            return heading
        else:
            heading=0 # up/north
            print("heading",heading)
            return heading

    if dy == 0:
        if dx > 0:
            heading=90 # right/east
            print("heading",heading)
            return heading
        else:
            heading=270 # left/west
            print("heading",heading)
            return heading

    # neither dx nor dy are zero
    rawheading=math.degrees(math.atan(dx/dy))
    # rawheading should be -90 to +90
    print("rawheading",rawheading)
    if dx > 0 and dy > 0:
        # south-east, rawheading should be 0 to +90
        heading=180-rawheading
    elif dx > 0 and dy < 0:
        # north-east, rawheading should be -90 to 0
        heading=-rawheading
    elif dx < 0 and dy > 0:
        # south-west, rawheading should be -90 to 0
        heading=180-rawheading
    else:
        # north-west, rawheading should be 0 to 90
        heading=360-rawheading

    print("heading",heading)
    return heading

def calculate_dx_dy(heading,distance):
    # Heading = 0 for North and clockwise from there.
    # +dx is right/east
    # +dy is down/south
    if distance == 0:
        return (0,0)

    r=math.radians(heading)
    s=math.sin(r)*distance
    c=math.cos(r)*distance

    dx=s
    dy=-c

    print("heading=",heading,"distance=",distance,"dx=",dx,"dy=",dy)

    return (dx,dy)

def build_default_obstruction_map():
    gbstate.obstructionmap=[0 for x in range(gbdata.map_width)]
    for data_x in range(gbdata.map_width):
        # Set all to 0 or unknown.
        gbstate.obstructionmap[data_x]=[0 for y in range(gbdata.map_height)]

def debug_obstructionmap():
    if gbstate.obstructionmap is None:
        print("no obstructionmap")
        return
    for y in range(gbdata.map_height):
        line=''
        for x in range(gbdata.map_width):
            v=gbstate.obstructionmap[x][y]
            c=' '
            if v == 1:
                c='u'
            elif v == 2:
                c='o'
            line+=c
        print(line)

def set_obstructed(mx,my):
    mx=int(round(mx))
    my=int(round(my))
    if gbstate.obstructionmap is None:
        build_default_obstruction_map()
    gbstate.obstructionmap[mx][my]=2

def set_not_obstructed(mx,my):
    mx=int(round(mx))
    my=int(round(my))
    if gbstate.obstructionmap is None:
        build_default_obstruction_map()
    gbstate.obstructionmap[mx][my]=1
    #debug_obstructionmap()

def set_unknown(mx,my):
    mx=int(round(mx))
    my=int(round(my))
    if gbstate.obstructionmap is None:
        build_default_obstruction_map()
    gbstate.obstructionmap[mx][my]=0

def set_standing_on_water(mx,my):
    mx=int(round(mx))
    my=int(round(my))
    print("standing on water",mx,my)
    if gbstate.obstructionmap is None:
        build_default_obstruction_map()
    gbstate.obstructionmap[mx][my]=3
