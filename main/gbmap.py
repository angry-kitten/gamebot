#
# Copyright 2021-2022 by angry-kitten
# Objects for working with the map.
#

import time, math
import colorsys
import numpy
import cv2
import gbdata
import gbstate
import gbscreen
import gbdisplay
import gbdijkstra
import gblogfile
import threadmanager

icons=[]

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
MapTypeBuilding=13
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
    'Dirt':  [MapTypeDirt, 'D'],
    'Plaza':  [MapTypePlaza, 'P'],
    'Junk':  [MapTypeJunk, 'J'],
    'Building':  [MapTypeBuilding, 'B'],
}

maptype_rev={}
for key in maptypes:
    maptype_rev[maptypes[key][0]]=[key,maptypes[key][1]]

class MapSquare:
    """MapSquare Object"""

    def __init__(self):
        self.objstruction_status=ObUnknown
        self.phonemap2=MapTypeUnknown
        self.diagonal0=MapTypeUnknown  # upper left or upper right
        self.diagonal1=MapTypeUnknown  # lower left or lower right
        self.dijkstra=[]
        self.dijkstra_distance=-1
        self.dijkstra_prev=-1
        self.dijkstra_new=[]
        self.r=0
        self.g=0
        self.b=0
        self.h=0
        self.s=0
        self.v=0
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

def is_valid_location(mx,my):
    if mx < 0:
        return False
    if mx >= gbdata.map_width:
        return False
    if my < 0:
        return False
    if my >= gbdata.map_height:
        return False
    return True

def map_level(mx,my):
    if not is_valid_location(mx,my):
        return None
    n=gbstate.mainmap[mx][my]
    t=n.phonemap2
    if t == MapTypeUnknown:
        return 0
    if t == MapTypeRock:
        return 0
    if t == MapTypeGrass0:
        return 0
    if t == MapTypeGrass1:
        return 1
    if t == MapTypeGrass2:
        return 2
    if t == MapTypeSand:
        return 0
    if t == MapTypeDock:
        return 0
    if t == MapTypeDirt:
        return 0
    if t == MapTypePlaza:
        return 0
    return None

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
    ep=node_equivalent_type(n)

    if ep == MapTypeGrass0:
        return False
    if ep == MapTypeGrass1:
        return False
    if ep == MapTypeGrass2:
        return False

    if ep == MapTypeUnknown:
        return False
    if ep == MapTypeWater:
        return True
    if ep == MapTypeDock:
        return True
    if ep == MapTypeDiagonalNW:
        return True
    if ep == MapTypeDiagonalSW:
        return True
    if ep == MapTypeBuilding:
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

def is_grass(typeid):
    if typeid == MapTypeGrass0:
        return True
    if typeid == MapTypeGrass1:
        return True
    if typeid == MapTypeGrass2:
        return True
    return False

    # Return equvalent types for things at the same level.
def node_equivalent_type(n):
    atype=n.phonemap2
    if MapTypeGrass2 == atype:
        return MapTypeGrass2
    if MapTypeGrass1 == atype:
        return MapTypeGrass1
    if MapTypeGrass0 == atype:
        return MapTypeGrass0
    if MapTypeRock == atype:
        return MapTypeGrass0
    if MapTypeSand == atype:
        return MapTypeGrass0
    if MapTypePlaza == atype:
        return MapTypeGrass0
    if MapTypeDiagonalNW == atype or MapTypeDiagonalSW == atype:
        a=n.diagonal0
        b=n.diagonal1
        if MapTypeGrass2 == a:
            return atype
        if MapTypeGrass1 == a:
            return atype
        if MapTypeGrass0 == a:
            if MapTypeRock == b:
                return MapTypeGrass0
            if MapTypeSand == b:
                return MapTypeGrass0
            if MapTypePlaza == b:
                return MapTypeGrass0
            return atype
        if MapTypeGrass2 == b:
            return atype
        if MapTypeGrass1 == b:
            return atype
        if MapTypeGrass0 == b:
            if MapTypeRock == a:
                return MapTypeGrass0
            if MapTypeSand == a:
                return MapTypeGrass0
            if MapTypePlaza == a:
                return MapTypeGrass0
            return atype
    return atype

def gather_phonemap_squares():
    print("gather_phonemap_squares")

    # Gather map statistics.
    gbstate.map2stats=[]
    gbstate.map2maybediagonals=[]
    gbstate.map2diagonals=[]
    sy1=int(round(gbdata.phonemap_origin_y))
    sy2=int(round(gbdata.phonemap_origin_y+gbdata.map_height*gbdata.phonemap_square_spacing))

    # Gather info to collect color data.
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

            process_phonemap_square1(mx,my,isx1,isx2,isy1,isy2)

    build_graph_data()

    # Make another pass that uses the color data.
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

            process_phonemap_square2(mx,my,isx1,isx2,isy1,isy2)


    # Sort and display the stats.

    # Sort by the first element in the entry array, avg.
    #print("stats")
    #sstats=sorted(gbstate.map2stats, key=lambda entry: entry[0])
    #for e in sstats:
    #    print(e)

    #print("maybe diagonals")
    #sdiagonals=sorted(gbstate.map2maybediagonals, key=lambda entry: entry[0])
    #for e in sdiagonals:
    #    print(e)

    return

