import math
from utility import *


class Item(pg.sprite.Sprite):
    def __init__(self, imgName, type, description="generic item") -> None:
        super().__init__()
        self.image, self.rect = load_image(imgName)
        self.description = description


#if its a weapon it can deal damage and needs to handle that kind of logic

class Weapon(Item):
    '''asbtract class for weapon types so that they can be equipped'''
    def __init__(self, imgName, type, description="generic item") -> None:
        super().__init__(imgName, type, description)

class RangedWeapon(Item):
    def __init__(self, imgName, type, description="generic item") -> None:
        super().__init__(imgName, type, description)

    def rollToDmg(self, roll:int, range:float) -> int:
        print("NOTICE: roll to damage not implemented yet")
        return 1

class MeleeWeapon(Item):
    def __init__(self, imgName, type, description="generic item") -> None:
        super().__init__(imgName, type, description)

    def getDamage(self, roll: int) -> int:
        print("NOTICE: getDamage for melee weapons not imlemented")
        return 1