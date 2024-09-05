from utility import *
from typing import Any, Protocol
from Item import *
'''
Contains components used for entities and game logic
'''
#ATTACKABLE gives health points and necessitates a tile location
#TALKABLE has dialogue interaction options

class MapEntity(pg.sprite.Sprite):
    def __init__(self, image, rect):
        self.image = image
        self.rect = rect
        self.tileLocation = (0,0)

class attackable(MapEntity):
    def __init__(self, image, rect, maxHP):
        super().__init__(image, rect)
        self.tileLocation = (0,0)
        self.maxHP = maxHP
        self.currHP = maxHP

class Inventory:
    def __init__(self, items=[]) -> None:
        self.items = items

class Character(MapEntity):
    def __init__(self, image, rect):
        super().__init__(image, rect)
        self.MAX_HP = 10
        self.hp = 10

        self.inventory: list[Item]
        self.equipped: Weapon | None = None

    def equip(self, weapon: Weapon):
        self.equipped = weapon



class Weapon:
    def attack(self, attacker, defender, map, mapentities):
        '''
        check the legality of the attack
        apply damage and effects to defender and all the other parties
        '''

class LevelState:
    def __init__(self, player, enemies, npcs, interactibles, tilemap):
