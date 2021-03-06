#
# Copyright 2021-2022 by angry-kitten
# Gamebot state variables.
#

import time
import gbdata

debug_state_on=False

keydown_time_ms=250 # milliseconds
debug_every=10 # seconds
detect_every=5 # seconds, do an object detection with this period
modelpath=None
ps=None # packet serial object
model=None
frame=None
categgory_index=None
drawn_on=None

# below are protected by the lock
detection_lock=None
detection_frame=None
detections=None
detections_set_time=0
digested=None
detim=None
# above are protected by the lock

detection_condition=None

tasks=None
task_stack_names=[]

label_id_offset=1

mainmap=None
mainmap_latest_update=0
mainmap_update_count=0
unreachable=False

# (node1,type)
dijkstra_waypoints=[]
# (node1,node2,type,cost)
dijkstra_walk_edges=[]
dijkstra_ladder_edges=[]
dijkstra_pole_edges=[]
dijkstra_new_walk_edges=[]
dijkstra_new_ladder_edges=[]
dijkstra_new_pole_edges=[]

map2stats=[]
map2maybediagonals=[]
map2diagonals=[]

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

# low and high severity obstruction
move_obstructed_low=False
move_obstructed_high=False

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
inventory_needed=False
inventory_size=20
inventory_locations=gbdata.inventory_locations_20
inventory_slots_full=0
inventory_slots_free=0
inventory_slots_unknown=0
inventory=None
inventory_name=None

inventory_has_net=False
inventory_has_pole=False
inventory_has_ladder=False
inventory_has_shovel=False
inventory_has_wetsuit=False
inventory_has_fishingpole=False
inventory_has_wateringcan=False
inventory_has_slingshot=False
inventory_has_stoneaxe=False
inventory_has_cuttingaxe=False
inventory_has_axe=False

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
do_draw_buildings=False

# binfo is [name,centermx,centermy,doormx,doormy]
building_info_campsite=None
building_info_museum=None
building_info_cranny=None
building_info_services=None
building_info_tailors=None
building_info_airport=None
building_info_player_house=None
player_house_sx=0
player_house_sy=0

ocr_worker_thread=None
ocr_detections=None
ocr_detections_set_time=0
ocr_frame=None
ocr_reader=None
ocr_name=None
ocr_name_within=30
ocr_menu=None

hand_slot=0

gathermap_worker_thread=None
gathermap_completed=False

buildgraph_worker_thread=None
buildgraph_completed=False

phonemap_pin_box_sx1=None
phonemap_pin_box_sy1=None
phonemap_pin_box_sx2=None
phonemap_pin_box_sy2=None

beachcomber_list=None

latest_save_restart=0

inside_building_count=0

map_is_gathered=False
graph_is_built=False

debug_window=False

log_file_lock=None

h_graph=None
s_graph=None
v_graph=None
h_graph_s=None
s_graph_s=None
v_graph_s=None
h_maxima=None
s_maxima=None
v_maxima=None

# measured peaks will vary by map and hardware
h_p1=None
h_p2a=None
h_p2b=None
h_p3=None
h_p4=None
h_p5=None
h_p6=None
h_p7=None
h_p8=None
h_p9=None

s_p1=None
s_p2=None
s_p3=None

v_p1=None
v_p2=None
v_p3=None
v_p4=None
v_p5=None
v_p6=None
v_p7=None
v_p8=None
v_p9=None
v_p10=None

# H V to type
hvtt=None

house_color_xy=[]

category_index=None

recipe_name_match=0.85
all_recipes=[]
character_recipes=[]