def gather_phonemap2():
    print("gather_phonemap2")
    if gbstate.mainmap is None:
        init_map()

    if gbstate.building_info_player_house is None:
        locate_player_house()

    tnow=time.monotonic()
    if gbstate.mainmap_latest_update != 0:
        telapsed=tnow-gbstate.mainmap_latest_update
        if gbstate.mainmap_update_count <= gbdata.mainmap_update_fast_limit:
            if telapsed < gbdata.mainmap_update_fast_rate:
                return
        else:
            if telapsed < gbdata.mainmap_update_slow_rate:
                return
    gbstate.mainmap_latest_update=tnow
    gbstate.mainmap_update_count+=1

    gather_phonemap_squares()

    locate_buildings()

    locate_player_house()

    gbstate.map_is_gathered=True

    gbdijkstra.trigger_buildgraph()

    if gbstate.drawn_on is not None:
        cv2.imwrite('gather.png',gbstate.drawn_on) #pylint: disable=no-member

    return

def ignore_pin(sx,sy):
    if sx is None:
        print("E sx is None")
        return False
    if sy is None:
        print("E sy is None")
        return False
    if gbstate.phonemap_pin_box_sx1 is None:
        print("E phonemap_pin_box_sx1 is None")
        return False

    if sx < gbstate.phonemap_pin_box_sx1:
        return False
    if sx > gbstate.phonemap_pin_box_sx2:
        return False
    if sy < gbstate.phonemap_pin_box_sy1:
        return False
    if sy > gbstate.phonemap_pin_box_sy2:
        return False
    return True

    # integer rgb to hsv
def i_rgb_to_hsv(r,g,b):
    fr=r/255
    fg=g/255
    fb=b/255
    (h,s,v)=colorsys.rgb_to_hsv(fr,fg,fb)
    h2=int(round(h*255))
    s2=int(round(s*255))
    v2=int(round(v*255))
    return (h2,s2,v2)

    # floating point rgb to hsv
def fp_rgb_to_hsv(r,g,b):
    fr=r/255
    fg=g/255
    fb=b/255
    (h,s,v)=colorsys.rgb_to_hsv(fr,fg,fb)
    h2=h*255
    s2=s*255
    v2=v*255
    return (h2,s2,v2)

def scale_graph(g):
    maxg=g[0]
    for v in g:
        if v > maxg:
            maxg=v
    if maxg < 1:
        maxg=1
    for i in range(len(g)):
        v=g[i]
        v2=int(round((255*v)/maxg))
        g[i]=v2
    return

def is_maxima(g,i):
    l=len(g)
    if i < 0:
        return False
    if i >= l:
        return False
    v=g[i]
    j=i-1
    while j >= 0:
        if g[j] > v:
            return False
        if g[j] < v:
            break
        j-=1
    j=i+1
    while j < l:
        if g[j] > v:
            return False
        if g[j] < v:
            break
        j+=1
    return True

def generate_maxima(g):
    maxima=[]
    l=len(g)
    if l < 1:
        return maxima
    for i in range(l):
        if is_maxima(g,i):
            maxima.append((g[i],i))
    maxima.sort(reverse=True)
    return maxima

def average_halfwindow(g,halfwindow,i):
    l=len(g)
    low=i-halfwindow
    high=i+halfwindow
    if low < 0:
        low=0
    if high >= l:
        high=l-1
    count=(high-low)+1
    gsum=0
    for j in range(low,high+1):
        gsum+=g[j]
    av=gsum/count
    return av

def smooth_graph(g,halfwindow):
    s=[]
    l=len(g)
    for i in range(l):
        s.append(average_halfwindow(g,halfwindow,i))
    return s

def highest_peak_near(e_array,maxima):
    l=len(maxima)
    if l < 1:
        return None
    best_i=None
    best_d=None
    best_p=None
    e=e_array[0]
    for m in maxima:
        (p,i)=m
        d=abs(e-i)
        if best_i is None:
            best_i=i
            best_d=d
            best_p=p
        elif d == best_d:
            if best_p < p:
                best_i=i
                best_d=d
                best_p=p
        elif d < best_d:
            best_i=i
            best_d=d
            best_p=p
    rv=e_array.copy()
    rv[0]=best_i
    return rv

def log_hsv(a,name):
    gblogfile.log(f'{name}\n')
    for e in a:
        (h,s,v)=i_rgb_to_hsv(e[0],e[1],e[2])
        gblogfile.log(f'{h} {s} {v} {e[0]} {e[1]} {e[2]}\n')
    return

    # Convert floating point to integer and bound to 0-255
