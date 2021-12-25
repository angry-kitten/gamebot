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
import gbtrack
import time
import gbscreenread
import gbmap

color_white=(255,255,255) # BGR
color_black=(0,0,0) # BGR
color_green=(0,255,0) # BGR
color_red=(0,0,255) # BGR
color_blue=(255,0,0) # BGR
color_yellow=(0,255,255) # BGR
color_orange=(0,165,255) # BGR

color_water=(195,224,129) # BGR
color_coastal_rock=(135,121,114) # BGR
color_grass0=(64,129,67) # BGR
color_grass1=(67,175,72) # BGR
color_grass2=(80,220,107) # BGR
color_sand=(167,232,235) # BGR
color_dock=(0,128,128) # BGR
color_dirt=(0,32,32) # BGR
color_plaza=(125,162,175) # BGR
color_junk=(255,0,255) # BGR

line_width=1
line_width_path=3
line_width_x_narrow=2
line_width_x=3
line_width_x_wide=6
line_type=cv2.LINE_AA
font_line_width=1
font_vertical_space=26
font_vertical_space_75=26
font_vertical_space_50=int(round(font_vertical_space*0.50))
font_vertical_space_25=int(round(font_vertical_space*0.25))
font=cv2.FONT_HERSHEY_SIMPLEX
#font=cv2.FONT_HERSHEY_PLAIN
#font=cv2.FONT_HERSHEY_DUPLEX
#font=cv2.FONT_HERSHEY_COMPLEX
#font=cv2.FONT_HERSHEY_TRIPLEX
#font=cv2.FONT_HERSHEY_COMPLEX_SMALL
#font=cv2.FONT_HERSHEY_SCRIPT_SIMPLEX
#font=cv2.FONT_HERSHEY_SCRIPT_COMPLEX
#font=cv2.FONT_ITALIC
font_scale=1
font_scale_75=font_scale*0.75
font_scale_50=font_scale*0.50
font_scale_25=font_scale*0.25

#pixels_per_square=124
pixels_per_square=124
#angle_to_center=39 # degrees
angle_to_center=38 # degrees
#degrees_per_square=angle_to_center/10
#degrees_per_square=angle_to_center/11
degrees_per_square=angle_to_center/12
cylinder_radius=1579
#distance_to_viewer=1500 # pixels from center position
distance_to_viewer=1500 # pixels from center position

def control_help(frame):
    x=0
    y=120
    i=26
    cv2.putText(frame,'a=left joy left',(x,y),font,font_scale,color_green,font_line_width,line_type)
    y+=i
    cv2.putText(frame,'d=left joy right',(x,y),font,font_scale,color_green,font_line_width,line_type)
    y+=i
    cv2.putText(frame,'w=left joy up',(x,y),font,font_scale,color_green,font_line_width,line_type)
    y+=i
    cv2.putText(frame,'s=left joy down',(x,y),font,font_scale,color_green,font_line_width,line_type)
    y+=i
    cv2.putText(frame,'f=right joy left',(x,y),font,font_scale,color_green,font_line_width,line_type)
    y+=i
    cv2.putText(frame,'h=right joy right',(x,y),font,font_scale,color_green,font_line_width,line_type)
    y+=i
    cv2.putText(frame,'t=right joy up',(x,y),font,font_scale,color_green,font_line_width,line_type)
    y+=i
    cv2.putText(frame,'g=right joy down',(x,y),font,font_scale,color_green,font_line_width,line_type)
    y+=i
    cv2.putText(frame,'8=X',(x,y),font,font_scale,color_green,font_line_width,line_type)
    y+=i
    cv2.putText(frame,'6=A',(x,y),font,font_scale,color_green,font_line_width,line_type)
    y+=i
    cv2.putText(frame,'4=Y',(x,y),font,font_scale,color_green,font_line_width,line_type)
    y+=i
    cv2.putText(frame,'2=B',(x,y),font,font_scale,color_green,font_line_width,line_type)
    y+=i
    cv2.putText(frame,'+=plus',(x,y),font,font_scale,color_green,font_line_width,line_type)
    y+=i
    cv2.putText(frame,'-=minus',(x,y),font,font_scale,color_green,font_line_width,line_type)
    y+=i
    cv2.putText(frame,'u=ZL',(x,y),font,font_scale,color_green,font_line_width,line_type)
    y+=i
    cv2.putText(frame,'j=L',(x,y),font,font_scale,color_green,font_line_width,line_type)
    y+=i
    cv2.putText(frame,'i=ZR',(x,y),font,font_scale,color_green,font_line_width,line_type)
    y+=i
    cv2.putText(frame,'k=R',(x,y),font,font_scale,color_green,font_line_width,line_type)
    y+=i
    cv2.putText(frame,'q=quit',(x,y),font,font_scale,color_green,font_line_width,line_type)
    y+=i
    cv2.putText(frame,'b=debug',(x,y),font,font_scale,color_green,font_line_width,line_type)
    y+=i
    cv2.putText(frame,'p=position',(x,y),font,font_scale,color_green,font_line_width,line_type)
    y+=i
    cv2.putText(frame,'z=test',(x,y),font,font_scale,color_green,font_line_width,line_type)

def minimap_position(frame):
    if gbstate.mainmap is None:
        return
    if gbstate.position_minimap_x < 0:
        return
    w=gbdata.stdscreen_size[0]
    h=gbdata.stdscreen_size[1]
    x=int((w*8)/16)
    y=h-2
    s=f'{gbstate.position_minimap_x:.4f} {gbstate.position_minimap_y:.4f}'
    cv2.putText(frame,s,(x,y),font,font_scale*0.75,color_white,font_line_width,line_type)

