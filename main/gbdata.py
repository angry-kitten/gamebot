#
# Copyright 2021 by angry-kitten
# A bunch of static data.
#

# Data representing the screen keyboard.
# US locale
# lower case AKA unshifted
skblc=[
['1','2','3','4','5','6','7','8','9','0','-'],
['q','w','e','r','t','y','u','i','o','p','/'],
['a','s','d','f','g','h','j','k','l',':','\''],
['z','x','c','v','b','n','m',',','.','?','!']
]
# upper case AKA shifted
skbuc=[
['#','[',']','$','%','^','&','*','(',')','_'],
['Q','W','E','R','T','Y','U','I','O','P','@'],
['A','S','D','F','G','H','J','K','L',';','"'],
['Z','X','C','V','B','N','M','<','>','+','=']
]
# delete is button B
# return is button -
# confirm is button +
# space is button Y
# bottom row is
# globe, shift, alphabet, symbol, accent 1, accent 2, space

# Standard screen size
stdscreen_size=[1280,720] # wxh upper left origin

# continue triangle info
conttriangle_loc=[641,663] # x and y based on 1280x720 upper left origin
conttriangle_color=[246,186,8] # RGB 0-255

# minimap pin color. It flashes between these two.
pin_orange1=[233,130,46] # rgb
pin_orange2=[230,92,45] # rgb
# The pin area below the central circle is at least 6x6. If we sample
# every 6 we should be able to find it without checking all pixels in
# the minimap area.
minimap_pin_search_x=6
minimap_pin_search_y=6
minimap_pin_width=19
minimap_pin_height=26
#minimap_pin_center_to_tip=18
minimap_pin_center_to_tip=19
minimap_pin_tune_mx=-0.5
minimap_pin_tune_my=0.0

# phonemap pin info
phonemap_pin_search_x=6
phonemap_pin_search_y=6
phonemap_pin_width=29
phonemap_pin_height=41
#phonemap_pin_center_to_tip=23
#phonemap_pin_center_to_tip=23.25
phonemap_pin_center_to_tip=23.50

# Some of the busy text screens can have about 200 characters to detect.
object_count=200

# The map starts in the upper left with mx=0,my=0. The center of
# the upper left square is mx=0.5,my=0.5.

# minimap screen pixel info
minimap_border_left=1013
minimap_border_right=1261
minimap_border_top=497
minimap_border_bottom=699
minimap_left=1019
minimap_right=1255
minimap_top=503
minimap_bottom=694
# sx
minimap_dashes_L2R_0=1057
minimap_dashes_L2R_1=1089
minimap_dashes_L2R_2=1121
minimap_dashes_L2R_3=1153
minimap_dashes_L2R_4=1185
minimap_dashes_L2R_5=1217
# these may be off by one too high
# sy
minimap_dashes_T2B_0=532
minimap_dashes_T2B_1=564
minimap_dashes_T2B_2=596
minimap_dashes_T2B_3=628
minimap_dashes_T2B_4=660
minimap_dashes_step=32
minimap_square_spacing=2
minimap_origin_x=minimap_dashes_L2R_0-minimap_dashes_step
minimap_origin_y=minimap_dashes_T2B_0-minimap_dashes_step
# The pin can go off the top of the minimap.
minimap_top_pin=minimap_top-minimap_pin_height

# phonemap screen pixel info
# sx
phonemap_dashes_L2R_0=440
phonemap_dashes_L2R_1=525
phonemap_dashes_L2R_2=610
phonemap_dashes_L2R_3=696
phonemap_dashes_L2R_4=781
phonemap_dashes_L2R_5=866
# these may be off by one too high
# sy
phonemap_dashes_T2B_0=203
phonemap_dashes_T2B_1=288
phonemap_dashes_T2B_2=374
phonemap_dashes_T2B_3=459
phonemap_dashes_T2B_4=544
phonemap_dashes_step=85
phonemap_square_spacing=phonemap_dashes_step/16
phonemap_origin_x=phonemap_dashes_L2R_0-phonemap_dashes_step
phonemap_origin_y=phonemap_dashes_T2B_0-phonemap_dashes_step

phonemap_left=phonemap_dashes_L2R_0-(phonemap_dashes_step*2)
phonemap_right=phonemap_dashes_L2R_5+(phonemap_dashes_step*2)
phonemap_top=phonemap_dashes_T2B_0-(phonemap_dashes_step*2)
phonemap_bottom=phonemap_dashes_T2B_4+(phonemap_dashes_step*2)
phonemap_top_pin=phonemap_top-phonemap_pin_height

