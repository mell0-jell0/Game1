import enum
from States.States import State
from gameMap import *
from Entities import *
from action import *

class Exploration(State):
    class ClickType(enum.Enum):
        ENTITY = enum.auto()
        MAP_TILE = enum.auto()
        BUTTON = enum.auto()
        INVALID = enum.auto()
    
    class Action:
        def __init__(self) -> None:
            pass
    '''
    free roam tile map exploration. you walk where you click and you can interact with characters and items in this mode. triggers Turn control when within range of enemy. will also be able to trigger fishing later
    '''
    def __init__(self, game, levelState: LevelState, player:MapEntity) -> None:
        self.game = game

        self.levelState = levelState
        self.player = player
        
        #MENU UI
        self.UIelements = pg.sprite.Group()

        #bounding box for UI elements on right side of screen
        self.UIbox = pg.rect.Rect(0,0,0,0)
        screenRect = self.game.screen.get_rect()
        self.UIbox.height = screenRect.height
        self.UIbox.width = screenRect.width // 6
        self.UIbox.topright = screenRect.topright

        self.inventoryButton = Button("Inventory")
        self.inventoryButton.rect.topleft = self.UIbox.topleft
        self.UIelements.add(self.inventoryButton)

        self.hpIndicator = Button(f"HP: ", "red", "black")
        self.hpIndicator.rect.topleft = self.inventoryButton.rect.bottomleft
        self.UIelements.add(self.hpIndicator)

        self.pointsCostIndicator = Button(f"Action will consume: points", size=12)
        self.pointsCostIndicator.rect.topleft = self.hpIndicator.rect.bottomleft
        self.UIelements.add(self.pointsCostIndicator)

        #movement handling variables
        self.path : deque = deque()
        self.moveTarget: None | tuple[int, int] = None

        #UI interaction variables
        self.currClickType: tuple = tuple()
        self.lastClickType: tuple = tuple()
        #move animation variables
        self.animProgress = 0 
        self.timePerTile = 250 #in ms

    def getClickType(self, clickPos: tuple[int, int]) -> tuple:
        '''
        function for classifying what was clicked on by the user for purposes of UI interaction
        returns a tuple with the click type as well as a the thing that was clicked on
        In the case of a game object, a reference to the object is returned
        In the case of a map tile, the tuple for that tile is returned
        '''
        #Check that click is over map
        if not self.levelState.tileMap.rect.collidepoint(clickPos): return (self.ClickType.INVALID, None)
        #Check for clicked entity
        clickTileLocation = self.levelState.tileMap.getTile(clickPos)
        for entity in self.levelState.entities:
            if entity.tileLocation == clickTileLocation:
                return (self.ClickType.ENTITY, entity)
        #No clicked entity then map clicked
        return (self.ClickType.MAP_TILE, clickTileLocation)

    def process(self, events: list[pg.event.Event]):
        for event in events:
            if event.type == pg.MOUSEBUTTONDOWN and event.button == pg.BUTTON_LEFT: #Click was made
                #TODO clean up all of this messy logic. maybe abstract out into action classes
                self.lastClickType = self.currClickType
                self.currClickType = self.getClickType(event.pos) 
                if self.currClickType[0] == self.ClickType.INVALID: break #don't handle this event
                if self.currClickType[0] == self.ClickType.ENTITY:
                    if hasattr(self.currClickType[1], "attackable"): print("we clicked an attackable")
                    # for action in actions if entity matches action then add action to available list
                    break
                if self.currClickType[0] == self.ClickType.MAP_TILE:
                    self.path = self.levelState.tileMap.getPath(self.player.tileLocation, self.currClickType[1])

    def update(self):
        #THIS IS THE PATH WALKING ALGORITHM
        if self.moveTarget == None and len(self.path) == 0: #no path to walk
            pass
        elif self.moveTarget != None and len(self.path) ==0: #new target, get the new path
            self.path = self.levelState.tileMap.getPath(self.player.tileLocation, self.moveTarget)
        elif self.moveTarget != None and len(self.path) != 0: #active target and path
            if self.moveTarget == self.path[-1]: #path is active for current target
                #animate normally until end of path
                self.animProgress += self.game.clock.get_time()
                if self.animProgress >= self.timePerTile:
                    self.animProgress = 0
                    self.player.tileLocation = self.path[0]
                    self.path.popleft()
            else: #target has changed from the old path
                if self.animProgress == 0: #if at break in path, update
                    self.path = self.levelState.tileMap.getPath(self.player.tileLocation, self.moveTarget)
                else: #if not at break in path, keep animating
                    self.animProgress += self.game.clock.get_time()
                    if self.animProgress >= self.timePerTile:
                        self.animProgress = 0
                        self.player.tileLocation = self.path[0]
                        self.path.popleft()
        

    def drawPath(self):
        PATH_THICKNESS = 2
        PATH_COLOR = "white"
        #Draw path to walk 
        for idx, tile in enumerate(self.path):
            if tile == self.path[-1]:
                pg.draw.circle(self.game.screen,
                               "green",
                               self.levelState.tileMap.tileToPixel(tile, center=True),
                               self.levelState.tileMap.TILE_WIDTH//4,
                               width=3)
            else:
                startPixel = self.levelState.tileMap.tileToPixel(tile, center=True)
                endPixel = self.levelState.tileMap.tileToPixel(self.path[idx+1], center=True)
                pg.draw.line(self.game.screen, PATH_COLOR, startPixel, endPixel, width=PATH_THICKNESS)
                #pg.draw.circle(self.game.screen, "pink", self.levelState.tileMap.tileToPixel(tile, center=True), self.levelState.tileMap.TILE_WIDTH//3)

    def render(self):
        for actor in self.levelState.entities:
            actor.rect.topleft = self.levelState.tileMap.tileToPixel(actor.tileLocation)

        self.levelState.tileMap.draw(self.game.screen)
        self.levelState.tileMap.drawCoverDebug(self.game.screen)
        for actor in self.levelState.entities:
            self.game.screen.blit(actor.image, actor.rect)
        
        self.drawPath()
        self.UIelements.draw(self.game.screen)
        self.game.screen.blit(attackAction.availableButton, (0,0))
        self.game.screen.blit(interactAction.availableButton, (0,attackAction.availableButton.get_rect().height))

    class GrenadeTargeting(State):
        def rayLength(self, ray: tuple[tuple[int,int], tuple[int, int]]):
            '''
            just the pythagorean theorem
            '''
            x1, y1 = ray[0]
            x2, y2 = ray[1]

            a = abs(x2 - x1)
            b = abs(y2 - y1)

            return math.sqrt(math.pow(a,2) + math.pow(b,2))
        
        def __init__(self, game, levelState, player):
            self.game = game
            self.levelState = levelState
            self.player = player
            
            #MENU UI
            self.UIelements = pg.sprite.Group()
    	    
            self.tileBlastRadius = 3
            #get the affected squares
            self.affectedSquares = []
            self.centerTile = (3,3)

        def getRays(self):
            '''
            returns list of every ray raycasted from grenade as a tuple of tuples of ints (a tuple containing both end points)
            all rays have their starting point at the center of the grenade tile and their endpoint at the center of the tile that was raycast to
            '''
            #THE GIST: we make a square around the grenade, the width of the square is the diameter of the blast (2 * blast radius)
            #for each tile in this square we raycast to it and check 2 things:
                #we check if the tile's center is in the blast radius
                #we check if the ray intersects cover
                #apply the effects of any cover hit by the raycast and then carry out the damage (assuming the center was within the blast radius)
            
            #get the bounding tile of the square
            topLeftLimit = (self.centerTile[0] - self.tileBlastRadius , self.centerTile[1] - self.tileBlastRadius)
            bottomRightLimit = (self.centerTile[0] + self.tileBlastRadius, self.centerTile[1] + self.tileBlastRadius)
            rays: list[tuple[tuple[int, int], tuple[int, int]]] = []
            #check every tile in the bounding square
            for row in range(topLeftLimit[0], bottomRightLimit[0]+1): #don't forget to include +1 because ranges don't count the end point
                for col in range(topLeftLimit[1], bottomRightLimit[1]+1):
                    #check that the tile is on the board (not too close to edge or corner)
                    if row < 0 or col < 0: continue
                    if row > self.levelState.tileMap.height - 1: continue
                    if col > self.levelState.tileMap.width - 1: continue

                    #now we make the ray (technically a segment, shut up)
                    ray = (self.levelState.tileMap.tileToPixel(self.centerTile, center=True), self.levelState.tileMap.tileToPixel((row, col), center=True))
                    rays.append(ray)
            return rays

        def drawRaysDebug(self):
            #I want to make sure that the shorter range rays aren't drawn over by the further ones, so I put in range and out of range in seperate lists and draw the longer ones first
            inRange = []
            OORange = []
            for ray in self.getRays():
                if self.rayLength(ray) < (self.tileBlastRadius * self.levelState.tileMap.TILE_WIDTH) + self.levelState.tileMap.TILE_WIDTH // 2:
                    inRange.append(ray)
                else:
                    OORange.append(ray)
                pg.draw.circle(self.game.screen, "black", ray[1], 4)
            
            for ray in OORange:
                pg.draw.line(self.game.screen, pg.Color(255,255,0), ray[0], ray[1])
            
            for ray in inRange:
                pg.draw.line(self.game.screen, pg.Color(255,0,0), ray[0], ray[1])
            
            pg.draw.circle(self.game.screen, 
                           "red", 
                           self.levelState.tileMap.tileToPixel(self.centerTile, center=True),
                           (self.tileBlastRadius * self.levelState.tileMap.TILE_WIDTH) + self.levelState.tileMap.TILE_WIDTH // 2,
                           width=2)
        
        def getAffectedSquares(self):
            '''
            calls the getRays function and then check each ray against the cover rects returned by the tilemap.
            returns the tiles that are fully exposed and the tiles that are only blocked by half cover
            '''
            rays = self.getRays()
            exposedTiles: list[tuple[int, int]] = []
            halfCoveredTiles: list[tuple[int, int]] = []
            fullCoverRects = self.levelState.tileMap.getFullCover()
            halfCoverRects = self.levelState.tileMap.getHalfCover()

            for ray in rays:
                #if ray is out of range skip it
                if self.rayLength(ray) > (self.tileBlastRadius * self.levelState.tileMap.TILE_WIDTH) + self.levelState.tileMap.TILE_WIDTH //2:
                    continue

                fullyCovered: bool = False
                halfCovered: bool = False

                for rect in fullCoverRects:
                    if len(rect.clipline(ray)) != 0:
                        #there is an intersection
                        fullyCovered = True
                        break
                    
                for rect in halfCoverRects:
                    if len(rect.clipline(ray)) != 0:
                        #the rect intersects the ray
                        halfCovered = True
                        break
                
                if (not fullyCovered) and (not halfCovered):
                    exposedTiles.append(self.levelState.tileMap.getTile(ray[1]))
                elif (not fullyCovered) and (halfCovered):
                    halfCoveredTiles.append(self.levelState.tileMap.getTile(ray[1]))
                else:
                    pass
                
            return (exposedTiles, halfCoveredTiles)


        def drawDebugAffectedSquares(self):
            exposedIndicator = load_image("grenadeExposedIndicator.png")
            halfCoverIndicator = load_image("grenadeHalfCoverIndicator.png")

            exposed, halfCovered = self.getAffectedSquares()

            for tile in exposed:
                exposedIndicator[1].topleft = self.levelState.tileMap.tileToPixel(tile)
                self.game.screen.blit(*exposedIndicator)
            
            for tile in halfCovered:
                halfCoverIndicator[1].topleft = self.levelState.tileMap.tileToPixel(tile)
                self.game.screen.blit(*halfCoverIndicator)


        def update(self):
            self.centerTile = self.levelState.tileMap.getTile(pg.mouse.get_pos())

        def render(self):
            self.game.screen.fill("black")
            self.levelState.tileMap.draw(self.game.screen)
            for enemy in self.levelState.entities:
                enemy.rect.topleft = self.levelState.tileMap.tileToPixel(enemy.tileLocation)
                self.game.screen.blit(enemy.image, enemy.rect)
            #self.drawRaysDebug()
            self.drawDebugAffectedSquares()