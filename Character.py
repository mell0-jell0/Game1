from utility import *
from typing import Protocol
#all characters have sprite, hp, inventory, and equipped items
'''sprite is the basic type that all the things inherit from. they get drawn, thats the bare minimum. anything further than that has it's type specified.'''

class Attackable:
    def __init__(self, maxHp) -> None:
        self.MAX_HP = maxHp
        self.health = maxHp

from Item import Item
class InventoryHolder:
    def __init__(self, inventory: pg.sprite.Group) -> None:
        self. inventory = inventory
        self.equipped = None
    
    def equip(self, item):
        if not item in self.inventory:
            print("item is not in inventory, cannot equip")
        else:
            self.equipped = item

class Character(pg.sprite.Sprite, Attackable, InventoryHolder):
    '''
    handles basic player character functionality such as health, the sprite, and inventory
    '''
    def __init__(self, imgName, maxHp, inventory) -> None:
        #sprite setup
        pg.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image(imgName)
        #attackable setup
        Attackable.__init__(self, maxHp)
        InventoryHolder.__init__(self, inventory)

        #character specifics
        self.tileLocation = (0,0)
        self.actionPoints = 3

    def moveTo(self, tile: tuple[int, int]):
        self.tileLocation = tile

    def draw(self, screen: pg.surface.Surface):
        screen.blit(self.image, self.rect)

#class interactable
#class inventoryHolder
#class AI

#player needs to have an inventory that knows about the gun. the gun needs to know about the defense attributes of the player that it attacks