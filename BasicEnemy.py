from utility import *

class BasicEnemy(pg.sprite.Sprite):
    '''
    handles ai, health, stats, equipment, etc for basic enemies

    maybe i should make another class entity which this one inherits from. entity type could be a member of entity.
    '''
    def __init__(self, imgName):
        pg.sprite.Sprite.__init__(self) #call sprite constructor
        self.image, self.rect = load_image(imgName)
        self.crossHair = load_image("crossHair1.png")
        self.tileLocation = (4,4)
        self.eType = entityType.ENEMY

        self.hp = 10

    def takeTurn(self, map, entities):
        #do basic ai action
        pass

    def onClick(self):
        pass
    # def draw(self, screen: pg.Surface, offset=(0,0)):
    #     screen.blit(self.image, self.rect)

    def draw(self, screen: pg.surface.Surface):
        screen.blit(self.image, self.rect)