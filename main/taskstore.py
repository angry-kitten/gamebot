#
# Copyright 2021-2022 by angry-kitten
# Go to the home and store stuff.
#

import gbdata, gbstate, gbscreen
import cv2
import gbocr
import taskobject
import taskpress
import tasksay
import taskdetect
import taskgotomain
import taskupdatemini
import taskpathplangoto
import taskheadinggoto
import tasktakeinventory
import taskocr

class TaskStore(taskobject.Task):
    """TaskStore Object"""

    def __init__(self):
        super().__init__()
        self.name="TaskStore"
        print("new",self.name,"object")
        self.step=0
        self.within=1
        self.ratio=0.30
        self.name_within=30
        self.ocr_name=None
        self.ocr_menu=None

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

        print(self.name,"step=",self.step)

        if self.step == 0:
            # Verify that player character is in front of the house.
            mx=gbstate.building_info_player_house[3]
            my=gbstate.building_info_player_house[4]
            if not (gbscreen.match_within(gbstate.player_mx,mx,self.within) and gbscreen.match_within(gbstate.player_my,my,self.within)):
                self.step=99
                return

            # Do a detect to get ready for is_inside_building_screen
            self.parent.Push(taskdetect.TaskDetect())

            # Wait for the entrance animation.
            self.parent.Push(taskobject.TaskTimed(12.0))

            # Press 'A' to enter the house.
            self.parent.Push(taskpress.TaskPress('A'))

            # Walk towards the door.
            self.parent.Push(taskheadinggoto.TaskHeadingGoTo(0,1.0))

            self.step=1
            return

        if self.step == 1:
            if not gbscreen.is_inside_building_screen():
                print("not inside")
                self.step=99
                return

            # Start by taking the normal inventory.
            self.parent.Push(tasktakeinventory.TaskTakeInventory())

            self.step=2
            return

        if self.step == 2:
            # open inventory
            self.parent.Push(taskdetect.TaskDetect())
            self.parent.Push(taskobject.TaskTimed(2.0)) # wait for the inventory to open
            self.parent.Push(taskpress.TaskPress('X'))
            gbstate.draw_inventory_locations=True
            self.step=3
            return

        if self.step == 3:
            # locate the hand
            # find the pointer hand
            hand_match=gbscreen.has_label_in_box('PointerHand',self.ratio,gbdata.inventory_sx1,gbdata.inventory_sx2,gbdata.inventory_sy1,gbdata.inventory_sy2)
            if hand_match is None:
                print("hand not found")
                self.step=80 # close inventory
                return

            # Find the slot number for the hand.
            x=hand_match[2]
            y=hand_match[3]
            # Estimate the inventory position the hand is pointing at.
            x-=gbdata.inventory_pointer_offset_x
            y-=gbdata.inventory_pointer_offset_y
            hand_slot=gbscreen.find_inventory_slot(x,y)
            print("hand_slot is",hand_slot)
            if hand_slot is None:
                print("hand_slot not found")
                self.step=80 # close inventory
                return
            gbstate.hand_slot=hand_slot
            self.store_slot=0

            self.step=10
            return

