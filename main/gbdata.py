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

# continue arrow info
contarrow_loc=[641,663] # x and y based on 1280x720 upper left origin
contarrow_color=[246,186,8] # RGB 0-255
