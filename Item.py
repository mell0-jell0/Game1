import math
from utility import *

class Popup(pg.sprite.Sprite):
    def __init__(self, buttonText: list[str], operations: list, textColor="black", bgColor="grey", textSize=10):
        #this are references to list we might need to do a deep copy or something
        self.buttonText = buttonText
        self.operations = operations
        self.location = (0,0)
        self.buttons = pg.sprite.Group()
        for text in buttonText:
            self.buttons.add(Button(text, size=textSize))
    
    def draw(self, screen: pg.surface.Surface):
        yDisplacement = 0
        for button in self.buttons:
            button.rect.topleft = (self.location[0], self.location[1] + yDisplacement)
            screen.blit(button.image, button.rect)
            yDisplacement += button.rect.height



class Item(pg.sprite.Sprite):
    def __init__(self, imgName, type, popup: Popup | None = None, description="generic item") -> None:
        super().__init__()
        self.image, self.rect = load_image(imgName)
        self.type = type
        self.description = description
        self.popup = popup
    def onClick(self):
        print("onClick not implemented")


#if its a weapon it can deal damage and needs to handle that kind of logic

class Weapon(Item):
    def __init__(self, imgName, type,  damage, maxRange, description="generic item",) -> None:
        super().__init__(imgName, type, description=description)
        self.damage = damage
        self.maxRange = maxRange
    #melee or ranged
    