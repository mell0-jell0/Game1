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
    # class pathWalk:
    #     def __init__(self, player, target, tileMap: GameMap):
    #         self.player = player
    #         self.target = target
    #         self.tilepath = tileMap.calcDistance
    

    def __init__(self, game, tileMap: GameMap, player: Player, otherTurnTakers: list, entities: list) -> None:
        self.game = game

        self.tileMap = tileMap
        self.player = player
        self.turnTakers = [self.player]
        for turnTaker in otherTurnTakers:
            self.turnTakers.append(turnTaker)
        
        #MENU UI
        self.UIelements = pg.sprite.Group()

        self.inventoryButton = Button("Inventory")
        self.inventoryButton.rect.topright = self.game.screen.get_rect().topright

        self.hpIndicator = Button(f"HP: {self.player.health}", "red", "black")
        self.hpIndicator.rect.topright = self.inventoryButton.rect.bottomright

        self.entities = entities # check to see if I should use sprite groups instead or something

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


class TurnControl(State):
    ## substates should just be able to use the State class. Im not sure how arbitrary nesting of code will work. If I was just doing one level deep I would make an enum and use switch case for the logic but that doesn't nest well. you end up with a million switch cases nested. I want something that can nest arbitrarily but that is also lightweight. I would just use the state like I have right now, but the switching makes it really clunky. I also don't know how to do persistent state.
    '''Does the turn based tactical handling like dnd encounters. Not exclusively combat. there are plans for negotiating and escaping.'''
    def __init__(self, game, tileMap: GameMap, player: Player, otherTurnTakers: list, entities: list) -> None:
        self.game = game

        self.tileMap = tileMap
        self.player = player
        self.turnTakers = [self.player]
        for turnTaker in otherTurnTakers:
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
        self.entities = entities # check to see if I should use sprite groups instead or something
            #my current thinking is that I will check clicks to see if they are on something in the entities list, and if they are, then I will check to see if that entity is interactable and what it's interaction methods are BTW ALT + Z TOGGLES LINE WRAPPING. USEFUL FOR COMMENTS LIKE THIS

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
            ####CHECK CLICKS ON ENTITIES
            clickedTile = self.tileMap.getTile(pos)
            for entity in self.entities:
                if entity.tileLocation == clickedTile:
                    #Handle confirmed click
                    if self.lastClickedTile == clickedTile and self.player.actionPoints >= 2: 
                        print("blamo, confirm clicked on an entity")
                        self.player.actionPoints -= 2
                        return True
                    self.shouldDrawCrossHairMarker = True
                    print("entity was clicked")
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
    def __init__(self, game, tileMap: GameMap, player: Player, otherTurnTakers: list, entities: list):
        self.game = game
        self.tileMap = tileMap
        self.player = player
        self.allTurnTakers = [player]
        for turnTaker in otherTurnTakers:
            self.allTurnTakers.append(turnTaker)
        self.entities = entities

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