def round_and_bound(fpv):
    iv=max(0,min(255,int(round(fpv))))
    return iv

def build_graph_data():
    gbstate.h_graph=[0 for i in range(256)]
    gbstate.s_graph=[0 for i in range(256)]
    gbstate.v_graph=[0 for i in range(256)]
    for my in range(gbdata.map_height):
        for mx in range(gbdata.map_width):
            me=gbstate.mainmap[mx][my]
            i_h=round_and_bound(me.h)
            i_s=round_and_bound(me.s)
            i_v=round_and_bound(me.v)
            gbstate.h_graph[i_h]+=1
            gbstate.s_graph[i_s]+=1
            gbstate.v_graph[i_v]+=1
    scale_graph(gbstate.h_graph)
    scale_graph(gbstate.s_graph)
    scale_graph(gbstate.v_graph)
    gbstate.h_graph_s=smooth_graph(gbstate.h_graph,2)
    gbstate.s_graph_s=smooth_graph(gbstate.s_graph,2)
    gbstate.v_graph_s=smooth_graph(gbstate.v_graph,2)

    gbstate.h_maxima=generate_maxima(gbstate.h_graph)
    gbstate.s_maxima=generate_maxima(gbstate.s_graph)
    gbstate.v_maxima=generate_maxima(gbstate.v_graph)
    gblogfile.log('h_maxima\n')
    for e in gbstate.h_maxima:
        gblogfile.log(f'{e}\n')
    gblogfile.log('s_maxima\n')
    for e in gbstate.s_maxima:
        gblogfile.log(f'{e}\n')
    gblogfile.log('v_maxima\n')
    for e in gbstate.v_maxima:
        gblogfile.log(f'{e}\n')

    gbstate.h_p1=highest_peak_near(gbdata.h_p1_e,gbstate.h_maxima)
    gbstate.h_p2a=highest_peak_near(gbdata.h_p2a_e,gbstate.h_maxima)
    gbstate.h_p2b=highest_peak_near(gbdata.h_p2b_e,gbstate.h_maxima)
    gbstate.h_p3=highest_peak_near(gbdata.h_p3_e,gbstate.h_maxima)
    gbstate.h_p4=highest_peak_near(gbdata.h_p4_e,gbstate.h_maxima)
    gbstate.h_p5=highest_peak_near(gbdata.h_p5_e,gbstate.h_maxima)
    gbstate.h_p6=highest_peak_near(gbdata.h_p6_e,gbstate.h_maxima)
    gbstate.h_p7=highest_peak_near(gbdata.h_p7_e,gbstate.h_maxima)
    gbstate.h_p8=highest_peak_near(gbdata.h_p8_e,gbstate.h_maxima)
    gbstate.h_p9=highest_peak_near(gbdata.h_p9_e,gbstate.h_maxima)

    gbstate.s_p1=highest_peak_near(gbdata.s_p1_e,gbstate.s_maxima)
    gbstate.s_p2=highest_peak_near(gbdata.s_p2_e,gbstate.s_maxima)
    gbstate.s_p3=highest_peak_near(gbdata.s_p3_e,gbstate.s_maxima)

    gbstate.v_p1=highest_peak_near(gbdata.v_p1_e,gbstate.v_maxima)
    gbstate.v_p2=highest_peak_near(gbdata.v_p2_e,gbstate.v_maxima)
    gbstate.v_p3=highest_peak_near(gbdata.v_p3_e,gbstate.v_maxima)
    gbstate.v_p4=highest_peak_near(gbdata.v_p4_e,gbstate.v_maxima)
    gbstate.v_p5=highest_peak_near(gbdata.v_p5_e,gbstate.v_maxima)
    gbstate.v_p6=highest_peak_near(gbdata.v_p6_e,gbstate.v_maxima)
    gbstate.v_p7=highest_peak_near(gbdata.v_p7_e,gbstate.v_maxima)
    gbstate.v_p8=highest_peak_near(gbdata.v_p8_e,gbstate.v_maxima)
    gbstate.v_p9=highest_peak_near(gbdata.v_p9_e,gbstate.v_maxima)
    gbstate.v_p10=highest_peak_near(gbdata.v_p10_e,gbstate.v_maxima)

    log_hsv(gbdata.pin_color_list,'pin')
    log_hsv(gbdata.player_house_colors,'house')

                # h_p1 v_p1 water
                # h_p1 v_p2 nothing
                # h_p1 v_p3 nothing
                # h_p2 v_p1 nothing
                # h_p2 v_p2 nothing
                # h_p2 v_p3 grass0
                # h_p3 v_p1 nothing
                # h_p3 v_p2 sand
                # h_p3 v_p3 nothing
                # h_p2 v_p4 grass1
                # h_p2 v_p5 not sure, 2 pixels, maybe grass0
                # h_p2 v_p6 grass1
                # h_p2 v_p7 nothing
                # h_p2 v_p8 nothing
                # h_p2 v_p9 nothing
                # h_p4 v_p1 nothing
                # h_p4 v_p2 nothing
                # h_p4 v_p3 nothing
                # h_p4 v_p4 nothing
                # h_p4 v_p5 weak grass0
                # h_p4 v_p6 nothing
                # h_p4 v_p7 grass2
                # h_p4 v_p8 not sure, 2 pixels, maybe grass2
                # h_p4 v_p9 nothing
                # h_p5 v_p9 plaza
                # h_p6 v_p1 nothing
                # h_p6 v_p2 nothing
                # h_p6 v_p3 nothing
                # h_p6 v_p4 nothing
                # h_p6 v_p5 nothing
                # h_p6 v_p6 nothing
                # h_p6 v_p7 nothing
                # h_p6 v_p8 nothing
                # h_p6 v_p9 nothing
                # h_p6 v_p10 rock
    gbstate.hvtt=[]
    gbstate.hvtt.append((gbstate.h_p1,gbstate.v_p1,MapTypeWater,'water'))
    gbstate.hvtt.append((gbstate.h_p2a,gbstate.v_p3,MapTypeGrass0,'grass0'))
    gbstate.hvtt.append((gbstate.h_p3,gbstate.v_p2,MapTypeSand,'sand'))
    gbstate.hvtt.append((gbstate.h_p2b,gbstate.v_p4,MapTypeGrass1,'grass1'))
    gbstate.hvtt.append((gbstate.h_p4,gbstate.v_p7,MapTypeGrass2,'grass2'))
    gbstate.hvtt.append((gbstate.h_p5,gbstate.v_p9,MapTypePlaza,'plaza'))
    gbstate.hvtt.append((gbstate.h_p6,gbstate.v_p10,MapTypeRock,'rock'))
    gbstate.hvtt.append((gbstate.h_p8,gbstate.v_p6,MapTypeDock,'dock'))
    return

