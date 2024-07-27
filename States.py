import math

from pygame.sprite import AbstractGroup
from utility import *
from Player import *
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
    '''
    free roam tile map exploration. you walk where you click and you can interact with characters and items in this mode. triggers Turn control when within range of enemy. will also be able to trigger fishing later
    '''
    def __init__(self, game, tileMap: GameMap, player: Player, enemies: list, friendlies: list, interactables: list) -> None:
        self.game = game

        self.tileMap = tileMap
        self.player = player
        self.enemies = enemies
        self.friendlies = friendlies
        self.turnTakers = [self.player]
        for turnTaker in enemies:
            self.turnTakers.append(turnTaker)
        
        #MENU UI
        self.UIelements = pg.sprite.Group()

        self.inventoryButton = Button("Inventory")
        self.inventoryButton.rect.topright = self.game.screen.get_rect().topright

        self.hpIndicator = Button(f"HP: {self.player.health}", "red", "black")
        self.hpIndicator.rect.topright = self.inventoryButton.rect.bottomright

        self.interactables = interactables # check to see if I should use sprite groups instead or something

        self.UIelements.add((self.inventoryButton, self.hpIndicator))

        #movement handling variables
        self.path : deque = deque()
        self.moveTarget: None | tuple[int, int] = None

        #move animation variables
        self.animProgress = 0 
        self.timePerTile = 250 #in ms

    
    def process(self, events: list[pg.event.Event]):
        for event in events:
            if event.type == pg.MOUSEBUTTONDOWN and event.button == pg.BUTTON_LEFT:
                if self.tileMap.rect.collidepoint(event.pos):
                    self.moveTarget = self.tileMap.getTile(event.pos)
                    print("clicked on map and got path")
                else:
                    print("didn't click on map")

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
            # #THE GIST: we make a square around the grenade, the width of the square is the diameter of the blast (2 * blast radius)
            # #for each tile in this square we raycast to it and check 2 things:
            #     #we check if the tile's center is in the blast radius
            #     #we check if the ray intersects cover
            #     #apply the effects of any cover hit by the raycast and then carry out the damage (assuming the center was within the blast radius)
            
            # #get the bounding tile of the square
            # topLeftLimit = (self.centerTile[0] - self.tileBlastRadius , self.centerTile[1] - self.tileBlastRadius)
            # bottomRightLimit = (self.centerTile[0] + self.tileBlastRadius, self.centerTile[1] + self.tileBlastRadius)

            # #check every tile in the bounding square
            # for row in range(topLeftLimit[0], bottomRightLimit[0]):
            #     for col in range(topLeftLimit[1], bottomRightLimit[1]):
            #         #check that the tile is on the board (not too close to edge or corner)
            #         if row < 0 or col < 0: continue
            #         if row > self.tileMap.height - 1: continue
            #         if col > self.tileMap.width - 1: continue

            #         #now we make the ray (technically a segment, shut up)
            #         ray = (self.tileMap.tileToPixel(self.centerTile, center=True), self.tileMap.tileToPixel((row, col), center=True))
            #         #check the ray for intersections

            #         #check the distance of the ray

        def render(self):
            self.game.screen.fill("black")
            self.tileMap.draw(self.game.screen)
            for enemy in self.turnTakers:
                enemy.rect.topleft = self.tileMap.tileToPixel(enemy.tileLocation)
                self.game.screen.blit(enemy.image, enemy.rect)
            #self.drawRaysDebug()
            self.drawDebugAffectedSquares()

