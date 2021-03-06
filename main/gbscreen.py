#
# Copyright 2021-2022 by angry-kitten
# Various functions for looking at the screen.
# gbscreen
#

import math
import cv2
import gbdata
import gbstate
import gbdisplay
import gblogfile
import gbmap
import gbocr
import taskobject
import taskpress
import taskdetect

def scale_and_bound(v,m):
    v2=int(round(v*m))
    if v2 < 0:
        return 0
    if v2 > 255:
        return 255
    return v2

def scale_components(f1):
    return
    height, width, channels=f1.shape #pylint: disable=unreachable
    for x in range(width):
        for y in range(height):
            (b,g,r)=f1[y,x]
            g=scale_and_bound(g,gbdata.win_scale_g)
            r=scale_and_bound(r,gbdata.win_scale_r)
            f1[y,x]=(b,g,r)
    return

def get_pixel(x,y):
    frame=gbstate.frame
    x=int(round(x))
    y=int(round(y))
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
    d=v1-v2
    if d < 0:
        d= -d
    if d <= within:
        return True
    return False

def color_match_rgb_0(pr,pg,pb,tr,tg,tb,within):
    #print("color_match_rgb",pr,pg,pb,tr,tg,tb,within)
    if not match_within(tr,pr,within):
        return False
    if not match_within(tg,pg,within):
        return False
    if not match_within(tb,pb,within):
        return False
    return True

def color_match_rgb(pr,pg,pb,tr,tg,tb,within):
    b=color_match_rgb_0(pr,pg,pb,tr,tg,tb,within)
    if not b:
        if gbstate.debug_window:
            gblogfile.log(f'no color_match_rgb {tr} {tg} {tb} {pr} {pg} {pb}\n')
    return b

def color_match_rgb_array(pr,pg,pb,a,within):
    return color_match_rgb(pr,pg,pb,a[0],a[1],a[2],within)

def color_match_rgb_array_list(pr,pg,pb,l,within):
    for a in l:
        b=color_match_rgb(pr,pg,pb,a[0],a[1],a[2],within)
        if b:
            return b
    return False

def color_match_rgb_array_list2(pr,pg,pb,l):
    for a in l:
        b=color_match_rgb(pr,pg,pb,a[0],a[1],a[2],a[3])
        if b:
            return b
    return False

def measure_how_close_rgb(pr,pg,pb,tr,tg,tb):
    dr=abs(pr-tr)
    dg=abs(pg-tg)
    db=abs(pb-tb)
    d=math.sqrt(dr*dr+dg*dg+db*db)
    return d

def measure_how_close_list2(pr,pg,pb,l):
    best_close=None
    for a in l:
        close=measure_how_close_rgb(pr,pg,pb,a[0],a[1],a[2])
        if best_close is None:
            best_close=close
        elif close < best_close:
            best_close=close
    return best_close

def measure_how_close(pr,pg,pb,l):
    return measure_how_close_list2(pr,pg,pb,l)

def color_match(x,y,tr,tg,tb,within):
    x=int(round(x))
    y=int(round(y))
    (pb,pg,pr)=get_pixel(x,y)
    if gbstate.debug_window:
        print("color_match tr,tg,tb pr,pg,pb",tr,tg,tb,pr,pg,pb,within)
    return color_match_rgb(pr,pg,pb,tr,tg,tb,within)

def color_match_array(x,y,a,within):
    x=int(round(x))
    y=int(round(y))
    return color_match(x,y,a[0],a[1],a[2],within)

def color_match_array_list(x,y,l,within):
    for a in l:
        b=color_match_array(x,y,a,within)
        if b:
            return b
    return False

def print_color_at(sx,sy):
    sx=int(round(sx))
    sy=int(round(sy))
    (pb,pg,pr)=get_pixel(sx,sy)
    print("rgb",pr,pg,pb)
    return

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
    with gbstate.detection_lock:
        if gbstate.digested is None:
            return False
        localdigested=gbstate.digested
    rv=False
    if gbstate.debug_window:
        print('has_label {',label) # }
    for det in localdigested:
        if gbstate.debug_window:
            print(det) # det is [name,score,cx,cy,bx,by]
        if det[0] == label:
            if det[1] >= ratio:
                if x < 0:
                    # don't match on location
                    print("has with no location")
                    rv=True
                    break
                if match_within(det[2],x,within):
                    if match_within(det[3],y,within):
                        print("has")
                        rv=True
                        break
    if gbstate.debug_window:
        # {
        print('} has_label',rv)
    return rv

