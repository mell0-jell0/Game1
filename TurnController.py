from utility import *
from Player import *
from BasicEnemy import *

pg.font.init()
class Button(pg.sprite.Sprite):
    BUTTON_WIDTH = 80
    BUTTON_HEIGHT = 30
    textWriter = pg.font.Font(pg.font.get_default_font(), BUTTON_HEIGHT)

    def __init__(self, text) -> None:
        pg.sprite.Sprite.__init__(self)
        self.image = self.textWriter.render(text, 1, "black", "grey")
        self.rect = self.image.get_rect()

class TurnController:
    def __init__(self, screen: pg.Surface, player) -> None:
        self.player = player
        self.isPlayerTurn = True
        #self.UIBox = pg.Surface(screen.get_size())
        self.nextTurnButton = Button("End Turn")
        self.nextTurnButton.rect.bottomleft = screen.get_rect().bottomleft

    def drawUI(self, screen: pg.Surface):
        '''
        draws basic turn ui onto the screen
        '''
        screen.blit(self.nextTurnButton.image, self.nextTurnButton.rect)
    
    def handleClick(self, pos: tuple[float, float]):
        if self.nextTurnButton.rect.collidepoint(pos):
            self.isPlayerTurn = not self.isPlayerTurn
            return True
        else:
            return False
