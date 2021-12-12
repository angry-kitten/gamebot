#!/usr/bin/env python3
# This script builds a new label map label_map.pbtxt. It sorts the images into
# the test and train directories. Then run the tfrecord script on the new test
# and train directories.
# The old files don't need to be removed first,
# this script will clean out the old.
# python .\rebuildtrain.py D:\gamebot\tutorial\TFODCourse Tensorflow\workspace\images\collectedimages Tensorflow\workspace\annotations Tensorflow\workspace\images


import sys
import os, stat
import random
import re
import shutil
import subprocess
from xml.etree import cElementTree as ET
import object_detection

# D:\gamebot\tutorial\TFODCourse
top=""

# Tensorflow\workspace\images\collectedimages
collected=""

# Tensorflow\workspace\annotations
annotations=""

# Tensorflow\workspace\images
images=""

# Set the percentage of images will be test images.
test_train_split_percent=15

# The file path of the generated label map.
label_map=""

# A list of all the labels from the xml files with a count of their use.
labeldict={}

# a list of full path xml files in their source locations
# D:\gamebot\tutorial\TFODCourse\Tensorflow\workspace\images\collectedimages
filelist=[]

tfrecord_script='Tensorflow\\scripts\\generate_tfrecord.py'

def process_file(fn):
    """parse the labels from the xml files into labeldict"""
    tree = ET.parse(fn)
    root = tree.getroot()

    for obj in root.findall('object'):
        label=obj.find('name').text
        if label:
            #print("label=", label)
            if label in labeldict:
                labeldict[label] += 1
            else:
                print("first time")
                labeldict[label]=1
            #print("count=", labeldict[label])
        else:
            print("not found")

def walk_tree(dname):
    """generate a list of xml files in their source locations
        D:\gamebot\tutorial\TFODCourse\Tensorflow\workspace\images\collectedimages
        Parse all the labels out of them into labeldict.
    """
    print("processing",dname)
    global filelist
    for root, dirs, files in os.walk(dname):
        print("root dirs files",root,dirs,files)
        for fn in files:
            print("file", fn)
            if fn.endswith(".xml"):
                print("xml file", fn)
                fullpath=os.path.join(root,fn)
                print("xml fullpath", fullpath)
                filelist.append(fullpath)
                process_file(fullpath)

def dump_label_map(dname):
    """dump the label map into label_map.pbtxt"""
    global label_map
    print("dump label map")
    fname=os.path.join(dname,"label_map.pbtxt")
    print(fname)
    label_map=fname
    with open(fname,"w") as f:
        id=1
        for key in labeldict.keys():
            print("item {",file=f) # }
            print(f"    name:'{key}'",file=f)
            print(f"    id:{id}",file=f)
            # {
            print("}",file=f)
            id+=1

def dump_label_report(dname):
    """dump the label info into label_report.txt"""
    print("dump label report")
    fname=os.path.join(dname,"label_report.txt")
    print(fname)
    with open(fname,"w") as f:
        for key in labeldict.keys():
            count=labeldict[key]
            print(f"[{key}] {count}",file=f) 

def find_image_file(f):
    """Find the image file given the .xml file."""
    imf=re.sub('\.xml$','.jpg',f)
    #print(imf)
    if f == imf:
        return None
    if os.path.exists(imf):
        return imf
    imf=re.sub('\.xml$','.png',f)
    #print(imf)
    if f == imf:
        return None
    if os.path.exists(imf):
        return imf
    return None

def build_test_train():
    """Select images to build new test train directories randomly"""
    global images, filelist, test_train_split_percent
    dtest=os.path.join(images,"test")
    dtrain=os.path.join(images,"train")
    print("dtest=",dtest)
    print("dtrain=",dtrain)

    if os.path.exists(dtest):
        print("removing old test directory")
        shutil.rmtree(dtest)

    if os.path.exists(dtrain):
        print("removing old train directory")
        shutil.rmtree(dtrain)

    os.mkdir(dtest)
    os.mkdir(dtrain)

    for f in filelist:
        print("f=",f)
        if random.randint(1,100) <= test_train_split_percent:
            dest=dtest
        else:
            dest=dtrain
        # Find the image file given the .xml file.
        imf=find_image_file(f)
        if imf:
            print("found")
            shutil.copy(f,dest)
            shutil.copy(imf,dest)
        else:
            print("not found")

# !python {files['TF_RECORD_SCRIPT']} -x {os.path.join(paths['IMAGE_PATH'], 'train')} -l {files['LABELMAP']} -o {os.path.join(paths['ANNOTATION_PATH'], 'train.record')} 
# !python {files['TF_RECORD_SCRIPT']} -x {os.path.join(paths['IMAGE_PATH'], 'test')} -l {files['LABELMAP']} -o {os.path.join(paths['ANNOTATION_PATH'], 'test.record')} 
def build_tfrecords():
    """Run the tfrecord script on the new test and train directories."""
    global top, images, annotation, label_map
    dtest=os.path.join(images,"test")
    dtrain=os.path.join(images,"train")
    print("dtest=",dtest)
    print("dtrain=",dtrain)
    print("label_map=",label_map)

    tfpath=os.path.join(top,tfrecord_script);
    print("tfpath=",tfpath)

    trainrec=os.path.join(annotations,'train.record')
    testrec=os.path.join(annotations,'test.record')
    print("trainrec=",trainrec)
    print("testrec=",testrec)

    subprocess.run(['python',tfpath,'-x',dtrain,'-l',label_map,'-o',trainrec],shell=True)
    subprocess.run(['python',tfpath,'-x',dtest,'-l',label_map,'-o',testrec],shell=True)

def main(args):
    print("rebuild train")
    random.seed()
    args.pop(0)
    print(len(args))
    if 4 != len(args):
        print("expecting four args, top, collected, annotations, images")
        sys.exit(1)
    global top, collected, annotations, images
    top=args[0]
    collected=args[1]
    annotations=args[2]
    images=args[3]

    print("top",top)
    print("collected",collected)
    print("annotations",annotations)
    print("images",images)

    collected=os.path.join(top,collected)
    annotations=os.path.join(top,annotations)
    images=os.path.join(top,images)
    print("collected",collected)
    print("annotations",annotations)
    print("images",images)

    # Get a list of all the xml files and parse out the labels.
    walk_tree(collected)

    #print(filelist)

    # dump the label map into label_map.pbtxt
    dump_label_map(annotations)

    # dump the label info into label_report.txt
    dump_label_report(top)

    # Select images to build new test train directories randomly
    build_test_train()

    # Run the tfrecord script on the new test and train directories.
    build_tfrecords()

    sys.exit(0)

if __name__ == "__main__":
    main(sys.argv)

