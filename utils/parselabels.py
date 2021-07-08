#!/usr/bin/env python3

import sys
import os
from xml.etree import cElementTree as ET

labeldict={}

def process_file(fn):
    tree = ET.parse(fn)
    root = tree.getroot()

    for obj in root.findall('object'):
        label=obj.find('name').text
        if label:
            print("label=", label)
            if label in labeldict:
                labeldict[label] += 1
            else:
                print("first time")
                labeldict[label]=1
            print("count=", labeldict[label])
        else:
            print("not found")

def walk_tree(dname):
    print("processing",dname)
    for root, dirs, files in os.walk(dname):
        print("root dirs files",root,dirs,files)
        for fn in files:
            print("file", fn)
            if fn.endswith(".xml"):
                print("xml file", fn)
                fullpath=os.path.join(root,fn)
                print("xml fullpath", fullpath)
                process_file(fullpath)

def dump_label_map():
    print("dump label map")
    with open("label_map.pbtxt","w") as f:
        id=1
        for key in labeldict.keys():
            print("item {",file=f) # }
            print(f"    name:'{key}'",file=f)
            print(f"    id:{id}",file=f)
            # {
            print("}",file=f)
            id+=1

def dump_label_report():
    print("dump label report")
    with open("label_report.txt","w") as f:
        for key in labeldict.keys():
            count=labeldict[key]
            print(f"[{key}] {count}",file=f) 

def main(args):
    print("parse labels")
    args.pop(0)
    for arg in args:
        print(f"arg=[{arg}]")
        walk_tree(arg)
    dump_label_map()
    dump_label_report()

if __name__ == "__main__":
    main(sys.argv)

