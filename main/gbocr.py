#
# Copyright 2021 by angry-kitten
# Gamebot OCR support.
#

import os, sys, time, random, threading
import easyocr
import gbdata, gbstate
import threadmanager

# example data:
# [([[968, 208], [1038, 208], [1038, 216], [968, 216]], '1', 0.008175754888339937), ([[1042, 208], [1064, 208], [1064, 216], [1042, 216]], '3', 0.010153401497510706), ([[1069, 208], [1153, 208], [1153, 216], [1069, 216]], '3', 0.007057148914849043), ([[98, 588], [218, 588], [218, 640], [98, 640]], '3.27', 0.7056293487548828), ([[228, 608], [282, 608], [282, 638], [228, 638]], 'AM', 0.9678678383256856), ([[46, 658], [236, 658], [236, 690], [46, 690]], 'December 27', 0.9993508211254571), ([[256, 656], [321, 656], [321, 686], [256, 686]], 'Mon:', 0.8180626034736633)]
# array of detections
# tuple(3) of box, text, score
# box is an array of four arrays, each with a screen x and y
#     upper left, upper right, lower right, lower left

def init_ocr():
    gbstate.ocr_reader=easyocr.Reader(['en'], gpu=False)
    gbstate.ocr_worker_thread=threadmanager.ThreadManager(ocr_worker)
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
        with gbstate.ocr_worker_thread.data_lock:
            gbstate.ocr_detections=[]
    print("after ocr_worker")
    return

def run_ocr_on_frame(frame):
    result=gbstate.ocr_reader.readtext(frame,paragraph=False,workers=4)
    print(result)
    if result is None:
        result=[]
    with gbstate.ocr_worker_thread.data_lock:
        gbstate.ocr_detections=result
    return
