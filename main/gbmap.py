#
# Copyright 2021 by angry-kitten
# Objects for working with the map.
#

import time
import gbdata
import gbstate
import gbscreen

waypoints=[]
possible_pole=[]
waypoint_pole=[]

step_cost=1
pole_cost=20
ladder_cost=10

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
MapTypePlaza=9
MapTypeJunk=10
MapTypeDiagonalNW=11  # Diagnonal starting from the North West cornier of the square
MapTypeDiagonalSW=12  # Diagnonal starting from the South West cornier of the square
MapTypeBitShift=4
MapTypeBitMask=0xf

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
        self.phonemap2=MapTypeUnknown
        self.diagonal0=MapTypeUnknown  # upper left or upper right
        self.diagonal1=MapTypeUnknown  # lower left or lower right
        return

def init_map():
    gbstate.mainmap=[0 for x in range(gbdata.map_width)]
    for data_x in range(gbdata.map_width):
        gbstate.mainmap[data_x]=[MapSquare() for y in range(gbdata.map_height)]
    gbstate.x_hist=[0 for x in range(gbdata.phonemap_swidth)]
    gbstate.y_hist=[0 for y in range(gbdata.phonemap_sheight)]
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

    p=n.phonemap2
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
    print("n1 is",n1.phonemap2)
    print("n2 is",n2.phonemap2)
    if not is_grass(n1.phonemap2):
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
        print("n is",n.phonemap2)
        if n.phonemap2 != MapTypeWater:
            print("maybe can pole")
            if not is_grass(n.phonemap2):
                print("end not grass")
                return False
            if n1.phonemap2 != n.phonemap2:
                print("mismatched grass")
                return False
            # Recurse to all the other checks. Just because it's not water
            # doesn't mean it can pole there if there is a different
            # type of obstruction. It could also be reached easier from another
            # direction.
            global pole_cost
            can=planning_pass_pair(mx1,my1,mx,my,pole_cost)
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

def planning_pass_pair(mx1,my1,mx2,my2,cost):
    # return True if something changed
    if is_bad_location(mx2,my2):
        return False
    n1=gbstate.mainmap[mx1][my1]
    n2=gbstate.mainmap[mx2][my2]
    if is_obstructed(mx1,my1):
        #print("ob",mx1,my1)
        return False
    if gbstate.inventory_has_pole:
        if n2.phonemap2 == MapTypeWater:
            # It might be able to pole over what otherwise would be an obstruction.
            if planning_pass_check_pole(mx1,my1,mx2,my2):
                return True
    if is_obstructed(mx2,my2):
        #print("ob",mx2,my2)
        return False
    if not gbstate.inventory_has_ladder:
        # Can't change levels without a ladder.
        # Everything is at level 0 unless it is grass1 or grass2.
        if n1.phonemap2 == MapTypeGrass1:
            # Start is level 1
            if n2.phonemap2 != MapTypeGrass1:
                # Destination is level 0 or 2.
                return False
        elif n1.phonemap2 == MapTypeGrass2:
            # Start is level 2
            if n2.phonemap2 != MapTypeGrass2:
                # Destination is level 0 or 1.
                return False
        else:
            # Start is level 0
            if n2.phonemap2 == MapTypeGrass1 or n2.phonemap2 == MapTypeGrass2:
                # Destination is level 1 or 2.
                return False

    # Add a new route.
    if n1.planning_distance == 0:
        if n2.planning_distance != 0:
            n1.planning_distance=n2.planning_distance+cost
            return True
        return False
    if n2.planning_distance == 0:
        if n1.planning_distance != 0:
            n2.planning_distance=n1.planning_distance+cost
            return True
        return False

    # Reduce the planning distance if this is a lower cost route.
    if n2.planning_distance > (n1.planning_distance+cost):
        n2.planning_distance=n1.planning_distance+cost
        return True
    if n1.planning_distance > (n2.planning_distance+cost):
        n1.planning_distance=n2.planning_distance+cost
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
                global step_cost
                if planning_pass_pair(mx,my,mx,my-1,step_cost):
                    changed=True
                if planning_pass_pair(mx,my,mx-1,my,step_cost):
                    changed=True
                if planning_pass_pair(mx,my,mx+1,my,step_cost):
                    changed=True
                if planning_pass_pair(mx,my,mx,my+1,step_cost):
                    changed=True
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
    if n.phonemap2 == MapTypeWater:
        print("standing on water")
        # That's awkword. We're standing on water. Maybe it's a
        # triangle edge on the water.
        #n.phonemap2=MapTypeUnknown
        n.phonemap2=MapTypeGrass0
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
    if gbstate.mainmap[mx][my].phonemap2 != MapTypeWater:
        print("first step not water")
        return (rmx,rmy)

    # find the other side
    for j in range(5):
        mx+=dx
        my+=dy
        if gbstate.mainmap[mx][my].phonemap2 != MapTypeWater:
            break

    # see if the water was too wide
    if gbstate.mainmap[mx][my].phonemap2 == MapTypeWater:
        print("water too wide")
        return (rmx,rmy)

    # make sure the source and destination type match
    if gbstate.mainmap[wmx][wmy].phonemap2 != gbstate.mainmap[mx][my].phonemap2:
        print("src dst type mismatch")
        return (rmx,rmy)

    # now make sure the destination distance is one cost less than the source
    global pole_cost
    v1-=pole_cost
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

