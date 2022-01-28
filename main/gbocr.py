#
# Copyright 2021 by angry-kitten
# Gamebot OCR support.
#

import os, sys, time, random, threading
import difflib
import easyocr
import gbdata, gbstate
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
    gbstate.ocr_reader=easyocr.Reader(['en'], gpu=False)
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
    result=None
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
    if s1 in s2:
        print("s1 in s2")
        return 0.95
    if s2 in s1:
        print("s2 in s1")
        return 0.95
    return v

def move_hand_to_slot(slot,obj):
    if slot == gbstate.hand_slot:
        print("pointing at slot")
        return
    slot_row=int(slot/10)
    slot_column=int(slot%10)
    hand_row=int(gbstate.hand_slot/10)
    hand_column=int(gbstate.hand_slot%10)
    while slot_row < hand_row:
        # move pointer hand up
        gbstate.hand_slot-=10
        obj.parent.Push(taskobject.TaskTimed(gbdata.move_wait)) # wait for animation
        obj.parent.Push(taskpress.TaskPress('hat_TOP'))
        hand_row=int(gbstate.hand_slot/10)
    while slot_row > hand_row:
        # move pointer hand down
        gbstate.hand_slot+=10
        obj.parent.Push(taskobject.TaskTimed(gbdata.move_wait)) # wait for animation
        obj.parent.Push(taskpress.TaskPress('hat_BOTTOM'))
        hand_row=int(gbstate.hand_slot/10)
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
                obj.parent.Push(taskobject.TaskTimed(gbdata.move_wait)) # wait for animation
                obj.parent.Push(taskpress.TaskPress('hat_RIGHT'))
                hand_column=int(gbstate.hand_slot%10)
        else:
            print("no wrap")
            while slot_column < hand_column:
                # move pointer hand left
                gbstate.hand_slot-=1
                obj.parent.Push(taskobject.TaskTimed(gbdata.move_wait)) # wait for animation
                obj.parent.Push(taskpress.TaskPress('hat_LEFT'))
                hand_column=int(gbstate.hand_slot%10)

    if slot_column > hand_column:
        # move pointer hand right
        delta=slot_column-hand_column
        if delta > 5:
            print("wrap")
            for j in range((10-delta)):
                # move pointer hand left
                if hand_column == 0:
                    gbstate.hand_slot+=9
                else:
                    gbstate.hand_slot-=1
                obj.parent.Push(taskobject.TaskTimed(gbdata.move_wait)) # wait for animation
                obj.parent.Push(taskpress.TaskPress('hat_LEFT'))
                hand_column=int(gbstate.hand_slot%10)
        else:
            print("no wrap")
            while slot_column > hand_column:
                # move pointer hand right
                gbstate.hand_slot+=1
                obj.parent.Push(taskobject.TaskTimed(gbdata.move_wait)) # wait for animation
                obj.parent.Push(taskpress.TaskPress('hat_RIGHT'))
                hand_column=int(gbstate.hand_slot%10)
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
        if mscore > best_mscore:
            best_mscore=mscore
    print("best_mscore",best_mscore)
    if best_mscore > 0.8:
        return True
    return False

def ocr_name_to_inv_name(ocr_name):
    inv_name=None
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
