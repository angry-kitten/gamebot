#
# Copyright 2021 by angry-kitten
# Look at the video and see if there is an interrupt with a continue
# triangle that needs to be acknowledged.
#

import random
import cv2
import gbdata, gbstate, gbscreen
import taskobject
import taskpress
import tasksay
import taskdetect
import taskgotomain
import taskupdatemini
import taskchat
import taskmuseum
import tasksell
import taskstore
import tasktakeinventory
import taskacceptnookmiles
import taskheadinggoto
import taskpathplangoto

class TaskCheckForInterrupt(taskobject.Task):
    """TaskCheckForInterrupt Object"""

    def __init__(self):
        super().__init__()
        self.name="TaskCheckForInterrupt"
        print("new",self.name,"object")
        self.step=0
        self.target_mx=gbstate.player_mx
        self.target_my=gbstate.player_my
        self.added_return=False
        self.added_sell=False
        self.added_store=False
        self.added_museum=False

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

        if gbscreen.is_continue_triangle_detect():
            # maybe announcements
            print("continue triangle detect")
            self.parent.Push(taskdetect.TaskDetect())
            # press B to continue
            self.parent.Push(taskpress.TaskPress('B',5.0))
            return
        if gbscreen.is_continue_triangle():
            # maybe announcements
            print("continue triangle")
            self.parent.Push(taskdetect.TaskDetect())
            # press B to continue
            self.parent.Push(taskpress.TaskPress('B',5.0))
            return
        if gbscreen.is_accept_controller_screen():
            # power hits cause this
            print("accept controller screen")
            self.parent.Push(taskdetect.TaskDetect())
            # press A to accept
            self.parent.Push(taskpress.TaskPress('A',5.0))
            return

        if gbscreen.is_inside_building_screen():
            print("maybe inside building")
            # Wait for the exit animation.
            self.parent.Push(taskobject.TaskTimed(10.0))
            # Walk out of the building, mapless.
            self.parent.Push(taskheadinggoto.TaskHeadingGoTo(180,8))
            return

        if gbscreen.is_main_screen():
            print("main screen")

            if self.step == 0:
                # Don't take inventory every time.
                if gbstate.inventory_needed:
                    self.parent.Push(tasktakeinventory.TaskTakeInventory())
                    gbstate.inventory_needed=False
                else:
                    mebbe=random.randint(0,5)
                    if 1 == mebbe:
                        self.parent.Push(tasktakeinventory.TaskTakeInventory())
                self.step=1
                return

            if self.step == 1:
                self.step=2
                if gbscreen.is_resident_nearby():
                    self.parent.Push(taskchat.TaskChat())
                    return
                return

            if self.step == 2:
                self.step=3
                print("full",gbstate.inventory_slots_full)
                print("size",gbstate.inventory_size)
                #if gbstate.inventory_slots_full == gbstate.inventory_size:
                if gbstate.inventory_slots_full >= (gbstate.inventory_size-2):
                    if self.target_mx >= 0:
                        if not self.added_return:
                            self.added_return=True
                            # Go back to the original location.
                            self.parent.Push(taskpathplangoto.TaskPathPlanGoTo(self.target_mx,self.target_my))
                    if not self.added_sell:
                        self.added_sell=True
                        self.parent.Push(tasksell.TaskSell())
                    if not self.added_store:
                        self.added_store=True
                        self.parent.Push(taskstore.TaskStore())
                    if not self.added_museum:
                        self.added_museum=True
                        self.parent.Push(taskmuseum.TaskMuseum())
                    return
                return

            if self.step == 3:
                self.step=4
                print("full",gbstate.inventory_slots_full)
                print("free",gbstate.inventory_slots_free)
                if gbstate.inventory_slots_full > 0 and gbstate.inventory_slots_free == 0:
                    if self.target_mx >= 0:
                        if not self.added_return:
                            self.added_return=True
                            # Go back to the original location.
                            self.parent.Push(taskpathplangoto.TaskPathPlanGoTo(self.target_mx,self.target_my))
                    if not self.added_sell:
                        self.added_sell=True
                        self.parent.Push(tasksell.TaskSell())
                    if not self.added_store:
                        self.added_store=True
                        self.parent.Push(taskstore.TaskStore())
                    if not self.added_museum:
                        self.added_museum=True
                        self.parent.Push(taskmuseum.TaskMuseum())
                    return
                return

            if self.step == 4:
                self.step=5
                if gbscreen.has_label('PhoneActive',0.30,-1,-1,-1):
                    self.parent.Push(taskacceptnookmiles.TaskAcceptNookMiles())
                elif gbscreen.has_label('PhoneActivePlus',0.30,-1,-1,-1):
                    self.parent.Push(taskacceptnookmiles.TaskAcceptNookMiles())
                return

            print(self.name,"done")
            self.taskdone=True
            return

        self.parent.Push(taskdetect.TaskDetect())
        return

    def Start(self):
        """Cause the task to begin doing whatever."""
        print(self.name,"Start")
        if self.started:
            return # already started
        self.started=True
        self.target_mx=gbstate.player_mx
        self.target_my=gbstate.player_my
        self.step=0
        # push tasks in reverse order
        self.parent.Push(taskdetect.TaskDetect())
        # Wait for things to settle.
        self.parent.Push(taskobject.TaskTimed(3.0))

    def DebugRecursive(self,indent=0):
        self.DebugPrint(self.name,indent)

    def NameRecursive(self):
        gbstate.task_stack_names.append(self.name)
        return self.name
