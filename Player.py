from utility import *
from Item import *

class Player(pg.sprite.Sprite):
    '''
    handles basic player character functionality such as health, the sprite, and inventory
    '''
    def __init__(self, imgName, health, weapon, inventory: pg.sprite.Group) -> None:
        pg.sprite.Sprite.__init__(self)
        self.health = health
        self.weapon = weapon
        self.inventory: pg.sprite.Group = inventory
        self.equipped: None | Weapon = None
        self.image, self.rect = load_image(imgName, scale=IMG_SCALE)
        self.tileLocation = (0,0)
        self.actionPoints = 3

    def equip(self, weapon: Weapon | None):
        self.equipped = weapon
    
    def attack(self, target):
        if self.equipped == None:
            print("No equipped weapon")
        else:
            target.health -= self.equipped.damage
            print(f"Target was dealt: {self.equipped.damage} damage")

    def moveTo(self, tile: tuple[int, int]):
        self.tileLocation = tile
    # def draw(self, screen: pg.Surface, pos):
    #     '''
    #     takes in screen and draws player to the location
    #     '''
    #     screen.blit(self.image, pos)
    def draw(self, screen: pg.surface.Surface):
        screen.blit(self.image, self.rect)