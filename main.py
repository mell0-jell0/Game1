import os

import pygame as pg
pg.init()
WIN_WIDTH = 1280
WIN_HEIGHT = 720
screen = pg.display.set_mode((WIN_WIDTH, WIN_HEIGHT))

from utility import *
from gameMap import *
from Entities import *
from Item import *
from States.states import *
from States.exploration import *
from game import game

'''
ACKNOWLEDGEMENTS
daFluffyPotato for inspiration and advice about coding
SplatterCat for exploring the niche world of indie games and convincing me that whatever weird shit I make can be enjoyed too
My friend A. for convincing me to get started and keeping me accountable by asking how "the game" was coming along
'''
            
# game = Game(screen)
def fa():
    print("option 1 pressed")
def fb():
    print("option 2 pressed")
fc = lambda : print("lambda option 1")
fd = lambda : print("lambda option 2")

bigMap = GameMap("manifest.csv", "testmap.csv")
weapon1 = Shotgun("bolty1.png", "weapon", EffectAnimation(load_images("bulletAnim"), 100//15), 1)
item1 = Item("bolty1.png", "placeholder type")
item2 = MedKit("medKit1.png", "placeholder type")

eventQ = deque()
#player = Character("16guySmaller.png", 10, "placeholder weapon", pg.sprite.Group([item1, item2]))
player = Player(*load_image("16GuySmaller.png"), eventQ)
player.setTileLocation((1,7))
player.equipped = weapon1
enemy1 = BasicEnemy(*load_image("basicEnemy.png"), eventQ)
enemy1.setTileLocation((9,9))
testContainer = Container(*load_image("cardBoardBox.png"), eventQ, [item1, item2])
cameraOffset = (-400,-80)
bigMap.setOffset(cameraOffset)

lvlState = LevelState(bigMap, [player, enemy1, testContainer], [player, enemy1], player)

expState = Exploration(game, lvlState, player)
expState.eventQ = eventQ

startMenu = StartMenu(game, expState)

print(bigMap.getFullCover())
print(bigMap.getHalfCover())
game.enterState(startMenu)
game.run()