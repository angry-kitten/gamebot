#!/usr/bin/env python3
#
# Copyright 2021 by angry-kitten
# Test easyocr
#

import os, sys, time, random, threading
import easyocr
import cv2
from matplotlib import pyplot as plt
import numpy as np

image_list=[ 'testocr1.png', 'testocr2.png','testocr3.png' ]

def testocr(fname):
    print(fname)
    reader=easyocr.Reader(['en'], gpu=False)
    result=reader.readtext(fname,paragraph=False,workers=4)
    print(result)
    return

def main(args):
    print("test easyocr")
    args.pop(0)
    for arg in args:
        print(f"arg=[{arg}]")

    for f in image_list:
        testocr(f)
    return

if __name__ == "__main__":
    main(sys.argv)