def hv_distance(h1,v1,h2,v2):
    dh=h1-h2
    dv=v1-v2
    d=math.sqrt(dh*dh+dv*dv)
    return d

def hv_to_type_1(h,v):
    if gbstate.hvtt is None:
        return None
    #for e in gbstate.hvtt:
    #    (h2,v2,t)=e
    #    if h == h2:
    #        if v == v2:
    #            return t
    best_d=None
    best_t=None
    for e in gbstate.hvtt:
        (h2,v2,t)=e
        d=hv_distance(h,v,h2,v2)
        if best_d is None:
            best_d=d
            best_t=t
        elif d < best_d:
            best_d=d
            best_t=t
    return best_t

def hsv_to_type_2(h,s,v):
    if gbstate.hvtt is None:
        return None
    best_d=None
    best_t=None
    for e in gbstate.hvtt:
        (h2,v2,t)=e
        h3=h2[0]
        v3=v2[0]
        if h < (h3-h2[1]):
            continue
        if h > (h3+h2[2]):
            continue
        if v < (v3-v2[1]):
            continue
        if v > (v3+v2[2]):
            continue
        d=hv_distance(h,v,h3,v3)
        if best_d is None:
            best_d=d
            best_t=t
        elif d < best_d:
            best_d=d
            best_t=t
    if best_d is None:
        gblogfile.log(f'not matched {h} {s} {v}')
    return best_t

def hsv_in_range(h,s,v,j):
    e=gbstate.hvtt[j]
    (h2,v2,t,n)=e
    h3=h2[0]
    v3=v2[0]
    brv=True
    lim=h3-h2[1]
    if h < lim:
        d=lim-h
        gblogfile.log(f'not matched 2 {d:6.2f} {h:6.2f} {s:6.2f} {v:6.2f} {j} {n} -h')
        brv=False
    lim=h3+h2[2]
    if h > lim:
        d=h-lim
        gblogfile.log(f'not matched 2 {d:6.2f} {h:6.2f} {s:6.2f} {v:6.2f} {j} {n} +h')
        brv=False
    lim=v3-v2[1]
    if v < lim:
        d=lim-v
        gblogfile.log(f'not matched 2 {d:6.2f} {h:6.2f} {s:6.2f} {v:6.2f} {j} {n} -v')
        brv=False
    lim=v3+v2[2]
    if v > lim:
        d=v-lim
        gblogfile.log(f'not matched 2 {d:6.2f} {h:6.2f} {s:6.2f} {v:6.2f} {j} {n} +v')
        brv=False
    return brv

