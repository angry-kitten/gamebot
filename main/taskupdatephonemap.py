#
# Copyright 2021 by angry-kitten
# Look at the current screen and capture the phone map and
# determine player location from the pin.
#

import time
import numpy
import taskobject
import gbdata
import gbstate
import cv2
import taskpress
import tasksay
import taskdetect
import taskgotomain
import gbscreen
import gbtrack
import gbdisplay

class TaskUpdatePhoneMap(taskobject.Task):
    """TaskUpdatePhoneMap Object"""

    def __init__(self):
        super().__init__()
        self.name="TaskUpdatePhoneMap"
        print("new",self.name,"object")
        self.step=0 # pop up phone
        self.icons=[]

    def Poll(self):
        """check if any action can be taken"""
        print(self.name,"Poll")
        if not self.started:
            self.Start()
            return
        if self.taskdone:
            return
        if gbstate.frame is None:
            return

        print("step is",self.step)

        if self.step == 0:
            self.select_map()
            return

        if self.step == 1:
            if not gbscreen.is_phone_map_screen():
                print("not on phone map screen")
                self.step=99
                self.parent.Push(taskpress.TaskPress('B',1.0))
                self.parent.Push(taskpress.TaskPress('B',1.0))
                self.parent.Push(taskpress.TaskPress('B',1.0))
                return
            print("yes on phone map screen")
            self.gather_phonemap()
            self.position_from_phonemap()
            self.locate_buildings()
            self.step=2
            return

        if self.step == 2:
            # close map
            self.parent.Push(taskpress.TaskPress('B',1.0))
            self.step=3
            return

        if self.step == 3:
            # close phone
            self.parent.Push(taskpress.TaskPress('B',1.0))
            self.step=99
            return

        print(self.name,"done")
        self.taskdone=True
        return

    def Start(self):
        """Cause the task to begin doing whatever."""
        print(self.name,"Start")
        if self.started:
            return # already started
        self.started=True
        self.step=0 # pop up phone

        # Move the pointer hand to the lower right so we know
        # where it is.
        self.parent.Push(taskpress.TaskPress('hat_BOTTOM'))
        self.parent.Push(taskpress.TaskPress('hat_BOTTOM'))
        self.parent.Push(taskpress.TaskPress('hat_RIGHT'))
        self.parent.Push(taskpress.TaskPress('hat_RIGHT'))

        # Move to the upper left.
        self.parent.Push(taskpress.TaskPress('hat_LEFT'))
        self.parent.Push(taskpress.TaskPress('hat_LEFT'))
        self.parent.Push(taskpress.TaskPress('hat_LEFT'))
        self.parent.Push(taskpress.TaskPress('hat_LEFT'))
        self.parent.Push(taskpress.TaskPress('hat_LEFT'))
        self.parent.Push(taskpress.TaskPress('hat_TOP'))
        self.parent.Push(taskpress.TaskPress('hat_TOP'))
        self.parent.Push(taskpress.TaskPress('hat_TOP'))

        # Wait for the phone screen to pop up.
        self.parent.Push(taskobject.TaskTimed(1.0))
        # Pop up the phone with ZL
        self.parent.Push(taskpress.TaskPress('ZL'))

    def DebugRecursive(self,indent=0):
        self.DebugPrint(self.name,indent)

    def NameRecursive(self):
        gbstate.task_stack_names.append(self.name)
        return self.name

    def find_icon_by_color(self):
        l=len(gbdata.phone_locations)
        for i in range(l):
            (sx,sy)=gbdata.phone_locations[i]
            sx2=sx+gbdata.phone_color_offset_x
            sy2=sy
            if gbscreen.color_match_array(sx2,sy2,gbdata.phone_map_color,5):
                return i
        return None

    def select_map(self):
        # Try finding the icon by color.
        best_slot=self.find_icon_by_color()
        if best_slot is None:
            print("no slot found by color")
            self.step=3
            return

        print("slot found",best_slot)
        # Wait for the phone screen to pop up and feature highlight
        # to finish.
        #self.parent.Push(taskobject.TaskTimed(30.0))
        self.parent.Push(taskobject.TaskTimed(4.0))
        # Pop up the map with A
        self.parent.Push(taskpress.TaskPress('A'))

        current_slot=8
        while current_slot > best_slot:
            delta=current_slot-best_slot
            if delta >= 3:
                # go up one
                print("go up one")
                #self.parent.Push(taskpress.TaskPress('hat_TOP',1.0))
                self.parent.Push(taskpress.TaskPress('hat_TOP'))
                current_slot-=3
            else:
                # go left one
                print("go left one")
                #self.parent.Push(taskpress.TaskPress('hat_LEFT',1.0))
                self.parent.Push(taskpress.TaskPress('hat_LEFT'))
                current_slot-=1

        print("set step 1")
        self.step=1

    def process_location(self,data_x,data_y,pixel_x,pixel_y):
        (b,g,r)=gbscreen.get_pixel(pixel_x,pixel_y)
        if gbscreen.color_match_rgb_array(r,g,b,gbdata.phonemap_color_water1,8):
            gbstate.phonemap[data_x][data_y]=gbdata.maptypes['Water'][0]
            return
        if gbscreen.color_match_rgb_array(r,g,b,gbdata.phonemap_color_water2,8):
            gbstate.phonemap[data_x][data_y]=gbdata.maptypes['Water'][0]
            return
        if gbscreen.color_match_rgb_array(r,g,b,gbdata.phonemap_color_rock,8):
            gbstate.phonemap[data_x][data_y]=gbdata.maptypes['Rock'][0]
            return
        if gbscreen.color_match_rgb_array(r,g,b,gbdata.phonemap_color_grass0,8):
            gbstate.phonemap[data_x][data_y]=gbdata.maptypes['Grass0'][0]
            return
        if gbscreen.color_match_rgb_array(r,g,b,gbdata.phonemap_color_grass1,8):
            gbstate.phonemap[data_x][data_y]=gbdata.maptypes['Grass1'][0]
            return
        if gbscreen.color_match_rgb_array(r,g,b,gbdata.phonemap_color_grass2,8):
            gbstate.phonemap[data_x][data_y]=gbdata.maptypes['Grass2'][0]
            return
        if gbscreen.color_match_rgb_array(r,g,b,gbdata.phonemap_color_sand,8):
            gbstate.phonemap[data_x][data_y]=gbdata.maptypes['Sand'][0]
            return
        if gbscreen.color_match_rgb_array(r,g,b,gbdata.phonemap_color_dock,8):
            gbstate.phonemap[data_x][data_y]=gbdata.maptypes['Dock'][0]
            return
        if gbscreen.color_match_rgb_array(r,g,b,gbdata.phonemap_color_dirt,8):
            gbstate.phonemap[data_x][data_y]=gbdata.maptypes['Dirt'][0]
            return
        #gbstate.phonemap[data_x][data_y]=gbdata.maptypes['Unknown'][0]

    def gather_phonemap(self):
        print("l1")
        if gbstate.phonemap is None:
            gbstate.phonemap=[0 for x in range(gbdata.phonemap_width)]
            for data_x in range(gbdata.phonemap_width):
                gbstate.phonemap[data_x]=[0 for y in range(gbdata.phonemap_height)]

        print("l2")
        square_center_offset=gbdata.phonemap_square_spacing/2
        pixel_start_x=gbdata.phonemap_origin_x+square_center_offset
        pixel_start_y=gbdata.phonemap_origin_y+square_center_offset
        for data_x in range(gbdata.phonemap_width):
            pixel_x=int(round((data_x*gbdata.phonemap_square_spacing)+pixel_start_x))
            for data_y in range(gbdata.phonemap_height):
                pixel_y=int(round((data_y*gbdata.phonemap_square_spacing)+pixel_start_y))
                self.process_location(data_x,data_y,pixel_x,pixel_y)
        print("l3")

    def debug_phonemap(self):
        if gbstate.phonemap is None:
            print("no phonemap")
            return
        for y in range(gbdata.phonemap_height):
            line=''
            for x in range(gbdata.phonemap_width):
                line+=gbdata.maptype_rev[gbstate.phonemap[x][y]][1]
            print(line)

    def is_pin_orange(self,pixel_x,pixel_y):
        pixel_x=int(round(pixel_x))
        pixel_y=int(round(pixel_y))
        if gbscreen.color_match_array(pixel_x,pixel_y,gbdata.pin_orange1,5):
            return True
        if gbscreen.color_match_array(pixel_x,pixel_y,gbdata.pin_orange2,5):
            return True
        return False

    def is_circle_gray(self,pixel_x,pixel_y):
        pixel_x=int(round(pixel_x))
        pixel_y=int(round(pixel_y))
        if gbscreen.color_match_array(pixel_x,pixel_y,gbdata.phonemap_circle_gray,5):
            return True
        return False

    def is_circle_icon(self,pixel_x,pixel_y):
        pixel_x=int(round(pixel_x))
        pixel_y=int(round(pixel_y))
        if gbscreen.color_match_array(pixel_x,pixel_y,gbdata.phonemap_circle_icon,2):
            return True
        return False

    def locate_vertical_center_line(self,startx,starty):
        # Now use the white circle to find the vertical center line.
        # Scan left from the previous center line.
        circle_left_x=startx
        circle_right_x=startx
        for j in range(1,gbdata.phonemap_pin_width):
            lx=startx-j
            if self.is_pin_orange(lx,starty):
                circle_left_x=lx
                break
        # Scan right from the previous center line.
        for j in range(1,gbdata.phonemap_pin_width):
            rx=startx+j
            if self.is_pin_orange(rx,starty):
                circle_right_x=rx
                break
        # circle_right_y and circle_left_y are one pixel right and left
        # of the white circle.
        print("circle_left_x=",circle_left_x)
        print("circle_right_x=",circle_right_x)
        circle_center_x=(circle_left_x+circle_right_x)/2
        print("circle_center_x=",circle_center_x)
        return circle_center_x

    def locate_horizontal_center_line(self,startx,starty):
        # Now use the white circle to find the horizontal center line.
        # Scan up from the previous center line.
        circle_top_y=starty
        circle_bottom_y=starty
        for j in range(1,gbdata.phonemap_pin_height):
            ty=starty-j
            if self.is_pin_orange(startx,ty):
                circle_top_y=ty
                break
        # Scan down from the previous center line.
        for j in range(1,gbdata.phonemap_pin_height):
            by=starty+j
            if self.is_pin_orange(startx,by):
                circle_bottom_y=by
                break
        # circle_top_y and circle_bottom_y are one pixel above and below
        # the white circle.
        print("circle_top_y=",circle_top_y)
        print("circle_bottom_y=",circle_bottom_y)
        circle_center_y=(circle_top_y+circle_bottom_y)/2
        print("circle_center_y=",circle_center_y)
        return circle_center_y

    def verify_pin_shape(self,x,y):
        """Verify that there is a pin at this location and
        not some other thing that happens to have the same color"""
        #print("verify_pin_shape")

        # Scan pixels left and right to try to find the vertical center line
        # of the orange part.
        left_x=x
        right_x=x
        for j in range(1,gbdata.phonemap_pin_width):
            lx=x-j
            if self.is_pin_orange(lx,y):
                left_x=lx
            rx=x+j
            if self.is_pin_orange(rx,y):
                right_x=rx
        #print("left_x=",left_x)
        #print("right_x=",right_x)
        cx=(left_x+right_x)/2
        #print("cx=",cx)

        # Scan pixels up and down to try to find vertical extent of the
        # orange part.
        up_y=y
        down_y=y
        for j in range(1,gbdata.phonemap_pin_height):
            uy=y-j
            if self.is_pin_orange(cx,uy):
                up_y=uy
            dy=y+j
            if self.is_pin_orange(cx,dy):
                down_y=dy
        #print("up_y=",up_y)
        #print("down_y=",down_y)
        yextent=(down_y-up_y)+1
        #print("l6")
        if yextent < (gbdata.phonemap_pin_height-10):
            return False
        #print("l7")
        if yextent > (gbdata.phonemap_pin_height+3):
            return False
        #print("l8")

        # Find the white circle in the head of the pin.
        # Scan down from the top.
        circle_top_y=up_y
        circle_bottom_y=down_y
        for j in range(1,gbdata.phonemap_pin_height):
            uy=up_y+j
            if self.is_pin_orange(cx,uy):
                circle_top_y=uy
            else:
                break # it stopped being orange
        # Scan up from the bottom.
        for j in range(1,gbdata.phonemap_pin_height):
            dy=down_y-j
            if self.is_pin_orange(cx,dy):
                circle_bottom_y=dy
            else:
                break # it stopped being orange
        # circle_top_y and circle_bottom_y are one pixel higher and lower
        # than the white circle.
        #print("circle_top_y=",circle_top_y)
        #print("circle_bottom_y=",circle_bottom_y)
        circle_center_y=(circle_bottom_y+circle_top_y)/2
        #print("circle_center_y=",circle_center_y)
        # circle_center_y is the center of the white circle

        # Now use the white circle to find the vertical center line again.
        # The assumption is that it will produce a better value than
        # the one above.
        circle_center_x=self.locate_vertical_center_line(cx,circle_center_y)
        #print("circle_center_x=",circle_center_x)

        # Now use the white circle to find the horizontal center line again.
        # This is an attempt to converge on a good center value.
        circle_center_y=self.locate_horizontal_center_line(circle_center_x,circle_center_y)
        #print("circle_center_y=",circle_center_y)

        # Now we use these new values to scan 5 times and average.

        sumx=0
        tmpx=self.locate_vertical_center_line(circle_center_x,circle_center_y-2)
        #print("tmpx=",tmpx)
        sumx+=tmpx
        tmpx=self.locate_vertical_center_line(circle_center_x,circle_center_y-1)
        #print("tmpx=",tmpx)
        sumx+=tmpx
        tmpx=self.locate_vertical_center_line(circle_center_x,circle_center_y)
        #print("tmpx=",tmpx)
        sumx+=tmpx
        tmpx=self.locate_vertical_center_line(circle_center_x,circle_center_y+1)
        #print("tmpx=",tmpx)
        sumx+=tmpx
        tmpx=self.locate_vertical_center_line(circle_center_x,circle_center_y+2)
        #print("tmpx=",tmpx)
        sumx+=tmpx

        sumy=0
        tmpy=self.locate_horizontal_center_line(circle_center_x-2,circle_center_y)
        #print("tmpy=",tmpy)
        sumy+=tmpy
        tmpy=self.locate_horizontal_center_line(circle_center_x-1,circle_center_y)
        #print("tmpy=",tmpy)
        sumy+=tmpy
        tmpy=self.locate_horizontal_center_line(circle_center_x,circle_center_y)
        #print("tmpy=",tmpy)
        sumy+=tmpy
        tmpy=self.locate_horizontal_center_line(circle_center_x+1,circle_center_y)
        #print("tmpy=",tmpy)
        sumy+=tmpy
        tmpy=self.locate_horizontal_center_line(circle_center_x+2,circle_center_y)
        #print("tmpy=",tmpy)
        sumy+=tmpy

        circle_center_x=sumx/5
        circle_center_y=sumy/5
        #print("circle_center_x=",circle_center_x)
        #print("circle_center_y=",circle_center_y)


        # Calculate a tip location.
        tip_x=circle_center_x
        tip_y=circle_center_y+gbdata.phonemap_pin_center_to_tip
        #print("tip_x=",tip_x)
        #print("tip_y=",tip_y)

        # Calculate the map location from the tip location.
        map_x=(tip_x-gbdata.phonemap_origin_x)/gbdata.phonemap_square_spacing
        map_y=(tip_y-gbdata.phonemap_origin_y)/gbdata.phonemap_square_spacing
        #print("map_x=",map_x)
        #print("map_y=",map_y)
        map_x+=gbdata.phonemap_pin_tune_mx
        map_y+=gbdata.phonemap_pin_tune_my
        #print("map_x=",map_x)
        #print("map_y=",map_y)

        gbstate.position_phonemap_x=map_x
        gbstate.position_phonemap_y=map_y

        gbtrack.set_current_position(map_x,map_y)

        return True

    def position_from_phonemap(self):
        print("position_from_phonemap")
        gbstate.position_phonemap_x=-1
        gbstate.position_phonemap_y=-1
        """Find the orange pin."""
        search_w=gbdata.phonemap_right-gbdata.phonemap_left
        search_h=gbdata.phonemap_bottom-gbdata.phonemap_top_pin
        for local_y in range(0,search_h,gbdata.phonemap_pin_search_y):
            pixel_y=gbdata.phonemap_top_pin+local_y
            for local_x in range(0,search_w,gbdata.phonemap_pin_search_x):
                pixel_x=gbdata.phonemap_left+local_x
                if self.is_pin_orange(pixel_x,pixel_y):
                    print("found phonemap pin at",pixel_x,pixel_y)
                    if self.verify_pin_shape(pixel_x,pixel_y):
                        return
        return

    def locate_buildings(self):
        # find gray circles
        search_w=gbdata.phonemap_right-gbdata.phonemap_left
        search_h=gbdata.phonemap_bottom-gbdata.phonemap_top_pin
        for local_y in range(0,search_h,gbdata.phonemap_gray_search_y):
            pixel_y=gbdata.phonemap_top+local_y
            for local_x in range(0,search_w,gbdata.phonemap_gray_search_x):
                pixel_x=gbdata.phonemap_left+local_x
                if self.is_circle_gray(pixel_x,pixel_y):
                    print("found possible circle at",pixel_x,pixel_y)
                    self.verify_circle(pixel_x,pixel_y)

        # Gather the icons from inside the circles.
        self.gather_icons()

        # Match the icons with known icons.
        self.match_icons()

        return

    def verify_circle(self,start_sx,start_sy):
        print("verify_circle",start_sx,start_sy)

        if self.is_already_found(start_sx,start_sy):
            print("already found")
            return

        max_diameter=gbdata.phonemap_circle_diameter+4
        color=gbdata.phonemap_circle_gray
        # Step left and right looking for the edges.
        left_sx=gbscreen.locate_horizontal_extent(color,start_sy,start_sx,start_sx-max_diameter)
        right_sx=gbscreen.locate_horizontal_extent(color,start_sy,start_sx,start_sx+max_diameter)
        print("left_sx",left_sx)
        print("right_sx",right_sx)

        w=right_sx-left_sx
        print("w",w)
        if w > (gbdata.phonemap_circle_diameter+4):
            # overlapping circles
            return

        center_sx=int(round((left_sx+right_sx)/2))
        print("center_sx",center_sx)

        # Step up and down looking for the edges.
        top_sy=gbscreen.locate_vertical_extent(color,start_sx,start_sy,start_sy-max_diameter)
        bottom_sy=gbscreen.locate_vertical_extent(color,start_sx,start_sy,start_sy+max_diameter)

        print("top_sy",top_sy)
        print("bottom_sy",bottom_sy)

        h=bottom_sy-top_sy
        print("h",h)
        if not gbscreen.match_within(h,gbdata.phonemap_circle_diameter,4):
            print("these are not the droids we are looking for")
            return

        center_sy=int(round((top_sy+bottom_sy)/2))
        print("center_sy",center_sy)

        self.add_gray_circle(center_sx,center_sy)

        return

    def add_gray_circle(self,center_sx,center_sy):
        # first see if it is already there
        for c in gbstate.gray_circle_list:
            if gbscreen.match_within(center_sx,c[0],3) and gbscreen.match_within(center_sy,c[1],3):
                # already there
                return
        gbstate.gray_circle_list.append([center_sx,center_sy])
        l=len(gbstate.gray_circle_list)
        print("l",l)
        return

    def is_already_found(self,start_sx,start_sy):
        radius=gbdata.phonemap_circle_diameter/2
        for c in gbstate.gray_circle_list:
            d=gbdisplay.calculate_distance(start_sx,start_sy,c[0],c[1])
            if d <= radius:
                # already found
                return True
        return False

    def gather_icons(self):
        self.icons=[]
        radius=gbdata.phonemap_circle_diameter/2
        for c in gbstate.gray_circle_list:
            icon=self.gather_an_icon(c[0],c[1])
            whereicon=[c[0],c[1],icon]
            self.icons.append(whereicon)
        return

    def gather_an_icon(self,start_sx,start_sy):
        diameter=gbdata.phonemap_circle_diameter
        radius=int(round(diameter/2))
        sx1=start_sx-radius
        sy1=start_sy-radius
        icon=[0 for i in range(diameter*diameter)]
        for sy2 in range(0,diameter):
            for sx2 in range(0,diameter):
                sx=sx1+sx2
                sy=sy1+sy2
                i=(sy2*diameter)+sx2
                # only collect info inside the circle
                d=gbdisplay.calculate_distance(start_sx,start_sy,sx,sy)
                if d <= radius:
                    if self.is_circle_icon(sx,sy):
                        icon[i]=1
        #print("icon",icon)
        #self.print_icon(icon)
        return icon

    def print_icon(self,icon):
        diameter=gbdata.phonemap_circle_diameter
        print("icon=[")

        for sy in range(0,diameter):
            for sx in range(0,diameter):
                i=(sy*diameter)+sx
                v=icon[i]
                print(v,",",sep='',end='')
            print("")

        print("]")
        return

    def match_icons(self):
        for whereicon in self.icons:
            self.match_an_icon(whereicon)

        # These aren't needed any more.
        self.icons=[]
        return

    def match_an_icon(self,whereicon):
        best_co=None
        best_match=None
        for ni in gbdata.named_icons:
            #print(ni[0])
            co=self.do_icon_match(whereicon[2],ni[1])
            if best_co is None:
                best_co=co
                best_match=ni
            else:
                if best_co < co:
                    best_co=co
                    best_match=ni
        if best_co is not None:
            print("found match")
            print(best_match[0],"is at",whereicon[0],whereicon[1])
            self.set_building(best_match[0],whereicon[0],whereicon[1])
            return
        return

    def do_icon_match(self,icon1,icon2):
        best_co=None
        off_by=1
        for offset_y in range(-off_by,off_by+1):
            for offset_x in range(-off_by,off_by+1):
                co=self.compare_icons_offsets(icon1,icon2,offset_x,offset_y)
                if best_co is None:
                    best_co=co
                else:
                    if best_co < co:
                        best_co=co
        return best_co

    def compare_icons_offsets(self,icon1,icon2,ox,oy):
        i1=icon1.copy()
        i2=icon2.copy()
        # offsets ox, oy are how much to adjust icon1
        diameter=gbdata.phonemap_circle_diameter
        adjust=(diameter*oy)+ox
        if adjust < 0:
            # Chop off the beginning of icon1 and append
            # zeros to the end.
            n=-adjust
            i1=i1[n:]
            i1.extend([0 for j in range(n)])
        elif adjust > 0:
            # Chop off the end of icon1 and append
            # zeros to the beginning.
            n=adjust
            i1tmp=[0 for j in range(n)]
            i1tmp.extend(i1[0:-n])
            i1=i1tmp

        l1=len(i1)
        l2=len(i2)
        #print("l1 l2",l1,l2)
        co=self.compare_icons(i1,i2)
        #print("co",co)
        return co

    def compare_icons(self,icon1,icon2):
        co=numpy.correlate(icon1,icon2)
        #print("co",co)
        return co

    def set_building(self,name,sx,sy):
        # Calculate the map location given the screen location.
        mx=(sx-gbdata.phonemap_origin_x)/gbdata.phonemap_square_spacing
        my=(sy-gbdata.phonemap_origin_y)/gbdata.phonemap_square_spacing

        # binfo is [name,centermx,centermy,doormx,doormy]
        if name == 'campsite':
            binfo=[name,mx,my,mx,my+3]
            gbstate.building_info_campsite=binfo
        elif name == 'museum':
            binfo=[name,mx,my,mx,my+3]
            gbstate.building_info_museum=binfo
        elif name == 'cranny':
            binfo=[name,mx,my,mx,my+3]
            gbstate.building_info_cranny=binfo
        elif name == 'services':
            binfo=[name,mx,my,mx,my+3]
            gbstate.building_info_services=binfo
        elif name == 'tailors':
            binfo=[name,mx,my,mx,my+3]
            gbstate.building_info_tailors=binfo
        elif name == 'airport':
            binfo=[name,mx,my,mx,my+3]
            gbstate.building_info_airport=binfo
        else:
            print("unknown building name")
        return
