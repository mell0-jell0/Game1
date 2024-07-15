from utility import *
#all characters have sprite, hp, inventory, and equipped items

class Character(pg.sprite.Sprite):
    '''
    handles basic player character functionality such as health, the sprite, and inventory
    '''
    def __init__(self, imgName, health, weapon) -> None:
        pg.sprite.Sprite.__init__(self)
        self.health = health
        self.weapon = weapon
        self.image, self.rect = load_image(imgName)
        self.tileLocation = (0,0)
        self.actionPoints = 3

    def moveTo(self, tile: tuple[int, int]):
        self.tileLocation = tile

    def draw(self, screen: pg.surface.Surface):
        screen.blit(self.image, self.rect)
