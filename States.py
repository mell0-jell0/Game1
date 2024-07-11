import math

from pygame.sprite import AbstractGroup
from utility import *
from Player import *
from BasicEnemy import *
from GameMap import *

class Button(pg.sprite.Sprite):
    '''
    basic class for keeping track of button images and rects (for click detection and drawing)
    '''
    BUTTON_WIDTH = 80
    BUTTON_HEIGHT = 30
    textWriter = pg.font.Font(pg.font.get_default_font(), BUTTON_HEIGHT)

    def __init__(self, text) -> None:
        pg.sprite.Sprite.__init__(self)
        self.image = self.textWriter.render(text, 1, "black", "grey")
        self.rect = self.image.get_rect()
    
    def updateText(self, newVal):
        '''
        uses static font object to render new text and updates image surface accordingly
        '''
        self.image = self.textWriter.render(newVal, 1, "black", "grey")


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
    def __init__(self, screen: pg.surface.Surface) -> None:
        self.screen = screen
        self.playButton = Button("Play")
        self.playButton.rect.center = screen.get_rect().center

    def process(self, events):
        super().process(events)
        for event in events:
            if event.type == pg.MOUSEBUTTONDOWN and event.button == pg.BUTTON_LEFT:
                if self.playButton.rect.collidepoint(event.pos):
                    print("go to next state")

    def render(self):
        self.screen.fill("black")
        self.screen.blit(self.playButton.image, self.playButton.rect)

