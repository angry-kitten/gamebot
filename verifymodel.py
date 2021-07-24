#!/usr/bin/env python3
#
# Copyright 2021 by angry-kitten
# Parse labels from labeled images and create a list for gamebot.
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

# change this to select which webcam to use
default_camera_index=2
detect_every=5 # seconds, do an object detection with this period
modelpath=os.path.join("model");
print("modelpath=",modelpath)

def do_one_object_detect(model,frame,category_index):

    # convert the image format to what is needed for object detection
    image_np=numpy.array(frame)
    input_tensor=tf.convert_to_tensor(numpy.expand_dims(image_np,0),dtype=tf.float32)

    # run the image through the model
    image_pre, shapes=model.preprocess(input_tensor)
    prediction_dict=model.predict(image_pre,shapes)
    detections=model.postprocess(prediction_dict,shapes)

    num_detections=int(detections.pop('num_detections'))
    detections={key: value[0, :num_detections].numpy()
                for key, value in detections.items()}
    detections['num_detections']=num_detections

    detections['detection_classes']=detections['detection_classes'].astype(numpy.int64)

    label_id_offset=1
    image_np_with_detections=image_np.copy()

    visualization_utils.visualize_boxes_and_labels_on_image_array(
        image_np_with_detections,
        detections['detection_boxes'],
        detections['detection_classes']+label_id_offset,
        detections['detection_scores'],
        category_index,
        use_normalized_coordinates=True,
        max_boxes_to_draw=64,
        min_score_thresh=.2,
        agnostic_mode=False)

    #cv2.imshow("verify model",cv2.resize(image_np_with_detections,(800,600)))
    cv2.imshow("verify model",image_np_with_detections)

def capture_loop(vid,model,category_index):

    capturetime=time.monotonic()+detect_every

    while(True):
        # get a frame
        ret, frame = vid.read()

        # show the frame as captured
        # scale it down to save screen space
        scaled=imutils.resize(frame,width=320) # maintains aspect
        cv2.imshow('captured',scaled)

        now=time.monotonic()
        if now >= capturetime:
            # we could do capturetime=capturetime+detect_every but
            # this allows for the time to do detection to be larger than
            # detect_every
            capturetime=time.monotonic()+detect_every
            # object detect on the frame
            do_one_object_detect(model,frame,category_index)

        # Exit on any key press.
        key=cv2.waitKey(2)
        if key > 0:
            break

def verify_model():

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

    category_index=label_map_util.create_category_index_from_labelmap(label_map)

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

    capture_loop(vid,detection_model,category_index)

    # clean up. If things stop working you may have to
    # reboot to reset the capture device.
    vid.release()
    cv2.destroyAllWindows()

def main(args):
    print("verify model")
    args.pop(0)
    for arg in args:
        print(f"arg=[{arg}]")
    verify_model()

if __name__ == "__main__":
    main(sys.argv)

