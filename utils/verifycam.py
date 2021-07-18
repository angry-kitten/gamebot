#!/usr/bin/env python3
#
# Copyright 2021 by angry-kitten
# Parse labels from labeled images and create a list for gamebot.
#

import sys
import os
import cv2

# change this to select which webcam to use
default_camera_index=2

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


def capture_loop(vid):
    while(True):
        # get a frame
        ret, frame = vid.read()

        #scaled=scale_image_to_inside_box(frame,640,480)
        scaled=scale_image_to_inside_box(frame,1024,768)

        # Display the frame in a window. It will be
        # created on first call and reused from then on.
        cv2.imshow("verify cam",scaled)

        # Exit on any key press.
        key=cv2.waitKey(2)
        if key > 0:
            break

def verify_camera():
    # Open the capture device
    vid = cv2.VideoCapture(default_camera_index)

    capture_loop(vid)

    # clean up. If things stop working you may have to
    # reboot to reset the capture device.
    vid.release()
    cv2.destroyAllWindows()

def main(args):
    print("verify cam")
    args.pop(0)
    for arg in args:
        print(f"arg=[{arg}]")
    verify_camera()

if __name__ == "__main__":
    main(sys.argv)

