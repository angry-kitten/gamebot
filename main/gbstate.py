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

# The map position calculated from the minimap.
position_minimap_x=-1
position_minimap_y=-1

# The current player map position calculated from whatever source
# like the minimap. This is the feet position.
player_mx=-1
player_my=-1

# The current map position of the center of the screen. Object
# positions are calculated from this. This can be +1.0 to -1.0 off
# in both x and y from the player map position.
center_mx=-1
center_my=-1

# Tune the feet box offset relative to the center.
#tune_fb_offset_my=0.80
tune_fb_offset_my=1.0

# This is the map position offset of the center of the feet box. It should range
# from +0.5 to -0.5 in both map x and y.
feet_box_offset_mx=-2
feet_box_offset_my=-2

# This is how fast the feet box moves relative to the center when
# the player position moves past the feet box.
feet_box_ratio_x=0.25
feet_box_ratio_y=0.25

# This is the attempted and actual map position move values. These
# are deltas or changes in position.
move_before_mx=-1
move_before_my=-1
move_after_mx=-1
move_after_my=-1
move_attempted_mx=-1
move_attempted_my=-1
move_actual_mx=-1
move_actual_my=-1
move_obstructed=False

# The target map position of TaskSimpleGoTo
goto_target_mx=-1
goto_target_my=-1

# The current target map position of tasks like TaskWeed
object_target_mx=-1
object_target_my=-1

# The target map position of TaskTrackGoTo
track_goto_target_mx=-1
track_goto_target_my=-1

# Draw inventory locations on the screen if True
draw_inventory_locations=False
