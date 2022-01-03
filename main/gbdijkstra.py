#
# Copyright 2021-2022 by angry-kitten
# Implement the Dijkstra shortest path algorithm for bot path planning.
#

import time, gc
import numpy
import gbdata
import gbstate
import gbscreen
import gbdisplay
import gbdijkstra
import gbmap
import gbmem
import threadmanager

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

def clear_memory():
    # Clear out the previous graph and edges, but not the
    # waypoint list.

    # The clear() empties the list in place and the =[] dumps
    # the old empty list for a new empty one.
    gbstate.dijkstra_walk_edges.clear()
    gbstate.dijkstra_walk_edges=[]
    gbstate.dijkstra_ladder_edges.clear()
    gbstate.dijkstra_ladder_edges=[]
    gbstate.dijkstra_pole_edges.clear()
    gbstate.dijkstra_pole_edges=[]

    if gbstate.mainmap is not None:
        for mx in range(gbdata.map_width):
            for my in range(gbdata.map_height):
                node=gbstate.mainmap[mx][my]
                node.dijkstra.clear()
                node.dijkstra=[]
                node.dijkstra_distance=-1
                node.dijkstra_prev=-1

    # Poke the garbage collector.
    gc.collect()
    return

def clear_new_memory():
    # Clear out the variables needed to build a new graph. These
    # will be swapped into the main variables once the build
    # is complete.

    # The clear() empties the list in place and the =[] dumps
    # the old empty list for a new empty one.
    gbstate.dijkstra_new_walk_edges.clear()
    gbstate.dijkstra_new_walk_edges=[]
    gbstate.dijkstra_new_ladder_edges.clear()
    gbstate.dijkstra_new_ladder_edges=[]
    gbstate.dijkstra_new_pole_edges.clear()
    gbstate.dijkstra_new_pole_edges=[]

    if gbstate.mainmap is not None:
        for mx in range(gbdata.map_width):
            for my in range(gbdata.map_height):
                node=gbstate.mainmap[mx][my]
                node.dijkstra_new.clear()
                node.dijkstra_new=[]

    # Poke the garbage collector.
    gc.collect()
    return

def swap_in_new_memory():
    # Swap the newly built graph into the main variables.

    # The clear() empties the list in place.
    gbstate.dijkstra_walk_edges.clear()
    gbstate.dijkstra_walk_edges=gbstate.dijkstra_new_walk_edges
    gbstate.dijkstra_new_walk_edges=[]

    gbstate.dijkstra_ladder_edges.clear()
    gbstate.dijkstra_ladder_edges=gbstate.dijkstra_new_ladder_edges
    gbstate.dijkstra_new_ladder_edges=[]

    gbstate.dijkstra_pole_edges.clear()
    gbstate.dijkstra_pole_edges=gbstate.dijkstra_new_pole_edges
    gbstate.dijkstra_new_pole_edges=[]

    if gbstate.mainmap is not None:
        for mx in range(gbdata.map_width):
            for my in range(gbdata.map_height):
                node=gbstate.mainmap[mx][my]
                node.dijkstra.clear()
                node.dijkstra=node.dijkstra_new
                node.dijkstra_new=[]

    # Poke the garbage collector.
    gc.collect()
    return

def clear_waypoints():
    # The clear() empties the list in place and the =[] dumps
    # the old empty list for a new empty one.
    gbstate.dijkstra_waypoints.clear()
    gbstate.dijkstra_waypoints=[]
    return

def build_graph():
    print("build_graph")
    print("here b 1",flush=True)

    clear_new_memory()

    print("here b 2",flush=True)
    # Build the ladder graph parts first to make for easy
    # de-duplication.
    build_ladder_edges()

    print("here b 3",flush=True)
    # Build the pole graph parts first to make for easy
    # de-duplication.
    build_pole_edges()
    print("here b 4",flush=True)

    build_walk_edges()

    print("here b 5",flush=True)
    build_main_graph()

    print("here b 6",flush=True)
    # Add the ladder and pole parts to the main graph.

    swap_in_new_memory()

    print("here b 7",flush=True)

    return