# Example inventory
# inventory_name ['InvNet', 'InvAxe', 'InvAxe', 'InvPole', 'InvPole', 'InvPole', 'InvNet', 'InvShovel', 'InvShovel', 'InvNet', 'InvFishingPole', 'InvWetSuit', 'InvSlingshot', 'InvWetSuit', 'InvWateringCan', 'InvHardWood', 'InvHardWood', 'InvNet', 'InvNet', 'InvNet', 'InvMedicine', 'InvLadder', 'InvEmpty', '', 'InvNet', 'InvNet', 'InvPole', 'InvNet', 'InvStoneAxe', 'InvShovel']
        if self.step == 10:
            print("hand_slot",gbstate.hand_slot)
            print("store_slot",self.store_slot)
            print("inventory_size",gbstate.inventory_size)
            if self.store_slot >= gbstate.inventory_size:
                # We are done storing.
                self.step=80
                return
            gbocr.move_hand_to_slot(self.store_slot,self)
            print("hand_slot",gbstate.hand_slot)
            self.step=11
            return

        if self.step == 11:
            # Select the item to bring up the menu. Then ocr the
            # object name and the menu at the same time.
            self.parent.Push(taskocr.TaskOCR())
            self.parent.Push(taskobject.TaskTimed(1.0)) # wait for menu to pop up
            self.parent.Push(taskpress.TaskPress('A'))
            self.step=12
            return

        if self.step == 12:
            self.digest_name_and_menu()
            print("ocr name",self.ocr_name)
            print("ocr menu",self.ocr_menu)
            if self.ocr_name is None and self.ocr_menu is None:
                # There may not be a menu. Assume there is no menu to
                # pop down.
                # Move to the next slot
                self.store_slot+=1
                self.step=10
                return
            if self.ocr_menu is None:
                self.step=19 # close the menu without selecting anything
                return

            # The menu was detected but not an item name.

            if self.ocr_name is None:
                # OCR didn't find a name or it couldn't detect a
                # long curved name.
                # Check for something from the basic "take inventory".
                inv_name=gbstate.inventory_name[self.store_slot]
            else:
                inv_name=gbocr.ocr_name_to_inv_name(self.ocr_name)

            print("inv_name",inv_name)

            store_it=False

            if inv_name is not None:
                if inv_name != '':
                    # Look at the item and decide if we want to store it.
                    if inv_name not in gbdata.item_store:
                        # We know the inventory name of the item and it
                        # is not in the list of things to store.
                        self.step=19 # close the menu without selecting anything
                        return
                    else:
                        store_it=True

            # At this point we either know the name of an item and will
            # store it or we don't know what it is.

            if len(self.ocr_menu) < 1:
                self.step=19 # close the menu without selecting anything
                return
            (index,is_last)=gbocr.locate_menu_text(self.ocr_menu,'Put in Storage')
            if index is None:
                self.step=19 # close the menu without selecting anything
                return

            if not store_it:
                # We don't know the inventory name of the item.
                # We know the item can be stored. Get hints from the menu
                # about the properties of the item.
                can_wear=False
                can_place=False
                can_hang=False
                can_drop=False
                can_grab=False
                can_show=False
                can_eat=False
                can_open=False
                can_clear_favorite=False
                can_favorite=False
                can_put_away=False
                (index2,is_last2)=gbocr.locate_menu_text(self.ocr_menu,'Wear')
                if index2 is not None:
                    can_wear=True
                (index2,is_last2)=gbocr.locate_menu_text(self.ocr_menu,'Place Item')
                if index2 is not None:
                    can_place=True
                (index2,is_last2)=gbocr.locate_menu_text(self.ocr_menu,'Hang on Wall')
                if index2 is not None:
                    can_hang=True
                (index2,is_last2)=gbocr.locate_menu_text(self.ocr_menu,'Drop Item')
                if index2 is not None:
                    can_drop=True
                (index2,is_last2)=gbocr.locate_menu_text(self.ocr_menu,'Grab 1')
                if index2 is not None:
                    can_grab=True
                (index2,is_last2)=gbocr.locate_menu_text(self.ocr_menu,'Show it off!')
                if index2 is not None:
                    can_show=True
                (index2,is_last2)=gbocr.locate_menu_text(self.ocr_menu,'Eat')
                if index2 is not None:
                    can_eat=True
                (index2,is_last2)=gbocr.locate_menu_text(self.ocr_menu,'Open')
                if index2 is not None:
                    can_open=True
                (index2,is_last2)=gbocr.locate_menu_text(self.ocr_menu,'Clear Favorite')
                if index2 is not None:
                    can_clear_favorite=True
                (index2,is_last2)=gbocr.locate_menu_text(self.ocr_menu,'Favorite')
                if index2 is not None:
                    can_favorite=True
                (index2,is_last2)=gbocr.locate_menu_text(self.ocr_menu,'Put Away')
                if index2 is not None:
                    can_put_away=True

                print(f"can_wear={can_wear}")
                print(f"can_place={can_place}")
                print(f"can_hang={can_hang}")
                print(f"can_drop={can_drop}")
                print(f"can_grab={can_grab}")
                print(f"can_show={can_show}")
                print(f"can_eat={can_eat}")
                print(f"can_open={can_open}")
                print(f"can_clear_favorite={can_clear_favorite}")
                print(f"can_favorite={can_favorite}")
                print(f"can_put_away={can_put_away}")

                if can_put_away:
                    # Most likely bag of bells. There shouldn't be
                    # a "Put in Storage" option anyway.
                    self.step=19 # close the menu without selecting anything
                    return
                elif can_clear_favorite or can_favorite:
                    # Most likely a tool. Don't store.
                    self.step=19 # close the menu without selecting anything
                    return
                elif can_eat:
                    # A fruit or meal of some kind. Store.
                    store_it=True
                elif can_wear and can_hang:
                    # An item of clothing, but not a flower (which can be worn)
                    store_it=True
                elif can_wear and not can_hang:
                    # A flower or similar item.
                    self.step=19 # close the menu without selecting anything
                    return
                elif can_drop and can_grab:
                    # A bulk item like iron or weeds.
                    store_it=True
                elif can_place and not can_wear:
                    # A house item that is not a flower.
                    store_it=True
                elif can_open:
                    # A present or message bottle.
                    # This code will probably not be reached because
                    # there shouldn't be a "Put in Storage" option.
                    store_it=True
                else:
                    # Not enough info to guess.
                    self.step=19 # close the menu without selecting anything
                    return

            # At this point we know we have an item to store and the
            # menu has an option for it. Move the pointer hand to the
            # menu entry and select it.

            self.parent.Push(taskobject.TaskTimed(1.0)) # wait for menu to pop down
            self.parent.Push(taskpress.TaskPress('A'))

            if index != 0:
                print("need to move the pointer hand")
                if is_last:
                    print("move up to wrap around to last item in menu")
                    self.parent.Push(taskobject.TaskTimed(1.0)) # wait for the animation
                    self.parent.Push(taskpress.TaskPress('hat_TOP'))
                else:
                    print("move down by",index)
                    for j in range(index):
                        self.parent.Push(taskobject.TaskTimed(1.0)) # wait for the animation
                        self.parent.Push(taskpress.TaskPress('hat_BOTTOM'))

            # Move to the next slot
            self.store_slot+=1
            self.step=10
            return

        if self.step == 19:
            # Close the menu without selecting anything.
            self.parent.Push(taskobject.TaskTimed(1.0)) # wait for menu to pop down
            self.parent.Push(taskpress.TaskPress('B'))
            # Move to the next slot
            self.store_slot+=1
            self.step=10
            return

        if self.step == 80:
            # close the inventory
            self.parent.Push(taskobject.TaskTimed(2.0)) # wait for the inventory to close
            self.parent.Push(taskpress.TaskPress('B'))
            gbstate.draw_inventory_locations=False
            self.step=90
            return

        if self.step == 90:
            # Exit the player house.
            # Wait for the exit animation.
            self.parent.Push(taskobject.TaskTimed(10.0))
            # Walk out of the building, mapless.
            self.parent.Push(taskheadinggoto.TaskHeadingGoTo(180,8))
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
        self.step=0

        if gbstate.building_info_player_house is None:
            self.step=99
            return
        mx=gbstate.building_info_player_house[3]
        my=gbstate.building_info_player_house[4]
        self.parent.Push(taskpathplangoto.TaskPathPlanGoTo(mx,my))
        return

    def DebugRecursive(self,indent=0):
        self.DebugPrint(self.name,indent)
        return

    def NameRecursive(self):
        gbstate.task_stack_names.append(self.name)
        return self.name

