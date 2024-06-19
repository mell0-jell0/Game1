import os

import pygame as pg

from utility import *


pg.init()
WIN_WIDTH = 1280
WIN_HEIGHT = 720
TILEWIDTH = 20
screen = pg.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
clock = pg.time.Clock()
dt = 0
player_pos = pg.Vector2(WIN_WIDTH/2, WIN_HEIGHT/2)



tile, tilerect = load_image("16grass1.png", scale=3)
TILEWIDTH = tilerect.width

def drawMap(mapGrid, tileDict):
    '''
    takes mapGrid and tileDict to draw map to screen
    '''
    for rowNum, row in enumerate(mapGrid):
        for itemNum, item in enumerate(row):
            tileDict[item][1].topleft = tileToPixel((itemNum, rowNum))
            screen.blit(tileDict[item][0], tileDict[item][1])

def loadMap(name):
    '''
    takes file name and loads csv map into grid
    '''
    mapPath = os.path.join(data_dir, name)
    with open(mapPath) as file_in:
        grid = []
        for line in file_in.readlines():
            line = line.strip('\n')
            line = line.split(",")
            grid.append(line)
    return grid

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
    tilex = pos[0] // TILEWIDTH
    tiley = pos[1] // TILEWIDTH
    return (tilex, tiley)

def tileToPixel(tileCoord):
    '''
    takes a tile x,y and spits out a pixel x,y for the top left of that tile
    '''
    pixelx = tileCoord[0] * TILEWIDTH
    pixely = tileCoord[1] * TILEWIDTH
    return (pixelx, pixely)

def readManifest(name) -> dict[str, tuple[pg.Surface, pg.Rect]]:
    '''
    reads in list of number that correspond to different tiles
    creates one image for each tile type
    maps '''
    manifestPath = os.path.join(data_dir, name)
    with open(manifestPath) as fileIn:
        lines = fileIn.readlines()
        tileMap = {}
        for line in lines:
            line = line.strip('\n')
            line = line.split(',')
            #load image and imagerect
            newImgTuple = load_image(line[1], scale=3)
            #store image and imagerect in the map at the character specified
            tileMap[line[0]] = newImgTuple
        return tileMap
            
tileDict = readManifest("manifest.csv")
tileGrid = loadMap("testmap.csv")
print(tileGrid)
#imgFile = "vectorTransparent.png"
imgFile = "16guySmaller.png"
image, imgrect = load_image(imgFile, scale = 3)
running = True

#MARK: Main game loop
while running:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        if event.type == pg.MOUSEBUTTONDOWN:
            if event.button == pg.BUTTON_LEFT:
                imgrect.topleft = tileToPixel(getTile(event.pos))
    screen.fill("black")
    drawMap(tileGrid, tileDict)
    screen.blit(image, imgrect)
    #render the game
    clock.tick(60)
    pg.display.flip()

pg.quit()