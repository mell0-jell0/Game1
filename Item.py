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

from Entities import MapEntity, LevelState, Attackable
class Weapon(Item):
    '''asbtract class for weapon types so that they can be equipped'''
    def __init__(self, imgName, type, attackAnim, description="generic weapon") -> None:
        super().__init__(imgName, type, description)
        self.attackAnim: EffectAnimation = attackAnim
    
    def resolveAttack(self, attacker: MapEntity, target: MapEntity, levelState: LevelState, animationSet: set[EffectAnimation]):
        assert(hasattr(target, "attackable"))
        print("resolveAttack not implemented for this weapon")

class Shotgun(Weapon):
    def __init__(self, imgName, type, attackAnim, description="generic weapon") -> None:
        super().__init__(imgName, type, attackAnim, description)
    
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
        # recenter the animation rect to be where its supposed to be
        # rotate the attack animation and add it to the animation set.
        # resolvee the actual attack effects