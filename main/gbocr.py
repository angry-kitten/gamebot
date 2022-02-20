#
# Copyright 2021-2022 by angry-kitten
# Gamebot OCR support.
#

import os, sys, time, random, threading
import re
import difflib
import easyocr
import gbdata, gbstate
import gbscreen
import threadmanager
import taskobject
import taskpress

# example data:
# [([[968, 208], [1038, 208], [1038, 216], [968, 216]], '1', 0.008175754888339937), ([[1042, 208], [1064, 208], [1064, 216], [1042, 216]], '3', 0.010153401497510706), ([[1069, 208], [1153, 208], [1153, 216], [1069, 216]], '3', 0.007057148914849043), ([[98, 588], [218, 588], [218, 640], [98, 640]], '3.27', 0.7056293487548828), ([[228, 608], [282, 608], [282, 638], [228, 638]], 'AM', 0.9678678383256856), ([[46, 658], [236, 658], [236, 690], [46, 690]], 'December 27', 0.9993508211254571), ([[256, 656], [321, 656], [321, 686], [256, 686]], 'Mon:', 0.8180626034736633)]
# array of detections
# tuple(3) of box, text, score
# box is an array of four arrays, each with a screen x and y
#     upper left, upper right, lower right, lower left

def init_ocr():
    #gbstate.ocr_reader=easyocr.Reader(['en'], gpu=False)
    #gbstate.ocr_reader=easyocr.Reader(['en'], gpu=True)
    gbstate.ocr_reader=easyocr.Reader(['en'], gpu='GPU:1')
    gbstate.ocr_worker_thread=threadmanager.ThreadManager(ocr_worker,"OCR")
    return

def ocr_worker():
    print("before ocr_worker")
    with gbstate.ocr_worker_thread.data_lock:
        gbstate.ocr_detections=None
        ocr_frame=gbstate.ocr_frame
        gbstate.ocr_frame=None
    if ocr_frame is not None:
        run_ocr_on_frame(ocr_frame)
    else:
        print("no ocr_frame")
        tnow=time.monotonic()
        with gbstate.ocr_worker_thread.data_lock:
            gbstate.ocr_detections=[]
            gbstate.ocr_detections_set_time=tnow
    print("after ocr_worker")
    return

def run_ocr_on_frame(frame):
    #result=gbstate.ocr_reader.readtext(frame,paragraph=False,workers=4)
    #result=gbstate.ocr_reader.readtext(frame,paragraph=False,workers=4,min_size=5)
    #result=None
    result=gbstate.ocr_reader.readtext(frame,paragraph=False)
    print(result)
    if result is None:
        result=[]
    tnow=time.monotonic()
    with gbstate.ocr_worker_thread.data_lock:
        gbstate.ocr_detections=result
        gbstate.ocr_detections_set_time=tnow
    return

def ocr_box_to_center(box):
    ul=box[0]
    ur=box[1]
    lr=box[2]
    ll=box[3]
    csx=(ul[0]+ur[0]+lr[0]+ll[0])/4
    csy=(ul[1]+ur[1]+lr[1]+ll[1])/4
    return (csx,csy)

# (index,is_last)=gbocr.locate_menu_text(self.ocr_menu,'Put in Storage')
def locate_menu_text(menu,text):
    print("locate_menu_text")
    index=None
    is_last=False
    l=len(menu)
    if l < 1:
        return (index,is_last)
    for j in range(l):
        entry=menu[j]
        print("entry",entry)
        if entry[1] == text:
            print("found",text)
            index=j
            if j == (l-1):
                is_last=True
            return (index,is_last)
    # Try again but with some fuzz
    best_score=0
    best_index=None
    best_is_last=False
    for j in range(l):
        entry=menu[j]
        print("entry",entry)
        score=score_close_string_match(entry[1],text)
        if best_index is None:
            best_index=j
            best_score=score
            if j == (l-1):
                best_is_last=True
            else:
                best_is_last=False
        elif best_score < score:
            best_index=j
            best_score=score
            if j == (l-1):
                best_is_last=True
            else:
                best_is_last=False
    if best_index is None:
        return (index,is_last)
    if best_score < 0.8:
        return (index,is_last)
    index=best_index
    is_last=best_is_last
    return (index,is_last)