def path_plan(fmx,fmy,tmx,tmy):
    print("path_plan")
    print("here 1",flush=True)
    fmx=int(round(fmx))
    fmy=int(round(fmy))
    tmx=int(round(tmx))
    tmy=int(round(tmy))

    # Make sure the graph is there first.
    while True:
        with gbstate.buildgraph_worker_thread.data_lock:
            if gbstate.dijkstra_walk_edges is not None:
                if len(gbstate.dijkstra_walk_edges) > 0:
                    break
        time.sleep(1)

    clear_waypoints()
    print("here 2",flush=True)

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

    print("here 3",flush=True)
    # Clear only the dijkstra_distance and dijkstra_prev. The other info is
    # reused with each path planning call.
    for mx in range(gbdata.map_width):
        for my in range(gbdata.map_height):
            node=gbstate.mainmap[mx][my]
            node.dijkstra_distance=-1
            node.dijkstra_prev=-1

    print("here 4",flush=True)
    node.dijkstra_distance=0
    node.dijkstra_prev=-1
    queue=[]
    index=xy_to_index(fmx,fmy)
    queue.append(index)
    # Nominally all the unvisited nodes are in queue. But
    # queue really only contains tentative nodes.

    print("here 5",flush=True)
    edge_count=0
    queue_count=0
    while len(queue) > 0:
        queue_count+=1
        print("queue_count",queue_count,flush=True)
        gbmem.memory_report()
        i1=node_with_min_distance(queue)
        queue.remove(i1)
        (mx,my)=index_to_xy(i1)
        if mx == tmx and my == tmy:
            print("found target",flush=True)
            build_waypoint_list(i1)
            print("after build",flush=True)
            reduce_waypoint_list()
            print("after reduce",flush=True)
            return
        n1=node_from_index(i1)

        for edge in n1.dijkstra:
            edge_count+=1
            print("edge_count",edge_count,flush=True)
            gbmem.memory_report()
            t=edge[2]
            if gbdata.dijkstra_pole_type == t:
                if not gbstate.inventory_has_pole:
                    continue
            if gbdata.dijkstra_ladder_type == t:
                if not gbstate.inventory_has_ladder:
                    continue
            d=type_to_distance(t)
            alt=n1.dijkstra_distance+d
            i2=other_index(i1,edge)
            n2=node_from_index(i2)
            if n2.objstruction_status == gbmap.Obstructed:
                continue
            if n2.dijkstra_distance == -1:
                n2.dijkstra_distance=alt
                n2.dijkstra_prev=i1
                queue.append(i2)
            elif i2 in queue:
                if alt < n2.dijkstra_distance:
                    n2.dijkstra_distance=alt
                    n2.dijkstra_prev=i1

    print("unreachable",flush=True)
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
    print("i1",i1)
    clear_waypoints()
    while True:
        print("add waypoint",flush=True)
        gbmem.memory_report()
        n1=node_from_index(i1)
        print("i1",i1)
        i2=n1.dijkstra_prev
        print("i2",i2)
        if i2 < 0: # -1
            print("single waypoint case")
            # We don't know what movement type because there
            # is no edge. It should be walk.
            wp=(i1,gbdata.dijkstra_walk_type)
            gbstate.dijkstra_waypoints.append(wp)
            # The distance should be 0.
            print("distance",n1.dijkstra_distance)
            break
        edge=find_edge(i1,i2,n1.dijkstra)
        t=edge[2]
        wp=(i1,t)
        gbstate.dijkstra_waypoints.append(wp)
        print("distance",n1.dijkstra_distance)
        if n1.dijkstra_distance == 0:
            break;
        i1=i2
    print("dijkstra",gbstate.dijkstra_waypoints,flush=True)
    gbmem.memory_report()
    return

def reduce_waypoint_list():
    # Combine waypoints that are the same type
    # and direction.
    # The waypoints are ordered from the destination to the start.
    new_waypoints=[]
    l=len(gbstate.dijkstra_waypoints)
    if l < 3:
        print("only one or two waypoints")
        return

    # The end waypoint stays the same.
    new_waypoints.append(gbstate.dijkstra_waypoints[0])

    for j in range(2,l):
        # move from i3 to i2 to i1
        wp1=gbstate.dijkstra_waypoints[j-2]
        wp2=gbstate.dijkstra_waypoints[j-1]
        wp3=gbstate.dijkstra_waypoints[j]
        (i1,t1)=wp1
        (i2,t2)=wp2
        (i3,t3)=wp3

        if t1 != t2:
            # Not the same type of edge/movement.
            new_waypoints.append(wp2)
            continue
        if t1 != gbdata.dijkstra_walk_type:
            # Don't reduce pole or ladder movements.
            new_waypoints.append(wp2)
            continue
        if t2 != gbdata.dijkstra_walk_type:
            # Don't reduce pole or ladder movements.
            new_waypoints.append(wp2)
            continue

        (mx1,my1)=index_to_xy(i1)
        (mx2,my2)=index_to_xy(i2)
        (mx3,my3)=index_to_xy(i3)

        dx1=mx1-mx2
        dy1=my1-my2
        dx2=mx2-mx3
        dy2=my2-my3
        if dx1 != dx2:
            # Not the same direction of movement.
            new_waypoints.append(wp2)
            continue
        if dy1 != dy2:
            # Not the same direction of movement.
            new_waypoints.append(wp2)
            continue

        # Reduce the list by not saving i2 to the new list.

    # The start waypoint stays the same.
    new_waypoints.append(gbstate.dijkstra_waypoints[l-1])

    gbstate.dijkstra_waypoints=new_waypoints
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
    gbstate.dijkstra_new_ladder_edges.clear()
    gbstate.dijkstra_new_ladder_edges=[]

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

    # Don't be too close to a corner of a cliff.
    dx=mx1-mx2
    dy=my1-my2
    if dx != 0:
        # Check that north and south are ordinary cliffs of
        # the same type.
        # Check north
        l3=gbmap.map_level(mx1,my1-1)
        if l3 is None:
            return
        if l3 != l1:
            return
        l4=gbmap.map_level(mx2,my1-1)
        if l4 is None:
            return
        if l4 != l2:
            return
        # Check south
        l3=gbmap.map_level(mx1,my1+1)
        if l3 is None:
            return
        if l3 != l1:
            return
        l4=gbmap.map_level(mx2,my1+1)
        if l4 is None:
            return
        if l4 != l2:
            return
    if dy != 0:
        # Check that west and east are ordinary cliffs of
        # the same type.
        # Check west
        l3=gbmap.map_level(mx1-1,my1)
        if l3 is None:
            return
        if l3 != l1:
            return
        l4=gbmap.map_level(mx1-1,my2)
        if l4 is None:
            return
        if l4 != l2:
            return
        # Check east
        l3=gbmap.map_level(mx1+1,my1)
        if l3 is None:
            return
        if l3 != l1:
            return
        l4=gbmap.map_level(mx1+1,my2)
        if l4 is None:
            return
        if l4 != l2:
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
    if edge in gbstate.dijkstra_new_ladder_edges:
        return
    gbstate.dijkstra_new_ladder_edges.append(edge)
    #print("ladder",gbstate.dijkstra_new_ladder_edges)
    return

