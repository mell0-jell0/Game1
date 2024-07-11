import os

import pygame as pg

from utility import *
from GameMap import *
from Player import *
#from TurnController import *
from States import *
'''
ACKNOWLEDGEMENTS
daFluffyPotato for inspiration and advice about coding
SplatterCat for exploring the niche world of indie games and convincing me that whatever weird shit I make can be enjoyed too
My friend A. for convincing me to get started and keeping me accountable by asking how "the game" was coming along
'''
            


class Game:
    def __init__(self) -> None:
        self.lastState: State = State()
        self.currentState: State = State()
        pg.init()
        self.WIN_WIDTH = 1280
        self.WIN_HEIGHT = 720
        self.screen = pg.display.set_mode((self.WIN_WIDTH, self.WIN_HEIGHT))
        self.clock = pg.time.Clock()
        self.dt = 0

    def changeState(self, nextState: State):
        self.lastState = self.currentState
        self.currentState = nextState

    def run(self):
        #MARK: Main game loop
        running = True
        while running:
            if pg.event.get(pg.QUIT):
                running = False
            self.currentState.process(pg.event.get())
            self.currentState.update()
            self.currentState.render()

            self.clock.tick(60)
            pg.display.flip()

        pg.quit()


game = Game()

bigMap = GameMap("manifest.csv", "testmap.csv")
player = Player("16guySmaller.png", 10, "placeholder")
enemy1 = BasicEnemy("basicEnemy.png")

cameraOffset = (-400,-80)
bigMap.setOffset(cameraOffset)


turnState = TurnControl(game, bigMap, player, [enemy1], [enemy1])

game.changeState(turnState)
game.run()