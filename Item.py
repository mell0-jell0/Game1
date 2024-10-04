import math
from abc import ABC
from Entities import Attackable, LevelState
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
    from Entities import LevelState, Attackable
    '''asbtract class for weapon types so that they can be equipped'''
    def __init__(self, imgName, type, description="generic weapon") -> None:
        super().__init__(imgName, type, description)
    
    def resolveAttack(self, target: Attackable, levelState: LevelState):
        print("resolveAttack not implemented for this weapon")

class shotgun(Weapon):
    def __init__(self, imgName, type, description="generic weapon") -> None:
        super().__init__(imgName, type, description)
    
    def resolveAttack(self, target: Attackable, levelState: LevelState):
        return super().resolveAttack(target, levelState)