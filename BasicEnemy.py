from utility import *

class BasicEnemy(pg.sprite.Sprite):
    '''
    handles ai, health, stats, equipment, etc for basic enemies
    '''
    def __init__(self, imgName):
        pg.sprite.Sprite.__init__(self) #call sprite constructor
        self.image, self.rect = load_image(imgName)

        self.hp = 10

    def draw(self, screen: pg.Surface):
        screen.blit(self.image, self.rect)