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

def drawMap(grid, tileDict):
    '''
    takes mapGrid and tileDict to draw map to screen
    '''
    for rowNum, row in enumerate(grid):
        for itemNum, item in enumerate(row):
            tileDict[item][1].topleft = tileToPixel((itemNum, rowNum))
            screen.blit(tileDict[item][0], tileDict[item][1])

def gedAdjList(grid):
    '''
    takes in the grid of tiles and produces adjacency grid for that map
    '''
    adjList = []
    for i in range(len(grid)): #iterate over height
        for j in range(len(grid[i])): #iterate over width
            if grid[i][j] != 0:
                return
        
def getTile(pos):
    '''
    takes an xy pixel position and returns an xy of the tile that location resides in
    '''
    tileRow = pos[1] // TILEWIDTH
    tileCol = pos[0] // TILEWIDTH
    return (tileRow, tileCol)

def tileToPixel(tileCoord):
    '''
    takes a tile x,y and spits out a pixel x,y for the top left of that tile
    '''
    pixelx = tileCoord[1] * TILEWIDTH
    pixely = tileCoord[0] * TILEWIDTH
    return (pixelx, pixely)

            
bigMap = GameMap("manifest.csv", "testmap.csv")

player = Player("16guySmaller.png", 10, "placeholder")
turnController = TurnController(screen, player)

running = True

#MARK: Main game loop
while running:
    screen.fill("black")
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        if event.type == pg.MOUSEBUTTONDOWN and event.button == pg.BUTTON_LEFT:
            if turnController.handleClick(event.pos):
                print("handled click")
            else:
                print(bigMap.calcDistance(getTile(player.rect.center), getTile(event.pos)))
                player.rect.topleft = tileToPixel(getTile(event.pos))

    #drawMap(tileGrid, tileDict)
    bigMap.draw(screen)
    #bigMap.drawDebug(screen)
    bigMap.drawAdjTile(screen, getTile(player.rect.center))
    player.draw(screen)
    turnController.drawUI(screen)
    #render the game
    clock.tick(60)
    pg.display.flip()

pg.quit()