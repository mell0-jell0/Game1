import os

import pygame as pg

from utility import *
from GameMap import *
from Player import *
from TurnController import *

pg.init()
WIN_WIDTH = 1280
WIN_HEIGHT = 720
TILEWIDTH = 20
screen = pg.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
clock = pg.time.Clock()
dt = 0

tile, tilerect = load_image("16grass1.png", scale=3)
TILEWIDTH = tilerect.width
            
bigMap = GameMap("manifest.csv", "testmap.csv")

player = Player("16guySmaller.png", 10, "placeholder")
turnController = TurnController(screen, player)
enemy1 = BasicEnemy("basicEnemy.png")
enemy1.rect.topleft = bigMap.tileToPixel((4,4))

running = True

#MARK: Main game loop
while running:
    screen.fill("black")
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        if event.type == pg.MOUSEBUTTONDOWN and event.button == pg.BUTTON_LEFT:
            if turnController.handleClick(event.pos, bigMap):
                print("handled click")
            else:
                print(bigMap.calcDistance(bigMap.getTile(player.rect.center), bigMap.getTile(event.pos)))
                player.rect.topleft = bigMap.tileToPixel(bigMap.getTile(event.pos))

    #drawMap(tileGrid, tileDict)
    bigMap.draw(screen)
    #bigMap.drawDebug(screen)
    bigMap.drawAdjTile(screen, bigMap.getTile(player.rect.center))
    enemy1.draw(screen)
    player.draw(screen)
    turnController.drawUI(screen)
    #render the game
    clock.tick(60)
    pg.display.flip()

pg.quit()