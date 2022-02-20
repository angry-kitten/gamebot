#
# Copyright 2021-2022 by angry-kitten
# Objects for working with recipes.
#

import time, math
import colorsys
import numpy
import cv2
import gbdata
import gbstate
import gbscreen
import gbdisplay
import gbdijkstra
import gblogfile
import gbocr
import threadmanager

class RecipeIngredient:
    """RecipeIngredient Object"""

    def __init__(self,name,invname,howmany):
        self.name=name
        self.invname=invname
        self.howmany=howmany
        return

class Recipe:
    """Recipe Object"""

    def __init__(self,name,invname):
        self.name=name
        self.invname=invname
        self.ingredients=[]
        return

    def add_ingredient(self,name,count):
        e=[name,count]
        self.ingredients.append(e)
        return

    def debug_print(self):
        print(f'name=[{self.name}]\n')
        print(f'invname=[{self.invname}]\n')
        for i in self.ingredients:
            print(f'ing=[{i}]\n')
        return

def load_recipe_database():
    return

def save_recipe_database():
    return

def character_clear_recipes():
    gbstate.character_recipes=[]
    return

def character_recipe_is_known(r):
    for cr in gbstate.character_recipes:
        mscore=gbocr.score_close_string_match(r.name,cr.name)
        print(f'3 mscore={mscore}\n')
        if mscore > gbstate.recipe_name_match:
            return True
    return False

def all_recipe_is_known(r):
    if len(gbstate.all_recipes) < 1:
        load_recipe_database()
    for cr in gbstate.all_recipes:
        mscore=gbocr.score_close_string_match(r.name,cr.name)
        print(f'4 mscore={mscore}\n')
        if mscore > gbstate.recipe_name_match:
            return True
    return False

def add_recipe(r):
    if not character_recipe_is_known(r):
        gbstate.character_recipes.append(r)
    if not all_recipe_is_known(r):
        gbstate.all_recipes.append(r)
        save_recipe_database()
    return
