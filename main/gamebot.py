#!/usr/bin/env python3
#
# Copyright 2021 by angry-kitten
# Gamebot main program.
#

import sys
import os
import time
import random
import threading
import cv2
import imutils
import object_detection
import tensorflow as tf
from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils
from object_detection.builders import model_builder
from object_detection.utils import config_util
import numpy
from matplotlib import pyplot

import gbdata
import gbstate
import gbdisplay

import taskobject
import tasksay
import taskdetect
import tasktakestock
import taskdosomething
import taskupdatemini
import tasktest
import tasktest2
import tasktest3
import tasktest4
import tasktest5
import taskupdatephonemap
import taskdetermineposition
import tasktrackgoto
import tasktakeinventory
import gbscreenread
import taskmuseum


sys.path.append(os.path.join(os.getcwd(),"..","..","gamebot-serial","pylib"))
#print(sys.path)
import packetserial

# change this to select which webcam to use
#default_camera_index=2
default_camera_index=0

gbstate.modelpath=os.path.join("..","model");
print("modelpath=",gbstate.modelpath)


# Set the apparently platform specific key codes.
print("os",os.name)

if "posix" == os.name:
    keycode_numpad_8=151
    keycode_numpad_6=152
    keycode_numpad_4=150
    keycode_numpad_2=153
    
def process_detections(d):
    if d is None:
        print("detections does not exist")
        return
    n=d['num_detections']
    print("n=",n)
    boxes=d['detection_boxes']
    scores=d['detection_scores']
    classes=d['detection_classes']
    anchors=d['detection_anchor_indices']
    #print("boxes=",boxes)
    #print("scores=",scores)
    #print("classes=",classes)
    #print("anchors=",anchors)
    #print("index=",gbstate.category_index)
    #print("offset=",gbstate.label_id_offset)

    # build a list of digested detections
    digested=[]
    for j in range(n):
        #print("j=",j)
        detectclass=classes[j]
        #print("detectclass=",detectclass)
        e=gbstate.category_index[detectclass+gbstate.label_id_offset]
        #print("e=",e)
        name=e['name']
        #print("name=",name)
        box=boxes[j]
        # box is [y1,x1,y2,x2]
        # y is down, x is right
        #print("box=",box)
        score=scores[j]
        #print("score=",score)
        y1=box[0]*gbdata.stdscreen_size[1]
        x1=box[1]*gbdata.stdscreen_size[0]
        y2=box[2]*gbdata.stdscreen_size[1]
        x2=box[3]*gbdata.stdscreen_size[0]
        #print(x1,y1,x2,y2)
        cx=(x1+x2)/2
        cy=(y1+y2)/2
        bx=cx
        by=y2
        #print(cx,cy)
        found=[name,score,cx,cy,bx,by,x1,x2,y1,y2]
        #print("found=",found)
        digested.append(found)
    #print(digested)
    for det in digested:
        print(det)
    return digested

def do_one_object_detect(dframe):

    # convert the image format to what is needed for object detection
    image_np=numpy.array(dframe)
    input_tensor=tf.convert_to_tensor(numpy.expand_dims(image_np,0),dtype=tf.float32)

    # run the image through the model
    image_pre, shapes=gbstate.model.preprocess(input_tensor)
    prediction_dict=gbstate.model.predict(image_pre,shapes)
    detections=gbstate.model.postprocess(prediction_dict,shapes)

    num_detections=int(detections.pop('num_detections'))
    detections={key: value[0, :num_detections].numpy()
                for key, value in detections.items()}
    detections['num_detections']=num_detections

    detections['detection_classes']=detections['detection_classes'].astype(numpy.int64)

    image_np_with_detections=image_np.copy()

    visualization_utils.visualize_boxes_and_labels_on_image_array(
        image_np_with_detections,
        detections['detection_boxes'],
        detections['detection_classes']+gbstate.label_id_offset,
        detections['detection_scores'],
        gbstate.category_index,
        use_normalized_coordinates=True,
        max_boxes_to_draw=gbdata.object_count,
        min_score_thresh=.1,
        agnostic_mode=False)

    #cv2.imshow("show detections",cv2.resize(image_np_with_detections,(800,600)))
    #cv2.imshow("show detections",image_np_with_detections)

    digested=process_detections(detections)

    return (detections,digested,image_np_with_detections)

def debug_show_state():
    gbstate.tasks.DebugRecursive()
    #print(gbstate.detections)

def debug_get_name():
    return gbstate.tasks.NameRecursive()

