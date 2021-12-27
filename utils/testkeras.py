#!/usr/bin/env python3
#
# Copyright 2021 by angry-kitten
# Test keras-ocr
#

import os, sys, time, random, threading
import keras_ocr

image_list=[ 'testocr1.png', 'testocr2.png','testocr3.png' ]

def testocr(fname):
    print(fname)
    pipeline=keras_ocr.pipeline.Pipeline()
    il=[ fname ]
    prediction_groups=pipeline.recognize(il)
    for g in prediction_groups:
        print("g")
        for text, box in g:
            print(text)
            print(box)
    return

def main(args):
    print("test keras-ocr")
    args.pop(0)
    for arg in args:
        print(f"arg=[{arg}]")

    for f in image_list:
        testocr(f)
    return

if __name__ == "__main__":
    main(sys.argv)

