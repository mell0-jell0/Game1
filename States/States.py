import math

from pygame.sprite import AbstractGroup
from utility import *
from Player import *
from Entities import *
from BasicEnemy import *
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

class StartMenu(State):
    def __init__(self, game) -> None:
        self.game = game
        self.playButton = Button("Play")
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


class InventoryMenu(State):
    def __init__(self, game, tileMap: GameMap, player: Player, enemies: list, friendlies: list, interactables: list):
        self.game = game
        self.tileMap = tileMap
        self.player = player
        self.allTurnTakers = [player]   
        for turnTaker in enemies:
            self.allTurnTakers.append(turnTaker)
        self.interactables = interactables

        self.menuRegion = pg.rect.Rect(0, 0, game.WIN_WIDTH // 2, game.WIN_HEIGHT)
        self.menuRegion.topright = game.screen.get_rect().topright

        self.img = pg.Surface((self.menuRegion.width, self.menuRegion.height))
        self.img.fill((80,80,80))

        self.activePopup = None
    
    def process(self, events: list[pg.event.Event]):
        for event in events:
            if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                print("should be popping inventory state from stack when state transitions are hooked up right")
                self.game.stateStack.pop()
            if event.type == pg.MOUSEBUTTONDOWN and event.button == pg.BUTTON_LEFT:
                #default to popup
                if self.activePopup != None:
                    if self.activePopup.pointCollide(event.pos):
                        self.activePopup.handleClick(event.pos)
                    else:
                        self.activePopup = None
                else:
                    #check for an item click
                    itemClicked = False
                    for invItem in self.player.inventory:
                        if invItem.rect.collidepoint(event.pos):
                            itemClicked = True
                            self.activePopup = invItem.popup
                            self.activePopup.location = invItem.rect.center
                    
                    if not itemClicked:
                        self.activePopup = None


    def update(self):
        for character in self.allTurnTakers:
            character.rect.topleft = self.tileMap.tileToPixel(character.tileLocation)

    def render(self):
        #render all the stuff from the background
        self.tileMap.draw(self.game.screen)
        for character in self.allTurnTakers:
            self.game.screen.blit(character.image, character.rect)
        
        #render the menu background
        self.game.screen.blit(self.img, self.menuRegion)

        yDisplacement = 0

        equippedText = Button("Equipped", "Black", "Pink", size=20)
        equippedText.rect.topleft = self.menuRegion.topleft
        self.game.screen.blit(equippedText.image, equippedText.rect)
        yDisplacement+= equippedText.rect.height
        
        if self.player.equipped != None:
            self.player.equipped.rect.topleft = equippedText.rect.bottomleft
            self.game.screen.blit(self.player.equipped.image, self.player.equipped.rect)
            yDisplacement += self.player.equipped.rect.height
        
        #divider between equipped and rest
        lineWidth = 4
        yDisplacement += lineWidth // 2
        lineStart = (self.menuRegion.topleft[0], self.menuRegion.topleft[1] + yDisplacement)
        lineEnd = (lineStart[0] + self.menuRegion.width, lineStart[1])
        pg.draw.line(self.game.screen, "black", lineStart, lineEnd, 4)
        yDisplacement += lineWidth // 2


        #render the other items
        for item in self.player.inventory:
            if item == self.player.equipped: continue
            item.rect.topleft = (self.menuRegion.topleft[0], self.menuRegion.topleft[1] + yDisplacement)
            yDisplacement += item.rect.height
            self.game.screen.blit(item.image, item.rect)
        
        #render the active popup
        if self.activePopup != None:
            self.activePopup.draw(self.game.screen)
    