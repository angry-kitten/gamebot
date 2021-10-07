#
# Copyright 2021 by angry-kitten
# Gamebot state variables.
#

import time

keydown_time_ms=250 # milliseconds
debug_every=10 # seconds
detect_every=5 # seconds, do an object detection with this period
modelpath=None
ps=None # packet serial object
model=None
frame=None
categgory_index=None

# below are protected by the lock
detection_lock=None
detection_frame=None
detections=None
digested=None
detim=None
# above are protected by the lock

tasks=None

label_id_offset=1

minimap=None
phonemap=None

position_minimap_x=-1
position_minimap_y=-1
player_mx=-1
player_my=-1
center_mx=-1
center_my=-1
goto_target_mx=-1
goto_target_my=-1
object_target_mx=-1
object_target_my=-1
