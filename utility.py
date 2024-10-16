import os
import math
import enum

import pygame as pg

IMG_SCALE = 3
main_dir = os.path.split(os.path.abspath(__file__))[0]
data_dir = os.path.join(main_dir, "data")

'''
contains basic functionality that multiple modules would need besides pygame
'''
def load_image(name, colorkey=None, scale=IMG_SCALE, path=data_dir):
    '''
    returns image, imgrect for the image that is specified
    '''
    fullname = os.path.join(path, name)
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

def load_images(folderName) -> list[pg.surface.Surface]:
    outputList: list[pg.surface.Surface] = []
    folderPath = os.path.join(data_dir, folderName)
    for item in os.listdir(folderPath):
        print(f"loading image named: {item}")
        if os.path.isfile(os.path.join(folderPath, item)):
            print(f"Appending image {item}")
            outputList.append(load_image(item, path=folderPath)[0])
    return outputList

pg.font.init()

class TextImg(pg.sprite.Sprite):
    '''
    basic class for keeping track of button images and rects and drawing text
    '''
    def __init__(self, text, textColor: str | pg.color.Color="black", bgColor: str | pg.color.Color="grey", size=30, callback = None) -> None:
        self.textWriter = pg.font.Font(pg.font.get_default_font(), size)
        pg.sprite.Sprite.__init__(self)
        self.image = self.textWriter.render(text, 1, textColor, bgColor)
        self.rect = self.image.get_rect()
    
    def updateText(self, newVal, textColor="black", bgColor="grey"):
        '''
        uses static font object to render new text and updates image surface accordingly
        '''
        self.image = self.textWriter.render(newVal, 1, textColor, bgColor)

class Button(pg.sprite.Sprite):
    '''
    Basic button class for handling
    '''
    def __init__(self, image: pg.surface.Surface, callback) -> None:
        pg.sprite.Sprite.__init__(self)
        self.image = image
        self.rect = self.image.get_rect()
        self.callback = callback

class Popup:
    def __init__(self, buttons, anchor) -> None:
        self.buttons: list[Button] = buttons
        self.anchor = anchor

class EffectAnimation(pg.sprite.Sprite):
    def __init__(self, imageFrames: list[pg.surface.Surface], TIME_PER_FRAME=33) -> None:
        super().__init__()
        self.complete = False
        self.imageFrames: list[pg.surface.Surface] = imageFrames
        self.currImageIndex = 0
        self.image: pg.surface.Surface = imageFrames[0]
        self.rect: pg.rect.Rect = pg.rect.Rect(0,0,0,0)
        self.frameProgress = 0
        self.TIME_PER_FRAME = TIME_PER_FRAME #this value in ms. By default is 33, so ~30FPS
        self.terminationCounter = 0
        self.terminationTime = 100
    
    def update(self, deltaTime):
        self.frameProgress += deltaTime
        if self.frameProgress >= self.TIME_PER_FRAME:
            self.currImageIndex = (self.currImageIndex + 1) % len(self.imageFrames)
            self.frameProgress = 0
            self.image = self.imageFrames[self.currImageIndex]
        
        self.terminationCounter += deltaTime
        if self.terminationCounter >= self.terminationTime: self.complete = True

    def draw(self, surf: pg.surface.Surface):
        surf.blit(self.image, self.rect)
    
    def rotated(self, degrees):
        '''
        Returns a deep copy of this animation with all of the frames rotated by provided number of degrees
        '''
        newImages = [pg.transform.rotate(img, degrees) for img in self.imageFrames]
        return EffectAnimation(newImages, self.TIME_PER_FRAME)

def rotateAndPlace(img, degrees: float, distance=0):
    ogWidth = img.get_rect().width
    ogHeight = img.get_rect().height
    rotatedImg = pg.transform.rotate(img, degrees)
    newCenter = rotatedImg.get_rect().center
    # use trig to get the vector difference between the topleft of the image and the "origin" of the image we want to draw
    drawOffset = (newCenter[0]+ogWidth/2*math.cos(math.radians(-90+degrees)),
                       newCenter[1]-ogHeight/2*math.sin(math.radians(-90+degrees)))

    drawOffset: tuple[int, int] =( int(drawOffset[0]+distance*math.cos(math.radians(-90+degrees))), 
                      int(drawOffset[1]-distance*math.sin(math.radians(-90+degrees))) )
    return rotatedImg, drawOffset
