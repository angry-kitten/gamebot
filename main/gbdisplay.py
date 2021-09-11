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

color_white=(255,255,255) # BGR
color_black=(0,0,0) # BGR
color_green=(0,255,0) # BGR
color_red=(0,0,255) # BGR
color_blue=(255,0,0) # BGR
line_width=1
line_type=cv2.LINE_AA
font_line_width=1
font_vertical_space=26
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

#pixels_per_square=124
pixels_per_square=124
#angle_to_player=39 # degrees
angle_to_player=38 # degrees
#degrees_per_square=angle_to_player/10
#degrees_per_square=angle_to_player/11
degrees_per_square=angle_to_player/12
cylinder_radius=1579
#distance_to_viewer=1500 # pixels from player position
distance_to_viewer=1500 # pixels from player position

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

def minimap_position(frame):
    if gbstate.minimap is None:
        return
    if gbstate.position_minimap_x < 0:
        return
    w=gbdata.stdscreen_size[0]
    h=gbdata.stdscreen_size[1]
    x=int((w*3)/4)
    y=h-2
    s=str(gbstate.position_minimap_x)+' '+str(gbstate.position_minimap_y)
    cv2.putText(frame,s,(x,y),font,font_scale*0.75,color_white,font_line_width,line_type)

def convert_map_to_pixel(mx,my):
    if gbstate.position_minimap_x < 0:
        return (-1,-1)
    w=gbdata.stdscreen_size[0]
    h=gbdata.stdscreen_size[1]
    cx=int(w/2)
    cy=int(h/2)

    player_x=gbstate.position_minimap_x
    player_y=gbstate.position_minimap_y

    # Map the center of the squares on a cylinder and calculate 3d coordinates.
    player_cyl_y=cylinder_radius*math.cos(math.radians(angle_to_player))
    #print("player_cyl_y",player_cyl_y)
    player_cyl_z=cylinder_radius*math.sin(math.radians(angle_to_player))
    #print("player_cyl_z",player_cyl_z)
    # Map the position relative to the player.
    rel_y=my-player_y
    #print("rel_y",rel_y)
    rel_x=mx-player_x
    #print("rel_x",rel_x)
    square_center_angle=angle_to_player+(rel_y*degrees_per_square)
    #print("square_center_angle",square_center_angle)
    cyl_x=rel_x*pixels_per_square
    cyl_y=player_cyl_y-(cylinder_radius*math.cos(math.radians(square_center_angle)))
    #print("cyl_y",cyl_y)
    cyl_z=(cylinder_radius*math.sin(math.radians(square_center_angle)))-player_cyl_z # more distant/into screen is negative

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
    print("convert_pixel_to_map",px,py)
    if gbstate.position_minimap_x < 0:
        return (-1,-1)
    converge=0.75
    limit=0.01
    trylimit=1000

    # Start with the player position as the first estimate.
    player_x=gbstate.position_minimap_x
    player_y=gbstate.position_minimap_y
    best_map_x=player_x;
    best_map_y=player_y;
    try_mx=best_map_x
    try_my=best_map_y
    print("player try_mx",try_mx,"try_my",try_my)
    (try_px,try_py)=convert_map_to_pixel(try_mx,try_my)
    print("player try_px",try_px,"try_py",try_py)
    if try_px < 0:
        return (-1,-1)
    if try_px == px and try_py == py:
        return (try_mx,try_my)
    best_distance=calculate_distance(px,py,try_px,try_py)
    print("bd",best_distance,"bmx",best_map_x,"bmy",best_map_y,"px",px,"py",py,"tx",try_px,"ty",try_py)

    if try_px < px:
        step_x=3.1415
    else:
        step_x=-3.1415
    if try_py < py:
        step_y=3.1415
    else:
        step_y=-3.1415
    print("sx",step_x,"sy",step_y)

    # Now loop trying to improve the estimate.
    while trylimit > 0:
        trylimit-=1
        try_mx+=step_x
        try_my+=step_y
        print("try_mx",try_mx,"try_my",try_my)

        (try_px,try_py)=convert_map_to_pixel(try_mx,try_my)
        print("try_px",try_px,"try_py",try_py)
        if try_px < 0:
            return (-1,-1)
        if try_px == px and try_py == py:
            return (try_mx,try_my)
        d=calculate_distance(px,py,try_px,try_py)
        print("d",d)
        if d < best_distance:
            best_distance=d
            best_map_x=try_mx
            best_map_y=try_my
        print("sx",step_x,"sy",step_y,"bd",best_distance,"bmx",best_map_x,"bmy",best_map_y,"px",px,"py",py,"tx",try_px,"ty",try_py)

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

        print("sx",step_x,"sy",step_y)

    return (-1,-1)

