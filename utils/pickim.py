#!/usr/bin/env python3

# Pick images from the source directory that have the labels
# in the input list, remove the extra labels and place the
# image copy and new label file in the destination directory.

import sys, os, stat
import random
import re
import shutil
import subprocess
#from xml.etree import cElementTree as ET
from xml.etree import ElementTree as ET
import yaml

picklist=None
srcim=None
dstim=None
pick_list=[]

top=""
collected=""
annotations=""
images=""
label_map=""
labeldict={}
filelist=[]

#   <annotation>
#       <folder>imageset1</folder>
#       <filename>vlcsnap-2021-07-03-13h16m23s484.png</filename>
#       <path>D:\gamebot\tutorial\TFODCourse\Tensorflow\workspace\images\collectedimages\imageset1\vlcsnap-2021-07-03-13h16m23s484.png</path>
#       <source>
#           <database>Unknown</database>
#       </source>
#       <size>
#           <width>1920</width>
#           <height>1080</height>
#           <depth>3</depth>
#       </size>
#       <segmented>0</segmented>
#       <object>
#           <name>Hole</name>
#           <pose>Unspecified</pose>
#           <truncated>0</truncated>
#           <difficult>0</difficult>
#           <bndbox>
#               <xmin>590</xmin>
#               <ymin>642</ymin>
#               <xmax>701</xmax>
#               <ymax>727</ymax>
#           </bndbox>
#       </object>
#       <object>
#           <name>GoldRose</name>
#           <pose>Unspecified</pose>
#           <truncated>1</truncated>
#           <difficult>0</difficult>
#           <bndbox>
#               <xmin>1408</xmin>
#               <ymin>976</ymin>
#               <xmax>1589</xmax>
#               <ymax>1080</ymax>
#           </bndbox>
#       </object>
#   </annotation>

def process_file(fn):
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

def has_text(fpath):
    tree = ET.parse(fpath)
    root = tree.getroot()

    for obj in root.findall('object'):
        label=obj.find('name').text
        if label:
            #print("x label=", label)
            i=label.find("Char")
            if 0 == i:
                #print("has text")
                return True

    return False

def has_nontext(fpath):
    tree = ET.parse(fpath)
    root = tree.getroot()

    for obj in root.findall('object'):
        label=obj.find('name').text
        if label:
            #print("y label=", label)
            i=label.find("Char")
            if -1 == i:
                #print("has nontext")
                return True

    return False

def copy_entire(xmlfn, xmlfpath, subdir):
    imfpath=find_image_file(xmlfpath)
    if imfpath is None:
        print("no image file")
        return
    print("imfpath",imfpath)
    imfn=os.path.basename(imfpath)
    print("imfn",imfn)
    dstpath=os.path.join(sortedimages,subdir)
    print("dstpath",dstpath)
    os.makedirs(dstpath,exist_ok=True)
    xmldstpath=os.path.join(dstpath,xmlfn)
    print("xmldstpath",xmldstpath)
    imdstpath=os.path.join(dstpath,imfn)
    print("imdstpath",imdstpath)
    shutil.copy(xmlfpath,xmldstpath)
    shutil.copy(imfpath,imdstpath)
    return

def split_into_two(xmlfn, xmlfpath):
    imfpath=find_image_file(xmlfpath)
    if imfpath is None:
        print("no image file")
        return
    print("imfpath",imfpath)
    imfn=os.path.basename(imfpath)
    print("imfn",imfn)

    # copy to both the ht and hnt destinations
    ht_dstpath=os.path.join(sortedimages,"ht")
    print("ht_dstpath",ht_dstpath)
    os.makedirs(ht_dstpath,exist_ok=True)
    ht_xmldstpath=os.path.join(ht_dstpath,xmlfn)
    print("ht_xmldstpath",ht_xmldstpath)
    ht_imdstpath=os.path.join(ht_dstpath,imfn)
    print("ht_imdstpath",ht_imdstpath)
    shutil.copy(xmlfpath,ht_xmldstpath)
    shutil.copy(imfpath,ht_imdstpath)

    hnt_dstpath=os.path.join(sortedimages,"hnt")
    print("hnt_dstpath",hnt_dstpath)
    os.makedirs(hnt_dstpath,exist_ok=True)
    hnt_xmldstpath=os.path.join(hnt_dstpath,xmlfn)
    print("hnt_xmldstpath",hnt_xmldstpath)
    hnt_imdstpath=os.path.join(hnt_dstpath,imfn)
    print("hnt_imdstpath",hnt_imdstpath)
    shutil.copy(xmlfpath,hnt_xmldstpath)
    shutil.copy(imfpath,hnt_imdstpath)

    edit_xml_in_place(ht_xmldstpath,True)
    edit_xml_in_place(hnt_xmldstpath,False)

    return

