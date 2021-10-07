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
pin_orange1=[233,130,46]
pin_orange2=[230,92,45]
# The pin area below the central circle is at least 6x6. If we sample
# every 6 we should be able to find it without checking all pixels in
# the minimap area.
pin_search_x=6
pin_search_y=6
pin_width=19
pin_height=26
#pin_center_to_tip=18
pin_center_to_tip=19

# Some of the busy text screens can have about 200 characters to detect.
object_count=200

# minimap screen pixel info
minimap_border_left=1013
minimap_border_right=1261
minimap_border_top=497
minimap_border_bottom=699
minimap_left=1019
minimap_right=1255
minimap_top=503
minimap_bottom=694
minimap_dashes_L2R_0=1057
minimap_dashes_L2R_1=1089
minimap_dashes_L2R_2=1121
minimap_dashes_L2R_3=1153
minimap_dashes_L2R_4=1185
minimap_dashes_L2R_5=1217
# these may be off by one too high
minimap_dashes_T2B_0=532
minimap_dashes_T2B_1=564
minimap_dashes_T2B_2=596
minimap_dashes_T2B_3=628
minimap_dashes_T2B_4=660
minimap_dashes_step=32
minimap_square_spacing=2
# The pin can go off the top of the minimap.
minimap_top_pin=minimap_top-pin_height

# minimap data info
# The minimap is 16x16 squares separated by dashes.
minimap_width=16*7
minimap_height=16*6

maptypes={
    'Unknown':  [0, '_'],
    'Water':  [1, 'W'],
    'Rock':  [2, 'R'],
    'Grass0':  [3, '0'],
    'Grass1':  [4, '1'],
    'Grass2':  [5, '2'],
    'Sand':  [6, 'S'],
    'Dock':  [7, 'd'],
    'Dirt':  [8, 'D']
}

maptype_rev={}
for key in maptypes:
    maptype_rev[maptypes[key][0]]=[key,maptypes[key][1]]

time_turn_180_seconds=0.5

# time in seconds, map distance
time_to_distance=[
    [ 2, 7.0 ],
    [ 1, 3.5 ],
    [ 0.5, 1.65 ],
    [ 0.2, 0.6 ],
    [ 0.1, 0.2 ],
    [ 0.05, 0.0 ]
]
