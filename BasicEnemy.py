from utility import *
import random

class BasicEnemy(pg.sprite.Sprite):
    '''
    handles ai, health, stats, equipment, etc for basic enemies

    maybe i should make another class entity which this one inherits from. entity type could be a member of entity.
    '''
    def __init__(self, imgName):
        pg.sprite.Sprite.__init__(self) #call sprite constructor
        #rendering information
        self.image, self.rect = load_image(imgName)
        self.crossHair = load_image("crossHair1.png")

        #game logic information
        self.tileLocation = (4,4)
        self.eType = entityType.ENEMY
        self.engageRange = 10
        self.hp = 10

    def takeTurn(self, map, player):
        #loop to pick a random move by 1 square
        while True:
            axis = random.choice(('row', 'col'))
            direction = random.choice((-1, 1))
            if axis == "row":
                moveTarget = (self.tileLocation[0] + direction, self.tileLocation[1])
            elif axis == "col":
                moveTarget = (self.tileLocation[0], self.tileLocation[1] + direction)

            if map.calcDistance(self.tileLocation, moveTarget) <= 1:
                self.tileLocation = moveTarget
                break
        
        #loop to attack
        roll = random.randint(1,6)
        print(f"enemy rolled a {roll}")
        if roll == 6:
            print("it hits")
            player.health -= 2
        else:
            print("it misses")


    def onClick(self):
        pass
    # def draw(self, screen: pg.Surface, offset=(0,0)):
    #     screen.blit(self.image, self.rect)

    def draw(self, screen: pg.surface.Surface):
        screen.blit(self.image, self.rect)