def draw_grid(frame):
    if gbstate.position_minimap_x < 0:
        return
    w=gbdata.stdscreen_size[0]
    h=gbdata.stdscreen_size[1]
    cx=int(w/2)
    cy=int(h/2)

    # For a given area of the map.
    player_x=int(gbstate.position_minimap_x)
    player_y=int(gbstate.position_minimap_y)
    # For this many squares around the player.
    #print("yyy")
    #square_surround=5
    square_surround=10
    map_low_x=player_x-square_surround
    map_high_x=player_x+square_surround
    map_low_y=player_y-square_surround
    map_high_y=player_y+square_surround
    if map_low_x < 0:
        map_low_x=0
    elif map_low_x >= gbdata.minimap_width:
        map_low_x=gbdata.minimap_width-1
    if map_low_y < 0:
        map_low_y=0
    elif map_low_y >= gbdata.minimap_height:
        map_low_y=gbdata.minimap_height-1
    if map_high_x < 0:
        map_high_x=0
    elif map_high_x >= gbdata.minimap_width:
        map_high_x=gbdata.minimap_width-1
    if map_high_y < 0:
        map_high_y=0
    elif map_high_y >= gbdata.minimap_height:
        map_high_y=gbdata.minimap_height-1
    #print("map_low_x",map_low_x)
    #print("map_high_x",map_high_x)
    #print("map_low_y",map_low_y)
    #print("map_high_y",map_high_y)

    # Map the center of the squares on a cylinder and calculate 3d coordinates.
    data_w=1+(map_high_x-map_low_x)
    data_h=1+(map_high_y-map_low_y)
    player_cyl_y=cylinder_radius*math.cos(math.radians(angle_to_player))
    #print("player_cyl_y",player_cyl_y)
    player_cyl_z=cylinder_radius*math.sin(math.radians(angle_to_player))
    #print("player_cyl_z",player_cyl_z)
    pcyl=[[(0,0,0) for y in range(data_h)] for x in range(data_w)]
    # Map the squares relative to the player.
    for dy in range(data_h):
        rel_y=dy+(map_low_y-player_y)
        #print("rel_y",rel_y)
        for dx in range(data_w):
            rel_x=dx+(map_low_x-player_x)
            #print("rel_x",rel_x)
            square_center_angle=angle_to_player+(rel_y*degrees_per_square)
            #print("square_center_angle",square_center_angle)
            cyl_x=rel_x*pixels_per_square
            cyl_y=player_cyl_y-(cylinder_radius*math.cos(math.radians(square_center_angle)))
            #print("cyl_y",cyl_y)
            cyl_z=(cylinder_radius*math.sin(math.radians(square_center_angle)))-player_cyl_z # more distant/into screen is negative
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
            cv2.line(frame,(int(x1),int(y1)),(int(x2),int(y2)),color_white,line_width)
    # draw "vertical" lines
    for gy in range(data_h-1):
        for gx in range(data_w):
            (x1,y1,z1)=pview[gx][gy]
            (x2,y2,z2)=pview[gx][gy+1]
            x1+=cx
            y1+=cy
            x2+=cx
            y2+=cy
            cv2.line(frame,(int(x1),int(y1)),(int(x2),int(y2)),color_white,line_width)

def draw_x_at(frame,x,y,color):
    cv2.line(frame,(int(x)-10,int(y)-10),(int(x)+10,int(y)+10),color,line_width)
    cv2.line(frame,(int(x)-10,int(y)+10),(int(x)+10,int(y)-10),color,line_width)

def draw_x_at_map(frame,mx,my,color):
    (px,py)=convert_map_to_pixel(mx,my)
    if px < 0:
        print("bad location")
        return
    draw_x_at(frame,px,py,color)

def draw_x_path(frame):
    if gbstate.position_minimap_x < 0:
        return
    player_x=int(gbstate.position_minimap_x)
    player_y=int(gbstate.position_minimap_y)
    for j in range(7):
            mx=j+player_x
            my=player_y-j
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
    if gbstate.position_minimap_x > 0:
        draw_x_at_map(frame,gbstate.position_minimap_x,gbstate.position_minimap_y,color_blue)
    if gbstate.target_mx > 0:
        draw_x_at_map(frame,gbstate.target_mx,gbstate.target_my,color_green)

def draw_on(frame):
    control_help(frame)
    minimap_position(frame)
    draw_grid(frame)
    #draw_x_path(frame)
    draw_targets(frame)
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
