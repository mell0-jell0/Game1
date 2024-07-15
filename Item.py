import math
from utility import *





class Item(pg.sprite.Sprite):
    def __init__(self, imgName, type, popup: Popup | None = None, description="generic item") -> None:
        super().__init__()
        self.image, self.rect = load_image(imgName)
        self.type = type
        self.description = description
        self.popup = popup
    def onClick(self):
        print("onClick not implemented")


#if its a weapon it can deal damage and needs to handle that kind of logic

class Weapon(Item):
    def __init__(self, imgName, type,  damage, maxRange, description="generic item",) -> None:
        super().__init__(imgName, type, description=description)
        self.damage = damage
        self.maxRange = maxRange
    #melee or ranged
    