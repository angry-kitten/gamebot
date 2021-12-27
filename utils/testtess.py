#!/usr/bin/env python3
#
# Copyright 2021 by angry-kitten
# Test tesseract
#

import os, sys, time, random, threading
import cv2
import pytesseract

image_list=[ 'testocr1.png', 'testocr2.png','testocr3.png' ]

def testocr(fname):
    print(fname)
    img=cv2.imread(fname)
    custom_config=r'--oem 3 --psm 6'
    s=pytesseract.image_to_string(img,config=custom_config)
    print(f'[{s}]')
    return

def main(args):
    print("test tesseract")
    args.pop(0)
    for arg in args:
        print(f"arg=[{arg}]")

    for f in image_list:
        testocr(f)
    return

if __name__ == "__main__":
    main(sys.argv)