def gather_phonemap2():
    print("gather_phonemap2")
    if gbstate.mainmap is None:
        init_map()

    ## Clear out the old data.
    #gbstate.x_hist=[0 for x in range(gbdata.phonemap_swidth)]
    #gbstate.y_hist=[0 for y in range(gbdata.phonemap_sheight)]

    pixel_start_x=gbdata.phonemap_left
    pixel_start_y=gbdata.phonemap_top

    ## Gather the y histogram first.
    #for data_x in range(gbdata.phonemap_swidth):
    #    pixel_x=pixel_start_x+data_x
    #    pr=-1
    #    pg=-1
    #    pb=-1
    #    for data_y in range(gbdata.phonemap_sheight):
    #        pixel_y=pixel_start_y+data_y
    #        (b,g,r)=gbscreen.get_pixel(pixel_x,pixel_y)
    #        r=int(r)
    #        g=int(b)
    #        b=int(b)
    #        if pr >= 0:
    #            dr=abs(r-pr)
    #            dg=abs(g-pg)
    #            db=abs(b-pb)
    #            gbstate.y_hist[data_y] += (dr+dg+db)
    #        pr=r
    #        pg=g
    #        pb=b

    #ymax=1
    #for data_y in range(gbdata.phonemap_sheight):
    #    if ymax < gbstate.y_hist[data_y]:
    #        ymax=gbstate.y_hist[data_y]

    #for data_y in range(gbdata.phonemap_sheight):
    #    gbstate.y_hist[data_y] /= ymax

    ## Gather the x histogram
    #for data_y in range(gbdata.phonemap_sheight):
    #    pixel_y=pixel_start_y+data_y
    #    pr=-1
    #    pg=-1
    #    pb=-1
    #    for data_x in range(gbdata.phonemap_swidth):
    #        pixel_x=pixel_start_x+data_x
    #        (b,g,r)=gbscreen.get_pixel(pixel_x,pixel_y)
    #        r=int(r)
    #        g=int(b)
    #        b=int(b)
    #        if pr >= 0:
    #            dr=abs(r-pr)
    #            dg=abs(g-pg)
    #            db=abs(b-pb)
    #            gbstate.x_hist[data_x] += (dr+dg+db)
    #        pr=r
    #        pg=g
    #        pb=b

    #xmax=1
    #for data_x in range(gbdata.phonemap_swidth):
    #    if xmax < gbstate.x_hist[data_x]:
    #        xmax=gbstate.x_hist[data_x]

    #for data_x in range(gbdata.phonemap_swidth):
    #    gbstate.x_hist[data_x] /= xmax

    ## Use the estimates of the dashed lines to find
    ## the measured dashed lines.

    #gbstate.phonemap_measured_dashes_L2R=[]
    #for l2r in gbdata.phonemap_dashes_L2R:
    #    iestimate=l2r-pixel_start_x
    #    imin=find_minimum_index(gbstate.x_hist,iestimate,1)
    #    print(iestimate,imin)
    #    m=pixel_start_x+imin
    #    print("m",m)
    #    gbstate.phonemap_measured_dashes_L2R.append(m)

    #for j in range(len(gbdata.phonemap_dashes_L2R)-1):
    #    v1=gbdata.phonemap_dashes_L2R[j]
    #    v2=gbdata.phonemap_dashes_L2R[j+1]
    #    dx=v2-v1
    #    print("dx",dx)

    #gbstate.phonemap_measured_dashes_T2B=[]
    #for t2b in gbdata.phonemap_dashes_T2B:
    #    iestimate=t2b-pixel_start_y
    #    imin=find_minimum_index(gbstate.y_hist,iestimate,1)
    #    print(iestimate,imin)
    #    m=pixel_start_y+imin
    #    print("m",m)
    #    gbstate.phonemap_measured_dashes_T2B.append(m)

    #for j in range(len(gbdata.phonemap_dashes_T2B)-1):
    #    v1=gbdata.phonemap_dashes_T2B[j]
    #    v2=gbdata.phonemap_dashes_T2B[j+1]
    #    dy=v2-v1
    #    print("dy",dy)

    # Gather map statistics.
    gbstate.map2stats=[]
    gbstate.map2maybediagonals=[]
    gbstate.map2diagonals=[]
    sy1=int(round(gbdata.phonemap_origin_y))
    sy2=int(round(gbdata.phonemap_origin_y+gbdata.map_height*gbdata.phonemap_square_spacing))
    for mx in range(gbdata.map_width):
        # Calculate floating point map x.
        sx1=gbdata.phonemap_origin_x+(mx*gbdata.phonemap_square_spacing)
        sx2=gbdata.phonemap_origin_x+((mx+1)*gbdata.phonemap_square_spacing)
        # Calculate integer map x inside the lines.
        isx1=int(round(sx1))+1
        isx2=int(round(sx2))-1
        for my in range(gbdata.map_height):
            # Calculate floating point map y.
            sy1=gbdata.phonemap_origin_y+(my*gbdata.phonemap_square_spacing)
            sy2=gbdata.phonemap_origin_y+((my+1)*gbdata.phonemap_square_spacing)
            # Calculate integer map y inside the lines.
            isy1=int(round(sy1))+1
            isy2=int(round(sy2))-1

            process_phonemap_square(mx,my,isx1,isx2,isy1,isy2)

    # Sort and display the stats.

    # Sort by the first element in the entry array, avg.
    print("stats")
    sstats=sorted(gbstate.map2stats, key=lambda entry: entry[0])
    for e in sstats:
        print(e)

    print("maybe diagonals")
    sdiagonals=sorted(gbstate.map2maybediagonals, key=lambda entry: entry[0])
    for e in sdiagonals:
        print(e)

    return