def hsv_to_type(h,s,v):
    if gbstate.hvtt is None:
        return None
    best_d=None
    best_j=None
    l=len(gbstate.hvtt)
    for j in range(l):
        e=gbstate.hvtt[j]
        (h2,v2,t,n)=e
        h3=h2[0]
        v3=v2[0]
        d=hv_distance(h,v,h3,v3)
        if best_d is None:
            best_d=d
            best_j=j
        elif d < best_d:
            best_d=d
            best_j=j
    if best_d is None:
        gblogfile.log(f'not matched 1 {h:6.2f} {s:6.2f} {v:6.2f}')
        return None
    if hsv_in_range(h,s,v,best_j):
        e=gbstate.hvtt[best_j]
        (h2,v2,t,n)=e
        return t
    return None

def rgb_to_hsv_to_type(r,g,b):
    (h,s,v)=fp_rgb_to_hsv(r,g,b)
    t=hsv_to_type(h,s,v)
    return t

    # Gather info to collect color data in pass 1.
def process_phonemap_square1(mx,my,isx1,isx2,isy1,isy2):
    # Find the average first.
    count=0
    sumr=0
    sumg=0
    sumb=0

    if ignore_pin(isx1,isy1):
        return
    if ignore_pin(isx2,isy1):
        return
    if ignore_pin(isx1,isy2):
        return
    if ignore_pin(isx2,isy2):
        return

    for sx in range(isx1,isx2+1):
        for sy in range(isy1,isy2+1):
            (b,g,r)=gbscreen.get_pixel(sx,sy)
            r2=int(r)
            g2=int(g)
            b2=int(b)
            sumr+=r2
            sumg+=g2
            sumb+=b2
            count+=1
    avgr=sumr/count
    avgg=sumg/count
    avgb=sumb/count
    me=gbstate.mainmap[mx][my]
    me.r=avgr
    me.g=avgg
    me.b=avgb
    (h,s,v)=fp_rgb_to_hsv(me.r,me.g,me.b)
    me.h=h
    me.s=s
    me.v=v

    return

    # Make another pass that uses the color data in pass 2.
def process_phonemap_square2(mx,my,isx1,isx2,isy1,isy2):

    if ignore_pin(isx1,isy1):
        return
    if ignore_pin(isx2,isy1):
        return
    if ignore_pin(isx1,isy2):
        return
    if ignore_pin(isx2,isy2):
        return

    # Use the averages collected in pass 1.
    me=gbstate.mainmap[mx][my]
    avgr=me.r
    avgg=me.g
    avgb=me.b

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
        #mt=color_to_maptype(avgr,avgg,avgb)
        mt=hsv_to_type(me.h,me.s,me.v)
        if mt is not None:
            if mt is not MapTypeJunk:
                gbstate.mainmap[mx][my].phonemap2=mt
            return
        #else:
        #    log_closest_type(avgr,avgg,avgb)

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
    #print("diagonal",maybe_diagonal)

    #gbstate.map2maybediagonals.append(maybe_diagonal)

    # yyy
    if score < 0.9:
        #print("diaginfo 2")
        if nw_avg <= sw_avg:
            # A diagonal starting at nw
            #print("nw",nw_u_avgr,nw_u_avgg,nw_u_avgb)
            #maptype_u=color_to_maptype(nw_u_avgr,nw_u_avgg,nw_u_avgb)
            maptype_u=rgb_to_hsv_to_type(nw_u_avgr,nw_u_avgg,nw_u_avgb)
            #print("m_u",maptype_u)
            if maptype_diagonal_is_allowed(maptype_u):
                #print("allowed 1",nw_l_avgr,nw_l_avgg,nw_l_avgb)
                #maptype_l=color_to_maptype(nw_l_avgr,nw_l_avgg,nw_l_avgb)
                maptype_l=rgb_to_hsv_to_type(nw_l_avgr,nw_l_avgg,nw_l_avgb)
                #print("m_l",maptype_l)
                if maptype_diagonal_is_allowed(maptype_l):
                    #print("allowed 2")
                    # The upper and lower triangle colors look reasonable.
                    if maptype_u != maptype_l:
                        #print("different")
                        m2=gbstate.mainmap[mx][my]
                        m2.phonemap2=MapTypeDiagonalNW
                        m2.diagonal0=maptype_u
                        m2.diagonal1=maptype_l
                        diaginfo=[isx1,isy1,isx2,isy2]
                        gbstate.map2diagonals.append(diaginfo)
                        return
        else:
            # A diagonal starting at sw
            #print("sw",sw_u_avgr,sw_u_avgg,sw_u_avgb)
            #maptype_u=color_to_maptype(sw_u_avgr,sw_u_avgg,sw_u_avgb)
            maptype_u=rgb_to_hsv_to_type(sw_u_avgr,sw_u_avgg,sw_u_avgb)
            #print("m_u",maptype_u)
            if maptype_diagonal_is_allowed(maptype_u):
                #print("allowed 1",sw_l_avgr,sw_l_avgg,sw_l_avgb)
                #maptype_l=color_to_maptype(sw_l_avgr,sw_l_avgg,sw_l_avgb)
                maptype_l=rgb_to_hsv_to_type(sw_l_avgr,sw_l_avgg,sw_l_avgb)
                #print("m_l",maptype_l)
                if maptype_diagonal_is_allowed(maptype_l):
                    #print("allowed 2")
                    # The upper and lower triangle colors look reasonable.
                    if maptype_u != maptype_l:
                        #print("different")
                        m2=gbstate.mainmap[mx][my]
                        m2.phonemap2=MapTypeDiagonalSW
                        m2.diagonal0=maptype_u
                        m2.diagonal1=maptype_l
                        diaginfo=[isx1,isy2,isx2,isy1]
                        gbstate.map2diagonals.append(diaginfo)
                        return

    gbstate.map2maybediagonals.append(maybe_diagonal)


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

