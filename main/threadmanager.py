#
# Copyright 2021 by angry-kitten
# Manage a worker thread.
#

import sys, os, time, random
import threading

class ThreadManager():
    """ThreadManager Object"""

    def __init__(self,runme,name):
        # Run this to process a work item.
        self.runme=runme
        # Data that is passed in or out in globals will be protected
        # by this lock.
        self.data_lock=threading.Lock()
        # This is used to trigger the worker to process
        # a work item.
        self.worker_condition=threading.Condition()
        self.worker_thread=threading.Thread(target=self.worker_thread_wrapper,daemon=True)
        self.worker_thread.name=name
        self.worker_thread.start()
        return

    def __del__(self):
        # destructor
        return

    def RunOnce(self):
        """run the work item once"""
        print("before RunOnce")
        self.worker_condition.acquire()
        self.worker_condition.notify()
        self.worker_condition.release()
        print("after RunOnce")
        return

    def worker_thread_wrapper(self):
        print("worker_thread_wrapper")

        while True:
            print("before wait")
            self.worker_condition.acquire()
            self.worker_condition.wait()
            self.worker_condition.release()
            print("after wait")
            time_before=time.monotonic()
            self.runme()
            time_after=time.monotonic()
            delta=time_after-time_before
            print("task time",delta,"seconds")

        print("worker thread returning")
        return