def phonemap_position(frame):
# cv::MARKER_CROSS = 0,
#  cv::MARKER_TILTED_CROSS = 1,
#  cv::MARKER_STAR = 2,
#  cv::MARKER_DIAMOND = 3,
#  cv::MARKER_SQUARE = 4,
#  cv::MARKER_TRIANGLE_UP = 5,
#  cv::MARKER_TRIANGLE_DOWN = 6
    #for (sx,sy) in gbdata.phone_locations:
    #    cv2.drawMarker(frame,(sx,sy),color_white,cv2.MARKER_TRIANGLE_UP)
    #    sx2=sx+gbdata.phone_color_offset_x
    #    sy2=sy
    #    cv2.drawMarker(frame,(sx2,sy2),color_white,cv2.MARKER_TRIANGLE_DOWN)

    if gbstate.mainmap is None:
        return
    if gbstate.position_phonemap_x < 0:
        return
    w=gbdata.stdscreen_size[0]
    h=gbdata.stdscreen_size[1]
    x=int((w*5)/16)
    y=h-2
    s=f'{gbstate.position_phonemap_x:.4f} {gbstate.position_phonemap_y:.4f}'
    cv2.putText(frame,s,(x,y),font,font_scale*0.75,color_white,font_line_width,line_type)

def player_position(frame):
    if gbstate.player_mx < 0:
        return
    w=gbdata.stdscreen_size[0]
    h=gbdata.stdscreen_size[1]
    x=int((w*2)/16)
    y=h-2
    s=f'{gbstate.player_mx:.4f} {gbstate.player_my:.4f}'
    cv2.putText(frame,s,(x,y),font,font_scale*0.75,color_white,font_line_width,line_type)

def convert_map_to_pixel(mx,my):
    if gbstate.center_mx >= 0:
        center_x=gbstate.center_mx
        center_y=gbstate.center_my
    elif gbstate.player_mx >= 0:
        center_x=gbstate.player_mx
        center_y=gbstate.player_my
    elif gbstate.position_minimap_x >= 0:
        center_x=gbstate.position_minimap_x
        center_y=gbstate.position_minimap_y
    else:
        return (-1,-1)

    w=gbdata.stdscreen_size[0]
    h=gbdata.stdscreen_size[1]
    cx=int(w/2)
    cy=int(h/2)

    # Map the center of the squares on a cylinder and calculate 3d coordinates.
    center_cyl_y=cylinder_radius*math.cos(math.radians(angle_to_center))
    #print("center_cyl_y",center_cyl_y)
    center_cyl_z=cylinder_radius*math.sin(math.radians(angle_to_center))
    #print("center_cyl_z",center_cyl_z)
    # Map the position relative to the center.
    rel_y=my-center_y
    #print("rel_y",rel_y)
    rel_x=mx-center_x
    #print("rel_x",rel_x)
    square_center_angle=angle_to_center+(rel_y*degrees_per_square)
    #print("square_center_angle",square_center_angle)
    cyl_x=rel_x*pixels_per_square
    cyl_y=center_cyl_y-(cylinder_radius*math.cos(math.radians(square_center_angle)))
    #print("cyl_y",cyl_y)
    cyl_z=(cylinder_radius*math.sin(math.radians(square_center_angle)))-center_cyl_z # more distant/into screen is negative

    # Map the cylinder coordinates the the point of view.
    #print("distance_to_viewer",distance_to_viewer)
    view_x=cyl_x*(distance_to_viewer/(distance_to_viewer-cyl_z))
    view_y=cyl_y*(distance_to_viewer/(distance_to_viewer-cyl_z))
    view_z=cyl_z
    x1=cx+view_x
    y1=cy+view_y
    return (x1,y1)

def calculate_distance(px1,py1,px2,py2):
    dx=px1-px2
    dy=py1-py2
    d=math.sqrt(dx*dx+dy*dy)
    return d

def convert_pixel_to_map(px,py):
    #print("convert_pixel_to_map",px,py)

    if gbstate.center_mx >= 0:
        center_x=gbstate.center_mx
        center_y=gbstate.center_my
    elif gbstate.player_mx >= 0:
        center_x=gbstate.player_mx
        center_y=gbstate.player_my
    elif gbstate.position_minimap_x >= 0:
        center_x=gbstate.position_minimap_x
        center_y=gbstate.position_minimap_y
    else:
        return (-1,-1)

    converge=0.75
    limit=0.01
    trylimit=1000

    # Start with the screen center position as the first estimate.
    best_map_x=center_x;
    best_map_y=center_y;
    try_mx=best_map_x
    try_my=best_map_y
    #print("center try_mx",try_mx,"try_my",try_my)
    (try_px,try_py)=convert_map_to_pixel(try_mx,try_my)
    #print("center try_px",try_px,"try_py",try_py)
    if try_px < 0:
        return (-1,-1)
    if try_px == px and try_py == py:
        return (try_mx,try_my)
    best_distance=calculate_distance(px,py,try_px,try_py)
    #print("bd",best_distance,"bmx",best_map_x,"bmy",best_map_y,"px",px,"py",py,"tx",try_px,"ty",try_py)

    if try_px < px:
        step_x=3.1415
    else:
        step_x=-3.1415
    if try_py < py:
        step_y=3.1415
    else:
        step_y=-3.1415
    #print("sx",step_x,"sy",step_y)

    # Now loop trying to improve the estimate.
    while trylimit > 0:
        trylimit-=1
        try_mx+=step_x
        try_my+=step_y
        #print("try_mx",try_mx,"try_my",try_my)

        (try_px,try_py)=convert_map_to_pixel(try_mx,try_my)
        #print("try_px",try_px,"try_py",try_py)
        if try_px < 0:
            return (-1,-1)
        if try_px == px and try_py == py:
            return (try_mx,try_my)
        d=calculate_distance(px,py,try_px,try_py)
        #print("d",d)
        if d < best_distance:
            best_distance=d
            best_map_x=try_mx
            best_map_y=try_my
        #print("sx",step_x,"sy",step_y,"bd",best_distance,"bmx",best_map_x,"bmy",best_map_y,"px",px,"py",py,"tx",try_px,"ty",try_py)

        if math.fabs(step_x) < limit and math.fabs(step_y) < limit:
            return (best_map_x,best_map_y)

        prev_step_x=step_x
        prev_step_y=step_y

        if try_px < px:
            # step should be positive
            if prev_step_x > 0:
                step_x=prev_step_x
            else:
                # change direction and reduce step size
                step_x=converge*(-prev_step_x)
        else:
            # step should be negative
            if prev_step_x < 0:
                step_x=prev_step_x
            else:
                # change direction and reduce step size
                step_x=converge*(-prev_step_x)
        if try_py < py:
            # step should be positive
            if prev_step_y > 0:
                step_y=prev_step_y
            else:
                # change direction and reduce step size
                step_y=converge*(-prev_step_y)
        else:
            # step should be negative
            if prev_step_y < 0:
                step_y=prev_step_y
            else:
                # change direction and reduce step size
                step_y=converge*(-prev_step_y)

        #print("sx",step_x,"sy",step_y)

    return (-1,-1)