# map and minimap data info
# The minimap is 16x16 squares separated by dashes.
map_width=16*7
map_height=16*6
minimap_width=map_width
minimap_height=map_height
phonemap_width=map_width
phonemap_height=map_height

maptype_water=1
maptypes={
    'Unknown':  [0, '_'],
    'Water':  [maptype_water, 'W'],
    'Rock':  [2, 'R'],
    'Grass0':  [3, '0'],
    'Grass1':  [4, '1'],
    'Grass2':  [5, '2'],
    'Sand':  [6, 'S'],
    'Dock':  [7, 'd'],
    'Dirt':  [8, 'D']
}
minimap_color_water1=[156,221,186] # rgb
minimap_color_water2=[121,207,180] # rgb
minimap_color_rock=[113,116,136] # rgb
minimap_color_grass0=[71,125,68] # rgb
minimap_color_grass1=[70,171,67] # rgb
minimap_color_grass2=[99,212,78] # rgb
minimap_color_sand=[245,234,165] # rgb
minimap_color_dock=[157,131,97] # rgb
minimap_color_dirt=[174,159,125] # rgb

phonemap_color_water1=[129,225,197] # rgb
phonemap_color_water2=[121,207,180] # rgb
phonemap_color_rock=[113,116,136] # rgb
phonemap_color_grass0=[71,131,66] # rgb
phonemap_color_grass1=[70,171,67] # rgb
phonemap_color_grass2=[99,212,78] # rgb
phonemap_color_sand=[236,231,162] # rgb
phonemap_color_dock=[162,140,102] # rgb
phonemap_color_dirt=[174,159,125] # rgb

obstruction_maptype_unknown=0
obstruction_maptype_not_obstructed=1
obstruction_maptype_obstructed=2
obstruction_maptype_standing_on_water=3

maptype_rev={}
for key in maptypes:
    maptype_rev[maptypes[key][0]]=[key,maptypes[key][1]]

# obsolete
# #time_turn_180_seconds=0.285
# time_turn_180_seconds=0.280
# #distance_turn_180=0.20
# distance_turn_180=0.19

# obsolete
# # time in seconds, map distance
# time_to_distance=[
#     [ 2, 7.0 ],
#     [ 1, 3.5 ],
#     [ 0.5, 1.65 ],
#     [ 0.2, 0.6 ],
#     [ 0.1, 0.2 ],
#     [ 0.05, 0.0 ]
# ]

#index_for_fit=-10
# meta slope
# -0.0014280442916581038 0.26976168054446614
# meta offset
# 0.01950835441527321 0.1813621758484305
distance_to_time=0.26976168054446614 # seconds per map square distance
angle_to_time=0.001950835441527321 # seconds per degree

# This is the extent of the inventory area in screen pixels.
inventory_sy1=75
inventory_sy2=450
inventory_sx1=300
inventory_sx2=980

# Screen locations for the 20 item inventory. The
# dot ones are the center of the InvEmpty dots.
inventory_locations_20 = [
    (338,199), # 0
    (403,181),
    (472,172),
    (538,167),
    (607,162),
    (674,164),
    (743,166),
    (804,171),
    (874,184),
    (941,200), # 9 dot
    (338,278), # 10 dot
    (404,263),
    (471,250),
    (540,244),
    (606,240),
    (674,239), # dot
    (741,243),
    (808,250),
    (876,262),
    (940,277)  # 19
]
inventory_pointer_offset_x=40
inventory_pointer_offset_y=39

gatherable_items=[
    "Weeds",
    "Branches",
    "Stone",
    "OrangeShell",
    "GrayShell",
    "SummerShell",
    "Coral",
    "Iron",
    "Clay",
    "Wood",
    "SoftWood",
    "HardWood",
    "Bamboo",
    "Orange",
    "Peach",
    "Pear",
    "Cherries",
    "Apple",
    "Coconut",
    "WeedsBag"
]

phone_box_top_sy=212
phone_box_bottom_sy=584
phone_box_left_sx=226
phone_box_right_sx=585

phone_locations = [
    (303,282),
    (398,282),
    (495,282),
    (303,385),
    (398,385),
    (495,385),
    (303,488),
    (398,488),
    (495,488)
]
# x offset for selecting a pixel for finding an
# icon by color.
phone_color_offset_x=-37
phone_map_color=[136,224,187] # rgb

# this is the background color of the phone map screen
phone_map_background=[130,224,195] # rgb 8

feet_region_x1=494
feet_region_x2=787
feet_region_y1=337
feet_region_y2=497

player_region_x1=494
player_region_x2=787
player_region_y1=207
player_region_y2=497