def process_key(key):
    print("key=",key)
    if ord('a') == key:
        #gbstate.ps.move_left_joy_left(gbstate.keydown_time_ms)
        gbstate.ps.move_left_joy_left()
        return 0
    if ord('d') == key:
        #gbstate.ps.move_left_joy_right(gbstate.keydown_time_ms)
        gbstate.ps.move_left_joy_right()
        return 0
    if ord('w') == key:
        #gbstate.ps.move_left_joy_up(gbstate.keydown_time_ms)
        gbstate.ps.move_left_joy_up()
        return 0
    if ord('s') == key:
        #gbstate.ps.move_left_joy_down(gbstate.keydown_time_ms)
        gbstate.ps.move_left_joy_down()
        return 0
    if ord('f') == key:
        #gbstate.ps.move_right_joy_left(gbstate.keydown_time_ms)
        gbstate.ps.move_right_joy_left()
        return 0
    if ord('h') == key:
        #gbstate.ps.move_right_joy_right(gbstate.keydown_time_ms)
        gbstate.ps.move_right_joy_right()
        return 0
    if ord('t') == key:
        #gbstate.ps.move_right_joy_up(gbstate.keydown_time_ms)
        gbstate.ps.move_right_joy_up()
        return 0
    if ord('g') == key:
        #gbstate.ps.move_right_joy_down(gbstate.keydown_time_ms)
        gbstate.ps.move_right_joy_down()
        return 0
    if ord('8') == key:
        gbstate.ps.press_X()
        return 0
    if ord('6') == key:
        gbstate.ps.press_A()
        return 0
    if ord('4') == key:
        gbstate.ps.press_Y()
        return 0
    if ord('2') == key:
        gbstate.ps.press_B()
        return 0
    if keycode_numpad_8 == key:
        gbstate.ps.press_X()
        return 0
    if keycode_numpad_6 == key:
        gbstate.ps.press_A()
        return 0
    if keycode_numpad_4 == key:
        gbstate.ps.press_Y()
        return 0
    if keycode_numpad_2 == key:
        gbstate.ps.press_B()
        return 0
    if ord('+') == key:
        gbstate.ps.press_PLUS()
        return 0
    if ord('-') == key:
        gbstate.ps.press_MINUS()
        return 0
    if ord('u') == key:
        gbstate.ps.press_ZL()
        return 0
    if ord('j') == key:
        gbstate.ps.press_L()
        return 0
    if ord('i') == key:
        gbstate.ps.press_ZR()
        return 0
    if ord('k') == key:
        gbstate.ps.press_R()
        return 0
    if ord('q') == key:
        return -1
    if ord('b') == key:
        debug_show_state()
        return 0
    if ord('p') == key:
        # get current position
        gbstate.tasks.AddToThread(0,taskdetermineposition.TaskDeterminePosition())
        return 0
    if ord('z') == key:
        # run a test task
        #gbstate.tasks.AddToThread(0,tasktest.TaskTest())
        #gbstate.tasks.AddToThread(0,tasktest2.TaskTest2())
        #gbstate.tasks.AddToThread(0,tasktest3.TaskTest3())
        #gbstate.tasks.AddToThread(0,taskupdatephonemap.TaskUpdatePhoneMap())
        #gbstate.tasks.AddToThread(0,tasktest4.TaskTest4())
        #gbstate.tasks.AddToThread(0,tasktest5.TaskTest5())
        #gbstate.tasks.AddToThread(0,tasktakeinventory.TaskTakeInventory())
        #gbstate.tasks.AddToThread(0,taskupdatephonemap.TaskUpdatePhoneMap())
        gbstate.tasks.AddToThread(0,taskmuseum.TaskMuseum())
        # yyy
        return 0
    if ord(';') == key:
        print("test up")
        gbstate.tasks.AddToThread(0,tasktrackgoto.TaskTrackGoTo(gbstate.player_mx,gbstate.player_my-1.0))
        return 0
    if ord('.') == key:
        print("test down")
        gbstate.tasks.AddToThread(0,tasktrackgoto.TaskTrackGoTo(gbstate.player_mx,gbstate.player_my+1.0))
        return 0
    if ord(',') == key:
        print("test left")
        gbstate.tasks.AddToThread(0,tasktrackgoto.TaskTrackGoTo(gbstate.player_mx-1.0,gbstate.player_my))
        return 0
    if ord('/') == key:
        print("test right")
        gbstate.tasks.AddToThread(0,tasktrackgoto.TaskTrackGoTo(gbstate.player_mx+1.0,gbstate.player_my))
        return 0
    return key

def query_state(ps):
    test_time_sec=10

    (flags,head,tail,count,ic,cem,echo_count)=ps.request_query_state()
    print(f"flags={flags}")
    if flags & ps.GB_FLAGS_CONFIGURED:
        print("configured")
    else:
        print("not configured")
    print(f"head={head}")
    print(f"tail={tail}")
    print(f"count={count}")
    print(f"ic={ic}")
    print(f"cem={cem}")
    print(f"echo_count={echo_count}")

def object_detection_thread():
    dframe=None
    do_detect=False
    localdetections=None
    localdigested=None
    while True:
        #print("odt")
        dframe=None
        do_detect=False
        localdetections=None
        localdigested=None
        with gbstate.detection_lock:
            if gbstate.detection_frame is not None:
                if gbstate.detections is None:
                    dframe=gbstate.detection_frame
                    do_detect=True
        if do_detect:
            print("start a detection")
            (localdetections,localdigested,localim)=do_one_object_detect(dframe)
            if localdetections is not None:
                with gbstate.detection_lock:
                    gbstate.detections=localdetections
                    gbstate.digested=localdigested
                    gbstate.detim=localim
        else:
            #print("no detection")
            time.sleep(1)

