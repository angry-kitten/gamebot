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
import gbdisplay
import time
import gbscreen

# Tracking the player position is difficult. The player character is not
# rooted to the center of the screen. We can get the player position from
# the pin on the minimap or phonemap. If we had good information about
# the player character on the screeen, we could calculate the map position
# of objects on the screen.
# The player position is inside a "feet box". As long as the map position
# stays inside the box, the screen does not scroll. If the player map
# position moves outside the box, the box moves. When the box moves, the
# screen may scroll.
# If the player keeps moving in the same direction, over a distance of
# about four or five map squares the screen will scroll to place the
# player character feet in the center of the screen for that direction.
# There are two additional scrolling actions in the perpendicular direction.
# Over two or three squares the feet box will scroll to place the feet in
# the center of that side of the feet box in the perpendicular direction.
# Over four or five squares the screen will scroll to the center of the
# side of the feet box in the perpendicular direction.
# From both of those the feet will eventually be centered on the screen.
# On top of all this the adjusted screen center moves.  It generally
# returns to +0.8,0.  Moving down it can be +1,0. Moving right or left it
# can be +0.25,0.  Moving up it can be 0,0.
# It slowly returns as the player moves.

def evaluate_position(mx,my):
    mx=int(round(mx))
    my=int(round(my))
    if not in_map_bounds(mx,my):
        return
    if gbstate.minimap is None:
        return
    v=gbstate.minimap[mx][my]
    if v == gbdata.maptype_water:
        set_standing_on_water(mx,my)

def set_current_position(map_x,map_y):
    if not in_map_bounds(map_x,map_y):
        return
    gbstate.player_mx=map_x
    gbstate.player_my=map_y
    set_not_obstructed(map_x,map_y)
    evaluate_position(map_x,map_y)

    if gbstate.center_mx < 0:
        gbstate.center_mx=gbstate.player_mx
        gbstate.center_my=gbstate.player_my
        gbstate.center_my-=gbstate.tune_sc_offset_my

    if gbstate.feet_box_center_mx < 0:
        # Default to the start map position.
        gbstate.feet_box_center_mx=gbstate.player_mx
        gbstate.feet_box_center_my=gbstate.player_my
        # gbstate.tune_sc_offset_my

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

    #print("heading=",heading,"distance=",distance,"dx=",dx,"dy=",dy)

    return (dx,dy)

def build_default_obstruction_map():
    gbstate.obstructionmap=[0 for x in range(gbdata.map_width)]
    for data_x in range(gbdata.map_width):
        # Set all to 0 or unknown.
        gbstate.obstructionmap[data_x]=[0 for y in range(gbdata.map_height)]

def in_map_bounds(mx,my):
    mx=int(round(mx))
    my=int(round(my))
    if mx < 0:
        return False
    if my < 0:
        return False
    if mx >= gbdata.map_width:
        return False
    if my >= gbdata.map_height:
        return False
    return True

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
    if not in_map_bounds(mx,my):
        return
    if gbstate.obstructionmap is None:
        build_default_obstruction_map()
    gbstate.obstructionmap[mx][my]=2

def set_not_obstructed(mx,my):
    mx=int(round(mx))
    my=int(round(my))
    if not in_map_bounds(mx,my):
        return
    if gbstate.obstructionmap is None:
        build_default_obstruction_map()
    gbstate.obstructionmap[mx][my]=1
    #debug_obstructionmap()

def set_unknown(mx,my):
    mx=int(round(mx))
    my=int(round(my))
    if not in_map_bounds(mx,my):
        return
    if gbstate.obstructionmap is None:
        build_default_obstruction_map()
    gbstate.obstructionmap[mx][my]=0

def set_standing_on_water(mx,my):
    mx=int(round(mx))
    my=int(round(my))
    if not in_map_bounds(mx,my):
        return
    print("standing on water",mx,my)
    if gbstate.obstructionmap is None:
        build_default_obstruction_map()
    gbstate.obstructionmap[mx][my]=3

