import math
from abc import ABC
from utility import *


class Item(pg.sprite.Sprite):
    '''
    Class for item trakcing. Intended to be used with inventory component.
    '''
    def __init__(self, imgName, type, description="generic item") -> None:
        super().__init__()
        self.image , self.rect = load_image(imgName)
        self.description = description


#if its a weapon it can deal damage and needs to handle that kind of logic

class Weapon(Item):
    '''asbtract class for weapon types so that they can be equipped'''
    def __init__(self, imgName, type, resolveAttack, description="generic weapon") -> None:
        super().__init__(imgName, type, description)
        self.resolveAttack = resolveAttack