def draw_grid(frame):
    if gbstate.center_mx >= 0:
        center_x=gbstate.center_mx
        center_y=gbstate.center_my
    elif gbstate.player_mx >= 0:
        center_x=gbstate.player_mx
        center_y=gbstate.player_my
    elif gbstate.position_minimap_x >= 0:
        center_x=gbstate.position_minimap_x
        center_y=gbstate.position_minimap_y
    else:
        return

    w=gbdata.stdscreen_size[0]
    h=gbdata.stdscreen_size[1]
    cx=int(w/2)
    cy=int(h/2)

    # For a given area of the map.
    center_x=int(center_x)
    center_y=int(center_y)
    # For this many squares around the center.
    #print("yyy")
    #square_surround=5
    square_surround=10
    map_low_x=center_x-square_surround
    map_high_x=center_x+square_surround
    map_low_y=center_y-square_surround
    map_high_y=center_y+square_surround
    if map_low_x < 0:
        map_low_x=0
    elif map_low_x >= gbdata.map_width:
        map_low_x=gbdata.map_width-1
    if map_low_y < 0:
        map_low_y=0
    elif map_low_y >= gbdata.map_height:
        map_low_y=gbdata.map_height-1
    if map_high_x < 0:
        map_high_x=0
    elif map_high_x >= gbdata.map_width:
        map_high_x=gbdata.map_width-1
    if map_high_y < 0:
        map_high_y=0
    elif map_high_y >= gbdata.map_height:
        map_high_y=gbdata.map_height-1
    #print("map_low_x",map_low_x)
    #print("map_high_x",map_high_x)
    #print("map_low_y",map_low_y)
    #print("map_high_y",map_high_y)

    # Map the center of the squares on a cylinder and calculate 3d coordinates.
    data_w=1+(map_high_x-map_low_x)
    data_h=1+(map_high_y-map_low_y)
    center_cyl_y=cylinder_radius*math.cos(math.radians(angle_to_center))
    #print("center_cyl_y",center_cyl_y)
    center_cyl_z=cylinder_radius*math.sin(math.radians(angle_to_center))
    #print("center_cyl_z",center_cyl_z)
    pcyl=[[(0,0,0) for y in range(data_h)] for x in range(data_w)]
    # Map the squares relative to the center.
    for dy in range(data_h):
        rel_y=dy+(map_low_y-center_y)
        #print("rel_y",rel_y)
        for dx in range(data_w):
            rel_x=dx+(map_low_x-center_x)
            #print("rel_x",rel_x)
            square_center_angle=angle_to_center+(rel_y*degrees_per_square)
            #print("square_center_angle",square_center_angle)
            cyl_x=rel_x*pixels_per_square
            cyl_y=center_cyl_y-(cylinder_radius*math.cos(math.radians(square_center_angle)))
            #print("cyl_y",cyl_y)
            cyl_z=(cylinder_radius*math.sin(math.radians(square_center_angle)))-center_cyl_z # more distant/into screen is negative
            pcyl[dx][dy]=(cyl_x,cyl_y,cyl_z)

    # Map the cylinder coordinates the the point of view.
    #print("distance_to_viewer",distance_to_viewer)
    pview=[[(0,0,0) for y in range(data_h)] for x in range(data_w)]
    for dy in range(data_h):
        for dx in range(data_w):
            (cyl_x,cyl_y,cyl_z)=pcyl[dx][dy]
            view_x=cyl_x*(distance_to_viewer/(distance_to_viewer-cyl_z))
            #view_y=cyl_y
            view_y=cyl_y*(distance_to_viewer/(distance_to_viewer-cyl_z))
            view_z=cyl_z
            pview[dx][dy]=(view_x,view_y,view_z)

    # draw horizontal lines
    for gy in range(data_h):
        for gx in range(data_w-1):
            (x1,y1,z1)=pview[gx][gy]
            (x2,y2,z2)=pview[gx+1][gy]
            x1+=cx
            y1+=cy
            x2+=cx
            y2+=cy
            #cv2.line(frame,(int(x1),int(y1)),(int(x2),int(y2)),color_white,line_width)
            cv2.line(frame,(int(x1),int(y1)),(int(x1+1),int(y1)),color_white,line_width)
    # draw "vertical" lines
    for gy in range(data_h-1):
        for gx in range(data_w):
            (x1,y1,z1)=pview[gx][gy]
            (x2,y2,z2)=pview[gx][gy+1]
            x1+=cx
            y1+=cy
            x2+=cx
            y2+=cy
            #cv2.line(frame,(int(x1),int(y1)),(int(x2),int(y2)),color_white,line_width)
            cv2.line(frame,(int(x1),int(y1)),(int(x1),int(y1+1)),color_white,line_width)

