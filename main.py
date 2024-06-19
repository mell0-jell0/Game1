import pygame as pg
import os

main_dir = os.path.split(os.path.abspath(__file__))[0]
data_dir = os.path.join(main_dir, "data")

pg.init()
WIN_WIDTH = 1280
WIN_HEIGHT = 720
TILEWIDTH = 20
screen = pg.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
clock = pg.time.Clock()
dt = 0
player_pos = pg.Vector2(WIN_WIDTH/2, WIN_HEIGHT/2)
'''
returns image, imgrect for the image that is specified
'''
def load_image(name, colorkey=None, scale=1):
    fullname = os.path.join(data_dir, name)
    image = pg.image.load(fullname)

    size = image.get_size()
    size = (size[0] * scale, size[1] * scale)
    image = pg.transform.scale(image, size)

    image = image.convert_alpha()
    if colorkey is not None:
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey, pg.RLEACCEL)
    return image, image.get_rect()

tile, tilerect = load_image("16grass1.png", scale=3)
TILEWIDTH = tilerect.width

def drawMap(mapGrid, tileDict):
    for rowNum, row in enumerate(mapGrid):
        for itemNum, item in enumerate(row):
            tileDict[item][1].topleft = tileToPixel((itemNum, rowNum))
            screen.blit(tileDict[item][0], tileDict[item][1])

def loadMap(name):
    mapPath = os.path.join(data_dir, name)
    with open(mapPath) as file_in:
        grid = []
        for line in file_in.readlines():
            line = line.strip('\n')
            line = line.split(",")
            grid.append(line)
    return grid

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

def readManifest(name):
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
#imgFile = "vectorTransparent.png"
imgFile = "16BasicguyWider.png"
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