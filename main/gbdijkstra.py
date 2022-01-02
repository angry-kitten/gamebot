#
# Copyright 2021-2022 by angry-kitten
# Implement the Dijkstra shortest path algorithm for bot path planning.
#

import time
import numpy
import gbdata
import gbstate
import gbscreen
import gbdisplay
import gbdijkstra
import gbmap

def xy_to_index(mx,my):
    i=mx+(my*gbdata.map_width)
    return i

def index_to_xy(i):
    mx=i%gbdata.map_width
    my=int(i/gbdata.map_width)
    return (mx,my)

def node_from_index(i):
    (mx,my)=index_to_xy(i)
    n1=gbstate.mainmap[mx][my]
    return n1

def build_graph():
    print("build_graph")

    gbstate.dijkstra_waypoints=[]
    gbstate.dijkstra_walk_edges=[]
    gbstate.dijkstra_ladder_edges=[]
    gbstate.dijkstra_pole_edges=[]

    # Build the ladder graph parts first to make for easy
    # de-duplication.
    build_ladder_edges()

    # Build the pole graph parts first to make for easy
    # de-duplication.
    build_pole_edges()

    build_walk_edges()

    # Build the walk graph parts as the start of the main graph.
    build_main_graph()

    # Add the ladder and pole parts to the main graph.
    return

def path_plan(fmx,fmy,tmx,tmy):
    print("path_plan")
    fmx=int(round(fmx))
    fmy=int(round(fmy))
    tmx=int(round(tmx))
    tmy=int(round(tmy))

    gbstate.dijkstra_waypoints=[]

    node=gbstate.mainmap[fmx][fmy]
    if len(node.dijkstra) < 1:
        print("orphan map location")
        # Pick a nearby location and pretend it is the start.
        (new_fmx,new_fmy)=alternate_start(fmx,fmy)
        if new_fmx is None:
            print("no alternate found")
            return
        fmx=new_fmx
        fmy=new_fmy
        node=gbstate.mainmap[fmx][fmy]

    for mx in range(gbdata.map_width):
        for my in range(gbdata.map_height):
            node=gbstate.mainmap[mx][my]
            node.dijkstra_distance=-1

    node.dijkstra_distance=0
    queue=[]
    index=xy_to_index(fmx,fmy)
    queue.append(index)
    # Nominally all the unvisited nodes are in queue. But
    # queue really only contains tentative nodes.

    while len(queue) > 0:
        i1=node_with_min_distance(queue)
        queue.remove(i1)
        (mx,my)=index_to_xy(i1)
        if mx == tmx and my == tmy:
            print("found target")
            build_waypoint_list(i1)
            return
        n1=node_from_index(i1)

        for edge in n1.dijkstra:
            t=edge[2]
            if gbdata.dijkstra_pole_type == t:
                if not gbstate.inventory_has_pole:
                    continue
            if gbdata.dijkstra_ladder_type == t:
                if not gbstate.inventory_has_ladder:
                    continue
            i2=other_index(i1,edge)
            n2=node_from_index(i2)
            if n2.dijkstra_distance == -1 or i2 in queue:
                t=edge[2]
                d=type_to_distance(t)
                alt=n1.dijkstra_distance+d
                if n2.dijkstra_distance == -1:
                    n2.dijkstra_distance=alt
                    n2.dijkstra_prev=i1
                    queue.append(i2)
                elif alt < n2.dijkstra_distance:
                    n2.dijkstra_distance=alt
                    n2.dijkstra_prev=i1

    print("unreachable")
    return

def node_with_min_distance(queue):
    if len(queue) < 1:
        return None
    i1=queue[0]
    n1=node_from_index(i1)
    best_node_index=i1
    best_distance=n1.dijkstra_distance
    for i1 in queue:
        n1=node_from_index(i1)
        d=n1.dijkstra_distance
        if d < best_distance:
            best_node_index=i1
            best_distance=n1.dijkstra_distance
    return best_node_index

def build_waypoint_list(i1):
    gbstate.dijkstra_waypoints=[]
    while True:
        gbstate.dijkstra_waypoints.append(i1)
        n1=node_from_index(i1)
        if n1.dijkstra_distance == 0:
            break;
        i1=n1.dijkstra_prev
    print("dijkstra",gbstate.dijkstra_waypoints)
    return