def has_label_prefix(label_prefix,ratio,x,y,within):
    with gbstate.detection_lock:
        if gbstate.digested is None:
            return False
        localdigested=gbstate.digested

    prefix_len=len(label_prefix)

    for det in localdigested:
        print(det) # det is [name,score,cx,cy,bx,by]
        name=det[0]
        prefix=name[0:prefix_len]
        print("prefix name",prefix,name)
        if prefix == label_prefix:
            if det[1] >= ratio:
                if x < 0:
                    # don't match on location
                    print("has with no location")
                    return True
                if match_within(det[2],x,within):
                    if match_within(det[3],y,within):
                        print("has")
                        return True
    return False

def has_label_in_box(label,ratio,x1,x2,y1,y2):
    bestmatch=None
    with gbstate.detection_lock:
        if gbstate.digested is None:
            return bestmatch
        localdigested=gbstate.digested
    for det in localdigested:
        #print("hlib",det) # det is [name,score,cx,cy,bx,by]
        if det[0] == label:
            if det[1] >= ratio:
                if is_inside_box(x1,x2,y1,y2,det[2],det[3]):
                    if bestmatch is None:
                        bestmatch=det
                    else:
                        if det[1] > bestmatch[1]:
                            bestmatch=det
    print("bestmatch",bestmatch)
    return bestmatch

def is_start_continue_screen():
    with gbstate.detection_lock:
        if gbstate.digested is None:
            return False
    count=0
    if not has_label('ButtonA',0.30,726,646,5):
        return False
    # If there is no current game, then thereis a ButtonHome.
    if has_label('ButtonHome',0.30,818,347,5):
        count+=1
    if has_label('ButtonY',0.30,65,645,5):
        count+=1
    if not has_label('SymbolBattery',0.16,1199,64,15):
        return False
    if not has_label('SymbolWiFi',0.20,1140,65,15):
        if not has_label('SymbolWiFi',0.20,1095,66,15):
            if not has_label('SymbolWiFi',0.20,1077,66,15):
                return False
    if count < 1:
        return False
    return True

def is_minimap():
    # check for minimap
    # look for the white border
    x1=int((gbdata.minimap_border_left+gbdata.minimap_left)/2)
    x2=int((gbdata.minimap_right+gbdata.minimap_border_right)/2)
    y1=int((gbdata.minimap_border_top+gbdata.minimap_top)/2)
    y2=int((gbdata.minimap_border_bottom+gbdata.minimap_bottom)/2)
    #print("minimap",x1,x2,y1,y2)
    if not color_match(x1,y1,252,252,227,5):
        return False
    if not color_match(x2,y1,252,252,230,5):
        return False
    if not color_match(x1,y2,253,253,230,5):
        return False
    if not color_match(x2,y2,252,252,227,5):
        return False
    print("minimap")
    return True

def is_main_screen():
    print("is_main_screen 1")
    #gbstate.debug_window=True
    # check for phone
    if not color_match(62,26,243,247,223,5):
        #gbstate.debug_window=False
        return False
    print("is_main_screen 2")
    if not color_match(89,94,243,247,223,5):
        #gbstate.debug_window=False
        return False
    print("is_main_screen 3")
    # check for minimap
    if not is_minimap():
        #gbstate.debug_window=False
        return False
    print("is_main_screen 4")
    # check for date line
    #if not color_match(64,646,250,255,233,5):
    #    return False
    #print("is_main_screen 5")
    #if not color_match(274,647,247,255,230,5):
    #    return False
    #print("is_main_screen 6")
    print("main screen")
    #gbstate.debug_window=False
    return True