def heading_difference(h1,h2):
    dh=0
    if h1 <= h2:
        dh=h2-h1
    else:
        dh=h1-h2
    if dh > 180:
        dh=360-dh
    return dh

def generate_data_code_for(name,data):

    print("# time in seconds, map distance [seconds,distance]")
    print(f"{name}=[")

    i=0
    for v in data:
        seconds=i/gbstate.data_distance_time_precision
        sum=v[0]
        count=v[1]
        if count >= 1:
            distance=sum/count
            print(f'    [{seconds},{distance}],')
        i+=1;

    print("]")

def generate_data_code():
    gbstate.latest_data_time=time.monotonic()
    generate_data_code_for('data_distance_time_1',gbstate.data_distance_time_1)
    generate_data_code_for('data_distance_time_5',gbstate.data_distance_time_5)
    generate_data_code_for('data_distance_time_10',gbstate.data_distance_time_10)
    generate_data_code_for('data_distance_time_20',gbstate.data_distance_time_20)
    generate_data_code_for('data_distance_time_30',gbstate.data_distance_time_30)
    generate_data_code_for('data_distance_time_40',gbstate.data_distance_time_40)
    generate_data_code_for('data_distance_time_50',gbstate.data_distance_time_50)
    generate_data_code_for('data_distance_time_60',gbstate.data_distance_time_60)
    generate_data_code_for('data_distance_time_70',gbstate.data_distance_time_70)
    generate_data_code_for('data_distance_time_80',gbstate.data_distance_time_80)
    generate_data_code_for('data_distance_time_90',gbstate.data_distance_time_90)
    generate_data_code_for('data_distance_time_100',gbstate.data_distance_time_100)
    generate_data_code_for('data_distance_time_110',gbstate.data_distance_time_110)
    generate_data_code_for('data_distance_time_120',gbstate.data_distance_time_120)
    generate_data_code_for('data_distance_time_130',gbstate.data_distance_time_130)
    generate_data_code_for('data_distance_time_140',gbstate.data_distance_time_140)
    generate_data_code_for('data_distance_time_150',gbstate.data_distance_time_150)
    generate_data_code_for('data_distance_time_160',gbstate.data_distance_time_160)
    generate_data_code_for('data_distance_time_170',gbstate.data_distance_time_170)
    generate_data_code_for('data_distance_time_180',gbstate.data_distance_time_180)

def take_data(hcas, distance, seconds):
    if hcas <= 1:
        data=gbstate.data_distance_time_1
    elif hcas <= 5:
        data=gbstate.data_distance_time_5
    elif hcas <= 10:
        data=gbstate.data_distance_time_10
    elif hcas <= 20:
        data=gbstate.data_distance_time_20
    elif hcas <= 30:
        data=gbstate.data_distance_time_30
    elif hcas <= 40:
        data=gbstate.data_distance_time_40
    elif hcas <= 50:
        data=gbstate.data_distance_time_50
    elif hcas <= 60:
        data=gbstate.data_distance_time_60
    elif hcas <= 70:
        data=gbstate.data_distance_time_70
    elif hcas <= 80:
        data=gbstate.data_distance_time_80
    elif hcas <= 90:
        data=gbstate.data_distance_time_90
    elif hcas <= 100:
        data=gbstate.data_distance_time_100
    elif hcas <= 110:
        data=gbstate.data_distance_time_110
    elif hcas <= 120:
        data=gbstate.data_distance_time_120
    elif hcas <= 130:
        data=gbstate.data_distance_time_130
    elif hcas <= 140:
        data=gbstate.data_distance_time_140
    elif hcas <= 150:
        data=gbstate.data_distance_time_150
    elif hcas <= 160:
        data=gbstate.data_distance_time_160
    elif hcas <= 170:
        data=gbstate.data_distance_time_170
    else:
        data=gbstate.data_distance_time_180

    i=int(round(seconds*gbstate.data_distance_time_precision))
    while len(data) <= i:
        data.append([0,0])
    v=data[i]
    v[0]+=distance
    v[1]+=1

    if gbstate.latest_data_time is None:
        generate_data_code()
    else:
        now=time.monotonic()
        dt=now-gbstate.latest_data_time
        if dt >= (10*60): # 10 minutes
            generate_data_code()

