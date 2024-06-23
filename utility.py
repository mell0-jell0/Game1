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


class entityType(enum.Enum):
    ENEMY = enum.auto()
    OTHER = enum.auto()
    #add interactable entities down here