def draw_x_at(frame,x,y,color,line_width=line_width_x):
    cv2.line(frame,(int(x)-10,int(y)-10),(int(x)+10,int(y)+10),color,line_width)
    cv2.line(frame,(int(x)-10,int(y)+10),(int(x)+10,int(y)-10),color,line_width)

def draw_x_at_map(frame,mx,my,color,line_width=line_width_x):
    (px,py)=convert_map_to_pixel(mx,my)
    if px < 0:
        #print("bad location")
        return
    draw_x_at(frame,px,py,color,line_width=line_width)

def draw_marker_at(frame,marker,sx,sy,color):
    sx=int(round(sx))
    sy=int(round(sy))
    cv2.drawMarker(frame,(sx,sy),color,marker)

def draw_marker_at_map(frame,marker,mx,my,color):
    (sx,sy)=convert_map_to_pixel(mx,my)
    if sx < 0:
        #print("bad location")
        return
    draw_marker_at(frame,marker,sx,sy,color)

def draw_x_path(frame):
    if gbstate.center_mx >= 0:
        center_x=gbstate.center_mx
        center_y=gbstate.center_my
    elif gbstate.player_mx >= 0:
        center_x=gbstate.player_mx
        center_y=gbstate.player_my
    elif gbstate.position_minimap_x >= 0:
        center_x=gbstate.position_minimap_x
        center_y=gbstate.position_minimap_y
    else:
        return
    center_x=int(center_x)
    center_y=int(center_y)
    for j in range(7):
            mx=j+center_x
            my=center_y-j
            (x1,y1)=convert_map_to_pixel(mx,my)
            if x1 < 0:
                return (-1,-1)
            #cv2.line(frame,(int(x1)-10,int(y1)-10),(int(x1)+10,int(y1)+10),color_black,line_width)
            #cv2.line(frame,(int(x1)-10,int(y1)+10),(int(x1)+10,int(y1)-10),color_black,line_width)
            draw_x_at(frame,x1,y1,color_black)
            (mx2,my2)=convert_pixel_to_map(x1,y1)
            if mx2 < 0:
                return (-1,-1)
            mx2+=1
            my2+=1
            (x2,y2)=convert_map_to_pixel(mx2,my2)
            if x2 < 0:
                return (-1,-1)
            #cv2.line(frame,(int(x2)-10,int(y2)-10),(int(x2)+10,int(y2)+10),color_red,line_width)
            #cv2.line(frame,(int(x2)-10,int(y2)+10),(int(x2)+10,int(y2)-10),color_red,line_width)
            draw_x_at(frame,x2,y2,color_red)

def draw_targets(frame):
    # Draw over the minimap
    if gbstate.position_minimap_x >= 0:
        draw_marker_at_map(frame,cv2.MARKER_CROSS,gbstate.position_minimap_x,gbstate.position_minimap_y,color_blue)
        sx=gbdata.minimap_origin_x+gbstate.position_minimap_x*gbdata.minimap_square_spacing
        sy=gbdata.minimap_origin_y+gbstate.position_minimap_y*gbdata.minimap_square_spacing
        draw_marker_at(frame,cv2.MARKER_CROSS,sx,sy,color_blue)

    if gbstate.position_phonemap_x >= 0:
        draw_marker_at_map(frame,cv2.MARKER_TILTED_CROSS,gbstate.position_phonemap_x,gbstate.position_phonemap_y,color_blue)
        sx=gbdata.minimap_origin_x+gbstate.position_phonemap_x*gbdata.minimap_square_spacing
        sy=gbdata.minimap_origin_y+gbstate.position_phonemap_y*gbdata.minimap_square_spacing
        draw_marker_at(frame,cv2.MARKER_TILTED_CROSS,sx,sy,color_blue)

    if gbstate.player_mx >= 0:
        draw_marker_at_map(frame,cv2.MARKER_DIAMOND,gbstate.player_mx,gbstate.player_my,color_green)
        sx=gbdata.minimap_origin_x+gbstate.player_mx*gbdata.minimap_square_spacing
        sy=gbdata.minimap_origin_y+gbstate.player_my*gbdata.minimap_square_spacing
        draw_marker_at(frame,cv2.MARKER_DIAMOND,sx,sy,color_green)

    if gbstate.goto_target_mx >= 0:
        draw_x_at_map(frame,gbstate.goto_target_mx,gbstate.goto_target_my,color_red,line_width=line_width_x_wide)
        x=gbdata.minimap_origin_x+gbstate.goto_target_mx*gbdata.minimap_square_spacing
        y=gbdata.minimap_origin_y+gbstate.goto_target_my*gbdata.minimap_square_spacing
        draw_x_at(frame,x,y,color_red,line_width=line_width_x_wide)

    if gbstate.object_target_mx >= 0:
        draw_x_at_map(frame,gbstate.object_target_mx,gbstate.object_target_my,color_green,line_width=line_width_x_wide)
        x=gbdata.minimap_origin_x+gbstate.object_target_mx*gbdata.minimap_square_spacing
        y=gbdata.minimap_origin_y+gbstate.object_target_my*gbdata.minimap_square_spacing
        draw_x_at(frame,x,y,color_green,line_width=line_width_x_wide)

    if gbstate.track_goto_target_mx >= 0:
        draw_x_at_map(frame,gbstate.track_goto_target_mx,gbstate.track_goto_target_my,color_orange,line_width=line_width_x_narrow)
        x=gbdata.minimap_origin_x+gbstate.track_goto_target_mx*gbdata.minimap_square_spacing
        y=gbdata.minimap_origin_y+gbstate.track_goto_target_my*gbdata.minimap_square_spacing
        draw_x_at(frame,x,y,color_orange,line_width=line_width_x_narrow)

    if gbstate.plan_goto_target_mx >= 0:
        draw_marker_at_map(frame,cv2.MARKER_STAR,gbstate.plan_goto_target_mx,gbstate.plan_goto_target_my,color_yellow)
        x=gbdata.minimap_origin_x+gbstate.plan_goto_target_mx*gbdata.minimap_square_spacing
        y=gbdata.minimap_origin_y+gbstate.plan_goto_target_my*gbdata.minimap_square_spacing
        draw_marker_at(frame,cv2.MARKER_STAR,x,y,color_yellow)

    # Draw over the phonemap
    w=gbdata.stdscreen_size[0]
    h=gbdata.stdscreen_size[1]
    origin_sx=w-(3*gbdata.map_width)
    origin_sy=0
    if gbstate.position_minimap_x >= 0:
        sx=origin_sx+1+gbstate.position_minimap_x*3
        sy=origin_sy+1+gbstate.position_minimap_y*3
        draw_marker_at(frame,cv2.MARKER_CROSS,sx,sy,color_blue)

    if gbstate.position_phonemap_x >= 0:
        sx=origin_sx+1+gbstate.position_phonemap_x*3
        sy=origin_sy+1+gbstate.position_phonemap_y*3
        draw_marker_at(frame,cv2.MARKER_TILTED_CROSS,sx,sy,color_blue)

    if gbstate.player_mx >= 0:
        sx=origin_sx+1+gbstate.player_mx*3
        sy=origin_sy+1+gbstate.player_my*3
        draw_marker_at(frame,cv2.MARKER_DIAMOND,sx,sy,color_green)

    if gbstate.goto_target_mx >= 0:
        x=origin_sx+1+gbstate.goto_target_mx*3
        y=origin_sy+1+gbstate.goto_target_my*3
        draw_x_at(frame,x,y,color_red,line_width=line_width_x_wide)

    if gbstate.object_target_mx >= 0:
        x=origin_sx+1+gbstate.object_target_mx*3
        y=origin_sy+1+gbstate.object_target_my*3
        draw_x_at(frame,x,y,color_green,line_width=line_width_x_wide)

    if gbstate.track_goto_target_mx >= 0:
        x=origin_sx+1+gbstate.track_goto_target_mx*3
        y=origin_sy+1+gbstate.track_goto_target_my*3
        draw_x_at(frame,x,y,color_orange,line_width=line_width_x_narrow)

    if gbstate.plan_goto_target_mx >= 0:
        x=origin_sx+1+gbstate.plan_goto_target_mx*3
        y=origin_sy+1+gbstate.plan_goto_target_my*3
        draw_marker_at(frame,cv2.MARKER_STAR,x,y,color_yellow)

    return

