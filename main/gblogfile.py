#!/usr/bin/env python3
#
# Copyright 2021-2022 by angry-kitten
# Gamebot log file support.
#

import sys, os, time, random
import threading

import gbmem
import gbdata, gbstate, gbdisplay
import gbocr
import gbmap
import gbdijkstra
import gbscreen
import threadmanager


def init_log_file_locks():
    gbstate.log_file_lock=threading.Lock()
    return

def log(s):
    l=len(s)
    if l > 0:
        if s[l-1] != '\n':
            s=s+'\n'
    else:
        s=s+'\n'
    with gbstate.log_file_lock:
        with open('l','a') as f:
            f.write(s)
    return
