import math

from pygame.sprite import AbstractGroup
from utility import *
from Player import *
from Character import *
from BasicEnemy import *
from GameMap import *


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


class Exploration(State):
    class ClickType(enum.Enum):
        ENEMY = enum.auto()
        NPC = enum.auto()
        MAP_TILE = enum.auto()
        INVALID = enum.auto()
    
    class Action:
        def __init__(self) -> None:
            pass
    '''
    free roam tile map exploration. you walk where you click and you can interact with characters and items in this mode. triggers Turn control when within range of enemy. will also be able to trigger fishing later
    '''
    def __init__(self, game, tileMap: GameMap, player: Player, enemies: list, friendlies: list, interactables: list) -> None:
        self.game = game

        self.tileMap = tileMap
        self.player = player
        self.enemies: list[Character] = enemies
        self.friendlies = friendlies
        self.turnTakers = [self.player]
        for turnTaker in enemies:
            self.turnTakers.append(turnTaker)
        
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

        self.hpIndicator = Button(f"HP: {self.player.health}", "red", "black")
        self.hpIndicator.rect.topleft = self.inventoryButton.rect.bottomleft
        self.UIelements.add(self.hpIndicator)

        self.pointsCostIndicator = Button(f"Action will consume: points", size=12)
        self.pointsCostIndicator.rect.topleft = self.hpIndicator.rect.bottomleft
        self.UIelements.add(self.pointsCostIndicator)

        self.interactables = interactables # check to see if I should use sprite groups instead or something

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
        #first check if the click was over the map 
        if not self.tileMap.rect.collidepoint(clickPos):
            print("user did not click over map")
            return self.ClickType.INVALID, None
        else:
            for enemy in self.enemies: # check if an enemy was click first
                if self.tileMap.getTile(clickPos) == enemy.tileLocation:
                    print("Enemy was clicked on")
                    return self.ClickType.ENEMY, enemy
            #if we fall through this far it was a click over map but not on enemy
            print("click classified as map click")
            return self.ClickType.MAP_TILE, self.tileMap.getTile(clickPos) 

    def process(self, events: list[pg.event.Event]):
        for event in events:
            if event.type == pg.MOUSEBUTTONDOWN and event.button == pg.BUTTON_LEFT: #Click was made
                #TODO clean up all of this messy logic. maybe abstract out into action classes
                self.lastClickType = self.currClickType
                self.currClickType = self.getClickType(event.pos) 
                if self.currClickType[0] == self.ClickType.INVALID: break #don't handle this event
                if self.currClickType == self.lastClickType:
                    match self.currClickType[0]:
                        case self.ClickType.MAP_TILE:
                            if self.tileMap.calcDistance(self.player.tileLocation, self.currClickType[1]) < 100000:
                                print("The player confirmed a legal movement")
                        case self.ClickType.ENEMY:
                            sightline = (self.tileMap.tileToPixel(self.player.tileLocation, True), self.tileMap.tileToPixel(self.currClickType[1].tileLocation, True))
                            unobstructed = True
                            for coverRect in self.tileMap.getFullCover():
                                if coverRect.clipline(sightline[0], sightline[1]) != tuple():
                                    unobstructed = False
                                    break
                            if unobstructed:
                                print("Player confirmed a legal attack")
                #if the clicks are identical, then execute if able
                #if the clicks are different, update the UI accordingly
                    #how do we update the UI? update the  UI depending on the click that happened.
                    #if enemy, check if can attack, check weapon stats to show
                    #if tile, check if naviagable, if naviagable, show cost
                    #if interactible TODO
                if self.currClickType == self.lastClickType and self.lastClickType[0] != self.ClickType.INVALID:
                    print("We should resolve the action if it is legal")\
                
                '''
                Enemies
                    show the click marker. show what the cost of the action is
                    if second click, carry out attack
                Tiles
                    show move marker and path
                    if second click, move them, implement pausing during path later
                Interactibles
                    give some sort of UI makr as to what kind of interaction will happen. For items that you can pick up, show a pick up icon, for containers show an open icon. for fishing spots show some sort of icon. 

                Actions are things that the player can do for their turn. they include attacks, moves, and interacts. every action should have a description
                on the first click you want to do checks and show the user what they are doing
                on a repeat click you want to confirm, that is the basis of the interactions
                need a way to display information about the action they may or may not be performing
                we want to tell the user what they are about to do with words. we want to display the correct UI information as well
                '''
                # if self.tileMap.rect.collidepoint(event.pos):
                #     self.moveTarget = self.tileMap.getTile(event.pos)
                #     print("clicked on map and got path")
                # else:
                #     print("didn't click on map")

    def update(self):
        for turnTaker in self.turnTakers:
            if turnTaker == self.player: continue
            if isinstance(turnTaker, BasicEnemy):
                xDist = abs(turnTaker.tileLocation[1] - self.player.tileLocation[1]) #remember flip xy rowcol
                yDist = abs(turnTaker.tileLocation[0] - self.player.tileLocation[0])
                if xDist <= turnTaker.engageRange and yDist <= turnTaker.engageRange:
                    self.game.enterState(ExplorationTurnTransition(self.game, self.tileMap, self.player, self.enemies, self.friendlies, []))

        if self.moveTarget == None and len(self.path) == 0: #no path to walk
            pass
        elif self.moveTarget != None and len(self.path) ==0: #new target, get the new path
            self.path = self.tileMap.getPath(self.player.tileLocation, self.moveTarget)
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
                    self.path = self.tileMap.getPath(self.player.tileLocation, self.moveTarget)
                else: #if not at break in path, keep animating
                    self.animProgress += self.game.clock.get_time()
                    if self.animProgress >= self.timePerTile:
                        self.animProgress = 0
                        self.player.tileLocation = self.path[0]
                        self.path.popleft()
        

    def render(self):
        PATH_THICKNESS = 2
        PATH_COLOR = "pink"
        for actor in self.turnTakers:
            actor.rect.topleft = self.tileMap.tileToPixel(actor.tileLocation)

        self.tileMap.draw(self.game.screen)
        self.tileMap.drawCoverDebug(self.game.screen)
        for actor in self.turnTakers:
            self.game.screen.blit(actor.image, actor.rect)
        
        for idx, tile in enumerate(self.path):
            if tile == self.path[-1]:
                pg.draw.circle(self.game.screen, "green", self.tileMap.tileToPixel(tile, center=True), self.tileMap.TILE_WIDTH//4)
            else:
                startPixel = self.tileMap.tileToPixel(tile, center=True)
                endPixel = self.tileMap.tileToPixel(self.path[idx+1], center=True)
                pg.draw.line(self.game.screen, PATH_COLOR, startPixel, endPixel, width=PATH_THICKNESS)
                #pg.draw.circle(self.game.screen, "pink", self.tileMap.tileToPixel(tile, center=True), self.tileMap.TILE_WIDTH//3)

        self.UIelements.draw(self.game.screen)

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
        
        def __init__(self, game, tileMap: GameMap, player: Player, enemies: list, friendlies: list, interactables: list):
            self.game = game

            self.tileMap = tileMap
            self.player = player
            self.turnTakers = [self.player]
            for turnTaker in enemies:
                self.turnTakers.append(turnTaker)
            
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
                    if row > self.tileMap.height - 1: continue
                    if col > self.tileMap.width - 1: continue

                    #now we make the ray (technically a segment, shut up)
                    ray = (self.tileMap.tileToPixel(self.centerTile, center=True), self.tileMap.tileToPixel((row, col), center=True))
                    rays.append(ray)
            return rays

        def drawRaysDebug(self):
            #I want to make sure that the shorter range rays aren't drawn over by the further ones, so I put in range and out of range in seperate lists and draw the longer ones first
            inRange = []
            OORange = []
            for ray in self.getRays():
                if self.rayLength(ray) < (self.tileBlastRadius * self.tileMap.TILE_WIDTH) + self.tileMap.TILE_WIDTH // 2:
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
                           self.tileMap.tileToPixel(self.centerTile, center=True),
                           (self.tileBlastRadius * self.tileMap.TILE_WIDTH) + self.tileMap.TILE_WIDTH // 2,
                           width=2)
        
        def getAffectedSquares(self):
            '''
            calls the getRays function and then check each ray against the cover rects returned by the tilemap.
            returns the tiles that are fully exposed and the tiles that are only blocked by half cover
            '''
            rays = self.getRays()
            exposedTiles: list[tuple[int, int]] = []
            halfCoveredTiles: list[tuple[int, int]] = []
            fullCoverRects = self.tileMap.getFullCover()
            halfCoverRects = self.tileMap.getHalfCover()

            for ray in rays:
                #if ray is out of range skip it
                if self.rayLength(ray) > (self.tileBlastRadius * self.tileMap.TILE_WIDTH) + self.tileMap.TILE_WIDTH //2:
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
                    exposedTiles.append(self.tileMap.getTile(ray[1]))
                elif (not fullyCovered) and (halfCovered):
                    halfCoveredTiles.append(self.tileMap.getTile(ray[1]))
                else:
                    pass
                
            return (exposedTiles, halfCoveredTiles)


        def drawDebugAffectedSquares(self):
            exposedIndicator = load_image("grenadeExposedIndicator.png")
            halfCoverIndicator = load_image("grenadeHalfCoverIndicator.png")

            exposed, halfCovered = self.getAffectedSquares()

            for tile in exposed:
                exposedIndicator[1].topleft = self.tileMap.tileToPixel(tile)
                self.game.screen.blit(*exposedIndicator)
            
            for tile in halfCovered:
                halfCoverIndicator[1].topleft = self.tileMap.tileToPixel(tile)
                self.game.screen.blit(*halfCoverIndicator)


        def update(self):
            self.centerTile = self.tileMap.getTile(pg.mouse.get_pos())

        def render(self):
            self.game.screen.fill("black")
            self.tileMap.draw(self.game.screen)
            for enemy in self.turnTakers:
                enemy.rect.topleft = self.tileMap.tileToPixel(enemy.tileLocation)
                self.game.screen.blit(enemy.image, enemy.rect)
            #self.drawRaysDebug()
            self.drawDebugAffectedSquares()