def draw_feet_box(frame):
    if gbstate.center_mx < 0:
        #print("unable to draw feet box 1")
        return
    if gbstate.feet_box_center_mx < 0:
        #print("unable to draw feet box 2")
        return
    # Start with the center_m* values so that they cancel
    # out even if incorrect.
    center_x=gbstate.feet_box_center_mx
    center_y=gbstate.feet_box_center_my
    x1=center_x-0.5
    x2=center_x+0.5
    y1=center_y-0.5
    y2=center_y+0.5
    (p1x,p1y)=convert_map_to_pixel(x1,y1)
    if p1x < 0:
        print("unable to draw feet box 3")
        return
    (p2x,p2y)=convert_map_to_pixel(x2,y1)
    if p2x < 0:
        print("unable to draw feet box 4")
        return
    (p3x,p3y)=convert_map_to_pixel(x1,y2)
    if p3x < 0:
        print("unable to draw feet box 5")
        return
    (p4x,p4y)=convert_map_to_pixel(x2,y2)
    if p4x < 0:
        print("unable to draw feet box 6")
        return
    cv2.line(frame,(int(p1x),int(p1y)),(int(p2x),int(p2y)),color_blue,line_width)
    cv2.line(frame,(int(p2x),int(p2y)),(int(p4x),int(p4y)),color_blue,line_width)
    cv2.line(frame,(int(p1x),int(p1y)),(int(p3x),int(p3y)),color_blue,line_width)
    cv2.line(frame,(int(p3x),int(p3y)),(int(p4x),int(p4y)),color_blue,line_width)

def draw_top_of_task_stack(frame):
    n=gbstate.tasks.NameRecursive()
    w=gbdata.stdscreen_size[0]
    h=gbdata.stdscreen_size[1]

    # Draw the names of multiple tasks on the top of the stack along
    # the right side of the screen.
    x=int((w*2)/4)
    i=font_vertical_space_50 # This is the spacing between the lines vertically.
    y=i
    l=len(gbstate.task_stack_names)
    for n in gbstate.task_stack_names:
        cv2.putText(frame,n,(x,y),font,font_scale_50,color_red,font_line_width,line_type)
        y+=i

def draw_inventory(frame):
    if not gbstate.draw_inventory_locations:
        return
    diam=10
    list=gbstate.inventory_locations
    for loc in list:
        cv2.circle(frame,loc,diam,color_black,line_width)

def draw_current_tool(frame):
    if gbstate.current_tool is None:
        n='None'
    else:
        n=gbstate.current_tool
    w=gbdata.stdscreen_size[0]
    h=gbdata.stdscreen_size[1]
    x=0
    y=h-2
    cv2.putText(frame,n,(x,y),font,font_scale*0.75,color_white,font_line_width,line_type)