def is_loading_screen():
    with gbstate.detection_lock:
        if gbstate.digested is None:
            return False
    if not has_label('LoadingPalmTree',0.30,1166,623,5):
        return False
    print("loading screen")
    return True

def is_continue_triangle():
    #gbstate.debug_window=True
    if color_match_array_list(gbdata.conttriangle_loc1[0],gbdata.conttriangle_loc1[1],gbdata.conttriangle_color_list,5):
        #gbstate.debug_window=False
        print("continue triangle")
        return True
    if color_match_array_list(gbdata.conttriangle_loc2[0],gbdata.conttriangle_loc2[1],gbdata.conttriangle_color_list,5):
        #gbstate.debug_window=False
        print("continue triangle")
        return True
    if color_match_array_list(gbdata.conttriangle_loc3[0],gbdata.conttriangle_loc3[1],gbdata.conttriangle_color_list,5):
        #gbstate.debug_window=False
        print("continue triangle")
        return True
    #gbstate.debug_window=False
    return False

def is_continue_triangle_detect():
    if has_label('ContinueTriangle',0.30,644,659,5):
        print("continue triangle detect")
        return True
    if has_label('ContinueTriangle',0.30,642,654,5):
        print("continue triangle detect")
        return True
    return False

def is_selection_screen_no_ACNH():
    with gbstate.detection_lock:
        if gbstate.digested is None:
            return False
    if not has_label('SOnlineLogo',0.10,316,546,5):
        return False
    if not has_label('SymbolBattery',0.15,1199,65,15):
        return False
    if not has_label('SymbolWiFi',0.20,1140,65,15):
        if not has_label('SymbolWiFi',0.20,1095,65,15):
            if not has_label('SymbolWiFi',0.20,1077,66,15):
                return False
    return True

def is_selection_screen():
    with gbstate.detection_lock:
        if gbstate.digested is None:
            return False
    if not is_selection_screen_no_ACNH():
        return False
    if not has_label('ACNHTile',0.30,236,323,5):
        return False
    return True

def is_user_selection_screen():
    with gbstate.detection_lock:
        if gbstate.digested is None:
            return False
    if not has_label('ButtonPlus',0.30,780,517,5):
        if not has_label('ButtonPlus',0.30,855,517,5):
            return False
    if not has_label('ButtonB',0.15,1029,684,5):
        return False
    if not has_label('ButtonA',0.20,1159,684,5):
        return False
    return True

def is_main_logo_screen():
    if gbocr.ocr_results_contain('Select a user'):
        return True
    with gbstate.detection_lock:
        if gbstate.digested is None:
            return False
    if has_label('ACNHMainLogo',0.95,625,200,20):
        return True
    if has_label('ACNHMainLogo',0.95,636,180,20):
        return True
    if not has_label('ACNHMainLogo',0.30,625,200,20):
        return False
    if not has_label('ButtonA',0.15,693,635,5):
        return False
    return True

def is_inside_box(x1,x2,y1,y2,x,y):
    if x < x1:
        return False
    if x > x2:
        return False
    if y < y1:
        return False
    if y > y2:
        return False
    return True

def is_near_within(x1,y1,x2,y2,within):
    d=gbdisplay.calculate_distance(x1,y1,x2,y2)
    if d <= within:
        return True
    return False

def is_inventory_screen():
    with gbstate.detection_lock:
        if gbstate.digested is None:
            return False
    if not has_label('PointerHand',0.30,-1,-1,-1):
        return False
    if not has_label('BellBagStar',0.30,gbdata.inventory_bag_10_x,gbdata.inventory_bag_10_y,20):
        if not has_label('BellBagStar',0.30,gbdata.inventory_bag_20_x,gbdata.inventory_bag_20_y,20):
            if not has_label('BellBagStar',0.30,gbdata.inventory_bag_30_x,gbdata.inventory_bag_30_y,20):
                return False
    if not has_label('ButtonA',0.30,1130,692,5):
        return False
    if not has_label('ButtonB',0.15,1001,693,5):
        return False
    return True

def is_accept_controller_screen():
    with gbstate.detection_lock:
        if gbstate.digested is None:
            return False
    if not has_label('ButtonA',0.80,556,597,5):
        return False
    return True