def type_to_distance(t):
    # type to cost, really
    if gbdata.dijkstra_walk_type == t:
        return gbdata.dijkstra_walk_cost
    if gbdata.dijkstra_pole_type == t:
        return gbdata.dijkstra_pole_cost
    if gbdata.dijkstra_ladder_type == t:
        return gbdata.dijkstra_ladder_cost
    return 1

def other_index(i0,edge):
    (i1,i2,t)=edge
    if i0 != i1:
        return i1
    return i2

def alternate_start(mx1,my1):
    # Look at nearby squares.
    for dx in range(3):
        for dy in range(3):
            if dx == 1 and dy == 1:
                continue
            mx2=mx1+(dx-1)
            my2=my1+(dy-1)
            node=gbstate.mainmap[mx2][my2]
            if len(node.dijkstra) >= 1:
                return (mx2,my2)
    # Use brute force
    best_mx=None
    best_my=None
    best_distance=None
    for mx in range(gbdata.map_width):
        for my in range(gbdata.map_height):
            node=gbstate.mainmap[mx][my]
            if len(node.dijkstra) >= 1:
                d=gbdisplay.calculate_distance(mx1,mx2,mx,my)
                if best_distance is None:
                    best_mx=mx
                    best_my=my
                    best_distance=d
                elif d < best_distance:
                    best_mx=mx
                    best_my=my
                    best_distance=d
    return (best_mx,best_my)

def build_ladder_edges():
    print("build_ladder_edges")
    gbstate.dijkstra_ladder_edges=[]

    for mx in range(gbdata.map_width):
        for my in range(gbdata.map_height):
            identify_ladder_positions(mx,my)
    return

def identify_ladder_positions(mx,my):
    test_ladder_pair(mx,my,mx+1,my)
    test_ladder_pair(mx,my,mx,my+1)
    return

def test_ladder_pair(mx1,my1,mx2,my2):
    if not gbmap.is_valid_location(mx2,my2):
        return
    l1=gbmap.map_level(mx1,my1)
    if l1 is None:
        return
    l2=gbmap.map_level(mx2,my2)
    if l2 is None:
        return
    n1=xy_to_index(mx1,my1)
    n2=xy_to_index(mx2,my2)
    if 0 == l1:
        if 1 == l2:
            add_ladder_edge(n1,n2)
            return
        return
    if 1 == l1:
        if 0 == l2:
            add_ladder_edge(n1,n2)
            return
        if 2 == l2:
            add_ladder_edge(n1,n2)
            return
        return
    if 2 == l1:
        if 1 == l2:
            add_ladder_edge(n1,n2)
            return
        return
    return

def add_ladder_edge(n1,n2):
    if n1 > n2:
        add_ladder_edge(n2,n1)
        return
    edge=(n1,n2,gbdata.dijkstra_ladder_type)
    if edge in gbstate.dijkstra_ladder_edges:
        return
    gbstate.dijkstra_ladder_edges.append(edge)
    #print("ladder",gbstate.dijkstra_ladder_edges)
    return

def build_pole_edges():
    print("build_pole_edges")
    gbstate.dijkstra_pole_edges=[]

    for mx in range(gbdata.map_width):
        for my in range(gbdata.map_height):
            identify_pole_positions(mx,my)
    return

def identify_pole_positions(mx,my):
    test_pole_pair(mx,my,1,0)
    test_pole_pair(mx,my,0,1)
    return

def test_pole_pair(mx1,my1,dx,dy):
    l1=gbmap.map_level(mx1,my1)
    if l1 is None:
        return

    mx2=mx1+dx
    my2=my1+dy
    if not gbmap.is_valid_location(mx2,my2):
        return

    t2=gbstate.mainmap[mx2][my2].phonemap2
    if gbmap.MapTypeWater != t2:
        return

    #print("test_pole_pair",mx1,my1,dx,dy)
    if is_grass_sand_transition(mx1,my1,dx,dy):
        # Don't pole near a grass-sand transition.
        return

    # Pole distance 1 to 5. 1 is already known to be water
    # For a distance of 5, 0 is land, 1-4 is water, 5 is land.
    for j in range(2,6):
        mx2=mx1+(dx*j)
        my2=my1+(dy*j)
        if not gbmap.is_valid_location(mx2,my2):
            return
        t2=gbstate.mainmap[mx2][my2].phonemap2
        if gbmap.MapTypeWater == t2:
            continue
        # This position is not water. It is the potential
        # landing spot.
        if 2 == j:
            # too short
            # For a distance of 2, 0 is land, 1 is water, 2 is land.
            return
        l2=gbmap.map_level(mx2,my2)
        if l2 is None:
            return
        if l1 != l2:
            return
        if is_grass_sand_transition(mx2,my2,dx,dy):
            # Don't pole near a grass-sand transition.
            return
        n1=xy_to_index(mx1,my1)
        n2=xy_to_index(mx2,my2)
        add_pole_edge(n1,n2)

    return