def draw_maps(frame):
    w=gbdata.stdscreen_size[0]
    h=gbdata.stdscreen_size[1]
    origin_sx=w-(3*gbdata.map_width)  # origin (upper left) screen x
    origin_sy=int(h/2)                # origin (upper left) screen y

    origin_sx=w-(3*gbdata.map_width)
    origin_sy=0
    # draw phonemap2
    if gbstate.mainmap is not None:
        cv2.rectangle(frame,(origin_sx,origin_sy),(origin_sx+gbdata.map_width,origin_sy+gbdata.map_height),color_red,1)
        for y in range(gbdata.map_height):
            for x in range(gbdata.map_width):
                sx=origin_sx+x*3
                sy=origin_sy+y*3
                me=gbstate.mainmap[x][y]

                c2=maptype_to_color(me.phonemap2)
                if c2 is not None:
                    # Draw a simple square.
                    cv2.rectangle(frame,(sx,sy),(sx+2,sy+2),c2,-1)
                elif me.phonemap2 == gbmap.MapTypeDiagonalNW:
                    # Draw a black background square.
                    cv2.rectangle(frame,(sx,sy),(sx+2,sy+2),color_black,-1)
                    cu=maptype_to_color(me.diagonal0)
                    cl=maptype_to_color(me.diagonal1)
                    if cu is not None:
                        # Draw the upper right pixels
                        cv2.rectangle(frame,(sx+1,sy),(sx+1,sy),cu,-1)
                        cv2.rectangle(frame,(sx+2,sy),(sx+2,sy),cu,-1)
                        cv2.rectangle(frame,(sx+2,sy+1),(sx+2,sy+1),cu,-1)
                    if cl is not None:
                        # Draw the lower left pixels
                        cv2.rectangle(frame,(sx,sy+1),(sx,sy+1),cl,-1)
                        cv2.rectangle(frame,(sx,sy+2),(sx,sy+2),cl,-1)
                        cv2.rectangle(frame,(sx+1,sy+2),(sx+1,sy+2),cl,-1)
                elif me.phonemap2 == gbmap.MapTypeDiagonalSW:
                    # Draw a black background square.
                    cv2.rectangle(frame,(sx,sy),(sx+2,sy+2),color_black,-1)
                    cu=maptype_to_color(me.diagonal0)
                    cl=maptype_to_color(me.diagonal1)
                    if cu is not None:
                        # Draw the upper left pixels
                        cv2.rectangle(frame,(sx,sy),(sx,sy),cu,-1)
                        cv2.rectangle(frame,(sx+1,sy),(sx+1,sy),cu,-1)
                        cv2.rectangle(frame,(sx,sy+1),(sx,sy+1),cu,-1)
                    if cl is not None:
                        # Draw the lower right pixels
                        cv2.rectangle(frame,(sx+2,sy+1),(sx+2,sy+1),cl,-1)
                        cv2.rectangle(frame,(sx+1,sy+2),(sx+1,sy+2),cl,-1)
                        cv2.rectangle(frame,(sx+2,sy+2),(sx+2,sy+2),cl,-1)
                else:
                    # Draw a simple square.
                    cv2.rectangle(frame,(sx,sy),(sx+2,sy+2),color_red,-1)

        # Draw the planned path on the mainmap display.
        # Draw the waypoint lines first then the points.
        psx=-1
        psy=-1
        n=0
        for wp in gbmap.waypoints:
            sx=origin_sx+wp[0]*3+1
            sy=origin_sy+wp[1]*3+1
            if psx >= 0:
                v=127+(n*32)%128
                c=[v,0,0] # BGR
                cv2.line(frame,(psx,psy),(sx,sy),c,line_width_path)
            psx=sx
            psy=sy
        for wp in gbmap.waypoints:
            sx=origin_sx+wp[0]*3
            sy=origin_sy+wp[1]*3
            # use a rectangle to draw a pixel
            cv2.rectangle(frame,(sx,sy),(sx+2,sy+2),color_red,-1)

    # draw obstruction map 1
    if gbstate.mainmap is not None:
        for y in range(gbdata.map_height):
            for x in range(gbdata.map_width):
                sx=origin_sx+x*3
                sy=origin_sy+y*3
                mo=gbstate.mainmap[x][y]
                v=mo.objstruction_status
                color=None
                if v == gbmap.Obstructed:
                    color=color_yellow # obstructed
                elif v == gbmap.ObStandingOnWater:
                    color=color_white
                if color is not None:
                    cv2.line(frame,(sx,sy),(sx+2,sy+2),color,line_width)
                    cv2.line(frame,(sx+2,sy),(sx,sy+2),color,line_width)

    origin_sy+=(3*gbdata.map_height)

    # draw obstruction map 2
    if gbstate.mainmap is not None:
        cv2.rectangle(frame,(origin_sx,origin_sy),(origin_sx+gbdata.map_width,origin_sy+gbdata.map_height),color_red,1)
        for y in range(gbdata.map_height):
            for x in range(gbdata.map_width):
                mo=gbstate.mainmap[x][y]
                v=mo.objstruction_status
                color=None
                if v == gbmap.ObOpen:
                    color=color_green # not obstructed
                elif v == gbmap.Obstructed:
                    color=color_red # obstructed
                elif v == gbmap.ObStandingOnWater:
                    color=color_white
                if color is not None:
                    sx=origin_sx+x
                    sy=origin_sy+y
                    # use a rectangle to draw a pixel
                    cv2.rectangle(frame,(sx,sy),(sx,sy),color,-1)

    origin_sx+=gbdata.map_width

    # draw path planning
    if gbstate.mainmap is not None:
        cv2.rectangle(frame,(origin_sx,origin_sy),(origin_sx+gbdata.map_width,origin_sy+gbdata.map_height),color_red,1)
        for y in range(gbdata.map_height):
            for x in range(gbdata.map_width):
                v=gbstate.mainmap[x][y].planning_distance
                v=v%256
                if v > 0:
                    color=(v,v,v) # BGR
                    sx=origin_sx+x
                    sy=origin_sy+y
                    # use a rectangle to draw a pixel
                    cv2.rectangle(frame,(sx,sy),(sx,sy),color,-1)

        # Draw the waypoint lines first then the points.
        psx=-1
        psy=-1
        n=0
        for wp in gbmap.waypoints:
            sx=origin_sx+wp[0]
            sy=origin_sy+wp[1]
            if psx >= 0:
                g=127+(n*32)%128
                c=[0,g,0]
                cv2.line(frame,(psx,psy),(sx,sy),c,line_width)
            psx=sx
            psy=sy
        for wp in gbmap.waypoints:
            sx=origin_sx+wp[0]
            sy=origin_sy+wp[1]
            # use a rectangle to draw a pixel
            cv2.rectangle(frame,(sx,sy),(sx,sy),color_red,-1)

    origin_sx+=gbdata.map_width
    # draw possible pole
    if len(gbmap.possible_pole) > 0:
        cv2.rectangle(frame,(origin_sx,origin_sy),(origin_sx+gbdata.map_width,origin_sy+gbdata.map_height),color_red,1)
        for possible in gbmap.possible_pole:
            sx1=origin_sx+possible[0]
            sy1=origin_sy+possible[1]
            sx2=origin_sx+possible[2]
            sy2=origin_sy+possible[3]
            cv2.line(frame,(sx1,sy1),(sx2,sy2),color_green,line_width)

    origin_sx=w-(3*gbdata.map_width)
    origin_sy+=gbdata.map_height
    # draw waypoint pole
    if len(gbmap.waypoint_pole) > 0:
        cv2.rectangle(frame,(origin_sx,origin_sy),(origin_sx+gbdata.map_width,origin_sy+gbdata.map_height),color_red,1)
        for waypole in gbmap.waypoint_pole:
            sx1=origin_sx+waypole[0]
            sy1=origin_sy+waypole[1]
            sx2=origin_sx+waypole[2]
            sy2=origin_sy+waypole[3]
            cv2.line(frame,(sx1,sy1),(sx2,sy2),color_green,line_width)

    return