def score_close_string_match(s1,s2):
    print(f"score_close_string_match [{s1}] [{s2}]")
    matcher=difflib.SequenceMatcher(None,s1,s2)
    v=matcher.ratio()
    print("ratio",v)
    if s1 == s2:
        return 1.0
    #if s1 in s2:
    #    print("s1 in s2")
    #    return 0.95
    #if s2 in s1:
    #    print("s2 in s1")
    #    return 0.95
    return v

def move_hand_to_slot(slot,obj):
    if slot == gbstate.hand_slot:
        print("pointing at slot")
        return

    # Build a list of moves, then push tasks in reverse order.

    move_list=[]
    if gbstate.hand_slot >= gbstate.inventory_size:
        print("pointer hand in irregular slots")
        if gbstate.hand_slot == gbstate.inventory_size:
            print("bag slot")
            # move pointer hand up
            gbstate.hand_slot-=10
            #obj.parent.Push(taskobject.TaskTimed(gbdata.move_wait)) # wait for animation
            #obj.parent.Push(taskpress.TaskPress('hat_TOP'))
            print("up from bag")
            move_list.append('up')
        elif gbstate.hand_slot == gbstate.inventory_size+1:
            print("clothing slot")
            # move pointer hand up
            gbstate.hand_slot-=9
            #obj.parent.Push(taskobject.TaskTimed(gbdata.move_wait)) # wait for animation
            #obj.parent.Push(taskpress.TaskPress('hat_TOP'))
            print("up from clothing")
            move_list.append('up')
    slot_row=int(slot/10)
    slot_column=int(slot%10)
    hand_row=int(gbstate.hand_slot/10)
    hand_column=int(gbstate.hand_slot%10)
    while slot_row < hand_row:
        # move pointer hand up
        gbstate.hand_slot-=10
        #obj.parent.Push(taskobject.TaskTimed(gbdata.move_wait)) # wait for animation
        #obj.parent.Push(taskpress.TaskPress('hat_TOP'))
        hand_row=int(gbstate.hand_slot/10)
        print("up")
        move_list.append('up')
    while slot_row > hand_row:
        # move pointer hand down
        gbstate.hand_slot+=10
        #obj.parent.Push(taskobject.TaskTimed(gbdata.move_wait)) # wait for animation
        #obj.parent.Push(taskpress.TaskPress('hat_BOTTOM'))
        hand_row=int(gbstate.hand_slot/10)
        print("down")
        move_list.append('down')
    if slot_column < hand_column:
        # move pointer hand left
        delta=hand_column-slot_column
        if delta > 5:
            print("wrap")
            for j in range((10-delta)):
                # move pointer hand right
                if hand_column == 9:
                    gbstate.hand_slot-=9
                else:
                    gbstate.hand_slot+=1
                #obj.parent.Push(taskobject.TaskTimed(gbdata.move_wait)) # wait for animation
                #obj.parent.Push(taskpress.TaskPress('hat_RIGHT'))
                hand_column=int(gbstate.hand_slot%10)
                print("right")
                move_list.append('right')
        else:
            print("no wrap")
            while slot_column < hand_column:
                # move pointer hand left
                gbstate.hand_slot-=1
                #obj.parent.Push(taskobject.TaskTimed(gbdata.move_wait)) # wait for animation
                #obj.parent.Push(taskpress.TaskPress('hat_LEFT'))
                hand_column=int(gbstate.hand_slot%10)
                print("left")
                move_list.append('left')

    if slot_column > hand_column:
        # move pointer hand right
        delta=slot_column-hand_column
        if delta > 5:
            print("wrap 2")
            for j in range((10-delta)):
                # move pointer hand left
                if hand_column == 0:
                    gbstate.hand_slot+=9
                else:
                    gbstate.hand_slot-=1
                #obj.parent.Push(taskobject.TaskTimed(gbdata.move_wait)) # wait for animation
                #obj.parent.Push(taskpress.TaskPress('hat_LEFT'))
                hand_column=int(gbstate.hand_slot%10)
                print("left 2")
                move_list.append('left')
        else:
            print("no wrap 2")
            while slot_column > hand_column:
                # move pointer hand right
                gbstate.hand_slot+=1
                #obj.parent.Push(taskobject.TaskTimed(gbdata.move_wait)) # wait for animation
                #obj.parent.Push(taskpress.TaskPress('hat_RIGHT'))
                hand_column=int(gbstate.hand_slot%10)
                print("right 2")
                move_list.append('right')

    # now push the moves in the reverse order so they run in the correct order
    move_list.reverse()
    for m in move_list:
        if m == 'up':
            obj.parent.Push(taskobject.TaskTimed(gbdata.move_wait)) # wait for animation
            obj.parent.Push(taskpress.TaskPress('hat_TOP'))
        elif m == 'down':
            obj.parent.Push(taskobject.TaskTimed(gbdata.move_wait)) # wait for animation
            obj.parent.Push(taskpress.TaskPress('hat_BOTTOM'))
        elif m == 'left':
            obj.parent.Push(taskobject.TaskTimed(gbdata.move_wait)) # wait for animation
            obj.parent.Push(taskpress.TaskPress('hat_LEFT'))
        elif m == 'right':
            obj.parent.Push(taskobject.TaskTimed(gbdata.move_wait)) # wait for animation
            obj.parent.Push(taskpress.TaskPress('hat_RIGHT'))
    return

