# TODO: Fix or make more elegant the "almost circular" imports between items and entities
# perhaps split each separate component into a different file. this might be cumbersome. think about it.
from typing import Any
from utility import *
from gameMap import *

'''
Contains components used for entities and game logic
New components should be added to this file as new systems are needed
New components should be kept minimal in funcitonality
'''

class MapEntity(pg.sprite.Sprite):
    '''
    Basic extenstion of sprite to include map tile location.
    Is basis for all things that exist on the map.
    COMPONENT SYSTEM: 
        attributes which are components should be named as the lower camel-case of the class name of the component
        i.e. a MapEntity will have an attribute attackable of type Attackable.
    '''
    def __init__(self, image, rect):
        self.image = image
        self.rect = rect
        self.tileLocation = (0,0)
    
    def setTileLocation(self, tileLoc:tuple[int, int]):
        self.tileLocation = tileLoc

class LevelState:
    '''
    Object for encapsulating level data
    Contains reference to the tile-map and list of all mapentities
    '''
    def __init__(self, tileMap: GameMap, entities: list[MapEntity], playerCharacter):
        self.tileMap = tileMap
        self.entities = entities
        self.playerCharacter = playerCharacter

class Attackable:
    '''
    Component that facilitates the attacking system
    Can be used for characters/NPCs or things such as destructible environment objects
    '''
    def __init__(self, maxHp) -> None:
        self.maxHp = maxHp
        self.hp = maxHp

from Item import *

class TurnTaker:
    '''
    Class for entities that respond/take an action when the turn state is stepped over.
    Can be used for characters/NPCs or things such as traps, moving objects etc.
    '''
    def __init__(self, takeTurn) -> None:
        self.takeTurn = takeTurn

class Inventory:
    '''
    Component for handling item storage
    '''
    pass

class Interactable:
    pass

class Player(MapEntity):
    def __init__(self, image, rect):
        pg.sprite.Sprite.__init__(self)
        super().__init__(image, rect)
        self.inventory: Inventory = Inventory()
        self.equipped: Weapon | None = None
        self.attackable: Attackable = Attackable(maxHp=10)

class BasicEnemy(MapEntity):
    def __init__(self, image, rect):
        pg.sprite.Sprite.__init__(self)
        super().__init__(image, rect)
        self.attackable: Attackable = Attackable(maxHp=10)
        self.interactable: Interactable = Interactable()
