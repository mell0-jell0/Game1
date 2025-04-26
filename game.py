import pygame as pg
from States.states import State

pg.init()
WIN_WIDTH = 1280
WIN_HEIGHT = 720
screen = pg.display.set_mode((WIN_WIDTH, WIN_HEIGHT))

class Game:
    def __init__(self, screen:pg.surface.Surface) -> None:
        self.stateStack: list[State] = []
        self.WIN_WIDTH = WIN_WIDTH
        self.WIN_HEIGHT = WIN_HEIGHT
        self.screen = screen
        self.clock = pg.time.Clock()
        self.dt = 0

    def enterState(self, nextState: State):
        self.stateStack.append(nextState)

    def run(self):
        #MARK: Main game loop
        running = True
        while running:
            if pg.event.get(pg.QUIT):
                running = False
            self.stateStack[-1].process(pg.event.get())
            self.stateStack[-1].update()
            self.stateStack[-1].render()

            self.clock.tick(60)
            pg.display.flip()
            self.screen.fill("black")

        pg.quit()


game = Game(screen)