def combine_menu_entries(menu):
    newmenu=[]
    if len(menu) < 1:
        return menu
    # Sort the menu by sy
    smenu=sorted(menu,key=lambda entry: entry[0])
    for e in smenu:
        l=len(newmenu)
        if l < 1:
            newmenu.append(e)
            continue
        previous_sy=newmenu[l-1][0]
        e_sy=e[0]
        print("previous and e",previous_sy,e_sy,e[1])
        if e_sy < (previous_sy+4):
            print("combine")
            newtext=newmenu[l-1][1]+' '+e[1]
            print("newtext",newtext)
            newmenu[l-1][1]=newtext
            continue
        newmenu.append(e)

    return newmenu

def ocr_results_contain(s):
    print("ocr_results_contain",s)
    with gbstate.ocr_worker_thread.data_lock:
        dets=gbstate.ocr_detections
    if dets is None:
        return False
    best_mscore=0
    for det in dets:
        print("det",det)
        (box,text,score)=det
        mscore=score_close_string_match(text,s)
        print("mscore",mscore)
        if mscore >= 1.0:
            return True
        if mscore > best_mscore:
            best_mscore=mscore
    print("best_mscore",best_mscore)
    if best_mscore > 0.8:
        return True
    return False

def ocr_name_to_inv_name(ocr_name):
    inv_name=None
    # Check for bell bag star first because it has the
    # number of bells in the ocr_name. This makes it hard
    # to match a fixed string.
    if re.fullmatch(r'\s*[\d,.]*\s*[Bb]ells\s*',ocr_name):
        inv_name='InvBellBagStar'
        return inv_name
    if ocr_name in gbdata.ocr_to_inventory:
        inv_name=gbdata.ocr_to_inventory[ocr_name]
        print("inv_name",inv_name)
        return inv_name
    best_ocr_name=None
    best_mscore=0
    for k in gbdata.ocr_to_inventory.keys():
        print("k",k)
        mscore=score_close_string_match(k,ocr_name)
        print("mscore",mscore)
        if best_ocr_name is None:
            best_ocr_name=k
            best_mscore=mscore
        else:
            if mscore > best_mscore:
                best_ocr_name=k
                best_mscore=mscore
    print("best",best_ocr_name,best_mscore)
    if best_mscore > 0.7:
        inv_name=gbdata.ocr_to_inventory[best_ocr_name]
        print("inv_name",inv_name)
    return inv_name

