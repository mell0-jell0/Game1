# TODO: Fix or make more elegant the "almost circular" imports between items and entities
# perhaps split each separate component into a different file. this might be cumbersome. think about it.
from typing import Any
from utility import *
from gameMap import *
from action import *

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

        self.defaultInteraction = None
        # the list that contains this entity. For the purposes of spawning or removing entities
        self.entityList = []
    
    def setTileLocation(self, tileLoc:tuple[int, int]):
        self.tileLocation = tileLoc

class LevelState:
    '''
    Object for encapsulating level data
    Contains reference to the tile-map and list of all mapentities
    '''
    def __init__(self, tileMap: GameMap, entities: list[MapEntity], playerCharacter):
        self.tileMap: GameMap = tileMap
        self.entities: list[MapEntity] = entities
        self.playerCharacter = playerCharacter

class Attackable:
    '''
    Component that facilitates the attacking system
    Can be used for characters/NPCs or things such as destructible environment objects
    '''
    def __init__(self, maxHp, on0hp) -> None:
        self.maxHp = maxHp
        self.hp = maxHp
        self.on0hp = on0hp
    
    def takeDmg(self, Dmg):
        '''
        Used to notify the attackable that it has taken damage (i.e. to further trigger death effects when reaching 0hp)'''
        self.hp -= Dmg
        if self.hp <= 0: self.on0hp()

from Item import *

class TurnTaker:
    '''
    Class for entities that respond/take an action when the turn state is stepped over.
    Can be used for characters/NPCs or things such as traps, moving objects etc.
    '''
    def __init__(self, takeTurn, isPlayer: bool) -> None:
        self.takeTurn = takeTurn
        self.isPlayer = isPlayer
        self.currentAction:TurnAction | None = None
        self.turnTakerList = []

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
        self.inventory: list[Item] = []
        self.equipped: Weapon | None = None
        def onDeath():
            print("Player has died")
        self.attackable: Attackable = Attackable(maxHp=10, on0hp=onDeath)
        self.turnTaker = TurnTaker(lambda: print("take turn not implemented for Player"), True)


class BasicEnemy(MapEntity):
    def __init__(self, image, rect):
        pg.sprite.Sprite.__init__(self)
        super().__init__(image, rect)
        self.defaultInteraction = Attackable

        def onDeath():
            print("BasicEnemy Died")
            if self.entityList.count(self) == 1:
                self.entityList.remove(self)
                self.turnTaker.turnTakerList.remove(self)
                # import gc
                # for idx, refr in enumerate(gc.get_referrers(self)):
                #     print(f"Referrer #{idx} is {refr}")
            else:
                print("Entity tried to remove itself from list that does not contain it")

        self.attackable: Attackable = Attackable(maxHp=10, on0hp=onDeath)
        self.interactable: Interactable = Interactable()
        self.turnTaker = TurnTaker(lambda:print("Turn taking not implemented for BasicEnemy"), False)

    def basicTakeTurn(self, levelState: LevelState, animationSet: set[EffectAnimation]):
        '''
        Function called by active game state to have character make decision
        '''
        # attempts to attack the player if in sight. Otherwise wanders around
        # how do characters know if a tile is occupied?
        for entity in levelState.entities:
            if entity == levelState.playerCharacter:
                print("we want to attack character")
                shotgun = testWeapon
                shotgun.resolveAttack(self, entity, levelState, animationSet)
        
        
        # This is where much heavier "AI" logic goes if you want to make something bigger. Data from the game map will be the most helpful with decision making

class Container(MapEntity):
    def __init__(self, image, rect, initialItems: list[Item] = []):
        super().__init__(image, rect)
        self.interactable = Interactable()
        self.items = initialItems
    def interact(self):
        print("container clicked on") 
    
    def getItems(self, item):
        '''Returns specific item and removes it from this container'''
        self.items.remove(item)
        return item

# class AIController:
#     '''
#     Component for handling decision making of AI. Is querie by the game state to get decisions
#     '''
#     def __init__(self) -> None:
#         pass
    
    # def basicTakeTurn(levelState: LevelState):
    #     for entity in levelState.entities:
    #         if entity == levelState.playerCharacter:
    #             print("we want to attack character")
    #     print("Decision making not implemented yet")