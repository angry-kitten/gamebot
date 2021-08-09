#
# Copyright 2021 by angry-kitten
# Various functions for looking at the screen.
# gbscreen
#

import taskobject
import gbdata
import gbstate
import cv2
import taskpress
import taskdetect

def get_pixel(x,y):
    frame=gbstate.frame
    x=int(x)
    y=int(y)
    height, width, channels=frame.shape
    if x < 0:
        x=0
    if x >= width:
        x=width-1
    if y < 0:
        y=0
    if y >= height:
        y=height-1
    (b,g,r)=frame[y,x]
    return (b,g,r)

def match_within(v1,v2,within):
    d=v1-v2;
    if d < 0:
        d= -d
    if d <= within:
        return True
    return False

def color_match(x,y,tr,tg,tb,within):
    (pb,pg,pr)=get_pixel(x,y)
    if not match_within(tr,pr,within):
        return False
    if not match_within(tg,pg,within):
        return False
    if not match_within(tb,pb,within):
        return False
    return True

def is_black_screen():
    # sample the screen instead of looking at all of it
    w=gbdata.stdscreen_size[0]
    h=gbdata.stdscreen_size[1]
    stepsize=10
    halfstep=int(stepsize/2)
    for y in range(halfstep,h,stepsize):
        for x in range(halfstep,w,stepsize):
            print(x,y)
            if not color_match(x,y,0,0,0,5):
                print("not black screen")
                return False
    print("black screen")
    return True

def is_color_bars():
    # 8 color bars
    bars=8
    barcolors_rgb=[
        [253,252,255],
        [251,255,13],
        [23,255,253],
        [19,255,10],
        [234,0,247],
        [231,0,3],
        [1,0,241],
        [0,0,0]
    ]
    bar_width=gbdata.stdscreen_size[0]/bars
    y=int(gbdata.stdscreen_size[1]/4)
    for b in range(8):
        x=int((b*bar_width)+(bar_width/2))
        print(x,y)
        colors=barcolors_rgb[b]
        if not color_match(x,y,colors[0],colors[1],colors[2],2):
            print("not match")
            return False
    print("match")
    return True

def has_label(label,ratio,x,y,within):
    if gbstate.digested is None:
        return False
    for det in gbstate.digested:
        print(det)
        if det[0] == label:
            if det[1] >= ratio:
                if match_within(det[2],x,within):
                    if match_within(det[3],y,within):
                        print("has")
                        return True
    return False

def is_start_continue_screen():
    if gbstate.digested is None:
        return False
    if not has_label('ButtonA',0.30,726,646,5):
        return False
    if not has_label('ButtonY',0.30,65,645,5):
        return False
    if not has_label('SymbolBattery',0.30,1199,64,5):
        return False
    if not has_label('SymbolWiFi',0.30,1140,65,5):
        return False
    return True

def is_main_screen():
    # check for phone
    if not color_match(62,26,243,247,223,5):
        return False
    if not color_match(89,94,243,247,223,5):
        return False
    # check for minimap
    if not color_match(1015,499,252,252,227,5):
        return False
    if not color_match(1259,499,252,252,230,5):
        return False
    if not color_match(1016,695,253,253,230,5):
        return False
    if not color_match(1259,698,252,252,227,5):
        return False
    # check for date line
    if not color_match(64,646,250,255,233,5):
        return False
    if not color_match(274,647,247,255,230,5):
        return False
    print("main screen")
    return True

def is_loading_screen():
    if gbstate.digested is None:
        return False
    if not has_label('LoadingPalmTree',0.30,1166,623,5):
        return False
    print("loading screen")
    return True

def is_continue_triangle():
    if not color_match(gbdata.conttriangle_loc[0],gbdata.conttriangle_loc[1],gbdata.conttriangle_color[0],gbdata.conttriangle_color[1],gbdata.conttriangle_color[2],5):
        return False
    print("continue triangle")
    return True

def is_continue_triangle_detect():
    if not has_label('ContinueTriangle',0.30,644,659,5):
        return False
    print("continue triangle detect")
    return True
