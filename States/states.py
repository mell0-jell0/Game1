import math

from pygame.sprite import AbstractGroup
from utility import *
from Entities import *
from gameMap import *


class State:
    '''Abstract class for game states'''
    def __init__(self, game) -> None:
        self.game = game
        pass
    
    def process(self, events):
        pass

    def update(self):
        pass

    def render(self):
        pass

def drawLevelState(levelState: LevelState, screen: pg.surface.Surface):
    '''Draws tilemap and entities onto screen'''
    levelState.tileMap.draw(screen)
    for entity in levelState.entities:
        screen.blit(entity.image, levelState.tileMap.tileToPixel(entity.tileLocation))

class UIBaseState(State):
    '''Foundation that draws all levelState information. Acts a basis for UI states like targeting grenade throws or heal usage'''
    def __init__(self, game, levelState):
        self.game = game
        self.levelState = levelState
    
    def process(self, events: list[pg.event.Event]):
        pass

    def update(self):
        pass

    def render(self):
        '''Draws all of the basic levelstate'''
        self.levelState.tileMap.draw(self.game.screen)
        self.levelState.tileMap.drawCoverDebug(self.game.screen)
        self.levelState.tileMap.drawDebug(self.game.screen)
        for actor in self.levelState.entities:
            self.game.screen.blit(actor.image, actor.rect)

class MultiFrameAction:
    def __init__(self) -> None:
        self.completed = False
    
    def update(self, deltaTime: int):
        print("update method for multiframeAction not implemented")

class StartMenu(State):
    def __init__(self, game, playState) -> None:
        self.game = game
        self.playButton = TextImg("Play")
        self.playButton.rect.center = game.screen.get_rect().center
        self.playState = playState

    def process(self, events):
        super().process(events)
        for event in events:
            if event.type == pg.MOUSEBUTTONDOWN and event.button == pg.BUTTON_LEFT:
                if self.playButton.rect.collidepoint(event.pos):
                    self.game.enterState(self.playState)
                    print("go to next state")

    def render(self):
        self.game.screen.fill("black")
        self.game.screen.blit(self.playButton.image, self.playButton.rect)

# class MedkitTargeting(State):
#     def __init__(self, game, levelState: LevelState) -> None:
#         super().__init__(game)
#         self.levelState = levelState

#     def render(self):
#         drawLevelState(self.levelState, self.game.screen)
#         return super().render()