def log_closest_type(avgr,avgg,avgb):
    #gblogfile.log(f'close={best_close:9.4f} {best_name} {avgr} {avgg} {avgb}\n')
    return

def maptype_diagonal_is_allowed(maptype):
    if maptype is None:
        return False
    if maptype is MapTypeJunk:
        return False
    #if maptype is MapTypePlaza:
    #    return False
    return True

def locate_buildings():
    print("locate_buildings")
    # find gray circles
    search_w=gbdata.phonemap_right_close-gbdata.phonemap_left_close
    search_h=gbdata.phonemap_bottom_close-gbdata.phonemap_top_close
    for local_y in range(0,search_h,gbdata.phonemap_gray_search_y):
        pixel_y=gbdata.phonemap_top_close+local_y
        for local_x in range(0,search_w,gbdata.phonemap_gray_search_x):
            pixel_x=gbdata.phonemap_left_close+local_x
            if is_circle_gray(pixel_x,pixel_y):
                #print("found possible circle at",pixel_x,pixel_y)
                verify_circle(pixel_x,pixel_y)

    print("circles",gbstate.gray_circle_list)

    print("before gather_icons")
    # Gather the icons from inside the circles.
    gather_icons()

    print("icon len",len(icons))

    print("before match_icons")
    # Match the icons with known icons.
    match_icons()
    print("after match_icons")

    print("icon len",len(icons))

    return

def verify_player_house(sx,sy):
    print("verify_player_house")
    # find horizontal center.
    sx_left=sx
    for i in range(1,gbdata.player_house_max_width):
        t1sx=sx-i
        if not is_player_house_color(t1sx,sy):
            print("end on left")
            gbscreen.print_color_at(t1sx,sy)
            break
        sx_left=t1sx
    sx_right=sx
    for i in range(1,gbdata.player_house_max_width):
        t1sx=sx+i
        if not is_player_house_color(t1sx,sy):
            print("end on right")
            gbscreen.print_color_at(t1sx,sy)
            break
        sx_right=t1sx
    print("sx left right",sx_left,sx_right)
    center_sx=int(round((sx_left+sx_right)/2))

    # find vertical center.
    sy_top=sy
    for i in range(1,gbdata.player_house_max_height):
        t1sy=sy-i
        if not is_player_house_color(center_sx,t1sy):
            print("end on top")
            gbscreen.print_color_at(center_sx,t1sy)
            break
        sy_top=t1sy
    sy_bottom=sy
    for i in range(1,gbdata.player_house_max_height):
        t1sy=sy+i
        if not is_player_house_color(center_sx,t1sy):
            print("end on bottom")
            gbscreen.print_color_at(center_sx,t1sy)
            break
        sy_bottom=t1sy
    print("sy top bottom",sy_top,sy_bottom)
    center_sy=int(round((sy_top+sy_bottom)/2))

    # find horizontal center again.
    window_sy=center_sy+4
    sx_left=center_sx
    for i in range(1,gbdata.player_house_max_width):
        t1sx=center_sx-i
        if not is_player_house_color(t1sx,window_sy):
            print("end on left")
            gbscreen.print_color_at(t1sx,window_sy)
            break
        sx_left=t1sx
    sx_right=center_sx
    for i in range(1,gbdata.player_house_max_width):
        t1sx=center_sx+i
        if not is_player_house_color(t1sx,window_sy):
            print("end on right")
            gbscreen.print_color_at(t1sx,window_sy)
            break
        sx_right=t1sx
    print("sx left right",sx_left,sx_right)
    center_sx=int(round((sx_left+sx_right)/2))

    w=sx_right-sx_left
    h=sy_bottom-sy_top
    print("w h",w,h)

    if w < 20:
        print("too narrow")
        return False
    if h < 18:
        print("too short")
        return False

    gbstate.player_house_sx=center_sx
    gbstate.player_house_sy=center_sy

    set_building('player_house',center_sx,center_sy)

    return True