class TurnControl(State):
        
        def __init__(self, screen: pg.Surface, tileMap: GameMap, player: Player, otherTurnTakers: list, entities: list) -> None:
            self.tileMap = tileMap
            self.player = player
            self.turnTakers = [self.player]
            for turnTaker in otherTurnTakers:
                self.turnTakers.append(turnTaker)
            
            self.currentTurn = 0
            
            #stack for holding active UI elements. i.e. inventory goes on top of main game and a popup for an inventory item goes on top of that
            self.activeElementsStack = []

            #MENU UI
            self.UIelements = pg.sprite.Group()

            self.nextTurnButton = Button("End Turn")
            self.nextTurnButton.rect.bottomleft = screen.get_rect().bottomleft

            self.turnIndicator = Button("Player's Turn")
            print(f"turn indicator is this many pixels wide:  {self.turnIndicator.image.get_width()}")

            self.turnIndicator.rect.topright = screen.get_rect().topright
            self.actionPointsIndicator = Button("Action Points: 3")
            self.actionPointsIndicator.rect.bottomright = screen.get_rect().bottomright

            self.inventoryButton = Button("Inventory")
            self.inventoryButton.rect.topright = self.turnIndicator.rect.bottomright
            #MAP UI
            self.lastClickpos: None | tuple[int, int] = None

            self.lastClickedTile = (-1, -1)
            self.clickedTileMarker = load_image("moveIndicator1.png") #perhaps rename to moveTileMarker
            self.shouldDrawMoveMarker = False

            self.crossHairMarker = load_image("crossHair1.png")
            self.shouldDrawCrossHairMarker = False
            #self.crossHairMarker[0]
            self.entities = entities # check to see if I should use sprite groups instead or something
                #my current thinking is that I will check clicks to see if they are on something in the entities list, and if they are, then I will check to see if that entity is interactable and what it's interaction methods are BTW ALT + Z TOGGLES LINE WRAPPING. USEFUL FOR COMMENTS LIKE THIS

            self.UIelements.add((self.turnIndicator, self.actionPointsIndicator, self.inventoryButton, self.nextTurnButton))

        def drawUI(self, screen: pg.Surface):
            '''
            draws basic turn ui onto the screen
            '''
            ####NEW WAY OF DRAWING WITH GROUPS instead of manual blits
            self.UIelements.draw(screen)

            #if the player has clicked on a tile show that
            if self.shouldDrawMoveMarker:
                screen.blit(*self.clickedTileMarker) #star unpacks tuple into arguments (in case i forget)
            if self.shouldDrawCrossHairMarker:
                screen.blit(*self.crossHairMarker)
        
        def handleClick(self, pos: tuple[float, float], gameMap: GameMap):
            #check for confirmed clicks
            #ELSE if on map or on entity set the marker
            #ELSE IF other, clear the UI and such
            '''does things for click, returns true if the click was handled, false if it still needs to be handled.'''
            #if self.turnTakers[self.currentTurn] != self.player: return False
            if len(self.activeElementsStack) != 0:
                #let the active element handle all the things.
                self.activeElementsStack[-1].handleClick(self.tileMap, self.entities)
                return
            
            #active elements will be sprite groups that get drawn to the screen and that have a handleClick method.
            self.shouldDrawCrossHairMarker = False

            self.shouldDrawMoveMarker = False

            ####HANDLE UI CLICKS
            if self.nextTurnButton.rect.collidepoint(pos):
                #do the next turn thing
                self.nextTurn()
                return True
            
            if self.turnTakers[self.currentTurn] != self.player: return False
            ####HANDLE CLICKS THAT HAPPEN OVER MAP
            elif gameMap.rect.collidepoint(pos):
                ####CHECK CLICKS ON ENTITIES
                clickedTile = gameMap.getTile(pos)
                for entity in self.entities:
                    if entity.tileLocation == clickedTile:
                        #Handle confirmed click
                        if self.lastClickedTile == clickedTile and self.player.actionPoints >= 2: 
                            print("blamo, confirm clicked on an entity")
                            self.player.actionPoints -= 2
                            return True
                        self.shouldDrawCrossHairMarker = True
                        print("entity was clicked")
                        self.crossHairMarker[1].topleft = gameMap.tileToPixel(gameMap.getTile(pos))
                        self.lastClickedTile = clickedTile
                        return True
                
                ####CHECK CLICKS ONLY ON MAP
                distance = gameMap.calcDistance(self.player.tileLocation, clickedTile)
                print(f"detected map click on tile {distance} units from player")
                canMove = gameMap.calcDistance(self.player.tileLocation, clickedTile) <= self.player.actionPoints * 3

                if clickedTile == self.lastClickedTile and canMove:
                    self.player.moveTo(clickedTile) #execute action
                    self.player.actionPoints -= math.ceil(distance / 3) #incur cost
                    print("confirmed click to move")
                elif not canMove:
                    print("too far buckaroo")
                elif clickedTile != self.lastClickedTile:
                    self.clickedTileMarker[1].topleft = gameMap.tileToPixel(clickedTile)
                    self.shouldDrawMoveMarker = True
                
                self.lastClickedTile = clickedTile
                #if is repeat click and is valid, move there
                #if not valid show message
                #if not repeat, update last clicked
                return True
                pass
            '''
            if the player clicks on a tile, check if that is a legal move and if it is, tell them how much it will cost
            if the player clicks on an enemy, tell them what range, and draw line to the enemy
            '''
        def updateActionPoints(self, newVal):
            self.actionPointsIndicator.updateText(f"Action Points {newVal}")

        def nextTurn(self):
            print(f"self.turnTakers is {self.turnTakers}")
            print(f"old turnIdx was {self.currentTurn}")
            self.currentTurn = (self.currentTurn + 1) % len(self.turnTakers)
            print(f"new turnIdx is {self.currentTurn}")
            self.turnTakers[self.currentTurn].actionPoints = 3

        def isPlayerTurn(self):
            return self.player == self.turnTakers[self.currentTurn]
        
        def update(self):
            '''Handles the processing of things that occur "automatically" such as transitions between frames of animations or updates to physics based on velocity. AFAIK I won't be doing much in here because most things are handled with rules or from the UI. I might be wrong though'''
            if self.player.health == 0:
                print("GAME OVER")

        def render(self, screen: pg.surface.Surface):
                self.tileMap.draw(screen)
                #bigMap.drawDebug(screen)
                self.tileMap.drawAdjTile(screen, self.player.tileLocation)

                for actor in self.turnTakers:
                    actor.rect.topleft = self.tileMap.tileToPixel(actor.tileLocation)
                    actor.draw(screen)

                self.drawUI(screen)

