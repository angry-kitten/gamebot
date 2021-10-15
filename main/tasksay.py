#
# Copyright 2021 by angry-kitten
# A task for the player character to say something using the screen
# keyboard.
#

import taskobject
import gbdata
import taskpress

class TaskSay(taskobject.Task):
    """TaskSay Object"""

    def __init__(self,saythis):
        super().__init__()
        self.name="TaskSay"
        print("new TaskSay object")
        self.saythis=saythis
        self.step=0
        self.substep=0
        self.skb_x=0 # + is right
        self.skb_y=0 # + is down

    def Poll(self):
        """check if any action can be taken"""
        print("TaskSay Poll")
        if not self.started:
            self.Start()
            return
        if self.taskdone:
            return
        print("TaskSay at step",self.step)
        if 0 == self.step:
            print("TaskSay press R")
            self.parent.Push(taskpress.TaskPress('R',1.0))
            self.step=1
            return
        if 1 == self.step:
            self.DriveScreenKeyboard()
            return
        if 2 == self.step:
            print("TaskSay press + (confirm)")
            self.parent.Push(taskpress.TaskPress('+',1.0))
            self.step=3
            return
        print("TaskSay done")
        self.taskdone=True

    def Start(self):
        """Cause the task to begin doing whatever."""
        print("TaskSay Start")
        if self.started:
            return # already started
        self.started=True

    def DebugRecursive(self,indent=0):
        self.DebugPrint("TaskSay",indent)

    def NameRecursive(self):
        gbstate.task_stack_names.append(self.name)
        myname="TaskSay"
        return myname

    def GetLetterPosition(self,l):
        y=0
        for row in gbdata.skblc:
            print("row",row)
            if l in row:
                x=row.index(l)
                print("x",x)
                return (x,y)
            y+=1
        # indicate not present
        return (-1,-1)

    def DriveScreenKeyboard(self):
        """The screen keyboard should be visible at this point. We
        need to move the cursor to the current letter we are trying
        to press and press it."""
        if self.substep >= len(self.saythis):
            self.step=2 # We are done with letters. Move to the next step.
            return
        current_letter=self.saythis[self.substep]
        print("current_letter",current_letter)
        (x,y)=self.GetLetterPosition(current_letter)
        if x < 0:
            self.step=2 # not found, bail out to the next step
            return

        # See if the x position is good. Move in x if not.
        if x != self.skb_x:
            # move in x
            if self.skb_x < x:
                # need to increment
                self.parent.Push(taskpress.TaskPress('hat_RIGHT'))
                self.skb_x+=1
                return
            # else need to decrement
            self.parent.Push(taskpress.TaskPress('hat_LEFT'))
            self.skb_x-=1
            return

        # See if the y position is good. Move in y if not.
        if y != self.skb_y:
            # move in y
            if self.skb_y < y:
                # need to increment
                self.parent.Push(taskpress.TaskPress('hat_BOTTOM'))
                self.skb_y+=1
                return
            # else need to decrement
            self.parent.Push(taskpress.TaskPress('hat_TOP'))
            self.skb_y-=1
            return

        # The position is correct. Select that letter.
        self.parent.Push(taskpress.TaskPress('A'))
        self.substep+=1