def maptype_to_color(maptype):
    if maptype == gbmap.MapTypeWater: # water
        return color_water
    elif maptype == gbmap.MapTypeRock: # rock (coastal)
        return color_coastal_rock
    elif maptype == gbmap.MapTypeGrass0: # grass level 0
        return color_grass0
    elif maptype == gbmap.MapTypeGrass1: # grass level 1
        return color_grass1
    elif maptype == gbmap.MapTypeGrass2: # grass level 2
        return color_grass2
    elif maptype == gbmap.MapTypeSand: # sand
        return color_sand
    elif maptype == gbmap.MapTypeDock: # dock
        return color_dock
    elif maptype == gbmap.MapTypeDirt: # dirt
        return color_dirt
    elif maptype == gbmap.MapTypePlaza:
        return color_plaza
    elif maptype == gbmap.MapTypeJunk:
        return color_junk
    return None

def draw_heading(frame):
    w=gbdata.stdscreen_size[0]
    h=gbdata.stdscreen_size[1]
    x3=int(w/2)
    y3=int(h/2)
    radius=int(h/4)
    (dsx,dsy)=gbtrack.calculate_dx_dy(gbstate.player_heading,radius)
    sx=int(round(x3+dsx))
    sy=int(round(y3+dsy))
    cv2.line(frame,(x3,y3),(sx,sy),color_green,line_width)

def draw_distance_time_dc(frame,data,color):
    scale=5
    origin_sx=0
    origin_sy=0
    i=0
    for v in data:
        x=i*scale
        sum=v[0]
        count=v[1]
        if count >= 1:
            distance=sum/count
            y=int(round(distance*10*scale))
            x+=origin_sx
            y+=origin_sy
            #cv2.line(frame,(x,y),(x,y+1),color,line_width)
            cv2.drawMarker(frame,(x,y),color,cv2.MARKER_STAR)
        i+=1;

def draw_distance_time(frame):
    draw_distance_time_dc(frame,gbstate.data_distance_time_180,color_green)
    draw_distance_time_dc(frame,gbstate.data_distance_time_90,color_blue)
    draw_distance_time_dc(frame,gbstate.data_distance_time_5,color_yellow)
    draw_distance_time_dc(frame,gbstate.data_distance_time_1,color_red)

def draw_pause_message(frame):
    if gbstate.pause_message is None:
        return
    w=gbdata.stdscreen_size[0]
    h=gbdata.stdscreen_size[1]
    sx=int(w/2)
    sy=int(h/2)
    cv2.putText(frame,gbstate.pause_message,(sx,sy),font,font_scale,color_red,line_width,line_type)

def draw_on(frame):
    control_help(frame)

    minimap_position(frame)
    phonemap_position(frame)
    player_position(frame)

    #draw_grid(frame)
    draw_feet_box(frame)
    #draw_x_path(frame)
    draw_inventory(frame)
    draw_current_tool(frame)
    w=gbdata.stdscreen_size[0]
    h=gbdata.stdscreen_size[1]
    x2=int(w/4)
    y2=int(h/4)
    x3=int(w/2)
    y3=int(h/2)
    x4=int((w*3)/4)
    y4=int((h*3)/4)
    #cv2.line(frame,(0,0),(x4,y4),color_white,line_width)
    #cv2.rectangle(frame,(x2,y2),(x4,y4),color_white,line_width)
    cv2.circle(frame,(x3,y3),y2,color_white,line_width)
    #cv2.putText(frame,'Gamebot',(x3,y3),font,font_scale,color_white,line_width,line_type)

    draw_top_of_task_stack(frame)

    draw_heading(frame)

    #draw_distance_time(frame)

    draw_pause_message(frame)


    gbscreenread.draw_screen_read(frame)

    draw_buildings(frame)

    draw_map2(frame)
    draw_maps(frame)
    draw_targets(frame)

    return