def process_phonemap_square(mx,my,isx1,isx2,isy1,isy2):
    # Find the average first.
    count=0
    sumr=0
    sumg=0
    sumb=0
    for sx in range(isx1,isx2+1):
        for sy in range(isy1,isy2+1):
            (b,g,r)=gbscreen.get_pixel(sx,sy)
            r=int(r)
            g=int(g)
            b=int(b)
            sumr+=r
            sumg+=g
            sumb+=b
            count+=1
    avgr=sumr/count
    avgg=sumg/count
    avgb=sumb/count

    count=0
    sumdr=0
    sumdg=0
    sumdb=0
    # Then find how much they vary. (very crude)
    for sx in range(isx1,isx2+1):
        for sy in range(isy1,isy2+1):
            (b,g,r)=gbscreen.get_pixel(sx,sy)
            r=int(r)
            g=int(g)
            b=int(b)
            dr=abs(r-avgr)
            dg=abs(g-avgg)
            db=abs(b-avgb)
            sumdr+=dr
            sumdg+=dg
            sumdb+=db
            count+=1

    avgdr=sumdr/count
    avgdg=sumdg/count
    avgdb=sumdb/count
    avg=(avgdr+avgdg+avgdb)/3
    entry=[avg,avgr,avgg,avgb,isx1,isy1,isx2,isy2,count]
    #print(entry)
    #gbstate.map2stats.append(entry)

    # yyy
    if avg <= 80.0:
        mt=color_to_maptype(avgr,avgg,avgb)
        if mt is not None:
            gbstate.mainmap[mx][my].phonemap2=mt
            return

    #gbstate.map2stats.append(entry)

    # look for diagonals
    # Evaluate the four possible triangles the same as the entire
    # square was evaluated above.

    diag_w=(isx2-isx1)+1
    diag_h=(isy2-isy1)+1
    diag_slope=diag_h/diag_w
    nw_u_count=0
    nw_u_sumr=0
    nw_u_sumg=0
    nw_u_sumb=0
    nw_l_count=0
    nw_l_sumr=0
    nw_l_sumg=0
    nw_l_sumb=0
    sw_u_count=0
    sw_u_sumr=0
    sw_u_sumg=0
    sw_u_sumb=0
    sw_l_count=0
    sw_l_sumr=0
    sw_l_sumg=0
    sw_l_sumb=0
    for sx in range(isx1,isx2+1):
        for sy in range(isy1,isy2+1):
            # nx and ny are the offsets inside this square
            nx=sx-isx1
            ny=sy-isy1
            # Calculate the y for the NW diagonal
            diag_nw_ny=int(round(nx*diag_slope))
            # Calculate the y for the SW diagonal
            diag_sw_ny=(diag_h-1)-diag_nw_ny

            (b,g,r)=gbscreen.get_pixel(sx,sy)
            r=int(r)
            g=int(g)
            b=int(b)

            if ny < diag_nw_ny:
                # This is the upper part of the NW diagonal
                nw_u_sumr+=r
                nw_u_sumg+=g
                nw_u_sumb+=b
                nw_u_count+=1
            elif ny > diag_nw_ny:
                # This is the lower part of the NW diagonal
                nw_l_sumr+=r
                nw_l_sumg+=g
                nw_l_sumb+=b
                nw_l_count+=1
            # else don't evaluate pixels on the diagonal

            if ny < diag_sw_ny:
                # This is the upper part of the SW diagonal
                sw_u_sumr+=r
                sw_u_sumg+=g
                sw_u_sumb+=b
                sw_u_count+=1
            elif ny > diag_sw_ny:
                # This is the lower part of the SW diagonal
                sw_l_sumr+=r
                sw_l_sumg+=g
                sw_l_sumb+=b
                sw_l_count+=1
            # else don't evaluate pixels on the diagonal

    nw_u_avgr=nw_u_sumr/nw_u_count
    nw_u_avgg=nw_u_sumg/nw_u_count
    nw_u_avgb=nw_u_sumb/nw_u_count
    nw_l_avgr=nw_l_sumr/nw_l_count
    nw_l_avgg=nw_l_sumg/nw_l_count
    nw_l_avgb=nw_l_sumb/nw_l_count
    sw_u_avgr=sw_u_sumr/sw_u_count
    sw_u_avgg=sw_u_sumg/sw_u_count
    sw_u_avgb=sw_u_sumb/sw_u_count
    sw_l_avgr=sw_l_sumr/sw_l_count
    sw_l_avgg=sw_l_sumg/sw_l_count
    sw_l_avgb=sw_l_sumb/sw_l_count

    nw_u_count=0
    nw_u_sumdr=0
    nw_u_sumdg=0
    nw_u_sumdb=0
    nw_l_count=0
    nw_l_sumdr=0
    nw_l_sumdg=0
    nw_l_sumdb=0
    sw_u_count=0
    sw_u_sumdr=0
    sw_u_sumdg=0
    sw_u_sumdb=0
    sw_l_count=0
    sw_l_sumdr=0
    sw_l_sumdg=0
    sw_l_sumdb=0

    for sx in range(isx1,isx2+1):
        for sy in range(isy1,isy2+1):
            # nx and ny are the offsets inside this square
            nx=sx-isx1
            ny=sy-isy1
            # Calculate the y for the NW diagonal
            diag_nw_ny=int(round(nx*diag_slope))
            # Calculate the y for the SW diagonal
            diag_sw_ny=(diag_h-1)-diag_nw_ny

            (b,g,r)=gbscreen.get_pixel(sx,sy)
            r=int(r)
            g=int(g)
            b=int(b)

            if ny < diag_nw_ny:
                # This is the upper part of the NW diagonal
                dr=abs(r-nw_u_avgr)
                dg=abs(g-nw_u_avgg)
                db=abs(b-nw_u_avgb)
                nw_u_sumdr+=dr
                nw_u_sumdg+=dg
                nw_u_sumdb+=db
                nw_u_count+=1
            elif ny > diag_nw_ny:
                # This is the lower part of the NW diagonal
                dr=abs(r-nw_l_avgr)
                dg=abs(g-nw_l_avgg)
                db=abs(b-nw_l_avgb)
                nw_l_sumdr+=dr
                nw_l_sumdg+=dg
                nw_l_sumdb+=db
                nw_l_count+=1
            # else don't evaluate pixels on the diagonal

            if ny < diag_sw_ny:
                # This is the upper part of the SW diagonal
                dr=abs(r-sw_u_avgr)
                dg=abs(g-sw_u_avgg)
                db=abs(b-sw_u_avgb)
                sw_u_sumdr+=dr
                sw_u_sumdg+=dg
                sw_u_sumdb+=db
                sw_u_count+=1
            elif ny > diag_sw_ny:
                # This is the lower part of the SW diagonal
                dr=abs(r-sw_l_avgr)
                dg=abs(g-sw_l_avgg)
                db=abs(b-sw_l_avgb)
                sw_l_sumdr+=dr
                sw_l_sumdg+=dg
                sw_l_sumdb+=db
                sw_l_count+=1
            # else don't evaluate pixels on the diagonal

    nw_u_avgdr=nw_u_sumdr/nw_u_count
    nw_u_avgdg=nw_u_sumdg/nw_u_count
    nw_u_avgdb=nw_u_sumdb/nw_u_count
    nw_u_avg=(nw_u_avgdr+nw_u_avgdg+nw_u_avgdb)/3
    nw_l_avgdr=nw_l_sumdr/nw_l_count
    nw_l_avgdg=nw_l_sumdg/nw_l_count
    nw_l_avgdb=nw_l_sumdb/nw_l_count
    nw_l_avg=(nw_l_avgdr+nw_l_avgdg+nw_l_avgdb)/3
    sw_u_avgdr=sw_u_sumdr/sw_u_count
    sw_u_avgdg=sw_u_sumdg/sw_u_count
    sw_u_avgdb=sw_u_sumdb/sw_u_count
    sw_u_avg=(sw_u_avgdr+sw_u_avgdg+sw_u_avgdb)/3
    sw_l_avgdr=sw_l_sumdr/sw_l_count
    sw_l_avgdg=sw_l_sumdg/sw_l_count
    sw_l_avgdb=sw_l_sumdb/sw_l_count
    sw_l_avg=(sw_l_avgdr+sw_l_avgdg+sw_l_avgdb)/3

    # Generate scores for the diagonals. Lower is better.

    nw_avg=(nw_u_avg+nw_l_avg)/2
    sw_avg=(sw_u_avg+sw_l_avg)/2

    if nw_avg <= sw_avg:
        score=nw_avg/(avg+0.000001)
    else:
        score=sw_avg/(avg+0.000001)

    maybe_diagonal=[score,nw_avg,sw_avg,avg,nw_u_avgr,nw_u_avgg,nw_u_avgb,nw_l_avgr,nw_l_avgg,nw_l_avgb,sw_u_avgr,sw_u_avgg,sw_u_avgb,sw_l_avgr,sw_l_avgg,sw_l_avgb,isx1,isy1,isx2,isy2]
    print("diagonal",maybe_diagonal)

    #gbstate.map2maybediagonals.append(maybe_diagonal)

    # yyy
    if score < 0.9:
        print("diaginfo 2")
        if nw_avg <= sw_avg:
            # A diagonal starting at nw
            print("nw",nw_u_avgr,nw_u_avgg,nw_u_avgb)
            maptype_u=color_to_maptype(nw_u_avgr,nw_u_avgg,nw_u_avgb)
            print("m_u",maptype_u)
            if maptype_diagonal_is_allowed(maptype_u):
                print("allowed 1",nw_l_avgr,nw_l_avgg,nw_l_avgb)
                maptype_l=color_to_maptype(nw_l_avgr,nw_l_avgg,nw_l_avgb)
                print("m_l",maptype_l)
                if maptype_diagonal_is_allowed(maptype_l):
                    print("allowed 2")
                    # The upper and lower triangle colors look reasonable.
                    if maptype_u != maptype_l:
                        print("different")
                        m2=gbstate.mainmap[mx][my]
                        m2.phonemap2=MapTypeDiagonalNW
                        m2.diagonal0=maptype_u
                        m2.diagonal1=maptype_l
                        diaginfo=[isx1,isy1,isx2,isy2]
                        gbstate.map2diagonals.append(diaginfo)
                        return
        else:
            # A diagonal starting at sw
            print("sw",sw_u_avgr,sw_u_avgg,sw_u_avgb)
            maptype_u=color_to_maptype(sw_u_avgr,sw_u_avgg,sw_u_avgb)
            print("m_u",maptype_u)
            if maptype_diagonal_is_allowed(maptype_u):
                print("allowed 1",sw_l_avgr,sw_l_avgg,sw_l_avgb)
                maptype_l=color_to_maptype(sw_l_avgr,sw_l_avgg,sw_l_avgb)
                print("m_l",maptype_l)
                if maptype_diagonal_is_allowed(maptype_l):
                    print("allowed 2")
                    # The upper and lower triangle colors look reasonable.
                    if maptype_u != maptype_l:
                        print("different")
                        m2=gbstate.mainmap[mx][my]
                        m2.phonemap2=MapTypeDiagonalSW
                        m2.diagonal0=maptype_u
                        m2.diagonal1=maptype_l
                        diaginfo=[isx1,isy2,isx2,isy1]
                        gbstate.map2diagonals.append(diaginfo)
                        return

    gbstate.map2maybediagonals.append(maybe_diagonal)

    ignore_me=[isx1,isy1]
    if ignore_me in gbdata.tmp_ignore:
        print("ignore this",ignore_me)
        return

    gbstate.map2stats.append(entry)

    return

