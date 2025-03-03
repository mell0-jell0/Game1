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
            self.TIME_PER_TILE = 130 # time in ms
            self.stepProgress = 0
        
        def update(self, deltaTime):
            if len(self.path) == 1:
                self.completed = True
                self.path.clear()
                return
            self.stepProgress += deltaTime
            if self.stepProgress > self.TIME_PER_TILE:
                self.entity.tileLocation = self.path[1] #move to next tile in path
                self.path.popleft() # If path includes source, remove it
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
    def __init__(self, game, levelState: LevelState, player: Player) -> None:
        self.game = game

        self.levelState = levelState
        
        #Make sure entities draw locations are their tile locations
        for entity in self.levelState.entities:
            entity.rect.topleft = self.levelState.tileMap.tileToPixel(entity.tileLocation)

        #Update every entity to have a reference to its containing list. Allows entity to remove itself or add new.
        for entity in self.levelState.entities:
            entity.entityList = self.levelState.entities
        
        self.player: Player = player

        #Turn Management
        self.turnTakers: list[MapEntity] = [entity for entity in levelState.entities if hasattr(entity, "turnTaker")] 
        '''TODO: fix this mess >_<. TurnTaker should maybe be a subclass of MapEntity 
        or the turntaker list should be constructed as needed by querying the entities
        in any case this is a pain and confusing. Removing something from entities 
        doesn't remove it from turntakers and gets confusing'''
        for entity in self.turnTakers:
            entity.turnTaker.turnTakerList = self.turnTakers
        self.turnTakerIndex: int = 0

        #MENU UI
        self.UIelements = pg.sprite.Group()
        self.activeButtons: set[Button] = set()
        self.activePopup: Popup | None = None

        #Turn UI
        turnIndicator = TextImg("Current Turn: ", "White", "black")
        self.UIelements.add(turnIndicator)

        #bounding box for UI elements on right side of screen
        self.UIbox = pg.rect.Rect(0,0,0,0)
        screenRect = self.game.screen.get_rect()
        self.UIbox.height = screenRect.height
        self.UIbox.width = screenRect.width // 6
        self.UIbox.topright = screenRect.topright

        launchInventory = lambda : self.game.stateStack.append(InventoryMenu(self.game, self.levelState.tileMap, self.player, [],[],[]))
        self.inventoryButton = Button(TextImg("Inventory").image,launchInventory)
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
        self.pathChain: deque[deque[tile]] = deque()
        #self.moveTarget: None | tuple[int, int] = None
        self.multiFrameActions:set[MultiFrameAction] = set() #maintains list of all of the things that need to be updated each frame

        #UI interaction variables
        self.currClickType: tuple = tuple()
        self.lastClickType: tuple = tuple()
        self.renderPopup = False

        #move animation variables
        self.animProgress = 0 
        self.timePerTile = 250 #in ms

        #Temporary animations / effects
        self.tempAnimations: set[EffectAnimation] = set()
        self.tempAnimations.add(EffectAnimation(load_images("testAnimation")))

        #Constant/persistent animations tied to entities
        # setting gameplayPause to a value other than 0 will induce a pause in *gameplay* logic for that many ms. (i.e.Animations and technical processing should continue but AI should not take turns etc.)
        self.gameplayPause = 0
    
    def nextTurn(self):
        '''
        Modular increment of turnTakerIndex
        sets gameplayPause to 1000
        '''
        self.turnTakerIndex = (self.turnTakerIndex + 1) % len(self.turnTakers)
        self.gameplayPause = 1000
        print(f"TurnTakerIndex is {self.turnTakerIndex}")
    
    def getClickType(self, clickPos: tuple[int, int]) -> tuple[ClickType, Any]:
        '''
        function for classifying what was clicked on by the user for purposes of UI interaction
        returns a tuple with the click type as well as a the thing that was clicked on
        In the case of a game object, a reference to the object is returned
        In the case of a map tile, the tuple for that tile is returned
        '''
        print(self.activeButtons)
        #First process clicks on buttons
        for button in self.activeButtons:
            if button.rect.collidepoint(clickPos):
                return (self.ClickType.BUTTON, button)

        if self.activePopup != None:
            for button in self.activePopup.buttons:
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

    def handleLeftClick(self, event):
        '''
        Extracted logic for handling left clicks to reduce nesting/reading complexity
        '''
        self.lastClickType = self.currClickType
        self.currClickType = self.getClickType(event.pos)
        #Reset tracking variables
        self.path.clear()
        self.pathChain.clear()
        if self.activePopup != None:
            for button in self.activePopup.buttons:
                self.activeButtons.remove(button)
        self.activePopup = None

        match self.currClickType:
            case (self.ClickType.MAP_TILE, tile):
                assert(isinstance(tile, tuple))
                print(f"clicked map tile {tile}")
                totalPath = self.levelState.tileMap.getPath(self.player.tileLocation, tile)
                if len(totalPath) < 1: return
                assert(len(totalPath) > 1)

                #Leapfrog along path and split it into chunks 4 nodes or less
                startIndex = 0
                endIndex = 0
                while True:
                    startIndex = endIndex
                    # check how much room we have. use as many of the remaining nodes as we can up to 4
                    nodesLeft = len(totalPath) - startIndex
                    if nodesLeft >= 4:
                        endIndex += 3
                    elif nodesLeft > 1:
                        endIndex += nodesLeft - 1
                    else:
                        break
                    self.pathChain.append(deque( [totalPath[i] for i in range(startIndex, endIndex+1)] ))

                self.path = self.pathChain[0]

                if self.currClickType == self.lastClickType: 
                    print(f"we confirmed a movement click to tile {tile}")
                    self.multiFrameActions.add(self.PathWalk(self.levelState, self.path, self.player))
                    self.nextTurn()
                    #figure out how to make sure that two path walks aren't added at the same time. Make first path walk block

            case (self.ClickType.ENTITY, entity):
                assert(isinstance(entity, MapEntity))
                print(f"clicked entity {entity}")
                popupButtons: list = []
                if hasattr(entity, "attackable"):
                    if self.player.equipped != None: # Update the callback of the attack button based on the weapon
                        # TODO: find better way to make sure turn ends when necessary
                        def attackAndEnd():
                            self.player.equipped.resolveAttack(self.player,entity, self.levelState,self.tempAnimations)
                            self.nextTurn()
                        #attackAction.availableButton.callback = lambda : self.player.equipped.resolveAttack(self.player, entity, self.levelState, self.tempAnimations)
                        attackAction.availableButton.callback = attackAndEnd
                    else:
                        attackAction.availableButton.callback = lambda : print("Player cannont attack: equipped weapon = None")
                    popupButtons.append(attackAction.availableButton)
                if isinstance(entity, Interactable):
                    entity.getInteractInfo(self.levelState, self.player)
                    if entity.canInteract(self.levelState, self.player):
                        popupButtons.append(interactAction.availableButton)
                    else:
                        popupButtons.append(interactAction.unavailableButton)
                
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

    def process(self, events: list[pg.event.Event]):
        for event in events:
            #If it is the players turn, then process their types of inputs
            if event.type == pg.MOUSEBUTTONDOWN and event.button == pg.BUTTON_LEFT: #Click was made
                self.handleLeftClick(event)
            if event.type == pg.KEYDOWN and event.key == pg.K_d: print(f"Pathchain is : {self.pathChain}")

    def update(self):
        # Process all MultiFrameActions
        finishedActions: list[MultiFrameAction] = []
        for action in self.multiFrameActions:
            if action.completed:
                finishedActions.append(action)
            else:
                action.update(self.game.clock.get_time())

        for action in finishedActions:
            self.multiFrameActions.remove(action)
            if isinstance(action, self.PathWalk): #if a pathwalk was just completed, remove the path from the pathchain
                self.pathChain.popleft
        
        # Process all temporary/effect animations
        finishedAnimations = []
        for anim in self.tempAnimations:
            anim.update(self.game.clock.get_time())
            if anim.complete:
                finishedAnimations.append(anim)
        
        for anim in finishedAnimations:
            self.tempAnimations.remove(anim)
        
        #check for pauses in game logic
        if self.gameplayPause > 0:
            self.gameplayPause -= self.game.clock.get_time()
            if self.gameplayPause < 0: self.gameplayPause = 0
            return

        # Handle parts of the turn taking scheme
        if self.turnTakers[self.turnTakerIndex] == self.player:
            pass #update the players action if they have one. if they don't have one, do nothing
        else:
            if isinstance(self.turnTakers[self.turnTakerIndex], BasicEnemy):
                self.turnTakers[self.turnTakerIndex].basicTakeTurn(self.levelState, self.tempAnimations)
                self.nextTurn()
            pass #update the ai's action if they have one. if they don't have one, query them for an update.
        

    def drawPathChain(self):
        PATH_THICKNESS = 2
        PATH_COLOR = "white"
        #Draw path to walk 
        for path in self.pathChain:
            # draw all the segments of the path
            # for each terminal of a path, draw the special symbol there
            # for the terminal terminal, draw the special symbol
            if path == self.pathChain[-1]:
                isTerminalPath = True
            else:
                isTerminalPath = False

            for idx, tile in enumerate(path):
                if tile == path[-1]:
                    if isTerminalPath: #do special drawing
                        # get the points based of the direction came from
                        #TODO: add logic to draw triangle in correct orientation of path movement
                        center = self.levelState.tileMap.tileToPixel(tile, center=True)
                        offset = self.levelState.tileMap.TILE_WIDTH //4
                        trianlgePts: tuple = (
                            (center[0], center[1]+offset),
                            (center[0]+offset, center[1]),
                            (center[0]-offset, center[1])
                        )
                        pg.draw.polygon(self.game.screen,
                                        "green",
                                        trianlgePts)
                    else:
                        pg.draw.circle(self.game.screen,
                                "green",
                                self.levelState.tileMap.tileToPixel(tile, center=True),
                                self.levelState.tileMap.TILE_WIDTH//4,
                                width=3)
                else:
                    startPixel = self.levelState.tileMap.tileToPixel(tile, center=True)
                    endPixel = self.levelState.tileMap.tileToPixel(path[idx+1], center=True)
                    pg.draw.line(self.game.screen, PATH_COLOR, startPixel, endPixel, width=PATH_THICKNESS)
                    #pg.draw.circle(self.game.screen, "pink", self.levelState.tileMap.tileToPixel(tile, center=True), self.levelState.tileMap.TILE_WIDTH//3)

    def render(self):
        self.levelState.tileMap.draw(self.game.screen)
        self.levelState.tileMap.drawCoverDebug(self.game.screen)
        self.levelState.tileMap.drawDebug(self.game.screen)
        for actor in self.levelState.entities:
            self.game.screen.blit(actor.image, actor.rect)

        # Draw UI 
        self.drawPathChain()
        pg.draw.rect(self.game.screen, "grey", self.UIbox)
        self.UIelements.draw(self.game.screen)

        if self.activePopup != None:
            drawanchor = self.activePopup.anchor
            for button in self.activePopup.buttons:
                self.game.screen.blit(button.image, drawanchor)
                drawanchor = (drawanchor[0], drawanchor[1]+button.rect.height)
        
        for anim in self.tempAnimations:
            anim.draw(self.game.screen)
        
         #for entity in self.levelState.entities[1:]:
             #self.levelState.tileMap.drawDebugLineOfSight(entity.tileLocation, self.player.tileLocation, self.game.screen)
        # Draw attack UI
        match self.currClickType:
            case None:
                pass
            case (self.ClickType.ENTITY, entity):
                if hasattr(entity, "attackable") and self.player.equipped:
                    self.player.equipped.drawUI(self.player, entity, self.levelState, self.game.screen)
        

        # Hover over effects
        for entity in self.levelState.entities:
            if hasattr(entity, "attackable"):
                left, top = self.levelState.tileMap.tileToPixel(entity.tileLocation)
                rect = pg.rect.Rect(left, top, self.levelState.tileMap.TILE_WIDTH, self.levelState.tileMap.TILE_WIDTH)
                if rect.collidepoint(pg.mouse.get_pos()):
                    self.player.equipped.drawUI(self.player, entity, self.levelState, self.game.screen)


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