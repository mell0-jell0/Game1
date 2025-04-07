from States.states import *
from Entities import *

class InventoryMenu(State):
    def __init__(self, game, levelState: LevelState, activeContainer: Container | None = None):
        self.game = game
        self.levelState = levelState

        self.menuRegion = pg.rect.Rect(0, 0, game.WIN_WIDTH // 2, game.WIN_HEIGHT)
        self.menuRegion.topright = game.screen.get_rect().topright

        self.img = pg.Surface((self.menuRegion.width, self.menuRegion.height))
        self.img.fill((80,80,80))

        self.activePopup: Popup | None = None
        self.activeContainer = activeContainer
    
    def handleLeftClick(self, pos: tuple[float, float]):
        if self.activePopup != None:
            for button in self.activePopup.buttons:
                if button.rect.collidepoint(pos): button.callback()
                break
            self.activePopup = None
        else:
            #check for an item click
            for invItem in self.levelState.player.inventory:
                if invItem.rect.collidepoint(pos):
                    popupButtons = []
                    print("Should iterate over properties of weapon to generate more popup items")
                    if self.activeContainer != None:
                        def moveItem():
                            print("moving item to container")
                            self.levelState.player.inventory.remove(invItem)
                            self.activeContainer.items.append(invItem)

                        popupButtons.append(
                            Button(TextImg("Transfer").image, moveItem)
                        )

                    if isinstance(invItem, Useable):
                        popupButtons.append(
                            Button(TextImg("Use").image, lambda: invItem.use(self.game, self.levelState))
                        )

                    popupButtons.append(
                        Button(TextImg("Drop").image, lambda: print("Should drop weapon"))
                    )

                    self.activePopup = Popup(
                        popupButtons,
                        invItem.rect.center
                    )
                    self.activePopup.anchor = invItem.rect.center

        # process clicks in the container
        if self.activeContainer == None: return
        for item in self.activeContainer.items:
            if item.rect.collidepoint(pos):
                print("We should put item from container into inventory and go to next turn")
                self.levelState.player.inventory.append(item)
                self.activeContainer.items.remove(item)
                break
        

            
    def process(self, events: list[pg.event.Event]):
        for event in events:
            if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                print("should be popping inventory state from stack when state transitions are hooked up right")
                self.game.stateStack.pop()
            if event.type == pg.MOUSEBUTTONDOWN and event.button == pg.BUTTON_LEFT:
                self.handleLeftClick(event.pos)
                #default to popup


    def update(self):
        for entity in self.levelState.entities:
            entity.rect.topleft = self.levelState.tileMap.tileToPixel(entity.tileLocation)

        # Check for interactions with the container        
        if self.activeContainer == None: return

        yOffset = TextImg("test").image.get_rect().height
        for item in self.activeContainer.items:
            item.rect.topleft = (0, yOffset)
            yOffset += item.image.get_rect().height
        
        yOffset = TextImg("test").image.get_rect().height
        xVal = self.menuRegion.topleft[0]
        for item in self.levelState.player.inventory:
            item.rect.topleft = (xVal, yOffset)
            yOffset += item.image.get_rect().height

        if self.activePopup == None: return

        yOffset = 0 
        for button in self.activePopup.buttons:
            button.rect.topleft = self.activePopup.anchor[0], self.activePopup.anchor[1] + yOffset
            yOffset += button.rect.height
            
        

    def render(self):
        #render all the stuff from the background
        drawLevelState(self.levelState, self.game.screen)

        #render the menu background
        self.game.screen.blit(self.img, self.menuRegion)

        yDisplacement = 0

        equippedText = TextImg("Equipped", "Black", "Pink", size=20)
        equippedText.rect.topleft = self.menuRegion.topleft
        self.game.screen.blit(equippedText.image, equippedText.rect)
        yDisplacement+= equippedText.rect.height
        
        if self.levelState.player.equipped != None:
            self.levelState.player.equipped.rect.topleft = equippedText.rect.bottomleft
            self.game.screen.blit(self.levelState.player.equipped.image, self.levelState.player.equipped.rect)
            yDisplacement += self.levelState.player.equipped.rect.height
        
        #divider between equipped and rest
        lineWidth = 4
        yDisplacement += lineWidth // 2
        lineStart = (self.menuRegion.topleft[0], self.menuRegion.topleft[1] + yDisplacement)
        lineEnd = (lineStart[0] + self.menuRegion.width, lineStart[1])
        pg.draw.line(self.game.screen, "black", lineStart, lineEnd, 4)
        yDisplacement += lineWidth // 2


        #render the other items
        for item in self.levelState.player.inventory:
            if item == self.levelState.player.equipped: continue
            self.game.screen.blit(item.image, item.rect)
            # item.rect.topleft = (self.menuRegion.topleft[0], self.menuRegion.topleft[1] + yDisplacement)
            # yDisplacement += item.rect.height
            # self.game.screen.blit(item.image, item.rect)
        
        #render the active popup
        if self.activePopup != None:
            x,y = self.activePopup.anchor
            for button in self.activePopup.buttons:
                button.rect.topleft = x,y
                self.game.screen.blit(
                    button.image,
                    button.rect
                ) 
                y += button.image.get_rect().height

        # If interacting with container, draw its contents/menu
        if self.activeContainer == None: return
        containerRegion = pg.rect.Rect(0,
                                       0,
                                       self.game.screen.get_rect().width // 3,
                                       self.game.screen.get_rect().width // 3)
        pg.draw.rect(self.game.screen, "gray",containerRegion)
        text = TextImg("Container Contents")
        self.game.screen.blit(text.image, (0,0))

        for item in self.activeContainer.items:
            self.game.screen.blit(item.image, item.rect)
            print(f"Drawing item {item}") 
        # Draw UI when hovering over item in container
        text = TextImg("Take (1 Turn)", size=15)
        for item in self.activeContainer.items:
            if item.rect.collidepoint(pg.mouse.get_pos()):
                text.rect.topleft = item.rect.topright
                text.rect.centery = item.rect.centery
                self.game.screen.blit(text.image, text.rect)