def find_minimum_index(a,i,width):
    imin=i
    vmin=a[i]
    low=i-width
    high=i+width
    for j in range(low,high+1):
        print(j)
        if vmin > a[j]:
            imin=j
            vmin=a[j]
    return imin

def color_to_maptype(avgr,avgg,avgb):
    #MapTypeUnknown=0
    #MapTypeWater=1
    #MapTypeRock=2
    #MapTypeGrass0=3
    #MapTypeGrass1=4
    #MapTypeGrass2=5
    #MapTypeSand=6
    #MapTypeDock=7
    #MapTypeDirt=8
    #MapTypePlaza=9
    #MapTypeJunk=10
    if gbscreen.color_match_rgb_array_list2(avgr,avgg,avgb,gbdata.phonemap2_color_junk):
        return MapTypeJunk
    if gbscreen.color_match_rgb_array_list2(avgr,avgg,avgb,gbdata.phonemap2_color_water):
        return MapTypeWater
    if gbscreen.color_match_rgb_array_list2(avgr,avgg,avgb,gbdata.phonemap2_color_rock):
        return MapTypeRock
    if gbscreen.color_match_rgb_array_list2(avgr,avgg,avgb,gbdata.phonemap2_color_grass0):
        return MapTypeGrass0
    if gbscreen.color_match_rgb_array_list2(avgr,avgg,avgb,gbdata.phonemap2_color_grass1):
        return MapTypeGrass1
    if gbscreen.color_match_rgb_array_list2(avgr,avgg,avgb,gbdata.phonemap2_color_grass2):
        return MapTypeGrass2
    if gbscreen.color_match_rgb_array_list2(avgr,avgg,avgb,gbdata.phonemap2_color_sand):
        return MapTypeSand
    if gbscreen.color_match_rgb_array_list2(avgr,avgg,avgb,gbdata.phonemap2_color_dock):
        return MapTypeDock
    if gbscreen.color_match_rgb_array_list2(avgr,avgg,avgb,gbdata.phonemap2_color_dirt):
        return MapTypeDirt
    if gbscreen.color_match_rgb_array_list2(avgr,avgg,avgb,gbdata.phonemap2_color_plaza):
        return MapTypePlaza
    return None

def maptype_diagonal_is_allowed(maptype):
    if maptype is None:
        return False
    if maptype is MapTypeJunk:
        return False
    #if maptype is MapTypePlaza:
    #    return False
    return True
