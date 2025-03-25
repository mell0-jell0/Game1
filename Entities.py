# TODO: Fix or make more elegant the "almost circular" imports between items and entities
# perhaps split each separate component into a different file. this might be cumbersome. think about it.
# TODO: Pick multiple inheritance or composition. MultiInheritance makes more sense for Interactables because you need lots of methods to call for them.
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
    def __init__(self, image, rect, eventQ: deque):
        pg.sprite.Sprite.__init__(self)
        self.image = image
        self.rect = rect
        self.tileLocation = (0,0)

        self.defaultInteraction = None
        # the list that contains this entity. For the purposes of spawning or removing entities 

    def setTileLocation(self, tileLoc:tuple[int, int]):
        self.tileLocation = tileLoc
    
    def getInfo(self):
        print(f"getInfo unimplemented for {self}")

class LevelState:
    '''
    Object for encapsulating level data
    Contains reference to the tile-map and list of all mapentities
    '''
    def __init__(self, tileMap: GameMap, entities: list[MapEntity], turnTakers: list[MapEntity], playerCharacter):
        self.tileMap: GameMap = tileMap
        self.entities: list[MapEntity] = entities
        self.turnTakers: list[MapEntity] = turnTakers
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
    def __init__(self, takeTurn) -> None:
        self.takeTurn = takeTurn
        self.currentAction:TurnAction | None = None

class Inventory:
    '''
    Component for handling item storage
    '''
    pass

class Interactable:
    def canInteract(self, levelState: LevelState, interactor: MapEntity):
        print(f"canInteract not implemented for {self}")
    
    def getInteractInfo(self, levelState: LevelState, interactor: MapEntity):
        text = f"getInteractInfo not implemented for {self}"
        print(text)
        return text

    

class Player(MapEntity, TurnTaker):
    def __init__(self, image, rect, eventQ):
        super().__init__(image, rect, eventQ)
        self.inventory: list[Item] = []
        self.equipped: Weapon | None = None
        def onDeath():
            print("Player has died")
        self.attackable: Attackable = Attackable(maxHp=10, on0hp=onDeath)
        TurnTaker.__init__(self, lambda: print("Take turn not implemented for player"))

class BasicEnemy(MapEntity, Interactable):
    def __init__(self, image, rect, eventQ):
        MapEntity.__init__(self, image, rect, eventQ)
        super().__init__(image, rect, eventQ)
        self.defaultInteraction = Attackable

        def onDeath(levelState: LevelState):
            print("BasicEnemy Died")
            if levelState.entities.count(self) == 1:
                levelState.entities.remove(self)
                levelState.turnTakers.remove(self)
                loot = Container(*load_image("cardBoardBox.png"), eventQ, [])
                loot.tileLocation = self.tileLocation
                levelState.entities.append(loot)
                # import gc
                # for idx, refr in enumerate(gc.get_referrers(self)):
                #     print(f"Referrer #{idx} is {refr}")
            else:
                print("Entity tried to remove itself from list that does not contain it")

        self.attackable: Attackable = Attackable(maxHp=10, on0hp=lambda: eventQ.append(onDeath))
        self.turnTaker = TurnTaker(lambda:print("Turn taking not implemented for BasicEnemy"))

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

class Container(MapEntity, Interactable):
    def __init__(self, image, rect, eventQ, initialItems: list[Item] = []):
        MapEntity.__init__(self, image, rect, eventQ)
        self.items = initialItems
    def interact(self):
        print("container clicked on") 
    
    def canInteract(self, levelState: LevelState, interactor: MapEntity):
        if levelState.tileMap.calcDistance(self.tileLocation, interactor.tileLocation) == 1:
            return True
        else:
            return False
    
    def getInteractInfo(self, levelState: LevelState, interactor: MapEntity):
        if levelState.tileMap.calcDistance(self.tileLocation, interactor.tileLocation) == 1:
            text = f"You are close enough to interact with object ({self})"
        else:
            text = f"Move close to interact with this object ({self})"
        print(text)
        return text
    
    def displayInfo(self):
        print("Interact with this contianer to obtain items")
    
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