def edit_xml_in_place(fpath,keep_text):
    tree = ET.parse(fpath)
    root = tree.getroot()

    #for obj in root.findall('object'):
    #    label=obj.find('name').text
    #    if label:
    #        print("z label=", label)
    #        i=label.find("Char")
    #        if 0 == i:
    #            print("has text")
    #            if not keep_text:
    #                print("delete this obj")
    #        else:
    #            print("has nontext")
    #            if keep_text:
    #                print("delete this obj")

    # Find all the objects below the root only.
    for l2 in root.findall('.//object'):
        print("l2",l2.tag)
        label=l2.find('name').text
        if label:
            print("w label=", label)
            i=label.find("Char")
            if 0 == i:
                print("has text")
                if not keep_text:
                    print("delete this obj")
                    root.remove(l2)
            else:
                print("has nontext")
                if keep_text:
                    print("delete this obj")
                    root.remove(l2)

    tree.write(fpath)

    return

def process_xml(fpath):
    tree = ET.parse(fpath)
    root = tree.getroot()

    for obj in root.findall('object'):
        label=obj.find('name').text
        #if label:
        #    print("x label=", label)

    keepcount=0
    deletecount=0
    # Find all the objects below the root only.
    for l2 in root.findall('.//object'):
        #print("l2",l2.tag)
        label=l2.find('name').text
        if label:
            #print("w label=", label)
            if label in pick_list:
                #print("keep this entry")
                keepcount+=1
            else:
                print("delete this entry",label)
                root.remove(l2)
                deletecount+=1

    if keepcount < 1:
        print("no labels to keep")
        return

    imfpath=find_image_file(fpath)
    if imfpath is None:
        print("no image file")
        return

    #print("fpath",fpath)
    xmlfn=os.path.basename(fpath)
    #print("xmlfn",xmlfn)

    #print("imfpath",imfpath)
    imfn=os.path.basename(imfpath)
    #print("imfn",imfn)

    global dstim
    xmldstpath=os.path.join(dstim,xmlfn)
    #print("xmldstpath",xmldstpath)
    imdstpath=os.path.join(dstim,imfn)
    #print("imdstpath",imdstpath)
    shutil.copy(imfpath,imdstpath)

    tree.write(xmldstpath)

    return

def walk_tree(dname):
    print("processing",dname)
    global filelist
    for root, dirs, files in os.walk(dname):
        #print("root dirs files",root,dirs,files)
        for fn in files:
            #print("file", fn)
            if fn.endswith(".xml"):
                fullpath=os.path.join(root,fn)
                #print("xml fullpath", fullpath)
                process_xml(fullpath)
    return

def find_image_file(f):
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

def read_picklist(fname):
    global pick_list
    with open(fname,'r') as file:
        pick_list=yaml.safe_load(file)
    #print("pick_list",pick_list)
    return

def main(args):
    print("pick images")
    random.seed()
    args.pop(0)
    print(len(args))
    if 3 != len(args):
        print("expecting three args, picklist.yaml sourceimages desinationimages")
        sys.exit(1)
    global picklist, srcim, dstim
    picklist=args[0]
    srcim=args[1]
    dstim=args[2]

    print("picklist",picklist)
    print("srcim",srcim)
    print("dstim",dstim)

    read_picklist(picklist)

    walk_tree(srcim)

    sys.exit(0)

if __name__ == "__main__":
    main(sys.argv)

