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

class TurnController:
    '''
    Don't know what im doing right now. this might do all the ui control, this might do the turn control, might do both.
    might get rid of this class and move it to main. right now (6/21/24) its doing ui and turn control.
    '''
    def __init__(self, screen: pg.Surface, player: Player) -> None:
        self.player = player
        self.isPlayerTurn = True
        #self.UIBox = pg.Surface(screen.get_size()) #might use for building ui in one surface and blitting all at once / for resizing
        self.nextTurnButton = Button("End Turn")
        self.nextTurnButton.rect.bottomleft = screen.get_rect().bottomleft
        self.turnIndicator = Button("Player's Turn")
        self.turnIndicator.rect.topright = screen.get_rect().topright

        self.lastClickedTile: tuple[int, int] = (-1,-1)
        self.clickedTileMarker = load_image("moveIndicator1.png") #perhaps rename to moveTileMarker
        self.crossHairTile: tuple[int, int] = (-1,-1)
        self.crossHairMarker = load_image("crossHair1.png")
        #self.crossHairMarker[0]
        self.entities = [] # check to see if I should use sprite groups instead or something
            #my current thinking is that I will check clicks to see if they are on something in the entities list, and if they are, then I will check to see if that entity is interactable and what it's interaction methods are BTW ALT + Z TOGGLES LINE WRAPPING. USEFUL FOR COMMENTS LIKE THIS

    def drawUI(self, screen: pg.Surface):
        '''
        draws basic turn ui onto the screen
        '''
        screen.blit(self.nextTurnButton.image, self.nextTurnButton.rect)
        screen.blit(self.turnIndicator.image, self.turnIndicator.rect)
        #if the player has clicked on a tile show that
        if self.lastClickedTile != (-1, -1):
            screen.blit(*self.clickedTileMarker) #star unpacks tuple into arguments (in case i forget)
        if self.crossHairTile != (-1,-1):
            screen.blit(*self.crossHairMarker)
    
    def handleClick(self, pos: tuple[float, float], gameMap: GameMap):
        #if not self.isPlayerTurn: return True
        self.crossHairTile = (-1,-1)

        #compute this bool for later
        entityClicked = False
        for entity in self.entities: 
            if entity.rect.collidepoint(pos): entityClicked = True
        
        if self.nextTurnButton.rect.collidepoint(pos): # handle clicks UI first
            self.isPlayerTurn = not self.isPlayerTurn
            return True
        elif entityClicked: #handle clicks on entities Just after UI, before checking to see if the map was clicked
            print("enemy was clicked")
            self.crossHairTile = gameMap.getTile(pos)
            self.crossHairMarker[1].topleft = gameMap.tileToPixel(gameMap.getTile(pos))
            return True
        elif gameMap.rect.collidepoint(pos): #Handle clicks on Map last
            print("detected map click")
            clickedTile = gameMap.getTile(pos)
            canMove = gameMap.calcDistance(gameMap.getTile(self.player.rect), clickedTile) < 7

            if clickedTile == self.lastClickedTile and canMove:
                self.player.rect.topleft = gameMap.tileToPixel(clickedTile)
            elif not canMove:
                print("too far buckaroo")
            elif clickedTile != self.lastClickedTile:
                self.lastClickedTile = clickedTile
                self.clickedTileMarker[1].topleft = gameMap.tileToPixel(clickedTile)
            #if is repeat click and is valid, move there
            #if not valid show message
            #if not repeat, update last clicked
            return True
            pass
        '''
        if the player clicks on a tile, check if that is a legal move and if it is, tell them how much it will cost
        if the player clicks on an enemy, tell them what range, and draw line to the enemy'''