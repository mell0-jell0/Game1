from utility import *

class Player(pg.sprite.Sprite):
    '''
    handles basic player character functionality such as health, the sprite, and inventory
    '''
    def __init__(self, imgName, health, weapon) -> None:
        pg.sprite.Sprite.__init__(self)
        self.health = health
        self.weapon = weapon
        self.image, self.rect = load_image(imgName, scale=IMG_SCALE)

    def draw(self, screen: pg.Surface):
        '''
        takes in screen and draws player to the location
        '''
        screen.blit(self.image, self.rect)