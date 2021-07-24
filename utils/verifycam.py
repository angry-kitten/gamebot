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

def capture_loop(vid):
    while(True):
        # get a frame
        ret, frame = vid.read()

        scaled=frame

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

    width=int(vid.get(cv2.CAP_PROP_FRAME_WIDTH))
    height=int(vid.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print("width=",width,"height=",height)

    vid.set(cv2.CAP_PROP_FRAME_WIDTH,1280)
    vid.set(cv2.CAP_PROP_FRAME_HEIGHT,720)

    width=int(vid.get(cv2.CAP_PROP_FRAME_WIDTH))
    height=int(vid.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print("width=",width,"height=",height)

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

