#
# Copyright 2021 by angry-kitten
# Gamebot state variables.
#

import time
import gbdata

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
task_stack_names=[]

label_id_offset=1

mainmap=None
unreachable=False

# The map position calculated from the minimap.
position_minimap_x=-1
position_minimap_y=-1

# The map position calculated from the phonemap.
position_phonemap_x=-1
position_phonemap_y=-1

# The current player map position calculated from whatever source
# like the minimap. This is the feet position.
player_mx=-1
player_my=-1

# The current player heading based on the latest move.
# The player character usually start the game heading down/south.
player_heading=180

# The current map position of the center of the screen. Object
# positions are calculated from this. This can be +1.0 to -1.0 off
# in both x and y from the player map position.
center_mx=-1
center_my=-1

# Tune the feet box offset relative to the center.
tune_sc_offset_mx=0.00 # not really used
tune_sc_offset_origin_my=0.80
tune_sc_offset_my=tune_sc_offset_origin_my
tune_sc_offset_down_my=1.0
#tune_sc_offset_up_my=0.0
tune_sc_offset_up_my=0.1
tune_sc_offset_left_my=0.25
tune_sc_offset_right_my=0.25
tune_sc_offset_ratio=0.20

## This is the map position offset of the center of the feet box. It should range
## from +0.5 to -0.5 in both map x and y.
#feet_box_offset_mx=-2
#feet_box_offset_my=-2

# This is the center of the feet box.
feet_box_center_mx=-1
feet_box_center_my=-1

# This is how fast the feet box moves relative to the center when
# the player position moves past the feet box.
#feet_box_ratio_x=0.25
#feet_box_ratio_y=0.25
#feet_box_ratio_x=0.20
#feet_box_ratio_y=0.20
feet_box_ratio_x=0.18
feet_box_ratio_y=0.18

# This is how fast the player feet position is adjusted inside the
# feet box in the perpendicular direction.
feet_box_cross_ratio_x=0.30
feet_box_cross_ratio_y=0.30

# This is how fast the box is adjusted to the center of the screen
# in the perpendicular direction.
box_center_cross_ratio_x=0.10
box_center_cross_ratio_y=0.10

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

# The target map position of TaskPathPlanGoTo
plan_goto_target_mx=-1
plan_goto_target_my=-1

# Draw inventory locations on the screen if True
draw_inventory_locations=False
inventory_size=20
inventory_locations=gbdata.inventory_locations_20
inventory_slots_full=0
inventory_slots_free=0
inventory_slots_unknown=0
inventory=None
inventory_name=None

current_tool=None

move_since_determine=True
move_since_detect=True

# indexed by time in seconds "how much distance corresponds to seconds"
data_distance_time_precision=100
latest_data_time=0
# contents are an array [sum,count]
data_distance_time_1=[]
data_distance_time_5=[]
data_distance_time_10=[]
data_distance_time_20=[]
data_distance_time_30=[]
data_distance_time_40=[]
data_distance_time_50=[]
data_distance_time_60=[]
data_distance_time_70=[]
data_distance_time_80=[]
data_distance_time_90=[]
data_distance_time_100=[]
data_distance_time_110=[]
data_distance_time_120=[]
data_distance_time_130=[]
data_distance_time_140=[]
data_distance_time_150=[]
data_distance_time_160=[]
data_distance_time_170=[]
data_distance_time_180=[]

pause_message=None

screen_chars=[]

gray_circle_list=[]

# binfo is [name,centermx,centermy,doormx,doormy]
building_info_campsite=None
building_info_museum=None
building_info_cranny=None
building_info_services=None
building_info_tailors=None
building_info_airport=None