# start mx my heading 31.850000000000023 84.0 90
# target mx my heading seconds 38 84 90 1.7571428571428507
# end mx my heading 37.25 83.94999999999999 89.46949868332608
#
def after_move_processing(start_mx, start_my, start_heading, target_mx, target_my, target_heading, target_seconds, end_mx, end_my):
    print("yyy after_move_processing")
    end_dmx=end_mx-start_mx
    end_dmy=end_my-start_my
    end_heading=calculate_heading(end_dmx,end_dmy)
    print("start mx my heading", start_mx, start_my, start_heading)
    print("target mx my heading seconds", target_mx, target_my, target_heading, target_seconds)
    print("end mx my heading", end_mx, end_my, end_heading)

    target_distance=gbdisplay.calculate_distance(start_mx,start_my,target_mx,target_my)
    print("target_distance",target_distance)
    end_distance=gbdisplay.calculate_distance(start_mx,start_my,end_mx,end_my)
    print("end_distance",end_distance)

    fraction=0.20
    target_distance_high=target_distance*(1.00+fraction)
    print("target_distance_high",target_distance_high)
    target_distance_low=target_distance*(1.00-fraction)
    print("target_distance_low",target_distance_low)

    error_mx=end_mx-target_mx
    error_my=end_my-target_my
    print("error mx my", error_mx, error_my)
    error_limit_mx_my=1
    #error_limit_degrees=1
    error_limit_degrees=5
    #heading_change_limit=1
    heading_change_limit=5

    heading_change_at_start=heading_difference(start_heading,target_heading)
    print("heading_change_at_start",heading_change_at_start)
    heading_error_target_end=heading_difference(target_heading,end_heading)
    print("heading_error_target_end",heading_error_target_end)

    heading_change=heading_difference(start_heading,end_heading)
    print("heading_change",heading_change)

    if heading_error_target_end <= error_limit_degrees:
        #if abs(error_mx) <= error_limit_mx_my and abs(error_my) <= error_limit_mx_my:
        if target_distance_low <= end_distance and end_distance <= target_distance_high:
            print("taking data for distance and time")
            take_data(heading_change_at_start,end_distance,target_seconds)

    # Update the feet box.
    if gbstate.feet_box_center_mx < 0:
        # Default to the start map position.
        gbstate.feet_box_center_mx=start_mx
        gbstate.feet_box_center_my=start_my
        # gbstate.tune_sc_offset_my

    # Before the feet box is moved, the adjusted screen center needs to
    # be in or on the feet box.
    # Calculate the adjusted screen center
    adjusted_screen_center_mx=gbstate.center_mx
    adjusted_screen_center_my=gbstate.center_my+gbstate.tune_sc_offset_my
    print("asc 1",adjusted_screen_center_mx,adjusted_screen_center_my)

    fbc_mx=gbstate.feet_box_center_mx
    fbc_my=gbstate.feet_box_center_my
    print("feet box center x y",fbc_mx,fbc_my)

    # calculate the feet box sides
    x1=fbc_mx-0.5 # left
    x2=fbc_mx+0.5 # right
    y1=fbc_my-0.5 # top
    y2=fbc_my+0.5 # bottom

    print("start feet sides",x1,x2,y1,y2)

    # Now make sure the adjusted screen center is inside or on the feet box.
    if adjusted_screen_center_mx < x1:
        adjusted_screen_center_mx=x1
    elif adjusted_screen_center_mx > x2:
        adjusted_screen_center_mx=x2
    if adjusted_screen_center_my < y1:
        adjusted_screen_center_my=y1
    elif adjusted_screen_center_my > y2:
        adjusted_screen_center_my=y2
    print("asc 2",adjusted_screen_center_mx,adjusted_screen_center_my)

    # Update the screen center in case the adjusted screen center moved.
    gbstate.center_mx=adjusted_screen_center_mx
    gbstate.center_my=adjusted_screen_center_my-gbstate.tune_sc_offset_my

    # See if the player movement was enough to move the feet box.
    past_x=0
    past_y=0
    if end_mx > x2:
        print("moved past the box to the right")
        past_x=end_mx-x2
    elif end_mx < x1:
        print("moved past the box to the left")
        past_x=end_mx-x1
    if end_my > y2:
        print("moved past the box to the bottom")
        past_y=end_my-y2
    elif end_my < y1:
        print("moved past the box to the top")
        past_y=end_my-y1

    print("past x y",past_x,past_y)

    print("tune_sc_offset_my before",gbstate.tune_sc_offset_my)
    tune_sc_dy=gbstate.tune_sc_offset_my-gbstate.tune_sc_offset_origin_my
    if tune_sc_dy != 0:
        adjust_amount=(abs(past_x)+abs(past_y))*gbstate.tune_sc_offset_ratio
        if tune_sc_dy > 0:
            if adjust_amount > tune_sc_dy:
                adjust_amount=tune_sc_dy
            gbstate.tune_sc_offset_my-=adjust_amount
        elif tune_sc_dy < 0:
            if adjust_amount > -tune_sc_dy:
                adjust_amount=-tune_sc_dy
            gbstate.tune_sc_offset_my+=adjust_amount
    print("tune_sc_offset_my after",gbstate.tune_sc_offset_my)

    # Adjust the tune value if the heading changed.
    if heading_change >= 80 or heading_change <= -80:
        if (end_heading >= 0 and end_heading < 45) or (end_heading >= 315 and end_heading <= 360):
            print("end_heading up/north")
            gbstate.tune_sc_offset_my=gbstate.tune_sc_offset_up_my
        elif end_heading >= 45 and end_heading < 135:
            print("end_heading right/east")
            gbstate.tune_sc_offset_my=gbstate.tune_sc_offset_right_my
        elif end_heading >= 135 and end_heading < 225:
            print("end_heading down/south")
            gbstate.tune_sc_offset_my=gbstate.tune_sc_offset_down_my
        elif end_heading >= 225 and end_heading < 315:
            print("end_heading left/west")
            gbstate.tune_sc_offset_my=gbstate.tune_sc_offset_left_my
    print("tune_sc_offset_my after 2",gbstate.tune_sc_offset_my)

    # Calculate the adjusted screen center with the new value.
    adjusted_screen_center_mx=gbstate.center_mx
    adjusted_screen_center_my=gbstate.center_my+gbstate.tune_sc_offset_my

    # Adjust the feet box center if needed.
    # the feet box moves to keep the player position inside or on
    fbc2_mx=fbc_mx+past_x
    fbc2_my=fbc_my+past_y
    print("new feet box center x y",fbc2_mx,fbc2_my)

    # Update the global state.
    gbstate.feet_box_center_mx=fbc2_mx
    gbstate.feet_box_center_my=fbc2_my

    # Over two or three squares the feet box will scroll to place the feet in
    # the center of that side of the feet box in the perpendicular direction.
    # When the player moves in one direction, the feet box is adjusted
    # to center the player position in the other direction.  If the
    # player moves down/south, the feet box can be adjusted left/west or
    # right/east.
    # This also adjusts the adjusted screen center the same amount.
    cross_x=abs(past_y)*gbstate.feet_box_cross_ratio_x
    cross_y=abs(past_x)*gbstate.feet_box_cross_ratio_y

    # Calculate the max the center can be adjusted.
    cross_max_x=end_mx-fbc2_mx
    cross_max_y=end_my-fbc2_my

    if cross_max_x > 0:
        # the player is to the right of the center
        # move the feet box center to the right
        if cross_x > cross_max_x:
            cross_x=cross_max_x
        fbc2_mx+=cross_x
        # move the adjusted screen center to the right
        adjusted_screen_center_mx+=cross_x
    elif cross_max_x < 0:
        # the player is to the left of the center
        # move the feet box center to the left
        if cross_x > -cross_max_x:
            cross_x=-cross_max_x
        fbc2_mx-=cross_x
        adjusted_screen_center_mx-=cross_x
    if cross_max_y > 0:
        # the player is below the center
        # move the feet box center down
        if cross_y > cross_max_y:
            cross_y=cross_max_y
        fbc2_my+=cross_y
        adjusted_screen_center_my+=cross_y
    elif cross_max_y < 0:
        # the player is above the center
        # move the feet box center up
        if cross_y > -cross_max_y:
            cross_y=-cross_max_y
        fbc2_my-=cross_y
        adjusted_screen_center_my-=cross_y

    print("new feet box center 2 x y",fbc2_mx,fbc2_my)

    # Update the global state.
    gbstate.feet_box_center_mx=fbc2_mx
    gbstate.feet_box_center_my=fbc2_my

    print("asc 2.5",adjusted_screen_center_mx,adjusted_screen_center_my)
    gbstate.center_mx=adjusted_screen_center_mx
    gbstate.center_my=adjusted_screen_center_my-gbstate.tune_sc_offset_my

    # At this point the feet box is adjusted and no more changes
    # to it are needed.

    # If the player doesn't move outside the feet box, then the screen
    # center does not change.
    # If the player does move outside the feet box, the screen center
    # moves towards the player position.

    # Calculate the maximum amount the adjusted screen center can move.
    max_adjusted_screen_center_move_mx=end_mx-adjusted_screen_center_mx
    max_adjusted_screen_center_move_my=end_my-adjusted_screen_center_my
    print("max",max_adjusted_screen_center_move_mx,max_adjusted_screen_center_move_my)

    # The screen center moves the amount the player moved outside the
    # feet box, plus an extra amount to draw the screen center closer
    # to the player.
    asc_move_mx=past_x+(past_x*gbstate.feet_box_ratio_x)
    asc_move_my=past_y+(past_y*gbstate.feet_box_ratio_y)
    print("move 1",asc_move_mx,asc_move_my)

    # Bound the screen center movement so that it doesn't overshoot.
    if asc_move_mx > 0:
        if max_adjusted_screen_center_move_mx > 0:
            # They are both greater than zero.
            if asc_move_mx > max_adjusted_screen_center_move_mx:
                asc_move_mx=max_adjusted_screen_center_move_mx
        else:
            # They are different directions.
            asc_move_mx=0
    elif asc_move_mx < 0:
        if max_adjusted_screen_center_move_mx < 0:
            # They are both less than zero.
            if asc_move_mx < max_adjusted_screen_center_move_mx:
                asc_move_mx=max_adjusted_screen_center_move_mx
        else:
            # They are different directions.
            asc_move_mx=0
    if asc_move_my > 0:
        if max_adjusted_screen_center_move_my > 0:
            # They are both greater than zero.
            if asc_move_my > max_adjusted_screen_center_move_my:
                asc_move_my=max_adjusted_screen_center_move_my
        else:
            # They are different directions.
            asc_move_my=0
    elif asc_move_my < 0:
        if max_adjusted_screen_center_move_my < 0:
            # They are both less than zero.
            if asc_move_my < max_adjusted_screen_center_move_my:
                asc_move_my=max_adjusted_screen_center_move_my
        else:
            # They are different directions.
            asc_move_my=0
    print("move 2",asc_move_mx,asc_move_my)

    # Now move the adjusted screen center.
    adjusted_screen_center_mx+=asc_move_mx
    adjusted_screen_center_my+=asc_move_my
    print("asc 3",adjusted_screen_center_mx,adjusted_screen_center_my)

    # Update the screen center in case the adjusted screen center moved.
    gbstate.center_mx=adjusted_screen_center_mx
    gbstate.center_my=adjusted_screen_center_my-gbstate.tune_sc_offset_my

    # Over four or five squares the screen will scroll to the center of the
    # side of the feet box in the perpendicular direction.

    # Calculate the amount of perpendicular movement based on how far the
    # player position moved past the feet box.
    cross_x=abs(past_y)*gbstate.box_center_cross_ratio_x
    cross_y=abs(past_x)*gbstate.box_center_cross_ratio_y
    print("cross x y",cross_x,cross_y)

    # Calculate the maximum amount the adjusted screen center can move.
    cross_max_x=fbc2_mx-adjusted_screen_center_mx
    cross_max_y=fbc2_my-adjusted_screen_center_my
    print("cross max x y",cross_max_x,cross_max_y)

    if cross_max_x > 0:
        # the box center is to the right of the screen center
        # move the screen center to the right
        if cross_x > cross_max_x:
            cross_x=cross_max_x
        adjusted_screen_center_mx+=cross_x
    elif cross_max_x < 0:
        # the box center is to the left of the screen center
        # move the screen center to the left
        if cross_x > -cross_max_x:
            cross_x=-cross_max_x
        adjusted_screen_center_mx-=cross_x
    if cross_max_y > 0:
        # the box center is below the screen center
        # move the screen center down
        if cross_y > cross_max_y:
            cross_y=cross_max_y
        adjusted_screen_center_my+=cross_y
    elif cross_max_y < 0:
        # the box center is above the screen center
        # move the screen center up
        if cross_y > -cross_max_y:
            cross_y=-cross_max_y
        adjusted_screen_center_my-=cross_y

    # Update the screen center in case the adjusted screen center moved.
    gbstate.center_mx=adjusted_screen_center_mx
    gbstate.center_my=adjusted_screen_center_my-gbstate.tune_sc_offset_my

    # Use detecting the feet as the big hammer.
    feet_match=gbscreen.has_label_in_box('Feet',0.20,gbdata.feet_region_x1,gbdata.feet_region_x2,gbdata.feet_region_y1,gbdata.feet_region_y2)
    if feet_match is not None:
        print("found feet",feet_match)

    player_match=gbscreen.has_label_in_box('Player',0.30,gbdata.player_region_x1,gbdata.player_region_x2,gbdata.player_region_y1,gbdata.player_region_y2)
    if player_match is not None:
        print("found player",player_match)

    use_feet=False
    feet_sx=0
    feet_sy=0
    if feet_match is not None:
        # Use the object center.
        feet_sx=feet_match[2]
        feet_sy=feet_match[3]
        use_feet=True
    else:
        if player_match is not None:
            # Use the object base.
            feet_sx=player_match[4]
            feet_sy=player_match[5]
            feet_sx+=0
            feet_sy+=15
            use_feet=True

    if use_feet:
        # Update the screen center based on object detection.

        # set center if not already set
        if gbstate.center_mx < 0:
            gbstate.center_mx=gbstate.move_before_mx
            gbstate.center_my=gbstate.move_before_my

        # Calculate the map position of the feet as if the
        # center values were accurate.
        (mx,my)=gbdisplay.convert_pixel_to_map(feet_sx,feet_sy)
        print("center",gbstate.center_mx,gbstate.center_my)
        print("feet",mx,my)

        # Since we know the real player position we can calculate
        # the difference from mx,my. This will give the error in
        # both the feet and center positions.
        error_mx=end_mx-mx
        error_my=end_my-my
        print("error",error_mx,error_my)

        # Adding the error to mx,my will give the real player position.
        # Adding the error to center_mx,center_my will give the real center position.
        gbstate.center_mx+=error_mx
        gbstate.center_my+=error_my
        print("new center",gbstate.center_mx,gbstate.center_my)

# distance_to_time=0.26976168054446614 # seconds per map square distance
# angle_to_time=0.001950835441527321 # seconds per degree
def heading_change_and_distance_to_time(heading1,heading2,distance):
    dh=heading_difference(heading1,heading2)
    seconds=dh*gbdata.angle_to_time
    seconds+=distance*gbdata.distance_to_time
    return seconds
