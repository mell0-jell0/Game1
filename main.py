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
from States.States import *
from States.exploration import *

'''
ACKNOWLEDGEMENTS
daFluffyPotato for inspiration and advice about coding
SplatterCat for exploring the niche world of indie games and convincing me that whatever weird shit I make can be enjoyed too
My friend A. for convincing me to get started and keeping me accountable by asking how "the game" was coming along
'''
            


class Game:
    def __init__(self, screen) -> None:
        self.stateStack: list[State] = []
        self.WIN_WIDTH = 1280
        self.WIN_HEIGHT = 720
        self.screen = screen
        self.clock = pg.time.Clock()
        self.dt = 0

    def enterState(self, nextState: State):
        self.stateStack.append(nextState)

    def run(self):
        #MARK: Main game loop
        running = True
        while running:
            if pg.event.get(pg.QUIT):
                running = False
            self.stateStack[-1].process(pg.event.get())
            self.stateStack[-1].update()
            self.stateStack[-1].render()

            self.clock.tick(60)
            pg.display.flip()

        pg.quit()


game = Game(screen)
def fa():
    print("option 1 pressed")
def fb():
    print("option 2 pressed")
fc = lambda : print("lambda option 1")
fd = lambda : print("lambda option 2")

bigMap = GameMap("manifest.csv", "testmap.csv")
weapon1 = Weapon("bolty1.png", "weapon")
item1 = Item("bolty1.png", "placeholder type")
item2 = Item("medKit1.png", "placeholder type")

#player = Character("16guySmaller.png", 10, "placeholder weapon", pg.sprite.Group([item1, item2]))
player = Player(*load_image("16GuySmaller.png"))
player.setTileLocation((1,7))
enemy1 = BasicEnemy(*load_image("basicEnemy.png"))
enemy1.setTileLocation((9,9))
cameraOffset = (-400,-80)
bigMap.setOffset(cameraOffset)

lvlState = LevelState(bigMap, [player, enemy1], player)

#turnState = TurnControl(game, bigMap, player, [enemy1], [], [])
expState = Exploration(game, lvlState, player)
# invState = InventoryMenu(game, bigMap, player, [enemy1], [], [])
# grenadeState = Exploration.GrenadeTargeting(game, bigMap, player, [enemy1], [], [enemy1, player])
#transitionState = ExplorationTurnTransition(game, bigMap, player, [enemy1], [], [enemy1, player])

print(bigMap.getFullCover())
print(bigMap.getHalfCover())
game.enterState(expState)
game.run()