import math
from utility import *
from Player import *
from BasicEnemy import *
from GameMap import *

pg.font.init()

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

class TurnAction:
    '''
    class for handling different types of legal actions on a combat turn
    keeps track of cost and handles the checks for legality and rules etc
    '''
    def __init__(self):
        self.cost = 2

class TurnController:
    '''
    Don't know what im doing right now. this might do all the ui control, this might do the turn control, might do both.
    might get rid of this class and move it to main. right now (6/21/24) its doing ui and turn control.
    '''
    '''
    UPDATE 6/23/24:
    turn controller handles the UI input and all that jazz for the player and the ai to engage in turns. it does not handles outside menu things, that will be handled in a whole separate spot probably in main. I think it makes a lot of sense to keep all the things pertinent to the procession of a round sorta in one spot like this. I can make other modules for different aspects of the game.
    '''
    def __init__(self, screen: pg.Surface, tileMap: GameMap, player: Player, otherTurnTakers: list, entities: list) -> None:
        self.tileMap = tileMap
        self.player = player
        self.turnTakers = [self.player]
        for turnTaker in otherTurnTakers:
            self.turnTakers.append(turnTaker)
        
        self.currentTurn = 0

        #self.UIBox = pg.Surface(screen.get_size()) #might use for building ui in one surface and blitting all at once / for resizing
        self.nextTurnButton = Button("End Turn")
        self.nextTurnButton.rect.bottomleft = screen.get_rect().bottomleft
        self.turnIndicator = Button("Player's Turn")
        print(f"turn indicator is this many pixels wide:  {self.turnIndicator.image.get_width()}")
        self.turnIndicator.rect.topright = screen.get_rect().topright
        self.actionPointsIndicator = Button("Action Points: 3")
        self.actionPointsIndicator.rect.bottomright = screen.get_rect().bottomright

        #MAP UI
        self.lastClickedTile: tuple[int, int] = (-1,-1)
        self.clickedTileMarker = load_image("moveIndicator1.png") #perhaps rename to moveTileMarker
        self.shouldDrawMoveMarker = False
        self.crossHairMarker = load_image("crossHair1.png")
        self.shouldDrawCrossHairMarker = False
        #self.crossHairMarker[0]
        self.entities = entities # check to see if I should use sprite groups instead or something
            #my current thinking is that I will check clicks to see if they are on something in the entities list, and if they are, then I will check to see if that entity is interactable and what it's interaction methods are BTW ALT + Z TOGGLES LINE WRAPPING. USEFUL FOR COMMENTS LIKE THIS

    def drawUI(self, screen: pg.Surface):
        '''
        draws basic turn ui onto the screen
        '''
        screen.blit(self.nextTurnButton.image, self.nextTurnButton.rect)
        screen.blit(self.turnIndicator.image, self.turnIndicator.rect)
        self.actionPointsIndicator.updateText(f"Action Points: {self.player.actionPoints}")
        screen.blit(self.actionPointsIndicator.image, self.actionPointsIndicator.rect)
        #if the player has clicked on a tile show that
        if self.shouldDrawMoveMarker:
            screen.blit(*self.clickedTileMarker) #star unpacks tuple into arguments (in case i forget)
        if self.shouldDrawCrossHairMarker:
            screen.blit(*self.crossHairMarker)
    
    def handleClick(self, pos: tuple[float, float], gameMap: GameMap):
        #if self.turnTakers[self.currentTurn] != self.player: return False

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
    
    def run(self, screen, clock):
        running = True
        while running:
            screen.fill("black")
        # figure out where to put the player turn in here
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False

                if event.type == pg.MOUSEBUTTONDOWN and event.button == pg.BUTTON_LEFT:
                    # print(bigMap.getTile(event.pos))
                    # continue
                    if self.handleClick(event.pos, self.tileMap):
                        print("handled click")
                    else:
                        print("no handle click")

            #drawMap(tileGrid, tileDict)
            self.tileMap.draw(screen)
            #bigMap.drawDebug(screen)
            self.tileMap.drawAdjTile(screen, self.player.tileLocation)

            #Render UI
            self.drawUI(screen)

            
            #update player location and draw
            self.player.rect.topleft = self.tileMap.tileToPixel(self.player.tileLocation)
            self.player.draw(screen)

            #framerate
            clock.tick(60)
            pg.display.flip()