class ExplorationTurnTransition(State):
    def __init__(self, game, tileMap: GameMap, player: Player, enemies: list, friendlies: list, interactables: list):
        self.game = game

        self.tileMap = tileMap
        self.player = player
        self.enemies = enemies
        self.friendlies = friendlies
        self.interactables = interactables
    
        self.textBanner = Button("Encounter Started", "white", "black", self.game.screen.get_rect().height // 7)
        self.textBanner.rect.centerx = self.game.screen.get_rect().centerx
        self.textBanner.rect.bottom = 0

        self.bgImage = self.game.screen.copy()
        #this is basic kinematics, however I want there to be "energy dissipated" during the bounce, so I need a second equation for after the bounce
        self.textVelocity = 1300 #velocity is down in pixel/sec
        self.textAcc = 900 # pixel/sec^2
        self.downEqn = lambda x : 0.5 * math.pow(x, 2)*self.textAcc + self.textVelocity*x + 0 #again, basic kinematic equation
        self.velocityImpact = 0
        self.upEqn = lambda x : 0.5 * math.pow(x, 2)*self.textAcc + (self.velocityImpact * -0.6)*x + self.game.screen.get_rect().height #basic kinematic equation, but with the velocity at impact reversed and diminished

        #animation variables
        self.timer = 0
        self.bounced = False
        self.returned = False
        #should take one second to reach the top
    def process(self, events: list[pg.event.Event]):
        pass

    def update(self):
        # # fill this in with a quadratic equation -1(t-0)(t-3) with a multiplier out front to get the height of the arc to be right
        # self.textBanner.rect.bottom += self.textVelocity * (self.game.clock.get_time() / 1000)
        # self.textVelocity += self.textAcc * (self.game.clock.get_time() / 1000)
        # if self.textBanner.rect.bottom >= self.game.screen.get_rect().bottom:
        #     self.textBanner.rect.bottom = self.game.screen.get_rect().bottom
        #     self.textVelocity = (self.textVelocity * -0.6)
        #     self.bounced = True
        # if self.bounced and self.textBanner.rect.top <= 0:
        #     self.textBanner.rect.top = 0


        self.timer += self.game.clock.get_time()
        if self.returned:
            if self.timer >= 2000:
                self.game.enterState(TurnControl(self.game, self.tileMap, self.player, self.enemies, self.friendlies, []))
                pass#print("go to next state")
            return
        if not self.bounced:
            self.textBanner.rect.bottom = int(self.downEqn(self.timer / 1000))
            if self.textBanner.rect.bottom >= self.game.screen.get_rect().height:
                self.bounced = True
                self.velocityImpact = self.textVelocity + ((self.timer / 1000)* self.textAcc)
                self.timer = 0
        else:
            self.timer += self.game.clock.get_time()
            self.textBanner.rect.bottom = int(self.upEqn(self.timer / 1000))
            if self.textBanner.rect.top <= 0 + 30:
                self.returned = True
                self.timer = 0
    
    def render(self):
        self.game.screen.blit(self.bgImage, (0,0))
        self.game.screen.blit(self.textBanner.image, self.textBanner.rect)


class TurnControl(State):
    ## substates should just be able to use the State class. Im not sure how arbitrary nesting of code will work. If I was just doing one level deep I would make an enum and use switch case for the logic but that doesn't nest well. you end up with a million switch cases nested. I want something that can nest arbitrarily but that is also lightweight. I would just use the state like I have right now, but the switching makes it really clunky. I also don't know how to do persistent state.
    '''Does the turn based tactical handling like dnd encounters. Not exclusively combat. there are plans for negotiating and escaping.'''
    def __init__(self, game, tileMap: GameMap, player: Player, enemies: list, friendlies, interactables: list) -> None:
        self.game = game

        self.tileMap = tileMap
        self.player = player
        self.enemies = enemies
        self.friendlies = friendlies
        self.turnTakers = [self.player]
        for turnTaker in enemies:
            self.turnTakers.append(turnTaker)
        
        self.currentTurn = 0
        
        #MENU UI
        self.UIelements = pg.sprite.Group()

        self.nextTurnButton = Button("End Turn")
        self.nextTurnButton.rect.bottomleft = game.screen.get_rect().bottomleft

        self.turnIndicator = Button("Player's Turn")
        print(f"turn indicator is this many pixels wide:  {self.turnIndicator.image.get_width()}")

        self.turnIndicator.rect.topright = game.screen.get_rect().topright
        self.actionPointsIndicator = Button("Action Points: 3")
        self.actionPointsIndicator.rect.bottomright = game.screen.get_rect().bottomright

        self.inventoryButton = Button("Inventory")
        self.inventoryButton.rect.topright = self.turnIndicator.rect.bottomright

        self.hpIndicator = Button(f"HP: {self.player.health}", "red", "black")
        self.hpIndicator.rect.topright = self.inventoryButton.rect.bottomright

        #MAP UI
        self.lastClickpos: None | tuple[int, int] = None

        self.lastClickedTile = (-1, -1)
        self.clickedTileMarker = load_image("moveIndicator1.png") #perhaps rename to moveTileMarker
        self.shouldDrawMoveMarker = False

        self.crossHairMarker = load_image("crossHair1.png")
        self.shouldDrawCrossHairMarker = False
        #self.crossHairMarker[0]
        self.interactables = interactables # check to see if I should use sprite groups instead or something
            #my current thinking is that I will check clicks to see if they are on something in the interactables list, and if they are, then I will check to see if that enemy is interactable and what it's interaction methods are BTW ALT + Z TOGGLES LINE WRAPPING. USEFUL FOR COMMENTS LIKE THIS

        self.UIelements.add((self.turnIndicator, self.actionPointsIndicator, self.inventoryButton, self.nextTurnButton, self.hpIndicator))

    def drawUI(self):
        '''
        draws basic turn ui onto the screen
        '''
        ####NEW WAY OF DRAWING WITH GROUPS instead of manual blits
        self.UIelements.draw(self.game.screen)

        #if the player has clicked on a tile show that
        if self.shouldDrawMoveMarker:
            self.game.screen.blit(*self.clickedTileMarker) #star unpacks tuple into arguments (in case i forget)
        if self.shouldDrawCrossHairMarker:
            self.game.screen.blit(*self.crossHairMarker)
    
    def process(self, events: list[pg.event.Event]):
        for event in events:
            if event.type == pg.MOUSEBUTTONDOWN and event.button == pg.BUTTON_LEFT:
                self.handleClick(event.pos)
            elif event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                print("testing state transitions")
                self.game.changeState(StartMenu(self.game))
    
    def handleClick(self, pos: tuple[float, float]):
        self.shouldDrawCrossHairMarker = False

        self.shouldDrawMoveMarker = False

        ####HANDLE UI CLICKS
        if self.nextTurnButton.rect.collidepoint(pos):
            #do the next turn thing
            self.nextTurn()
            return True
        
        if self.turnTakers[self.currentTurn] != self.player: return False
        ####HANDLE CLICKS THAT HAPPEN OVER MAP
        elif self.tileMap.rect.collidepoint(pos):
            ####CHECK CLICKS ON interactables
            clickedTile = self.tileMap.getTile(pos)
            for enemy in self.enemies:
                if enemy.tileLocation == clickedTile:
                    #Handle confirmed click
                    if self.lastClickedTile == clickedTile and self.player.actionPoints >= 2: 
                        print("blamo, confirm clicked on an enemy")
                        self.player.actionPoints -= 2
                        return True
                    self.shouldDrawCrossHairMarker = True
                    print("enemy was clicked")
                    self.crossHairMarker[1].topleft = self.tileMap.tileToPixel(self.tileMap.getTile(pos))
                    self.lastClickedTile = clickedTile
                    return True
            
            ####CHECK CLICKS ONLY ON MAP
            distance = self.tileMap.calcDistance(self.player.tileLocation, clickedTile)
            print(f"detected map click on tile {distance} units from player")
            canMove = self.tileMap.calcDistance(self.player.tileLocation, clickedTile) <= self.player.actionPoints * 3

            if clickedTile == self.lastClickedTile and canMove:
                self.player.moveTo(clickedTile) #execute action
                self.player.actionPoints -= math.ceil(distance / 3) #incur cost
                print("confirmed click to move")
            elif not canMove:
                print("too far buckaroo")
            elif clickedTile != self.lastClickedTile:
                self.clickedTileMarker[1].topleft = self.tileMap.tileToPixel(clickedTile)
                self.shouldDrawMoveMarker = True
            
            self.lastClickedTile = clickedTile
            return True


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
        self.actionPointsIndicator.updateText(f"Action Points: {self.player.actionPoints}")
        self.hpIndicator.updateText(f"HP: {self.player.health}", "red", "black")

        if self.turnTakers[self.currentTurn] != self.player:
            self.turnTakers[self.currentTurn].takeTurn(self.tileMap, self.player)
            self.nextTurn()

    def render(self):
            self.game.screen.fill("black")

            self.tileMap.draw(self.game.screen)
            #bigMap.drawDebug(screen)
            self.tileMap.drawAdjTile(self.game.screen, self.player.tileLocation)

            for actor in self.turnTakers:
                actor.rect.topleft = self.tileMap.tileToPixel(actor.tileLocation)
                actor.draw(self.game.screen)

            self.drawUI()


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
                #self.game.stateStack.pop()
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