def find_slot_from_array(x,y,slot_array):
    best_slot=None
    best_distance=None
    l=len(slot_array)
    for i in range(l):
        (sx,sy)=slot_array[i]
        d=gbdisplay.calculate_distance(x,y,sx,sy)
        if best_distance is None:
            best_distance=d
            best_slot=i
        else:
            if d < best_distance:
                best_distance=d
                best_slot=i
    return best_slot

def find_inventory_slot(x,y):
    best_slot=find_slot_from_array(x,y,gbstate.inventory_locations)
    return best_slot

def is_phone_screen():
    with gbstate.detection_lock:
        if gbstate.digested is None:
            return False

    match_count=0
    # camera, nook miles, critter,
    # diy, design, map,
    # chat, passport,rescue
    match=has_label_in_box('PhoneCameraIcon',0.20,gbdata.phone_box_left_sx,gbdata.phone_box_right_sx,gbdata.phone_box_top_sy,gbdata.phone_box_bottom_sy)
    if match is not None:
        match_count+=1
    match=has_label_in_box('PhoneNookMilesIcon',0.20,gbdata.phone_box_left_sx,gbdata.phone_box_right_sx,gbdata.phone_box_top_sy,gbdata.phone_box_bottom_sy)
    if match is not None:
        match_count+=1
    match=has_label_in_box('PhoneCritterIcon',0.20,gbdata.phone_box_left_sx,gbdata.phone_box_right_sx,gbdata.phone_box_top_sy,gbdata.phone_box_bottom_sy)
    if match is not None:
        match_count+=1
    match=has_label_in_box('PhoneDIYIcon',0.20,gbdata.phone_box_left_sx,gbdata.phone_box_right_sx,gbdata.phone_box_top_sy,gbdata.phone_box_bottom_sy)
    if match is not None:
        match_count+=1
    match=has_label_in_box('PhoneCustomDesignsIcon',0.20,gbdata.phone_box_left_sx,gbdata.phone_box_right_sx,gbdata.phone_box_top_sy,gbdata.phone_box_bottom_sy)
    if match is not None:
        match_count+=1
    match=has_label_in_box('PhoneMapIcon',0.10,gbdata.phone_box_left_sx,gbdata.phone_box_right_sx,gbdata.phone_box_top_sy,gbdata.phone_box_bottom_sy)
    if match is not None:
        match_count+=1
    match=has_label_in_box('PhoneChatIcon',0.20,gbdata.phone_box_left_sx,gbdata.phone_box_right_sx,gbdata.phone_box_top_sy,gbdata.phone_box_bottom_sy)
    if match is not None:
        match_count+=1
    match=has_label_in_box('PhonePassportIcon',0.10,gbdata.phone_box_left_sx,gbdata.phone_box_right_sx,gbdata.phone_box_top_sy,gbdata.phone_box_bottom_sy)
    if match is not None:
        match_count+=1
    match=has_label_in_box('PhoneRescueServiceIcon',0.20,gbdata.phone_box_left_sx,gbdata.phone_box_right_sx,gbdata.phone_box_top_sy,gbdata.phone_box_bottom_sy)
    if match is not None:
        match_count+=1
    print("match_count",match_count)
    if match_count >= 4:
        return True
    return False

def is_phone_map_screen():
    match_count=0
    if color_match_array_list(18,31,gbdata.phone_map_background_list,7):
        match_count+=1
    if color_match_array_list(28,681,gbdata.phone_map_background_list,7):
        match_count+=1
    if color_match_array_list(1258,17,gbdata.phone_map_background_list,7):
        match_count+=1
    if color_match_array_list(1263,694,gbdata.phone_map_background_list,7):
        match_count+=1
    if color_match_array_list(674,686,gbdata.phone_map_background_list,7):
        match_count+=1
    if color_match_array_list(829,708,gbdata.phone_map_background_list,7):
        match_count+=1
    print("match_count",match_count)
    if match_count >= 5:
        return True
    return False

def is_resident_nearby():
    if has_label_prefix('Res',0.30,-1,-1,-1):
        return True
    return False