def main_loop(vid):

    debugtime=time.monotonic()+gbstate.debug_every
    start_delay_frames=5 # capture this many frames to get past startup noise
    prebuild_window=True

    while(True):
        #query_state(gbstate.ps)
        # From query_state it shows that when the console is powered down
        # or in sleep mode that the USB device is not configured. That
        # makes it impossible to wake it from the USB device without
        # USB remote wakeup support.

        if gbstate.frame is None:
            print("g_frame does not exist")

        gbstate.tasks.Poll()
        #gbstate.tasks.DebugRecursive()
        #n=debug_get_name()
        #print("n=",n)

        # get a frame
        ret, frame = vid.read()

        #print("ret",ret);
        height, width, channels=frame.shape
        #print("width",width,"height",height,"channels",channels)

        gbstate.frame=frame

        # show the frame as captured
        # scale it down to save screen space
        #scaled=imutils.resize(frame,width=320) # maintains aspect
        scaled=frame.copy()
        if prebuild_window:
            cv2.imshow("show detections",scaled)
            cv2.moveWindow("show detections",1024,0)
            prebuild_window=False
        gbdisplay.draw_on(scaled)
        cv2.imshow('captured',scaled)

        if start_delay_frames > 0:
            start_delay_frames-=1
            continue

        now=time.monotonic()
        if now >= debugtime:
            debugtime=time.monotonic()+gbstate.debug_every
            #gbstate.tasks.DebugRecursive()

        if gbstate.frame is not None:
            with gbstate.detection_lock:
                gbstate.detection_frame=gbstate.frame

        showme=None
        with gbstate.detection_lock:
            if gbstate.detim is not None:
                showme=gbstate.detim
        if showme is not None:
            cv2.imshow("show detections",showme)

        # Exit on any key press.
        key=cv2.waitKey(2)
        if key > 0:
            result=process_key(key)
            print("result=",result)
            if result < 0:
                break

def setup_run_cleanup():
    random.seed()

    # get a packetserial object
    gbstate.ps=packetserial.PacketSerial()
    gbstate.ps=packetserial.PacketSerial()
    gbstate.ps.OpenAndClear()

    # load the object detection model
    pipeline_config=os.path.join(gbstate.modelpath,"pipeline.config")
    print("pipeline_config=",pipeline_config)
    checkpoint_path=os.path.join(gbstate.modelpath,"checkpoint","ckpt-0")
    print("checkpoint_path=",checkpoint_path)
    label_map=os.path.join(gbstate.modelpath,"label_map.pbtxt")
    print("label_map=",label_map)

    configs=config_util.get_configs_from_pipeline_file(pipeline_config)

    detection_model=model_builder.build(model_config=configs['model'],is_training=False)

    ckpt=tf.compat.v2.train.Checkpoint(model=detection_model)
    ckpt.restore(checkpoint_path).expect_partial()

    gbstate.model=detection_model

    gbstate.category_index=label_map_util.create_category_index_from_labelmap(label_map)

    # Open the capture device
    vid = cv2.VideoCapture(default_camera_index)

    width=int(vid.get(cv2.CAP_PROP_FRAME_WIDTH))
    height=int(vid.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print("width=",width,"height=",height)

    vid.set(cv2.CAP_PROP_FRAME_WIDTH,gbdata.stdscreen_size[0])
    vid.set(cv2.CAP_PROP_FRAME_HEIGHT,gbdata.stdscreen_size[1])

    width=int(vid.get(cv2.CAP_PROP_FRAME_WIDTH))
    height=int(vid.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print("width=",width,"height=",height)

    # give time for the capture device to settle
    time.sleep(5)

    gbstate.tasks=taskobject.TaskThreads()
    # yyy
    gbstate.tasks.AddToThread(0,taskdosomething.TaskDoSomething())
    #gbstate.tasks.AddToThread(0,tasksay.TaskSay("gamebot"))
    gbstate.tasks.AddToThread(0,tasktakestock.TaskTakeStock())
    gbstate.tasks.AddToThread(0,taskdetect.TaskDetect())

    # create the lock to synchronize data with the object detection
    # thread
    gbstate.detection_lock=threading.Lock()

    # start the object detection thread
    odt=threading.Thread(target=object_detection_thread,daemon=True)
    odt.start()

    main_loop(vid)

    # clean up. If things stop working you may have to
    # reboot to reset the capture device.
    vid.release()
    cv2.destroyAllWindows()
    gbstate.ps.Close()

def main(args):
    print("verify model")
    args.pop(0)
    for arg in args:
        print(f"arg=[{arg}]")
    setup_run_cleanup()

if __name__ == "__main__":
    main(sys.argv)

