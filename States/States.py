import math

from pygame.sprite import AbstractGroup
from utility import *
from Entities import *
from gameMap import *


class State:
    '''Abstract class for game states'''
    def __init__(self) -> None:
        pass
    
    def process(self, events):
        pass

    def update(self):
        pass

    def render(self):
        pass


class MultiFrameAction:
    def __init__(self) -> None:
        self.completed = False
    
    def update(self, deltaTime: int):
        print("update method for multiframeAction not implemented")

class StartMenu(State):
    def __init__(self, game) -> None:
        self.game = game
        self.playButton = TextImg("Play")
        self.playButton.rect.center = game.screen.get_rect().center

    def process(self, events):
        super().process(events)
        for event in events:
            if event.type == pg.MOUSEBUTTONDOWN and event.button == pg.BUTTON_LEFT:
                if self.playButton.rect.collidepoint(event.pos):
                    print("go to next state")

    def render(self):
        self.game.screen.fill("black")
        self.game.screen.blit(self.playButton.image, self.playButton.rect)