def locate_vertical_transition(color,sx,sy1,sy2):

    # Get the initial location to determine if we are looking for the
    # color to go away or to appear.

    if color_match_array(sx,sy1,color,5):
        # We are looking for the color to go away.
        for sy in range(sy1+1,sy2+1):
            if not color_match_array(sx,sy,color,5):
                return sy-1 # return the last location where the color was found
    else:
        # We are looking for the color to appear.
        for sy in range(sy1+1,sy2+1):
            if color_match_array(sx,sy,color,5):
                return sy # return the first location where the color was found
    return -1

def locate_horizontal_extent(color,sy,sx1,sx2):
    extent_sx=sx1
    if sx1 < sx2:
        # search right
        start_sx=sx1
        end_sx=sx2+1
        step=1
    else:
        # search left
        start_sx=sx1
        end_sx=sx2-1
        step=-1
    for sx in range(start_sx,end_sx,step):
        if color_match_array(sx,sy,color,5):
            extent_sx=sx
    return extent_sx

def locate_vertical_extent(color,sx,sy1,sy2):
    extent_sy=sy1
    if sy1 < sy2:
        # search down
        start_sy=sy1
        end_sy=sy2+1
        step=1
    else:
        # search up
        start_sy=sy1
        end_sy=sy2-1
        step=-1
    #print(start_sy,end_sy,step)
    for sy in range(start_sy,end_sy,step):
        if color_match_array(sx,sy,color,5):
            extent_sy=sy
    return extent_sy

def is_nook_miles_screen():
    with gbstate.detection_lock:
        if gbstate.digested is None:
            return False
    if not has_label('PointerHand',0.30,-1,-1,-1):
        print("no PointerHand")
        return False
    match_count=0
    if has_label('ButtonPlus',0.10,723,68,5):
        match_count+=1
    if has_label('ButtonB',0.30,999,692,5):
        match_count+=1
    if has_label('ButtonA',0.10,1130,691,5):
        match_count+=1
    if match_count < 2:
        print("match_count 1",match_count)
        return False
    match_count=0
    if color_match_array(31,44,gbdata.nook_miles_screen_banner_color,5):
        match_count+=1
    if color_match_array(1039,48,gbdata.nook_miles_screen_banner_color,5):
        match_count+=1
    if color_match_array(14,164,gbdata.nook_miles_screen_color,5):
        match_count+=1
    if color_match_array(20,679,gbdata.nook_miles_screen_color,5):
        match_count+=1
    if color_match_array(1265,155,gbdata.nook_miles_screen_color,5):
        match_count+=1
    if color_match_array(1257,665,gbdata.nook_miles_screen_color,5):
        match_count+=1
    if match_count >= 5:
        return True
    print("match_count 2",match_count)
    return False

def is_diy_screen():
    gblogfile.log('is_diy_screen')
    gbstate.debug_window=True
    match_count=0
    if color_match_array_list(16,16,gbdata.diy_screen_color_list,5):
        match_count+=1
    if color_match_array_list(16,720-16,gbdata.diy_screen_color_list,5):
        match_count+=1
    if color_match_array_list(1280-16,16,gbdata.diy_screen_color_list,5):
        match_count+=1
    if color_match_array_list(1280-16,720-16,gbdata.diy_screen_color_list,5):
        match_count+=1
    gbstate.debug_window=False
    if match_count >= 3:
        return True
    print("match_count 3",match_count)
    return False

def is_inside_building_screen():
    with gbstate.detection_lock:
        if gbstate.digested is None:
            return False
    if is_minimap():
        return False
    if not has_label('ButtonZL',0.30,94,56,5):
        if not has_label('ButtonZL',0.30,73,37,5):
            return False
    return True

def is_pin_orange(pixel_x,pixel_y):
    pixel_x=int(round(pixel_x))
    pixel_y=int(round(pixel_y))
    if color_match_array_list(pixel_x,pixel_y,gbdata.pin_color_list,5):
        return True
    (pb,pg,pr)=get_pixel(pixel_x,pixel_y)
    gbmap.log_closest_type(pr,pg,pb)
    return False
