#
# Copyright 2021-2022 by angry-kitten
# Gather the recipe inventory.
#

import re
import gbdata
import gbstate
import gbscreen
import gbdisplay
import gbocr
import gbrecipe
import taskobject
import taskpress
import taskdetect
import taskocr
import taskopenphone

class TaskRecipeInv(taskobject.Task):
    """TaskRecipeInv Object"""

    def __init__(self):
        super().__init__()
        self.name="TaskRecipeInv"
        print("new",self.name,"object")
        self.step=0
        # This isn't the column number. We need to make sure
        # we check all five columns per row.
        self.column_count=0
        self.going_up=True
        self.skipping_just_gathered=False
        self.r_previous=None

    def Poll(self):
        """check if any action can be taken"""
        print(self.name,"Poll")
        if not self.started:
            self.Start()
            return
        if self.taskdone:
            return

        if self.step == 0:
            if not gbscreen.is_diy_screen():
                print('diy screen is not open')
                self.step=90
                return
            print('diy screen is open')
            self.step=1
            return

        if self.step == 1:
            # make sure we are on 'Everything'
            self.parent.Push(taskocr.TaskOCR())
            self.step=2
            return

        if self.step == 2:
            if gbocr.ocr_results_contain('Everything'):
                self.column_count=0
                self.going_up=True
                gbrecipe.character_clear_recipes()
                self.step=3
                return
            self.parent.Push(taskobject.TaskTimed(1.0))
            self.parent.Push(taskpress.TaskPress('L'))
            self.step=1
            return

        if self.step == 3:
            if self.column_count >= 5:
                self.parent.Push(taskocr.TaskOCR())
                self.parent.Push(taskobject.TaskTimed(1.0)) # wait for animation
                if self.going_up:
                    self.parent.Push(taskpress.TaskPress('hat_TOP'))
                else:
                    self.parent.Push(taskpress.TaskPress('hat_BOTTOM'))
                #self.parent.Push(taskobject.TaskTimed(1.0)) # wait for animation
                #self.parent.Push(taskpress.TaskPress('hat_RIGHT'))
                self.column_count=0
                self.step=3
                return
            r=self.gather_recipe()
            if r is None:
                self.step=4
                return
            r.debug_print()
            if gbrecipe.character_recipe_is_known(r):
                if self.going_up:
                    # change direction and skip
                    self.going_up=False
                    self.skipping_just_gathered=True
                    self.parent.Push(taskocr.TaskOCR())
                elif self.skipping_just_gathered:
                    if self.r_previous is not None:
                        mscore=gbocr.score_close_string_match(r.name,self.r_previous.name)
                        print(f'2 mscore={mscore}\n')
                        if mscore > gbstate.recipe_name_match:
                            # Same recipe as before. We started gathering on the last row
                            # of recipes.
                            # done gathering recipes
                            self.step=4
                            return
                    self.parent.Push(taskocr.TaskOCR())
                else:
                    # done gathering recipes
                    self.step=4
                    return
                self.parent.Push(taskobject.TaskTimed(1.0)) # wait for animation
                self.parent.Push(taskpress.TaskPress('hat_BOTTOM'))
                self.step=3
                return
            self.skipping_just_gathered=False
            gbrecipe.add_recipe(r)
            self.r_previous=r
            self.column_count+=1
            if self.column_count < 5:
                self.parent.Push(taskocr.TaskOCR())
            self.parent.Push(taskobject.TaskTimed(1.0)) # wait for animation
            self.parent.Push(taskpress.TaskPress('hat_RIGHT'))
            self.step=3
            return

        if self.step == 4:
            self.step=90
            return

        if self.step == 90:
            # close DIY
            self.parent.Push(taskobject.TaskTimed(1.0)) # wait for animation
            self.parent.Push(taskpress.TaskPress('B'))
            self.step=91
            return

        if self.step == 91:
            # close phone
            self.parent.Push(taskobject.TaskTimed(1.0)) # wait for animation
            self.parent.Push(taskpress.TaskPress('B'))
            self.step=99
            return

        print(self.name,"done")
        self.taskdone=True

    def Start(self):
        """Cause the task to begin doing whatever."""
        print(self.name,"Start")
        if self.started:
            return # already started
        self.started=True
        self.step=0

        # open recipes
        self.parent.Push(taskopenphone.TaskOpenPhone("DIY"))
        return

    def DebugRecursive(self,indent=0):
        self.DebugPrint(self.name,indent)

    def NameRecursive(self):
        myname=self.name
        gbstate.task_stack_names.append(myname)
        return myname

    def gather_recipe(self):
        r=None
        ta=gbocr.digest_recipe_screen_text()
        if ta is None:
            return r
        j=gbocr.nearest_entry_index(ta,gbdata.ocr_recipe_title_y)
        if j is None:
            return r
        title=ta[j][1]
        print(f'title=[{title}]\n')
        title=self.process_title(title)
        print(f'title=[{title}]\n')

        # sort text fragments into ingredient lines
        ilines=[]
        for sy in gbdata.ocr_recipe_ingredients_y:
            aline=[]
            for f in ta:
                dy=abs(sy-f[0])
                if dy < gbdata.ocr_recipe_ingredients_y_within:
                    aline.append(f)
            ilines.append(aline)

        for aline in ilines:
            print('ingredient line')
            for f in aline:
                print('fragment',f[1])

        r=gbrecipe.Recipe(title,'')

        for aline in ilines:
            print('ingredient line')
            ingredient_name=None
            ingredient_available=0
            ingredient_count=1
            for f in aline:
                print('fragment',f[1])
                csy=f[0]
                text=f[1]
                box=f[2]
                ul=box[0]
                lr=box[2]
                x1=ul[0]
                x2=lr[0]
                if x1 < gbdata.ocr_recipe_avail_x and x2 < gbdata.ocr_recipe_avail_x:
                    # This is an ingredient name with no numbers.
                    ingredient_name=self.process_name(text)
                elif x1 >= gbdata.ocr_recipe_avail_x and x2 < gbdata.ocr_recipe_slash_x:
                    # This is the number available in inventory.
                    ingredient_available=int(text)
                elif x1 >= gbdata.ocr_recipe_slash_x and x2 < gbdata.ocr_recipe_count_x:
                    # This is the slash. It may appear as '/' or '1'.
                    # Throw it away.
                    pass
                elif x1 >= gbdata.ocr_recipe_count_x:
                    # This is a count of ingredient item needed.
                    ingredient_count=int(text)
                elif x1 >= gbdata.ocr_recipe_slash_x and x2 > gbdata.ocr_recipe_count_x:
                    # This is a slash with count.
                    c=self.process_slash_count(text)
                    ingredient_count=c
                elif x1 >= gbdata.ocr_recipe_avail_x and x2 > gbdata.ocr_recipe_count_x:
                    # This is a available with count.
                    c=self.process_available_count(text)
                    ingredient_count=c
                elif x1 < gbdata.ocr_recipe_avail_x and x2 > gbdata.ocr_recipe_count_x:
                    # This is an ingredient name with available and count.
                    (n,a,c)=self.process_name_available_count(text)
                    ingredient_name=n
                    ingredient_available=a
                    ingredient_count=c
                else:
                    print("unknown")
            print("name",ingredient_name)
            print("available",ingredient_available)
            print("count",ingredient_count)
            if ingredient_name is not None:
                r.add_ingredient(ingredient_name,ingredient_count)

        return r

    def process_name(self,s):
        s2=re.sub(r'_+',r' ',s)
        s2=re.sub(r'\s+',r' ',s2)
        s2=re.sub(r'^\s+',r'',s2)
        s2=re.sub(r'\s+$',r'',s2)
        n=re.sub(r'[-\s\d/]*$',r'',s2)
        return n

    def process_slash_count(self,s):
        s2=re.sub(r'\s+',r' ',s)
        s2=re.sub(r'^\s+',r'',s2)
        s2=re.sub(r'\s+$',r'',s2)
        parts=re.split(r'\s+',s2)
        l=len(parts)
        if l < 1:
            c=1
            return c
        if l == 1:
            # There may be a leading '/', '[',  or '1'.
            s3=re.sub(r'^[/1\[]',r'',s2)
            if len(s3) == 0:
                c=1
                return c
            c=int(s3)
            if c < 1:
                c=1
            return c
        s3=parts[l-1]
        c=int(s3)
        if c < 1:
            c=1
        return c

    def process_available_count(self,s):
        s2=re.sub(r'\s+',r' ',s)
        s2=re.sub(r'^\s+',r'',s2)
        s2=re.sub(r'\s+$',r'',s2)
        parts=re.split(r'\s+',s2)
        l=len(parts)
        if l < 1:
            c=1
            return c
        if l == 1:
            # There may be a leading number with '/', '[', or '1'.
            s3=re.sub(r'^[^/\[]*[/1\[]',r'',s2)
            if len(s3) == 0:
                c=1
                return c
            c=int(s3)
            if c < 1:
                c=1
            return c
        s3=parts[l-1]
        # There may be a leading number with '/' or '1'.
        s3=re.sub(r'^[^/\[]*[/1\[]',r'',s3)
        if len(s3) == 0:
            c=1
            return c
        c=int(s3)
        if c < 1:
            c=1
        return c

    def process_name_available_count(self,s):
        s2=re.sub(r'_+',r' ',s)
        s2=re.sub(r'\s+',r' ',s2)
        s2=re.sub(r'^\s+',r'',s2)
        s2=re.sub(r'\s+$',r'',s2)
        n=re.sub(r'[-\s\d/\[]*$',r'',s2)
        a=0
        parts=re.split(r'\s+',s2)
        l=len(parts)
        if l < 1:
            c=1
            return (n,a,c)
        if l == 1:
            # There may be a leading number with '/', '[', or '1'.
            s3=re.sub(r'^[^/\[]*[/1\[]',r'',s2)
            if len(s3) == 0:
                c=1
                return (n,a,c)
            c=int(s3)
            if c < 1:
                c=1
            return (n,a,c)
        if l == 2:
            # There may be a leading number with '/', '[', or '1'.
            s3=re.sub(r'^[^/\[]*[/1\[]',r'',parts[l-1])
            if len(s3) == 0:
                c=1
                return (n,a,c)
            c=int(s3)
            if c < 1:
                c=1
            return (n,a,c)
        if parts[l-2] == '1' or parts[l-2] == '/':
            c=int(parts[l-1])
            if c < 1:
                c=1
            return (n,a,c)
        # There may be a leading number with '/', '[', or '1'.
        s3=re.sub(r'^[^/\[]*[/1\[]',r'',parts[l-1])
        if len(s3) == 0:
            c=1
            return (n,a,c)
        c=int(s3)
        if c < 1:
            c=1
        return (n,a,c)

    def process_string(self,s):
        s2=re.sub(r'_',r' ',s)
        s2=re.sub(r'\s+',r' ',s2)
        s2=re.sub(r'^\s+',r'',s2)
        s2=re.sub(r'\s+$',r'',s2)
        return s2

    def process_title(self,t):
        t2=self.process_string(t)
        return t2
