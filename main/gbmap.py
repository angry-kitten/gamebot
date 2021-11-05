#
# Copyright 2021 by angry-kitten
# Objects for working with the map.
#

import time
import gbdata
import gbstate

waypoints=[]
possible_pole=[]
waypoint_pole=[]

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

def is_grass(id):
    if id == MapTypeGrass0:
        return True
    if id == MapTypeGrass1:
        return True
    if id == MapTypeGrass2:
        return True
    return False

def planning_pass_check_pole(mx1,my1,mx2,my2):
    # We know that mx2 my2 is water.
    print("planning_check_pole",mx1,my1,mx2,my2)
    n1=gbstate.mainmap[mx1][my1]
    n2=gbstate.mainmap[mx2][my2]
    print("n1 is",n1.phonemap)
    print("n2 is",n2.phonemap)
    if not is_grass(n1.phonemap):
        print("start not grass")
        return False
    dx=mx2-mx1
    dy=my2-my1
    if dx < -1 or dx > 1:
        # Block recursion
        return False
    if dy < -1 or dy > 1:
        # Block recursion
        return False
    for j in range(1,5): # We already know j=0 is water
        mx=mx2+(dx*j)
        my=my2+(dy*j)
        if is_bad_location(mx,my):
            return False
        print("mx my",mx,my)
        n=gbstate.mainmap[mx][my]
        print("n is",n.phonemap)
        if n.phonemap != MapTypeWater:
            print("maybe can pole")
            if not is_grass(n.phonemap):
                print("end not grass")
                return False
            if n1.phonemap != n.phonemap:
                print("mismatched grass")
                return False
            # Recurse to all the other checks. Just because it's not water
            # doesn't mean it can pole there if there is a different
            # type of obstruction. It could also be reached easier from another
            # direction.
            can=planning_pass_pair(mx1,my1,mx,my)
            if can:
                print("can")
                print("able to poll from",mx1,my1,"to",mx,my)
                possible1=[mx1,my1,mx,my]
                possible2=[mx,my,mx1,my1]
                global possible_pole
                if possible1 not in possible_pole:
                    if possible2 not in possible_pole:
                        possible_pole.append(possible1)
                    else:
                        print("already possible2")
                else:
                    print("already possible1")
            return can
    return False

def planning_pass_pair(mx1,my1,mx2,my2):
    # return True if something changed
    if is_bad_location(mx2,my2):
        return False
    n1=gbstate.mainmap[mx1][my1]
    n2=gbstate.mainmap[mx2][my2]
    if is_obstructed(mx1,my1):
        #print("ob",mx1,my1)
        return False
    if gbstate.inventory_has_pole:
        if n2.phonemap == MapTypeWater:
            # It might be able to pole over what otherwise would be an obstruction.
            if planning_pass_check_pole(mx1,my1,mx2,my2):
                return True
    if is_obstructed(mx2,my2):
        #print("ob",mx2,my2)
        return False
    if not gbstate.inventory_has_ladder:
        # Can't change levels without a ladder.
        # Everything is at level 0 unless it is grass1 or grass2.
        if n1.phonemap == MapTypeGrass1:
            # Start is level 1
            if n2.phonemap != MapTypeGrass1:
                # Destination is level 0 or 2.
                return False
        elif n1.phonemap == MapTypeGrass2:
            # Start is level 2
            if n2.phonemap != MapTypeGrass2:
                # Destination is level 0 or 1.
                return False
        else:
            # Start is level 0
            if n2.phonemap == MapTypeGrass1 or n2.phonemap == MapTypeGrass2:
                # Destination is level 1 or 2.
                return False

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
    global possible_pole
    possible_pole=[]
    global waypoint_pole
    waypoint_pole=[]
    planning_clear()
    mx=int(round(from_mx))
    my=int(round(from_my))
    n=gbstate.mainmap[mx][my]
    if n.phonemap == MapTypeWater:
        print("standing on water")
        # That's awkword. We're standing on water. Maybe it's a
        # triangle edge on the water.
        #n.phonemap=MapTypeUnknown
        n.phonemap=MapTypeGrass0
        n.obstruction_status=ObStandingOnWater
    n.planning_distance=1
    print("has pole",gbstate.inventory_has_pole)
    while planning_pass():
        pass
    return