def digest_inv_screen_name():
    gbstate.ocr_name=None
    with gbstate.ocr_worker_thread.data_lock:
        dets=gbstate.ocr_detections
    if dets is None:
        return
    (slot_sx,slot_sy)=gbstate.inventory_locations[gbstate.hand_slot]
    expect_name_sx=slot_sx
    expect_name_sy=slot_sy+gbdata.ocr_inv_name_offset_y
    for det in dets:
        print("det",det)
        (box,text,score)=det
        (csx,csy)=ocr_box_to_center(box)
        if gbscreen.is_near_within(expect_name_sx,expect_name_sy,csx,csy,gbstate.ocr_name_within):
            print("item name")
            gbstate.ocr_name=text
            continue
    return

# Example OCR data
# [([[439, 35], [641, 35], [641, 73], [439, 73]], 'Vaulting pole', 0.9577903529709549), ([[797, 339], [959, 339], [959, 380], [797, 380]], 'Place Item', 0.8997346079334698), ([[327, 394], [454, 394], [454, 446], [327, 446]], '23,555', 0.726360381715388), ([[801, 394], [1015, 394], [1015, 433], [801, 433]], 'Put in Storage', 0.9066206404337775), ([[802, 452], [924, 452], [924, 484], [802, 484]], 'Favorite', 0.9996292247387993), ([[989, 681], [1009, 681], [1009, 703], [989, 703]], 'B', 0.9999361048414812), ([[1013, 675], [1096, 675], [1096, 711], [1013, 711]], 'Close', 0.9999234436005648), ([[1148, 678], [1238, 678], [1238, 710], [1148, 710]], 'Select', 0.9999911425992467), ([[377.4871464448379, 184.4665807565786], [552.2369732838534, 160.82192444134853], [556.5128535551621, 223.5334192434214], [382.7630267161465, 247.17807555865147]], '0 P &', 0.6320404477802022)]
def digest_inv_screen_menu():
    gbstate.ocr_menu=None
    with gbstate.ocr_worker_thread.data_lock:
        dets=gbstate.ocr_detections
    if dets is None:
        return
    menu=digest_screen_region_text(gbdata.ocr_inv_menu_lane_x1,gbdata.ocr_inv_menu_lane_x2,gbdata.ocr_inv_menu_lane_y1,gbdata.ocr_inv_menu_lane_y2)
    if menu is None:
        return
    gbstate.ocr_menu=menu
    return

def digest_screen_region_text(x1,x2,y1,y2):
    result=None
    with gbstate.ocr_worker_thread.data_lock:
        dets=gbstate.ocr_detections
    if dets is None:
        return result
    result=[]
    for det in dets:
        print("det",det)
        (box,text,score)=det
        (csx,csy)=ocr_box_to_center(box)
        if gbscreen.is_inside_box(x1,x2,y1,y2,csx,csy):
            print("text item")
            entry=[csy,text,box]
            result.append(entry)
            continue
    if len(result) < 1:
        result=None
    else:
        # Sort the text by sy
        result=sorted(result,key=lambda entry: entry[0])
    return result

def digest_recipe_screen_text():
    result=None
    with gbstate.ocr_worker_thread.data_lock:
        dets=gbstate.ocr_detections
    if dets is None:
        return result
    result=digest_screen_region_text(gbdata.ocr_recipe_lane_x1,gbdata.ocr_recipe_lane_x2,gbdata.ocr_recipe_lane_y1,gbdata.ocr_recipe_lane_y2)
    return result

def nearest_entry_index(t,sy):
    if t is None:
        return None
    if len(t) < 1:
        return None
    best_dy=None
    best_j=None
    for j in range(len(t)):
        e=t[j]
        ty=e[0]
        dy=int(abs(sy-ty))
        if best_dy is None:
            best_dy=dy
            best_j=j
        elif dy < best_dy:
            best_dy=dy
            best_j=j

    if best_dy is None:
        return None
    return best_j
