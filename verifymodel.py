#!/usr/bin/env python3
#
# Copyright 2021 by angry-kitten
# Parse labels from labeled images and create a list for gamebot.
#

import sys
import os
import cv2
import object_detection
import tensorflow as tf
from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as viz_utils
from object_detection.builders import model_builder
from object_detection.utils import config_util
import numpy as np
from matplotlib import pyplot as plt
#%matplotlib inline

# change this to select which webcam to use
default_camera_index=2
modelpath=os.path.join("model");
print("modelpath=",modelpath)

def scale_image_to_inside_box(frame,box_w,box_h):
    scalew=box_w/frame.shape[1]
    scaleh=box_h/frame.shape[0]
    if scalew <= scaleh:
        scale=scalew
    else:
        scale=scaleh
    w2=int(scale*frame.shape[1])
    h2=int(scale*frame.shape[0])
    dim=(w2,h2)
    scaled=cv2.resize(frame,dim)
    return scaled

def detect_fn(model,image):
    image, shapes=model.preprocess(image)
    prediction_dict=model.predict(image,shapes)
    detections=model.postprocess(prediction_dict,shapes)
    return detections

def capture_loop(vid,model,category_index):
    while(True):
        # get a frame
        ret, frame = vid.read()
        image_np=np.array(frame)

        input_tensor=tf.convert_to_tensor(np.expand_dims(image_np,0),dtype=tf.float32)
        detections=detect_fn(model,input_tensor)

        num_detections=int(detections.pop('num_detections'))
        detections={key: value[0, :num_detections].numpy()
                    for key, value in detections.items()}
        detections['num_detections']=num_detections

        detections['detection_classes']=detections['detection_classes'].astype(np.int64)

        label_id_offset=1
        image_np_with_detections=image_np.copy()

        viz_utils.visualize_boxes_and_labels_on_image_array(
            image_np_with_detections,
            detections['detection_boxes'],
            detections['detection_classes']+label_id_offset,
            detections['detection_scores'],
            category_index,
            use_normalized_coordinates=True,
            max_boxes_to_draw=32,
            min_score_thresh=.2,
            agnostic_mode=False)

        #scaled=scale_image_to_inside_box(frame,640,480)
        #scaled=scale_image_to_inside_box(frame,1024,768)
        ## Display the frame in a window. It will be
        ## created on first call and reused from then on.
        #cv2.imshow("verify cam",scaled)

        cv2.imshow("verify model",cv2.resize(image_np_with_detections,(800,600)))

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

