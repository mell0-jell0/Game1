import os

import pygame as pg

from utility import *
from GameMap import *
from Player import *
from TurnController import *
'''
ACKNOWLEDGEMENTS
daFluffyPotato for inspiration and advice about coding
SplatterCat for exploring the niche world of indie games and convincing me that whatever weird shit I make can be enjoyed too
My friend A. for convincing me to get started and keeping me accountable by asking how "the game" was coming along
'''
pg.init()
WIN_WIDTH = 1280
WIN_HEIGHT = 720
screen = pg.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
clock = pg.time.Clock()
dt = 0

            
bigMap = GameMap("manifest.csv", "testmap.csv")

player = Player("16guySmaller.png", 10, "placeholder")

enemy1 = BasicEnemy("basicEnemy.png")
enemy1.rect.topleft = bigMap.tileToPixel((4,4))
turnController = TurnController(screen, bigMap, player, [enemy1], [enemy1])

cameraOffset = (-400,-80)
bigMap.setOffset(cameraOffset)
running = True

playButton = Button("Play game")
playButton.rect.center = screen.get_rect().center


#MARK: Main game loop
while running:
    screen.fill("black")
    # figure out where to put the player turn in here
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False

        if event.type == pg.MOUSEBUTTONDOWN and event.button == pg.BUTTON_LEFT:
            if playButton.rect.collidepoint(event.pos):
                print("play button pressed")
                turnController.run(screen, clock)

    screen.blit(playButton.image, playButton.rect)
    # #drawMap(tileGrid, tileDict)
    # bigMap.draw(screen)
    # #bigMap.drawDebug(screen)
    # bigMap.drawAdjTile(screen, player.tileLocation)
    # screen.blit(enemy1.image, bigMap.tileToPixel(enemy1.tileLocation))
    # screen.blit(player.image, bigMap.tileToPixel(player.tileLocation))
    # turnController.drawUI(screen)
    # #render the game
    clock.tick(60)
    pg.display.flip()

pg.quit()