def planning_build_waypoints_from_to(from_mx,from_my,to_mx,to_my):
    print("planning_build_waypoints_from_to",from_mx,from_my,to_mx,to_my)
    global waypoints
    waypoints=[]
    global waypoint_pole
    waypoint_pole=[]

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
        gbstate.mainmap[wmx][wmy].move_type=MoveStep
        return (nmx,nmy)
    # try up/north
    (nmx,nmy)=planning_try_going(wmx,wmy,0,-1)
    if nmx >=0:
        gbstate.mainmap[wmx][wmy].move_type=MoveStep
        return (nmx,nmy)
    # try right/east
    (nmx,nmy)=planning_try_going(wmx,wmy,1,0)
    if nmx >=0:
        gbstate.mainmap[wmx][wmy].move_type=MoveStep
        return (nmx,nmy)
    # try left/west
    (nmx,nmy)=planning_try_going(wmx,wmy,-1,0)
    if nmx >=0:
        gbstate.mainmap[wmx][wmy].move_type=MoveStep
        return (nmx,nmy)

    if gbstate.inventory_has_pole:
        # try down/south
        (nmx,nmy)=planning_try_going_pole(wmx,wmy,0,1)
        if nmx >=0:
            gbstate.mainmap[wmx][wmy].move_type=MovePole
            return (nmx,nmy)
        # try up/north
        (nmx,nmy)=planning_try_going_pole(wmx,wmy,0,-1)
        if nmx >=0:
            gbstate.mainmap[wmx][wmy].move_type=MovePole
            return (nmx,nmy)
        # try right/east
        (nmx,nmy)=planning_try_going_pole(wmx,wmy,1,0)
        if nmx >=0:
            gbstate.mainmap[wmx][wmy].move_type=MovePole
            return (nmx,nmy)
        # try left/west
        (nmx,nmy)=planning_try_going_pole(wmx,wmy,-1,0)
        if nmx >=0:
            gbstate.mainmap[wmx][wmy].move_type=MovePole
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

def planning_try_going_pole(wmx,wmy,dx,dy):
    print("planning_try_going_pole",wmx,wmy,dx,dy)
    v1=gbstate.mainmap[wmx][wmy].planning_distance
    print("v1",v1)
    mx=wmx
    my=wmy
    rmx=-1
    rmy=-1

    # make sure the first step is water
    mx+=dx
    my+=dy
    if gbstate.mainmap[mx][my].phonemap != MapTypeWater:
        print("first step not water")
        return (rmx,rmy)

    # find the other side
    for j in range(5):
        mx+=dx
        my+=dy
        if gbstate.mainmap[mx][my].phonemap != MapTypeWater:
            break

    # see if the water was too wide
    if gbstate.mainmap[mx][my].phonemap == MapTypeWater:
        print("water too wide")
        return (rmx,rmy)

    # make sure the source and destination type match
    if gbstate.mainmap[wmx][wmy].phonemap != gbstate.mainmap[mx][my].phonemap:
        print("src dst type mismatch")
        return (rmx,rmy)

    # now make sure the destination distance is one less than the source
    v1-=1
    v2=gbstate.mainmap[mx][my].planning_distance
    if v1 != v2:
        print("distance mismatch")
        return (rmx,rmy)

    # ok, we can pole across
    rmx=mx
    rmy=my
    print("result",rmx,rmy)
    print("add poll to waypoints from",wmx,wmy,"to",rmx,rmy)
    waypole=[rmx,rmy,wmx,wmy]
    global waypoint_pole
    waypoint_pole.append(waypole)
    return (rmx,rmy)
