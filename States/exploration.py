import enum
from States.States import *
from gameMap import *
from Entities import *
from action import *

class Exploration(State):
    class ClickType(enum.Enum):
        ENTITY = enum.auto()
        MAP_TILE = enum.auto()
        BUTTON = enum.auto()
        INVALID = enum.auto()
    
    class PathWalk(MultiFrameAction):
        '''
        MultiFrameAction subclass for walking paths on the map
        maintains information about the path and handling movement of character sprite and updating of character tile location
        '''
        def __init__(self, levelState: LevelState, path: deque[tuple[int,int]], entity: MapEntity) -> None:
            super().__init__()
            self.levelState = levelState
            self.path = path
            self.entity = entity
            self.TIME_PER_TILE = 250 # time in ms
            self.stepProgress = 0
        
        def update(self, deltaTime):
            if len(self.path) == 1:
                self.completed = True
                self.path.clear()
                return
            self.stepProgress += deltaTime
            if self.stepProgress > self.TIME_PER_TILE:
                self.entity.tileLocation = self.path[1] #move to next tile in path
                self.path.popleft()
                self.stepProgress = 0
                self.entity.rect.topleft = self.levelState.tileMap.tileToPixel(self.entity.tileLocation)
                pass
            else:
                # linterp sprite location
                startPoint = self.levelState.tileMap.tileToPixel(self.entity.tileLocation, center=True)
                endPoint= self.levelState.tileMap.tileToPixel(self.path[1], center=True)
                xLoc = pg.math.lerp(startPoint[0], endPoint[0], self.stepProgress/self.TIME_PER_TILE)
                yLoc = pg.math.lerp(startPoint[1], endPoint[1], self.stepProgress/self.TIME_PER_TILE)
                self.entity.rect.center = (xLoc, yLoc)
                pass
            # do the path walking algorithm
            # at every step get the time. add the time to the progress bar, linterp the characters position between the two tiles. If the progress is >= 100 then place them on the tile and move on to the next step in the path 
    '''
    free roam tile map exploration. you walk where you click and you can interact with characters and items in this mode. triggers Turn control when within range of enemy. will also be able to trigger fishing later
    '''
    def __init__(self, game, levelState: LevelState, player:MapEntity) -> None:
        self.game = game

        self.levelState = levelState
        
        #Make sure entities draw locations are their tile locations
        for actor in self.levelState.entities:
            actor.rect.topleft = self.levelState.tileMap.tileToPixel(actor.tileLocation)

        self.player = player
        
        #MENU UI
        self.UIelements = pg.sprite.Group()
        self.activeButtons: set[Button] = set()
        self.activePopup: Popup | None = None

        #bounding box for UI elements on right side of screen
        self.UIbox = pg.rect.Rect(0,0,0,0)
        screenRect = self.game.screen.get_rect()
        self.UIbox.height = screenRect.height
        self.UIbox.width = screenRect.width // 6
        self.UIbox.topright = screenRect.topright

        self.inventoryButton = Button(TextImg("Inventory").image, lambda: print("inventory button no callback"))
        self.inventoryButton.rect.topleft = self.UIbox.topleft
        self.activeButtons.add(self.inventoryButton)
        self.UIelements.add(self.inventoryButton)

        self.hpIndicator = TextImg(f"HP: ", "red", "black")
        self.hpIndicator.rect.topleft = self.inventoryButton.rect.bottomleft
        self.UIelements.add(self.hpIndicator)

        self.pointsCostIndicator = TextImg(f"Action will consume: points", size=12)
        self.pointsCostIndicator.rect.topleft = self.hpIndicator.rect.bottomleft
        self.UIelements.add(self.pointsCostIndicator)

        #movement handling variables
        self.path : deque = deque()
        #self.moveTarget: None | tuple[int, int] = None
        self.multiFrameActions:set[MultiFrameAction] = set() #maintains list of all of the things that need to be updated each frame

        #UI interaction variables
        self.currClickType: tuple = tuple()
        self.lastClickType: tuple = tuple()
        self.renderPopup = False

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
        #First process clicks on buttons
        for button in self.activeButtons:
            if button.rect.collidepoint(clickPos):
                return (self.ClickType.BUTTON, button)
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
                self.lastClickType = self.currClickType
                self.currClickType = self.getClickType(event.pos)
                #Reset tracking variables
                self.path.clear()
                self.activePopup = None
                self.activeButtons.clear()

                match self.currClickType:
                    case (self.ClickType.MAP_TILE, tile):
                        assert(isinstance(tile, tuple))
                        print(f"clicked map tile {tile}")
                        self.path = self.levelState.tileMap.getPath(self.player.tileLocation, tile)
                        if self.currClickType == self.lastClickType: 
                            print(f"we confirmed a movement click to tile {tile}")
                            self.multiFrameActions.add(self.PathWalk(self.levelState, self.path, self.player))
                            #figure out how to make sure that two path walks aren't added at the same time. Make first path walk block

                    case (self.ClickType.ENTITY, entity):
                        assert(isinstance(entity, MapEntity))
                        print(f"clicked entity {entity}")
                        popupButtons: list = []
                        if hasattr(entity, "attackable"):
                            popupButtons.append(attackAction.availableButton)
                        if hasattr(entity, "interactable"):
                            popupButtons.append(interactAction.availableButton)
                        
                        self.activePopup = Popup(popupButtons, self.levelState.tileMap.tileToPixel(entity.tileLocation, center=True))
                        topLeftPointer = self.activePopup.anchor
                        for button in self.activePopup.buttons:
                            self.activeButtons.add(button)
                            button.rect.topleft = topLeftPointer
                            topLeftPointer = (topLeftPointer[0], topLeftPointer[1]+button.rect.height)


                    case (self.ClickType.INVALID, _):
                        print("invalid click")

                    case (self.ClickType.BUTTON, button):
                        print(f"clicked button {button}")
                        button.callback()

    def update(self):
        finishedActions: list[MultiFrameAction] = []
        for action in self.multiFrameActions:
            if action.completed:
                finishedActions.append(action)
            else:
                action.update(self.game.clock.get_time())

        for action in finishedActions:
            self.multiFrameActions.remove(action)
        # #calll update on every multiframe process
        # #THIS IS THE PATH WALKING ALGORITHM
        # if self.moveTarget == None and len(self.path) == 0: #no path to walk
        #     pass
        # elif self.moveTarget != None and len(self.path) ==0: #new target, get the new path
        #     self.path = self.levelState.tileMap.getPath(self.player.tileLocation, self.moveTarget)
        # elif self.moveTarget != None and len(self.path) != 0: #active target and path
        #     if self.moveTarget == self.path[-1]: #path is active for current target
        #         #animate normally until end of path
        #         self.animProgress += self.game.clock.get_time()
        #         if self.animProgress >= self.timePerTile:
        #             self.animProgress = 0
        #             self.player.tileLocation = self.path[0]
        #             self.path.popleft()
        #     else: #target has changed from the old path
        #         if self.animProgress == 0: #if at break in path, update
        #             self.path = self.levelState.tileMap.getPath(self.player.tileLocation, self.moveTarget)
        #         else: #if not at break in path, keep animating
        #             self.animProgress += self.game.clock.get_time()
        #             if self.animProgress >= self.timePerTile:
        #                 self.animProgress = 0
        #                 self.player.tileLocation = self.path[0]
        #                 self.path.popleft()
        

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
        self.levelState.tileMap.draw(self.game.screen)
        self.levelState.tileMap.drawCoverDebug(self.game.screen)
        for actor in self.levelState.entities:
            self.game.screen.blit(actor.image, actor.rect)
        
        self.drawPath()
        self.UIelements.draw(self.game.screen)

        if self.activePopup != None:
            drawanchor = self.activePopup.anchor
            for button in self.activePopup.buttons:
                self.game.screen.blit(button.image, drawanchor)
                drawanchor = (drawanchor[0], drawanchor[1]+button.rect.height)


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