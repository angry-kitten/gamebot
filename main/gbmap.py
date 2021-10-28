#
# Copyright 2021 by angry-kitten
# Objects for working with the map.
#

import time
import gbdata
import gbstate

ObUnknown=0
ObOpen=1
Obstructed=2
ObStandingOnWater=3

MoveUnknown=0
MoveStep=1
MovePole=2
MoveLadder=3

MapTypeUnknown=0
MapTypeWater=1
MapTypeRock=2
MapTypeGrass0=3
MapTypeGrass1=4
MapTypeGrass2=5
MapTypeSand=6
MapTypeDock=7
MapTypeDirt=8

maptypes={
    'Unknown':  [MapTypeUnknown, '_'],
    'Water':  [MapTypeWater, 'W'],
    'Rock':  [MapTypeRock, 'R'],
    'Grass0':  [MapTypeGrass0, '0'],
    'Grass1':  [MapTypeGrass1, '1'],
    'Grass2':  [MapTypeGrass2, '2'],
    'Sand':  [MapTypeSand, 'S'],
    'Dock':  [MapTypeDock, 'd'],
    'Dirt':  [MapTypeDirt, 'D']
}

maptype_rev={}
for key in maptypes:
    maptype_rev[maptypes[key][0]]=[key,maptypes[key][1]]

class MapSquare:
    """MapSquare Object"""

    def __init__(self):
        self.objstruction_status=ObUnknown
        self.planning_distance=0
        self.move_type=MoveUnknown
        self.minimap=MapTypeUnknown
        self.phonemap=MapTypeUnknown
        return

def init_map():
    gbstate.mainmap=[0 for x in range(gbdata.map_width)]
    for data_x in range(gbdata.map_width):
        gbstate.mainmap[data_x]=[MapSquare() for y in range(gbdata.map_height)]
    return

def is_bad_location(mx,my):
    mx=int(round(mx))
    my=int(round(my))
    if mx < 0:
        return True
    if mx >= gbdata.map_width:
        return True
    if my < 0:
        return True
    if my >= gbdata.map_height:
        return True
    return False

def is_obstructed(mx,my):
    mx=int(round(mx))
    my=int(round(my))
    if gbstate.mainmap is None:
        init_map()
    if is_bad_location(mx,my):
        return True
    return

def set_obstruction(mx,my,v):
    mx=int(round(mx))
    my=int(round(my))
    if gbstate.mainmap is None:
        init_map()
    return
