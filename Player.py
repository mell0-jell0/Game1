from utility import *
from Item import *

class Player(pg.sprite.Sprite):
    '''
    handles basic player character functionality such as health, the sprite, and inventory
    '''
    def __init__(self, imgName, health, inventory: pg.sprite.Group) -> None:
        pg.sprite.Sprite.__init__(self)
        self.health = health
        self.weapon: None | Weapon = None
        self.inventory: pg.sprite.Group = inventory
        self.equipped: None | Weapon = None
        self.image, self.rect = load_image(imgName, scale=IMG_SCALE)
        self.tileLocation = (1,7)
        self.actionPoints = 3

    def equip(self, weapon: Weapon | None):
        self.equipped = weapon

    def moveTo(self, tile: tuple[int, int]):
        self.tileLocation = tile

    def draw(self, screen: pg.surface.Surface):
        screen.blit(self.image, self.rect)