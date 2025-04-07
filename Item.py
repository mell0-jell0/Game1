import math
from abc import ABC
from Entities import Attackable, LevelState
from utility import *
from gameMap import *
from action import *


class Item(pg.sprite.Sprite):
    '''
    Class for item tracking. Intended to be used with inventory component.
    '''
    def __init__(self, imgName, type, description="generic item") -> None:
        super().__init__()
        self.image , self.rect = load_image(imgName)
        self.description = description

#if its a weapon it can deal damage and needs to handle that kind of logic

from Entities import MapEntity, LevelState, Attackable, TurnTaker, MultiTurnAction
from States.states import State, drawLevelState

class Useable(Item):
    '''Item type that can be used in the inventory'''
    def __init__(self, imgName, type, description="generic item") -> None:
        super().__init__(imgName, type, description)

    def use(self, game, levelState: LevelState):
        print(f"Use not implemented for item {self}")


class MedkitState(State):
    def __init__(self, game, levelState: LevelState) -> None:
        super().__init__(game)
        self.levelState = levelState
    
    def render(self):
        super().render()
        drawLevelState(self.levelState, self.game.screen)
        tileMap = self.levelState.tileMap
        player = self.levelState.player

        for entity in self.levelState.entities:
            if entity.rect.collidepoint(pg.mouse.get_pos()):
                color = "grey"
                if tileMap.calcDistance(player.tileLocation, entity.tileLocation) == 1:
                    color = "green"
                
                pg.draw.circle(self.game.screen, color, entity.rect.center, tileMap.TILE_WIDTH,2)


class MedKit(Useable):
    def __init__(self, imgName, type):
        super().__init__(imgName, type, "basic med kit")

    def use(self, game, levelState: LevelState):
        game.stateStack.pop()
        game.stateStack.append(MedkitState(game, levelState))
        # assert(hasattr("Attackable", target))
        # assert(isinstance(target, TurnTaker))
        # def effect(): target.attackable.hp += 3
        # print(f"Adding healing turnaction to {target}")
        # target.currentAction = MultiTurnAction(False, 2, effect)

class Weapon(Item):
    '''asbtract class for weapon types so that they can be equipped'''
    def __init__(self, imgName, type, attackAnim, attackCost: int, description="generic weapon") -> None:
        super().__init__(imgName, type, description)
        self.attackAnim: EffectAnimation = attackAnim
        self.attackCost = attackCost
    
    def resolveAttack(self, attacker: MapEntity, target: MapEntity, levelState: LevelState, animationSet: set[EffectAnimation]):
        assert(hasattr(target, "attackable"))
        print("resolveAttack not implemented for this weapon")

    def drawUI(self, attacker: MapEntity, target: MapEntity, levelState: LevelState, screen: pg.surface.Surface):
        print(f"DrawUI not Implemented for {self}")

class Shotgun(Weapon):
    def __init__(self, imgName, type, attackAnim, attackCost, description="generic weapon") -> None:
        super().__init__(imgName, type, attackAnim, attackCost, description)
        self.rangeNumbers = [
            1, 3, 5,
            11, 13, 18 
        ]
    
    def resolveAttack(self, attacker: MapEntity, target: MapEntity, levelState: LevelState, animationSet: set[EffectAnimation]):
        assert(hasattr(target, "attackable"))
        # TODO: finish resolveattack method for shotgun
        # get the angle to rotate the animation
        attackX, attackY = levelState.tileMap.tileToPixel(attacker.tileLocation)
        targetX, targetY= levelState.tileMap.tileToPixel(target.tileLocation)
        dx = targetX - attackX
        dy = attackY - targetY

        if dx == 0: #guard for division by 0
            if dy>0:
                angle = 90
            else:
                angle = 270
        else:
            angle = math.degrees(math.atan(dy / dx))

        if dx < 0:
            angle = 180 + angle #adjust atan answer into Q2 and Q3

        angle = angle - 90 #If textures are read in pointing up, then rotate them clockwise 90 degrees to be at 0.

        print(f"attackerx,y is :{attackX}, {attackY}")
        print(f"defenderx,y is :{targetX}, {targetY}")
        animation = self.attackAnim.rotated(angle)
        _, offset = rotateAndPlace(self.attackAnim.image, angle)
        animation.rect.topleft = levelState.tileMap.tileToPixel(attacker.tileLocation, center=True)
        animation.rect.topleft = animation.rect.topleft[0]-offset[0], animation.rect.topleft[1]-offset[1]
        animationSet.add(animation)
        if levelState.tileMap.checkLineOfSight(attacker.tileLocation, target.tileLocation):
            target.attackable.takeDmg(3)
        else:
            print("There's no line of sight")
        # recenter the animation rect to be where its supposed to be
        # rotate the attack animation and add it to the animation set.
        # resolvee the actual attack effects
        
    def drawUI(self, attacker: MapEntity, target: MapEntity, levelState: LevelState, screen: pg.surface.Surface):
        attackX, attackY = levelState.tileMap.tileToPixel(attacker.tileLocation, center=True)
        targetX, targetY= levelState.tileMap.tileToPixel(target.tileLocation, center=True)
        line: tuple[tuple[int,int],tuple[int, int]] = ((attackX, attackY),(targetX, targetY))
        blocked = False
        for rect in levelState.tileMap.getFullCover():
            if rect.clipline(line) != ():
                blocked = True
        color = "grey" if blocked else "green"
        pg.draw.line(screen, color, *line)

testWeapon = Shotgun("bolty1.png", "weapon", EffectAnimation(load_images("bulletAnim"), 100//15), 1)