# class TurnControl(State):
    # ## substates should just be able to use the State class. Im not sure how arbitrary nesting of code will work. If I was just doing one level deep I would make an enum and use switch case for the logic but that doesn't nest well. you end up with a million switch cases nested. I want something that can nest arbitrarily but that is also lightweight. I would just use the state like I have right now, but the switching makes it really clunky. I also don't know how to do persistent state.
    # '''Does the turn based tactical handling like dnd encounters. Not exclusively combat. there are plans for negotiating and escaping.'''
    # def __init__(self, game, tileMap: GameMap, player: Player, enemies: list, friendlies, interactables: list) -> None:
    #     self.game = game

    #     self.tileMap = tileMap
    #     self.player = player
    #     self.enemies = enemies
    #     self.friendlies = friendlies
    #     self.turnTakers = [self.player]
    #     for turnTaker in enemies:
    #         self.turnTakers.append(turnTaker)
        
    #     self.currentTurn = 0
        
    #     #MENU UI
    #     self.UIelements = pg.sprite.Group()

    #     self.nextTurnButton = Button("End Turn")
    #     self.nextTurnButton.rect.bottomleft = game.screen.get_rect().bottomleft

    #     self.turnIndicator = Button("Player's Turn")
    #     print(f"turn indicator is this many pixels wide:  {self.turnIndicator.image.get_width()}")

    #     self.turnIndicator.rect.topright = game.screen.get_rect().topright
    #     self.actionPointsIndicator = Button("Action Points: 3")
    #     self.actionPointsIndicator.rect.bottomright = game.screen.get_rect().bottomright

    #     self.inventoryButton = Button("Inventory")
    #     self.inventoryButton.rect.topright = self.turnIndicator.rect.bottomright

    #     self.hpIndicator = Button(f"HP: {self.player.health}", "red", "black")
    #     self.hpIndicator.rect.topright = self.inventoryButton.rect.bottomright

    #     #MAP UI
    #     self.lastClickpos: None | tuple[int, int] = None

    #     self.lastClickedTile = (-1, -1)
    #     self.clickedTileMarker = load_image("moveIndicator1.png") #perhaps rename to moveTileMarker
    #     self.shouldDrawMoveMarker = False

    #     self.crossHairMarker = load_image("crossHair1.png")
    #     self.shouldDrawCrossHairMarker = False
    #     #self.crossHairMarker[0]
    #     self.interactables = interactables # check to see if I should use sprite groups instead or something
    #         #my current thinking is that I will check clicks to see if they are on something in the interactables list, and if they are, then I will check to see if that enemy is interactable and what it's interaction methods are BTW ALT + Z TOGGLES LINE WRAPPING. USEFUL FOR COMMENTS LIKE THIS

    #     self.UIelements.add((self.turnIndicator, self.actionPointsIndicator, self.inventoryButton, self.nextTurnButton, self.hpIndicator))

    # def drawUI(self):
    #     '''
    #     draws basic turn ui onto the screen
    #     '''
    #     ####NEW WAY OF DRAWING WITH GROUPS instead of manual blits
    #     self.UIelements.draw(self.game.screen)

    #     #if the player has clicked on a tile show that
    #     if self.shouldDrawMoveMarker:
    #         self.game.screen.blit(*self.clickedTileMarker) #star unpacks tuple into arguments (in case i forget)
    #     if self.shouldDrawCrossHairMarker:
    #         self.game.screen.blit(*self.crossHairMarker)
    
    # def process(self, events: list[pg.event.Event]):
    #     for event in events:
    #         if event.type == pg.MOUSEBUTTONDOWN and event.button == pg.BUTTON_LEFT:
    #             self.handleClick(event.pos)
    #         elif event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
    #             print("testing state transitions")
    #             self.game.changeState(StartMenu(self.game))
    
    # def resolveAttack(self, attacker, target, weapon):
    #     #get the cover rects
    #     fullCover = self.tileMap.getFullCover()
    #     halfCover = self.tileMap.getHalfCover()
    #     #cast line between attacker and target
    #     attackLine = (), ()
    #     #check range for max range and roll thresholds
    #     #roll die
    #     #resolve effects, deal damage, reduce ammo or whatever, play particle effect
    #     pass
    # def handleClick(self, pos: tuple[float, float]):
    #     self.shouldDrawCrossHairMarker = False

    #     self.shouldDrawMoveMarker = False

    #     ####HANDLE UI CLICKS
    #     if self.nextTurnButton.rect.collidepoint(pos):
    #         #do the next turn thing
    #         self.nextTurn()
    #         return True
    #     if self.inventoryButton.rect.collidepoint(pos):
    #         self.game.enterState(InventoryMenu(self.game, self.tileMap, self.player, self.enemies, self.friendlies, self.interactables))
        
    #     if self.turnTakers[self.currentTurn] != self.player: return False
    #     ####HANDLE CLICKS THAT HAPPEN OVER MAP
    #     elif self.tileMap.rect.collidepoint(pos):
    #         ####CHECK CLICKS ON interactables
    #         clickedTile = self.tileMap.getTile(pos)
    #         for enemy in self.enemies:
    #             if enemy.tileLocation == clickedTile:
    #                 #Handle confirmed click
    #                 if self.lastClickedTile == clickedTile and self.player.actionPoints >= 2: 
    #                     print("blamo, confirm clicked on an enemy")
    #                     self.player.actionPoints -= 2
    #                     return True
    #                 self.shouldDrawCrossHairMarker = True
    #                 print("enemy was clicked")
    #                 self.crossHairMarker[1].topleft = self.tileMap.tileToPixel(self.tileMap.getTile(pos))
    #                 self.lastClickedTile = clickedTile
    #                 return True
            
    #         ####CHECK CLICKS ONLY ON MAP
    #         distance = self.tileMap.calcDistance(self.player.tileLocation, clickedTile)
    #         print(f"detected map click on tile {distance} units from player")
    #         canMove = self.tileMap.calcDistance(self.player.tileLocation, clickedTile) <= self.player.actionPoints * 3

    #         if clickedTile == self.lastClickedTile and canMove:
    #             self.player.moveTo(clickedTile) #execute action
    #             self.player.actionPoints -= math.ceil(distance / 3) #incur cost
    #             print("confirmed click to move")
    #         elif not canMove:
    #             print("too far buckaroo")
    #         elif clickedTile != self.lastClickedTile:
    #             self.clickedTileMarker[1].topleft = self.tileMap.tileToPixel(clickedTile)
    #             self.shouldDrawMoveMarker = True
            
    #         self.lastClickedTile = clickedTile
    #         return True


    # def updateActionPoints(self, newVal):
    #     self.actionPointsIndicator.updateText(f"Action Points {newVal}")

    # def nextTurn(self):
    #     print(f"self.turnTakers is {self.turnTakers}")
    #     print(f"old turnIdx was {self.currentTurn}")
    #     self.currentTurn = (self.currentTurn + 1) % len(self.turnTakers)
    #     print(f"new turnIdx is {self.currentTurn}")
    #     self.turnTakers[self.currentTurn].actionPoints = 3

    # def isPlayerTurn(self):
    #     return self.player == self.turnTakers[self.currentTurn]
    
    # def update(self):
    #     '''Handles the processing of things that occur "automatically" such as transitions between frames of animations or updates to physics based on velocity. AFAIK I won't be doing much in here because most things are handled with rules or from the UI. I might be wrong though'''
    #     if self.player.health == 0:
    #         print("GAME OVER")
    #     self.actionPointsIndicator.updateText(f"Action Points: {self.player.actionPoints}")
    #     self.hpIndicator.updateText(f"HP: {self.player.health}", "red", "black")

    #     if self.turnTakers[self.currentTurn] != self.player:
    #         self.turnTakers[self.currentTurn].takeTurn(self.tileMap, self.player)
    #         self.nextTurn()

    # def render(self):
    #         self.game.screen.fill("black")

    #         self.tileMap.draw(self.game.screen)
    #         #bigMap.drawDebug(screen)
    #         self.tileMap.drawAdjTile(self.game.screen, self.player.tileLocation)

    #         for actor in self.turnTakers:
    #             actor.rect.topleft = self.tileMap.tileToPixel(actor.tileLocation)
    #             actor.draw(self.game.screen)

    #         self.drawUI()


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
    