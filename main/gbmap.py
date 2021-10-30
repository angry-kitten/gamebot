#
# Copyright 2021 by angry-kitten
# Objects for working with the map.
#

import time
import gbdata
import gbstate

waypoints=[]

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
        self.minimap=MapTypeUnknown
        self.phonemap=MapTypeUnknown
        self.planning_distance=0
        self.move_type=MoveUnknown
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
    n=gbstate.mainmap[mx][my]

    p=n.phonemap
    #print("ob p",p)
    if p == MapTypeWater:
        return True

    v=n.objstruction_status
    #print("ob v",v)
    if v == ObUnknown:
        return False
    if v == ObOpen:
        return False
    if v == Obstructed:
        return True

    return False

def set_obstruction(mx,my,v):
    mx=int(round(mx))
    my=int(round(my))
    if gbstate.mainmap is None:
        init_map()
    n=gbstate.mainmap[mx][my]
    n.objstruction_status=v
    return

def planning_clear():
    for mx in range(gbdata.map_width):
        for my in range(gbdata.map_height):
            n=gbstate.mainmap[mx][my]
            n.planning_distance=0
            n.move_type=MoveUnknown

def planning_pass_pair(mx1,my1,mx2,my2):
    # return True if something changed
    if is_bad_location(mx2,my2):
        return False
    if is_obstructed(mx1,my1):
        #print("ob",mx1,my1)
        return False
    if is_obstructed(mx2,my2):
        #print("ob",mx2,my2)
        return False
    n1=gbstate.mainmap[mx1][my1]
    n2=gbstate.mainmap[mx2][my2]
    if n1.planning_distance == 0:
        if n2.planning_distance != 0:
            n1.planning_distance=n2.planning_distance+1
            return True
        return False
    if n2.planning_distance == 0:
        if n1.planning_distance != 0:
            n2.planning_distance=n1.planning_distance+1
            return True
        return False
    if n2.planning_distance > (n1.planning_distance+1):
        n2.planning_distance=n1.planning_distance+1
        return True
    if n1.planning_distance > (n2.planning_distance+1):
        n1.planning_distance=n2.planning_distance+1
        return True
    return False

def planning_pass():
    # return True if something changed
    changed=False
    for mx in range(gbdata.map_width):
        for my in range(gbdata.map_height):
            n=gbstate.mainmap[mx][my]
            if n.planning_distance != 0:
                #print("planning",mx,my,n.planning_distance)
                #if planning_pass_pair(mx,my,mx-1,my-1):
                #    changed=True
                if planning_pass_pair(mx,my,mx,my-1):
                    changed=True
                #if planning_pass_pair(mx,my,mx+1,my-1):
                #    changed=True
                if planning_pass_pair(mx,my,mx-1,my):
                    changed=True
                if planning_pass_pair(mx,my,mx+1,my):
                    changed=True
                #if planning_pass_pair(mx,my,mx-1,my+1):
                #    changed=True
                if planning_pass_pair(mx,my,mx,my+1):
                    changed=True
                #if planning_pass_pair(mx,my,mx+1,my+1):
                #    changed=True
    return changed

def planning_build_distance_grid(from_mx,from_my):
    print("planning_build_distance_grid",from_mx,from_my)
    global waypoints
    waypoints=[]
    planning_clear()
    mx=int(round(from_mx))
    my=int(round(from_my))
    n=gbstate.mainmap[mx][my]
    n.planning_distance=1
    while planning_pass():
        pass
    return

def planning_build_waypoints_from_to(from_mx,from_my,to_mx,to_my):
    print("planning_build_waypoints_from_to",from_mx,from_my,to_mx,to_my)
    global waypoints
    waypoints=[]
    fmx=int(round(from_mx))
    fmy=int(round(from_my))
    tmx=int(round(to_mx))
    tmy=int(round(to_my))

    print("fmx fmy",fmx,fmy)
    print("tmx tmy",tmx,tmy)

    pd=gbstate.mainmap[fmx][fmy].planning_distance
    if pd != 1:
        print("bad planning_distance at from",pd)
        return
    print("good planning_distance at from",pd)

    # plan back from the to position to the from position
    walk_mx=tmx
    walk_my=tmy

    while walk_mx != fmx or walk_my != fmy:
        waypoints.append([walk_mx,walk_my])
        print("planning waypoints",waypoints)
        (nmx,nmy)=planning_next_waypoint(walk_mx,walk_my)
        if nmx < 0:
            print("error")
            break
        walk_mx=nmx
        walk_my=nmy
    return

def planning_next_waypoint(wmx,wmy):
    print("planning_next_waypoint",wmx,wmy)
    # try down/south
    (nmx,nmy)=planning_try_going(wmx,wmy,0,1)
    if nmx >=0:
        return (nmx,nmy)
    # try up/north
    (nmx,nmy)=planning_try_going(wmx,wmy,0,-1)
    if nmx >=0:
        return (nmx,nmy)
    # try right/east
    (nmx,nmy)=planning_try_going(wmx,wmy,1,0)
    if nmx >=0:
        return (nmx,nmy)
    # try left/west
    (nmx,nmy)=planning_try_going(wmx,wmy,-1,0)
    if nmx >=0:
        return (nmx,nmy)
    return (-1,-1)

def planning_try_going(wmx,wmy,dx,dy):
    print("planning_try_going",wmx,wmy,dx,dy)
    v1=gbstate.mainmap[wmx][wmy].planning_distance
    print("v1",v1)
    mx=wmx
    my=wmy
    rmx=-1
    rmy=-1
    while True:
        mx+=dx
        my+=dy
        v1-=1
        print("v1",v1,mx,my)
        v2=gbstate.mainmap[mx][my].planning_distance
        print("v2",v2,mx,my)
        if v2 != v1:
            break
        rmx=mx
        rmy=my
        if v1 == 1: # at start position
            print("at start")
            break
    print("result",rmx,rmy)
    return (rmx,rmy)
