import os

import pygame as pg

from utility import *
from GameMap import *
from Player import *
from Character import Character
from Item import *
#from TurnController import *
from States.States import *
'''
ACKNOWLEDGEMENTS
daFluffyPotato for inspiration and advice about coding
SplatterCat for exploring the niche world of indie games and convincing me that whatever weird shit I make can be enjoyed too
My friend A. for convincing me to get started and keeping me accountable by asking how "the game" was coming along
'''
            


class Game:
    def __init__(self) -> None:
        self.stateStack: list[State] = []
        pg.init()
        self.WIN_WIDTH = 1280
        self.WIN_HEIGHT = 720
        self.screen = pg.display.set_mode((self.WIN_WIDTH, self.WIN_HEIGHT))
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


game = Game()
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
player = Player("16guySmaller.png", 10, pg.sprite.Group([item1, item2]))
player.equip(weapon1)
enemy1 = BasicEnemy("basicEnemy.png", (7,8))

cameraOffset = (-400,-80)
bigMap.setOffset(cameraOffset)


#turnState = TurnControl(game, bigMap, player, [enemy1], [], [])
expState = Exploration(game, bigMap, player, [enemy1], [], [])
invState = InventoryMenu(game, bigMap, player, [enemy1], [], [])
grenadeState = Exploration.GrenadeTargeting(game, bigMap, player, [enemy1], [], [enemy1, player])
#transitionState = ExplorationTurnTransition(game, bigMap, player, [enemy1], [], [enemy1, player])

print(bigMap.getFullCover())
print(bigMap.getHalfCover())
game.enterState(grenadeState)
game.run()