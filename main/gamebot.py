#!/usr/bin/env python3
#
# Copyright 2021 by angry-kitten
# Gamebot main program.
#

import sys
import os
import time
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

import taskobject
import tasksay

sys.path.append(os.path.join(os.getcwd(),"..","..","gamebot-serial","pylib"))
#print(sys.path)
import packetserial
keydown_time_ms=250 # milliseconds

# change this to select which webcam to use
#default_camera_index=2
default_camera_index=0
g_debug_every=10 # seconds
g_detect_every=5 # seconds, do an object detection with this period
modelpath=os.path.join("..","model");
print("modelpath=",modelpath)

g_ps=None
g_model=None
g_frame=None
g_categgory_index=None
g_detections=None

g_tasks=taskobject.TaskThreads()

# Set the apparently platform specific key codes.
print("os",os.name)

if "posix" == os.name:
    keycode_numpad_8=151
    keycode_numpad_6=152
    keycode_numpad_4=150
    keycode_numpad_2=153
    

def do_one_object_detect():

    global g_detections
    g_detections=None

    # convert the image format to what is needed for object detection
    image_np=numpy.array(g_frame)
    input_tensor=tf.convert_to_tensor(numpy.expand_dims(image_np,0),dtype=tf.float32)

    # run the image through the model
    image_pre, shapes=g_model.preprocess(input_tensor)
    prediction_dict=g_model.predict(image_pre,shapes)
    detections=g_model.postprocess(prediction_dict,shapes)

    num_detections=int(detections.pop('num_detections'))
    detections={key: value[0, :num_detections].numpy()
                for key, value in detections.items()}
    detections['num_detections']=num_detections

    detections['detection_classes']=detections['detection_classes'].astype(numpy.int64)

    label_id_offset=1
    image_np_with_detections=image_np.copy()

    global g_category_index

    visualization_utils.visualize_boxes_and_labels_on_image_array(
        image_np_with_detections,
        detections['detection_boxes'],
        detections['detection_classes']+label_id_offset,
        detections['detection_scores'],
        g_category_index,
        use_normalized_coordinates=True,
        max_boxes_to_draw=64,
        min_score_thresh=.2,
        agnostic_mode=False)

    #cv2.imshow("show detections",cv2.resize(image_np_with_detections,(800,600)))
    cv2.imshow("show detections",image_np_with_detections)

    g_detections=detections

def debug_show_state():
    g_tasks.DebugRecursive()
    #print(g_detections)

def process_key(key):
    print("key=",key)
    if ord('a') == key:
        g_ps.move_left_joy_left(keydown_time_ms)
        return 0
    if ord('d') == key:
        g_ps.move_left_joy_right(keydown_time_ms)
        return 0
    if ord('w') == key:
        g_ps.move_left_joy_up(keydown_time_ms)
        return 0
    if ord('s') == key:
        g_ps.move_left_joy_down(keydown_time_ms)
        return 0
    if ord('8') == key:
        g_ps.press_X()
        return 0
    if ord('6') == key:
        g_ps.press_A()
        return 0
    if ord('4') == key:
        g_ps.press_Y()
        return 0
    if ord('2') == key:
        g_ps.press_B()
        return 0
    if keycode_numpad_8 == key:
        g_ps.press_X()
        return 0
    if keycode_numpad_6 == key:
        g_ps.press_A()
        return 0
    if keycode_numpad_4 == key:
        g_ps.press_Y()
        return 0
    if keycode_numpad_2 == key:
        g_ps.press_B()
        return 0
    if ord('+') == key:
        g_ps.press_PLUS()
        return 0
    if ord('-') == key:
        g_ps.press_MINUS()
        return 0
    if ord('u') == key:
        g_ps.press_XL()
        return 0
    if ord('j') == key:
        g_ps.press_L()
        return 0
    if ord('i') == key:
        g_ps.press_XR()
        return 0
    if ord('k') == key:
        g_ps.press_R()
        return 0
    if ord('q') == key:
        return -1
    if ord('b') == key:
        debug_show_state()
        return 0
    return key

def main_loop(vid):

    debugtime=time.monotonic()+g_debug_every
    capturetime=time.monotonic()+g_detect_every

    while(True):
        g_tasks.Poll()
        g_tasks.DebugRecursive()

        # get a frame
        ret, frame = vid.read()

        global g_frame
        g_frame=frame

        # show the frame as captured
        # scale it down to save screen space
        #scaled=imutils.resize(frame,width=320) # maintains aspect
        scaled=frame
        cv2.imshow('captured',scaled)

        now=time.monotonic()
        if now >= debugtime:
            debugtime=time.monotonic()+g_debug_every
            g_tasks.DebugRecursive()

        if now >= capturetime:
            # we could do capturetime=capturetime+g_detect_every but
            # this allows for the time to do detection to be larger than
            capturetime=time.monotonic()+g_detect_every
            # object detect on the frame
            #do_one_object_detect()

        # Exit on any key press.
        key=cv2.waitKey(2)
        if key > 0:
            result=process_key(key)
            print("result=",result)
            if result < 0:
                break

def setup_run_cleanup():
    # get a packetserial object
    global g_ps
    g_ps=packetserial.PacketSerial()
    g_ps=packetserial.PacketSerial()
    g_ps.OpenAndClear()

    # load the object detection model
    pipeline_config=os.path.join(modelpath,"pipeline.config")
    print("pipeline_config=",pipeline_config)
    checkpoint_path=os.path.join(modelpath,"checkpoint","ckpt-0")
    print("checkpoint_path=",checkpoint_path)
    label_map=os.path.join(modelpath,"label_map.pbtxt")
    print("label_map=",label_map)

    configs=config_util.get_configs_from_pipeline_file(pipeline_config)

    detection_model=model_builder.build(model_config=configs['model'],is_training=False)

    ckpt=tf.compat.v2.train.Checkpoint(model=detection_model)
    ckpt.restore(checkpoint_path).expect_partial()

    global g_model
    g_model=detection_model

    global g_category_index
    g_category_index=label_map_util.create_category_index_from_labelmap(label_map)

    # Open the capture device
    vid = cv2.VideoCapture(default_camera_index)

    width=int(vid.get(cv2.CAP_PROP_FRAME_WIDTH))
    height=int(vid.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print("width=",width,"height=",height)

    vid.set(cv2.CAP_PROP_FRAME_WIDTH,1280)
    vid.set(cv2.CAP_PROP_FRAME_HEIGHT,720)

    width=int(vid.get(cv2.CAP_PROP_FRAME_WIDTH))
    height=int(vid.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print("width=",width,"height=",height)

    # give time for the capture device to settle
    time.sleep(5)

    g_tasks.AddToThread(0,tasksay.TaskSay(g_ps,"gamebot"))

    main_loop(vid)

    # clean up. If things stop working you may have to
    # reboot to reset the capture device.
    vid.release()
    cv2.destroyAllWindows()
    g_ps.Close()

def main(args):
    print("verify model")
    args.pop(0)
    for arg in args:
        print(f"arg=[{arg}]")
    setup_run_cleanup()

if __name__ == "__main__":
    main(sys.argv)