def is_grass_sand_transition(mx1,my1,dx,dy):
    #print("is_grass_sand_transition",mx1,my1,dx,dy)
    if 0 != dx:
        dx2=0
        dy2=1
    elif 0 != dy:
        dx2=1
        dy2=0
    else:
        return False
    #print("dx2 dy2",dx2,dy2)

    if is_grass_sand_pair(mx1,my1,mx1+dx2,my1+dy2):
        return True
    if is_grass_sand_pair(mx1,my1,mx1-dx2,my1-dy2):
        return True
    return False

def is_grass_sand_pair(mx1,my1,mx2,my2):
    #print("is_grass_sand_pair",mx1,my1,mx2,my2)
    if not gbmap.is_valid_location(mx2,my2):
        return False
    t1=gbstate.mainmap[mx1][my1].phonemap2
    t2=gbstate.mainmap[mx2][my2].phonemap2
    #print("t1 t2",t1,t2)
    if gbmap.MapTypeGrass0 == t1:
        if gbmap.MapTypeSand == t2:
            #print("transition")
            return True
        return False
    if gbmap.MapTypeSand == t1:
        if gbmap.MapTypeGrass0 == t2:
            #print("transition")
            return True
        return False
    return False

def add_pole_edge(n1,n2):
    if n1 > n2:
        add_pole_edge(n2,n1)
        return
    edge=(n1,n2,gbdata.dijkstra_pole_type)
    if edge in gbstate.dijkstra_pole_edges:
        return
    gbstate.dijkstra_pole_edges.append(edge)
    #print("pole",gbstate.dijkstra_pole_edges)
    return

def build_walk_edges():
    print("build_walk_edges")
    gbstate.dijkstra_walk_edges=[]

    for mx in range(gbdata.map_width):
        for my in range(gbdata.map_height):
            identify_walk_positions(mx,my)
    return

def identify_walk_positions(mx,my):
    test_walk_pair(mx,my,mx+1,my)
    test_walk_pair(mx,my,mx,my+1)
    return

def test_walk_pair(mx1,my1,mx2,my2):
    if not gbmap.is_valid_location(mx2,my2):
        return
    l1=gbmap.map_level(mx1,my1)
    if l1 is None:
        return
    l2=gbmap.map_level(mx2,my2)
    if l2 is None:
        return
    if l1 != l2:
        return
    n1=xy_to_index(mx1,my1)
    n2=xy_to_index(mx2,my2)
    add_walk_edge(n1,n2)
    return

def add_walk_edge(n1,n2):
    if n1 > n2:
        add_walk_edge(n2,n1)
        return
    edge=(n1,n2,gbdata.dijkstra_walk_type)
    if edge in gbstate.dijkstra_walk_edges:
        return
    gbstate.dijkstra_walk_edges.append(edge)
    #print("walk",gbstate.dijkstra_walk_edges)
    return

def build_main_graph():
    print("build_main_graph")
    for mx in range(gbdata.map_width):
        for my in range(gbdata.map_height):
            identify_edges_for_node(mx,my)
    return

def identify_edges_for_node(mx,my):
    node=gbstate.mainmap[mx][my]
    index=xy_to_index(mx,my)
    node.dijkstra=[]
    identify_edges_in_list(node,index,gbstate.dijkstra_walk_edges)
    identify_edges_in_list(node,index,gbstate.dijkstra_pole_edges)
    identify_edges_in_list(node,index,gbstate.dijkstra_ladder_edges)
    return

def identify_edges_in_list(node,index,list):
    for edge in list:
        (n1,n2,t)=edge
        if n1 != index:
            if n2 != index:
                continue
        node.dijkstra.append(edge)
    return

def find_edge(i1,i2,edgelist):
    for edge in edgelist:
        if i1 == edge[0] and i2 == edge[1]:
            return edge
        if i1 == edge[1] and i2 == edge[0]:
            return edge
    return None
