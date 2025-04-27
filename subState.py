from States.states import State, drawLevelState
from Entities import LevelState, Attackable
import pygame as pg

class MedkitState(State):
    def __init__(self, game, levelState: LevelState) -> None:
        super().__init__(game)
        self.levelState = levelState
    
    def render(self):
        '''
        Renders in addition to the basic UI of the exploration state
        '''
        tileMap = self.levelState.tileMap
        player = self.levelState.player

        for entity in self.levelState.entities:
            if entity.rect.collidepoint(pg.mouse.get_pos()):
                color = "grey"
                if tileMap.calcDistance(player.tileLocation, entity.tileLocation) == 1:
                    color = "green"
                
                pg.draw.circle(self.game.screen, color, entity.rect.center, tileMap.TILE_WIDTH,2)
    
    def process(self, events):
        for event in events:
            if event == pg.MOUSEBUTTONDOWN:
                for entity in self.levelState.entities:
                    if not isinstance(entity, Attackable): continue
                    if not entity.rect.collidepoint(event.pos): continue
                    print(f"we shall heal {entity}")
        return super().process(events)
print("imported substate")

