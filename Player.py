from utility import *

class Player:
    def __init__(self, health, weapon, imgName) -> None:
        self.health = health
        self.weapon = weapon
        self.img, self.rect = load_image(imgName, scale=IMG_SCALE)

    def draw(self, screen: pg.Surface):
        '''
        takes in screen and draws player to the location
        '''
        screen.blit(self.img, self.rect)