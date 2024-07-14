from pygame.sprite import _Group
from utility import *

class Item(pg.sprite.Sprite):
    
    def __init__(self, imgName, type) -> None:
        super().__init__()
        self.image, self.rect = load_image(imgName)
        self.type = type