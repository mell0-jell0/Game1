import os
import enum

import pygame as pg

IMG_SCALE = 3
main_dir = os.path.split(os.path.abspath(__file__))[0]
data_dir = os.path.join(main_dir, "data")

'''
contains basic functionality that multiple modules would need besides pygame
'''
def load_image(name, colorkey=None, scale=IMG_SCALE):
    '''
    returns image, imgrect for the image that is specified
    '''
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
        self.callback = callback
    
    def updateText(self, newVal, textColor="black", bgColor="grey"):
        '''
        uses static font object to render new text and updates image surface accordingly
        '''
        self.image = self.textWriter.render(newVal, 1, textColor, bgColor)

class Popup(pg.sprite.Sprite):
    '''
    small popup menu with buttons and actions associated with each button
    active state must implement popup handling
    '''
    def __init__(self, buttonText: list[str], operations: list, textColor="black", bgColor="grey", textSize=10):
        #this are references to list we might need to do a deep copy or something
        assert(len(operations) == len(buttonText))
        self.buttonText = buttonText
        self.location = (0,0)
        self.buttons = pg.sprite.Group()
        for idx, text in enumerate(buttonText):
            #give buttons the matching callback in the operations list
            self.buttons.add(TextImg(text, size=textSize, callback=operations[idx]))
    
    def draw(self, screen: pg.surface.Surface):
        yDisplacement = 0
        for button in self.buttons:
            button.rect.topleft = (self.location[0], self.location[1] + yDisplacement)
            screen.blit(button.image, button.rect)
            yDisplacement += button.rect.height

    def pointCollide(self, pos):
        for button in self.buttons:
            if button.rect.collidepoint(pos):
                return True

    def handleClick(self, pos):
        clicked = False
        for button in self.buttons:
            if button.rect.collidepoint(pos):
                button.callback()