def locate_player_house():
    print("locate_player_house")
    gbstate.house_color_xy=[]
    # find player house colors
    search_w=gbdata.phonemap_right_close-gbdata.phonemap_left_close
    search_h=gbdata.phonemap_bottom_close-gbdata.phonemap_top_close
    for local_y in range(0,search_h,gbdata.phonemap_gray_search_y):
        pixel_y=gbdata.phonemap_top_close+local_y
        for local_x in range(0,search_w,gbdata.phonemap_gray_search_x):
            pixel_x=gbdata.phonemap_left_close+local_x
            if is_player_house_color(pixel_x,pixel_y):
                if verify_player_house(pixel_x,pixel_y):
                    return
                # YYY only do one now for debug
                return # YYY
    return

def verify_circle(start_sx,start_sy):
    #print("verify_circle",start_sx,start_sy)

    if is_already_found(start_sx,start_sy):
        #print("already found")
        return

    max_diameter=gbdata.phonemap_circle_diameter+4
    color=gbdata.phonemap_circle_gray
    # Step left and right looking for the edges.
    left_sx=gbscreen.locate_horizontal_extent(color,start_sy,start_sx,start_sx-max_diameter)
    right_sx=gbscreen.locate_horizontal_extent(color,start_sy,start_sx,start_sx+max_diameter)
    #print("left_sx",left_sx)
    #print("right_sx",right_sx)

    w=right_sx-left_sx
    #print("w",w)
    if w > (gbdata.phonemap_circle_diameter+4):
        # overlapping circles
        return

    center_sx=int(round((left_sx+right_sx)/2))
    #print("center_sx",center_sx)

    # Step up and down looking for the edges.
    top_sy=gbscreen.locate_vertical_extent(color,start_sx,start_sy,start_sy-max_diameter)
    bottom_sy=gbscreen.locate_vertical_extent(color,start_sx,start_sy,start_sy+max_diameter)

    #print("top_sy",top_sy)
    #print("bottom_sy",bottom_sy)

    h=bottom_sy-top_sy
    #print("h",h)
    if not gbscreen.match_within(h,gbdata.phonemap_circle_diameter,3):
        print("these are not the droids we are looking for")
        return

    center_sy=int(round((top_sy+bottom_sy)/2))
    #print("center_sy",center_sy)

    add_gray_circle(center_sx,center_sy)

    return

def add_gray_circle(center_sx,center_sy):
    # first see if it is already there
    for c in gbstate.gray_circle_list:
        if gbscreen.match_within(center_sx,c[0],3) and gbscreen.match_within(center_sy,c[1],3):
            # already there
            return
    gbstate.gray_circle_list.append([center_sx,center_sy])
    l=len(gbstate.gray_circle_list)
    #print("l",l)
    return

def is_already_found(start_sx,start_sy):
    radius=gbdata.phonemap_circle_diameter/2
    for c in gbstate.gray_circle_list:
        d=gbdisplay.calculate_distance(start_sx,start_sy,c[0],c[1])
        if d <= (radius+4):
            # already found
            return True
    return False

def gather_icons():
    global icons
    icons=[]
    radius=gbdata.phonemap_circle_diameter/2
    for c in gbstate.gray_circle_list:
        icon=gather_an_icon(c[0],c[1])
        whereicon=[c[0],c[1],icon]
        icons.append(whereicon)
    print("icon len",len(icons))
    return

def gather_an_icon(start_sx,start_sy):
    diameter=gbdata.phonemap_circle_diameter
    radius=int(round(diameter/2))
    sx1=start_sx-radius
    sy1=start_sy-radius
    icon=[0 for i in range(diameter*diameter)]
    for sy2 in range(0,diameter):
        for sx2 in range(0,diameter):
            sx=sx1+sx2
            sy=sy1+sy2
            i=(sy2*diameter)+sx2
            # only collect info inside the circle
            d=gbdisplay.calculate_distance(start_sx,start_sy,sx,sy)
            if d <= radius:
                if is_circle_icon(sx,sy):
                    icon[i]=1
    #print("icon",icon)
    #print_icon(icon)
    return icon

def print_icon(icon):
    diameter=gbdata.phonemap_circle_diameter
    print("icon=[")

    for sy in range(0,diameter):
        for sx in range(0,diameter):
            i=(sy*diameter)+sx
            v=icon[i]
            print(v,",",sep='',end='')
        print("")

    print("]")
    return

def match_icons():
    print("match_icons")
    global icons
    print("icon len",len(icons))
    for whereicon in icons:
        match_an_icon(whereicon)

    # These aren't needed any more.
    icons=[]
    return

def match_an_icon(whereicon):
    print("match_an_icon")
    best_co=None
    best_match=None
    for ni in gbdata.named_icons:
        #print(ni[0])
        co=do_icon_match(whereicon[2],ni[1])
        if best_co is None:
            best_co=co
            best_match=ni
        else:
            if best_co < co:
                best_co=co
                best_match=ni
    if best_co is not None:
        print("found match")
        print(best_match[0],"is at",whereicon[0],whereicon[1])
        set_building(best_match[0],whereicon[0],whereicon[1])
        return
    return