# Example OCR data
# [([[439, 35], [641, 35], [641, 73], [439, 73]], 'Vaulting pole', 0.9577903529709549), ([[797, 339], [959, 339], [959, 380], [797, 380]], 'Place Item', 0.8997346079334698), ([[327, 394], [454, 394], [454, 446], [327, 446]], '23,555', 0.726360381715388), ([[801, 394], [1015, 394], [1015, 433], [801, 433]], 'Put in Storage', 0.9066206404337775), ([[802, 452], [924, 452], [924, 484], [802, 484]], 'Favorite', 0.9996292247387993), ([[989, 681], [1009, 681], [1009, 703], [989, 703]], 'B', 0.9999361048414812), ([[1013, 675], [1096, 675], [1096, 711], [1013, 711]], 'Close', 0.9999234436005648), ([[1148, 678], [1238, 678], [1238, 710], [1148, 710]], 'Select', 0.9999911425992467), ([[377.4871464448379, 184.4665807565786], [552.2369732838534, 160.82192444134853], [556.5128535551621, 223.5334192434214], [382.7630267161465, 247.17807555865147]], '0 P &', 0.6320404477802022)]
    def digest_name_and_menu(self):
        self.ocr_name=None
        self.ocr_menu=None
        with gbstate.ocr_worker_thread.data_lock:
            dets=gbstate.ocr_detections
        if dets is None:
            return
        (slot_sx,slot_sy)=gbstate.inventory_locations[gbstate.hand_slot]
        expect_name_sx=slot_sx
        expect_name_sy=slot_sy+gbdata.ocr_inv_name_offset_y
        menu=[]
        for det in dets:
            print("det",det)
            (box,text,score)=det
            (csx,csy)=gbocr.ocr_box_to_center(box)
            if gbscreen.is_inside_box(gbdata.ocr_inv_menu_lane_x1,gbdata.ocr_inv_menu_lane_x2,gbdata.ocr_inv_menu_lane_y1,gbdata.ocr_inv_menu_lane_y2,csx,csy):
                print("menu item")
                entry=[csy,text]
                menu.append(entry)
                continue
            if gbscreen.is_near_within(expect_name_sx,expect_name_sy,csx,csy,self.name_within):
                print("item name")
                self.ocr_name=text
                continue
        if len(menu) < 1:
            self.ocr_menu=None
        else:
            # Sort the menu by sy
            self.ocr_menu=sorted(menu,key=lambda entry: entry[0])
        return
