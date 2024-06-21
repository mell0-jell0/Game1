from utility import *

class BasicEnemy(pg.sprite.Sprite):
    def __init__(self, imgName):
        pg.sprite.Sprite.__init__(self) #call sprite constructor
        self.image, self.rect = load_image(imgName)

        self.hp = 10