def do_icon_match(icon1,icon2):
    best_co=None
    off_by=1
    for offset_y in range(-off_by,off_by+1):
        for offset_x in range(-off_by,off_by+1):
            co=compare_icons_offsets(icon1,icon2,offset_x,offset_y)
            if best_co is None:
                best_co=co
            else:
                if best_co < co:
                    best_co=co
    return best_co

def compare_icons_offsets(icon1,icon2,ox,oy):
    i1=icon1.copy()
    i2=icon2.copy()
    # offsets ox, oy are how much to adjust icon1
    diameter=gbdata.phonemap_circle_diameter
    adjust=(diameter*oy)+ox
    if adjust < 0:
        # Chop off the beginning of icon1 and append
        # zeros to the end.
        n=-adjust
        i1=i1[n:]
        i1.extend([0 for j in range(n)])
    elif adjust > 0:
        # Chop off the end of icon1 and append
        # zeros to the beginning.
        n=adjust
        i1tmp=[0 for j in range(n)]
        i1tmp.extend(i1[0:-n])
        i1=i1tmp

    l1=len(i1)
    l2=len(i2)
    #print("l1 l2",l1,l2)
    co=compare_icons(i1,i2)
    #print("co",co)
    return co

def compare_icons(icon1,icon2):
    co=numpy.correlate(icon1,icon2)
    #print("co",co)
    return co

def set_building(name,sx,sy):
    # Calculate the map location given the screen location.
    #mx=int(round((sx-gbdata.phonemap_origin_x)/gbdata.phonemap_square_spacing))
    #my=int(round((sy-gbdata.phonemap_origin_y)/gbdata.phonemap_square_spacing))
    mx=(sx-gbdata.phonemap_origin_x)/gbdata.phonemap_square_spacing
    my=(sy-gbdata.phonemap_origin_y)/gbdata.phonemap_square_spacing

    w=4
    h=4

    # binfo is [name,centermx,centermy,doormx,doormy]
    if name == 'campsite':
        binfo=[name,mx,my,mx,my+2]
        gbstate.building_info_campsite=binfo
        w=4
        h=4
    elif name == 'museum':
        binfo=[name,mx,my,mx,my+2]
        print("museum",binfo)
        gbstate.building_info_museum=binfo
        w=7
        h=4
    elif name == 'cranny':
        binfo=[name,mx,my,mx,my+2]
        gbstate.building_info_cranny=binfo
        w=7
        h=4
    elif name == 'services':
        binfo=[name,mx,my,mx,my+2]
        gbstate.building_info_services=binfo
        # The tent is little. The building is larger.
        w=4
        h=2
    elif name == 'tailors':
        binfo=[name,mx,my,mx,my+2]
        gbstate.building_info_tailors=binfo
        w=5
        h=4
    elif name == 'airport':
        binfo=[name,mx,my,mx,my+2]
        gbstate.building_info_airport=binfo
        w=4
        h=4
    elif name == 'player_house':
        binfo=[name,mx,my,mx,my+2]
        print("player house",binfo)
        gbstate.building_info_player_house=binfo
        w=5
        h=4
    else:
        print("unknown building name")
        w=4
        h=4

    ulmx=int(round(mx-(w/2)))
    ulmy=int(round(my-(h/2)))

    for mx2 in range(w):
        for my2 in range(h):
            mx3=ulmx+mx2
            my3=ulmy+my2
            n=gbstate.mainmap[mx3][my3]
            n.phonemap2=MapTypeBuilding
    return

def is_circle_gray(pixel_x,pixel_y):
    pixel_x=int(round(pixel_x))
    pixel_y=int(round(pixel_y))
    if gbscreen.color_match_array(pixel_x,pixel_y,gbdata.phonemap_circle_gray,5):
        return True
    return False

def is_circle_icon(pixel_x,pixel_y):
    pixel_x=int(round(pixel_x))
    pixel_y=int(round(pixel_y))
    if gbscreen.color_match_array(pixel_x,pixel_y,gbdata.phonemap_circle_icon,2):
        return True
    return False

def is_player_house_color(pixel_x,pixel_y):
    pixel_x=int(round(pixel_x))
    pixel_y=int(round(pixel_y))
    if gbscreen.color_match_array_list(pixel_x,pixel_y,gbdata.player_house_colors,5):
        t=(pixel_x,pixel_y)
        if t not in gbstate.house_color_xy:
            gbstate.house_color_xy.append(t)
        return True
    return False

def init_gathermap():
    gbstate.gathermap_worker_thread=threadmanager.ThreadManager(gathermap_worker,"gathermap")
    return

def gathermap_worker():
    print("before gathermap_worker")

    gather_phonemap2()

    with gbstate.gathermap_worker_thread.data_lock:
        gbstate.gathermap_completed=True

    print("after gathermap_worker")
    return
