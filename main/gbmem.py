#
# Copyright 2021-2022 by angry-kitten
# Monitor gamebot memory usage.
#

import os, sys, time, gc
import psutil

time_of_last_report=0
#report_period=30 # seconds
report_period=10 # seconds

def memory_report():
    tnow=time.monotonic()
    global time_of_last_report, report_period
    if (time_of_last_report+report_period) > tnow:
        return
    time_of_last_report=tnow
    print("memory_report start",flush=True)
    c=psutil.cpu_percent()
    print("c",c)
    vm=psutil.virtual_memory()
    print("vm",vm)
    mem_percent=vm.percent
    print("mem_percent",mem_percent)

    this_process=psutil.Process(os.getpid())
    print("this process",this_process)
    this_use=this_process.memory_info()
    print("this use",this_use)

    rss_percent=100.0*(this_use.rss/vm.total)
    vms_percent=100.0*(this_use.vms/vm.total)
    print("rss_percent",rss_percent)
    print("vms_percent",vms_percent)

    if mem_percent > 80:
        print("too much system memory",flush=True)
        sys.exit(1)
    if rss_percent > 35:
        print("too much process memory",flush=True)
        sys.exit(1)

    print("memory_report end",flush=True)
    return