def build_pole_edges():
    print("build_pole_edges")
    gbstate.dijkstra_new_pole_edges.clear()
    gbstate.dijkstra_new_pole_edges=[]

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
        break

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
    if edge in gbstate.dijkstra_new_pole_edges:
        return
    gbstate.dijkstra_new_pole_edges.append(edge)
    #print("pole",gbstate.dijkstra_new_pole_edges)
    return

def build_walk_edges():
    print("build_walk_edges")
    gbstate.dijkstra_new_walk_edges.clear()
    gbstate.dijkstra_new_walk_edges=[]

    for mx in range(gbdata.map_width):
        for my in range(gbdata.map_height):
            identify_walk_positions(mx,my)
    return

def identify_walk_positions(mx,my):
    test_walk_pair(mx,my,mx+1,my)
    test_walk_pair(mx,my,mx,my+1)
    test_walk_pair(mx,my,mx+1,my-1)
    test_walk_pair(mx,my,mx+1,my+1)
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
    if edge in gbstate.dijkstra_new_walk_edges:
        return
    gbstate.dijkstra_new_walk_edges.append(edge)
    #print("walk",gbstate.dijkstra_new_walk_edges)
    return

def build_main_graph():
    print("build_main_graph")
    for mx in range(gbdata.map_width):
        for my in range(gbdata.map_height):
            identify_edges_for_node(mx,my)
    return

def identify_edges_for_node(mx,my):
    print("here c 1",flush=True)
    node=gbstate.mainmap[mx][my]
    index=xy_to_index(mx,my)
    node.dijkstra_new.clear()
    node.dijkstra_new=[]
    print("here c 2",flush=True)
    identify_edges_in_list(node,index,gbstate.dijkstra_new_walk_edges)
    print("here c 3",flush=True)
    identify_edges_in_list(node,index,gbstate.dijkstra_new_pole_edges)
    print("here c 4",flush=True)
    identify_edges_in_list(node,index,gbstate.dijkstra_new_ladder_edges)
    print("here c 5",flush=True)
    return

def identify_edges_in_list(node,index,list):
    for edge in list:
        (n1,n2,t)=edge
        if n1 != index:
            if n2 != index:
                continue
        node.dijkstra_new.append(edge)
    return

def find_edge(i1,i2,edgelist):
    #print("find_edge",i1,i2,edgelist)
    for edge in edgelist:
        if i1 == edge[0] and i2 == edge[1]:
            return edge
        if i1 == edge[1] and i2 == edge[0]:
            return edge
    return None

def init_buildgraph():
    gbstate.buildgraph_worker_thread=threadmanager.ThreadManager(buildgraph_worker,"buildgraph")
    return

def buildgraph_worker():
    print("before buildgraph_worker")

    build_graph()

    with gbstate.buildgraph_worker_thread.data_lock:
        gbstate.buildgraph_completed=True

    print("after buildgraph_worker")
    return

def trigger_buildgraph():
    with gbstate.buildgraph_worker_thread.data_lock:
        gbstate.buildgraph_completed=False
    gbstate.buildgraph_worker_thread.RunOnce()
    return
