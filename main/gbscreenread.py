#
# Copyright 2021 by angry-kitten
# Look at the detections and pull the characters out. Set the results up
# for display in gbdisplay.py
#

import taskobject
import gbdata
import gbstate
import cv2
import taskpress
import taskdetect
import gbdisplay
import math
import time

def screen_read():
    print("screen_read")
    with gbstate.detection_lock:
        if gbstate.digested is None:
            return False
        localdigested=gbstate.digested

    # Format is [ letter_string, sx, sy ]
    gbstate.screen_chars=[]
    first_pass=[]
    for det in localdigested:
        print(det) # det is [name,score,cx,cy,bx,by,x1,x2,y1,y2]
        # Set a minimum score of 10%
        if det[1] >= 0.1:
            name=det[0]
            prefix=name[0:4] # The first 4 letters of name
            if prefix == 'Char':
                body=name[4:] # Everything after the first 4 characters
                print(name,prefix,body)
                l=len(body)
                body2=body
                if l == 1:
                    # It's one of the basic characters.
                    # entry is [name,score,cx,cy,x1,x2,y1,y2]
                    body2=body
                elif body == 'Dot':
                    body2='.'
                elif body == 'PercentSign':
                    body2='%'
                elif body == 'Colon':
                    body2=':'
                elif body == 'Comma':
                    body2=','
                elif body == 'Exclamation':
                    body2='!'
                elif body == 'Apostrophe':
                    body2="'"

                entry=[body2,det[1],det[2],det[3],det[6],det[7],det[8],det[9]]
                first_pass.append(entry)

    # Now go through the list and clear out overlaps.
    # Overlap means one character overlaps the center of the other.
    second_pass=[]
    for entry in first_pass:
        if check_no_overlap(entry,second_pass):
            second_pass.append(entry)

    # Now remove all the entries with name set to None
    third_pass=[]
    for entry in second_pass:
        if entry[0] is not None:
            third_pass.append(entry)

    gbstate.screen_chars=third_pass

def is_overlap_a_over_b(entry1,entry2):
    # entry is [name,score,cx,cy,x1,x2,y1,y2]
    cx=entry2[2]
    cy=entry2[3]
    x1=entry1[4]
    x2=entry1[5]
    y1=entry1[6]
    y2=entry1[7]
    if x1 <= cx and cx <= x2:
        if y1 <= cy and cy <= y2:
            return True
    return False

def is_overlap(entry1,entry2):
    if is_overlap_a_over_b(entry1,entry2):
        return True
    if is_overlap_a_over_b(entry2,entry1):
        return True
    return False

def check_no_overlap(entry,new_list):
    j=0
    l=len(new_list)
    for j in range(l):
        entry2=new_list[j]
        if entry2[0] is not None:
            if is_overlap(entry,entry2):
                # Compare scores.
                if entry[1] <= entry2[1]:
                    return False  # Don't add entry to the list.
                # entry2 needs to be delted from the list.
                entry2[0]=None
    return True # entry does not overlap anything in new_list

def draw_screen_read(frame):
    """Draw the detected characters on the main window."""
    #print("draw_screen_read")

    for entry in gbstate.screen_chars:
        # entry is [name,score,cx,cy,x1,x2,y1,y2]
        body=entry[0]
        sx=entry[2]
        sy=entry[3]
        sx=int(round(sx))
        sy=int(round(sy))
        cv2.putText(frame,body,(sx,sy),gbdisplay.font,gbdisplay.font_scale_50,gbdisplay.color_black,gbdisplay.font_line_width,gbdisplay.line_type)