def find_detect(target_list,d_mx,d_my,distance,count,score):
    print("find_detect")
    found_list=None
    with gbstate.detection_lock:
        if gbstate.digested is None:
            print("no digested")
            return found_list
        localdigested=gbstate.digested
    if gbstate.center_mx < 0:
        print("no center")
        return found_list

    l=len(localdigested)
    if l < 1:
        print("empty localdigested")
        return found_list

    if score <= 0:
        score_list=localdigested
    else:
        score_list=[]
        for det in localdigested:
            # det is [name,score,cx,cy,bx,by]
            if det[1] >= score:
                score_list.append(det)

    l=len(score_list)
    if l < 1:
        print("empty score_list")
        return found_list

    if target_list is None:
        targeted_list=score_list
    else:
        targeted_list=[]
        for det in score_list:
            # det is [name,score,cx,cy,bx,by]
            if target_list.count(det[0]) > 0:
                targeted_list.append(det)

    l=len(targeted_list)
    if l < 1:
        print("empty targeted_list")
        return found_list

    if distance < 0:
        distance_list=targeted_list
    else:
        distance_list=[]
        for thing in targeted_list:
            if gbdata.treeable_items.count(thing[0]) > 0:
                # use bx by
                sx=thing[4]
                sy=thing[5]
            else:
                # use cx cy
                sx=thing[2]
                sy=thing[3]
            (mx,my)=convert_pixel_to_map(sx,sy)
            d=calculate_distance(mx,my,d_mx,d_my)
            if d <= distance:
                distance_list.append(thing)

    print("distance_list",distance_list)
    l=len(distance_list)
    if l < 1:
        print("empty distance_list")
        return found_list

    if count <= 0:
        count_list=distance_list
    else:
        l=len(distance_list)
        if l <= count:
            count_list=distance_list
        else:
            sorted_scores=[]
            for det in distance_list:
                # det is [name,score,cx,cy,bx,by]
                sorted_scores.append(det[1])
            print("sorted_scores",sorted_scores)
            sorted_scores.sort(reverse=True)
            print("sorted_scores",sorted_scores)
            score_limit=sorted_scores[count]
            count_list=[]
            for det in distance_list:
                if det[1] >= score_limit:
                    count_list.append(det)
            del count_list[count:]

    print("count_list",count_list)
    l=len(count_list)
    if l < 1:
        print("empty count_list")
        return found_list

    found_list=count_list
    return found_list

def draw_buildings(frame):
    if not gbstate.do_draw_buildings:
        return
    radius=int(round(gbdata.phonemap_circle_diameter/2))
    for c in gbstate.gray_circle_list:
        cv2.circle(frame,(c[0],c[1]),radius,color_red,line_width)
    return

def draw_map2(frame):
    #if gbstate.y_hist is None:
    #    return
    origin_sx=gbdata.phonemap_left
    origin_sy=gbdata.phonemap_top

    #for data_y in range(gbdata.phonemap_sheight):
    #    v=gbstate.y_hist[data_y]
    #    sx=int(round(v*100))
    #    sy=origin_sy+data_y
    #    #cv2.rectangle(frame,(sx,sy),(sx,sy),color_red,-1)
    #    cv2.line(frame,(50,sy),(sx,sy),color_red,1)

    #for data_x in range(gbdata.phonemap_swidth):
    #    v=gbstate.x_hist[data_x]
    #    sx=origin_sx+data_x
    #    sy=int(round(v*100))
    #    #cv2.rectangle(frame,(sx,sy),(sx,sy),color_red,-1)
    #    cv2.line(frame,(sx,50),(sx,sy),color_red,1)

    #sy1=int(round(gbdata.phonemap_origin_y))
    #sy2=int(round(gbdata.phonemap_origin_y+gbdata.map_height*gbdata.phonemap_square_spacing))
    #for mx in range(gbdata.map_width+1):
    #    sx=gbdata.phonemap_origin_x+(mx*gbdata.phonemap_square_spacing)
    #    sx=int(round(sx))
    #    cv2.line(frame,(sx,sy1),(sx,sy2),color_green,1)

    #sx1=int(round(gbdata.phonemap_origin_x))
    #sx2=int(round(gbdata.phonemap_origin_x+gbdata.map_width*gbdata.phonemap_square_spacing))
    #for my in range(gbdata.map_height+1):
    #    sy=gbdata.phonemap_origin_y+(my*gbdata.phonemap_square_spacing)
    #    sy=int(round(sy))
    #    cv2.line(frame,(sx1,sy),(sx2,sy),color_green,1)

    #if gbdata.phonemap_dashes_L2R is not None:
    #    for sx in gbdata.phonemap_dashes_L2R:
    #        cv2.line(frame,(sx,110),(sx,gbdata.phonemap_bottom),color_blue,1)
    #if gbdata.phonemap_dashes_T2B is not None:
    #    for sy in gbdata.phonemap_dashes_T2B:
    #        cv2.line(frame,(110,sy),(gbdata.phonemap_right,sy),color_blue,1)

    #for e in gbstate.map2stats:
    #    avg=e[0]
    #    avgr=e[1]
    #    avgg=e[2]
    #    avgb=e[3]
    #    sx=e[4]
    #    sy=e[5]
    #    cv2.rectangle(frame,(sx,sy),(sx,sy),color_red,-1)

    #for diaginfo in gbstate.map2diagonals:
    #    print("diaginfo",diaginfo)
    #    cv2.line(frame,(diaginfo[0],diaginfo[1]),(diaginfo[2],diaginfo[3]),color_yellow,1)

    return
