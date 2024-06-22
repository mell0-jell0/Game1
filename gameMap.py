from collections import deque
from utility import *

IMG_SCALE = 3
DEBUG = True

class GameMap:
    def __init__(self, manifestName: str, mapName: str):
        '''
        reads in list of number that correspond to different tiles
        creates one image for each tile type
        maps '''
        manifestPath = os.path.join(data_dir, manifestName)
        with open(manifestPath) as fileIn:
            lines = fileIn.readlines()
            textureMap = {}
            navMap = {}
            for line in lines:
                line = line.strip('\n')
                line = line.split(',')
                #load image and imagerect
                newImgTuple = load_image(line[1], scale=IMG_SCALE)
                self.TILE_WIDTH = newImgTuple[1].width
                #store image and imagerect in the map at the character specified
                textureMap[line[0]] = newImgTuple
                navMap[line[0]] = line[2]
            # contains map of {tileSymbol -> (imageSurface, imageRect)}
            self.textureMap: dict[str, tuple[pg.Surface, pg.Rect]] = textureMap
            # contains map from {tileSymbol -> (yes/no navigable)}
            self.navMap: dict[str, str] = navMap

        '''
        takes file name and loads csv map into grid
        '''
        mapPath = os.path.join(data_dir, mapName)
        with open(mapPath) as file_in:
            grid = []
            for line in file_in.readlines():
                line = line.strip('\n')
                line = line.split(",")
                grid.append(line)
            # contains grid of all the symbols in the map
            self.tileMap: list[list[str]] = grid
            # get height and width from the tilemap we just made
            print("we still need to validate csv inputs. height, width, and map may be broken")
            self.height: int = len(self.tileMap)
            self.width: int = len(self.tileMap[0])

        print(self.tileMap)
        print(self.textureMap)

        '''
        create the adjacency list
        '''
        self.adjList: dict[tuple[int, int], list[tuple[int, int]] ] = {}
        for rowNum, row in enumerate(self.tileMap):
            for colNum, tile in enumerate(row):
                tileAdjacencies: list[tuple[int, int]] = [] # this dict maps from coord tuple, to list of adjacencies for each tile.
                if navMap[tile] == "no": # break if tile non navigable
                    self.adjList[(rowNum, colNum)] = tileAdjacencies
                    continue
                if rowNum > 0:
                        if navMap[self.tileMap[rowNum-1][colNum]] == "yes":
                            tileAdjacencies.append((rowNum-1, colNum))
                if rowNum < self.height - 1: # remember minus one, it cannot be the last tile must be second to last
                        if navMap[self.tileMap[rowNum+1][colNum]] == "yes":
                            tileAdjacencies.append((rowNum+1, colNum))
                if colNum > 0:
                        if navMap[self.tileMap[rowNum][colNum-1]] == "yes":
                            tileAdjacencies.append((rowNum, colNum-1))
                if colNum < self.width - 1:
                        if navMap[self.tileMap[rowNum][colNum+1]] == "yes":
                            tileAdjacencies.append((rowNum, colNum+1))
                self.adjList[(rowNum, colNum)] = tileAdjacencies
        print(self.adjList)
    
    
    def draw(self, screen: pg.Surface):
         '''
         takes pygame screen as parameter
         uses texturemap and tilemap to blit all tiles to screen
         '''
         for rowNum, row in enumerate(self.tileMap):
              for colNum, tile in enumerate(row):
                   pos = (colNum*self.TILE_WIDTH, rowNum*self.TILE_WIDTH)
                   screen.blit(self.textureMap[tile][0], pos)
    
    def drawDebug(self, screen: pg.Surface):
        #this is just a stopgap measure. Should not be loading images every call.
        redX = load_image("redX.png", scale=IMG_SCALE)
        greenMarker = load_image("greenMarker.png", scale=IMG_SCALE)

        for rowNum, row in enumerate(self.tileMap):
              for colNum, tile in enumerate(row):
                    pos = (colNum*self.TILE_WIDTH, rowNum*self.TILE_WIDTH)
                    if self.navMap[tile] == "no":
                        screen.blit(redX[0], pos)
                    elif self.navMap[tile] == "yes":
                        screen.blit(greenMarker[0], pos)
    
    def drawAdjTile(self, screen, tile: tuple[int, int]):
        greenMarker = load_image("greenMarker.png", scale=IMG_SCALE)
        for tile in self.adjList[tile]:
            screen.blit(greenMarker[0], (tile[1]*self.TILE_WIDTH, tile[0]*self.TILE_WIDTH))
    #write a bfs/dfs to find the shortest path to 1 points OR all points within a certain distance so that i can display them on screen
    
    def calcDistance(self, source: tuple[int, int], target: tuple[int, int]) -> int:
        toVisit = deque([source]) #basic bfs queue
        visited = set() #keep track of what we already visited
        parents = {} #track parent pointers for pathing later
        distance: dict[tuple[int, int], int] = {source: 0}

        while True:
            currTile = toVisit.pop() # get the next thing to visit
            for tile in self.adjList[currTile]: #update all the newly discovered tiles if applicable
                if tile not in visited:
                    parents[tile] = currTile
                    toVisit.appendleft(tile) #add the tile to the list if it hasn't been explored
                    distance[tile] = distance[currTile] + 1 #update the distance
            visited.add(currTile)
            if currTile == target: return distance[currTile]
# def readManifest(name) -> dict[str, tuple[pg.Surface, pg.Rect]]:
#     '''
#     reads in list of number that correspond to different tiles
#     creates one image for each tile type
#     maps '''
#     manifestPath = os.path.join(data_dir, name)
#     with open(manifestPath) as fileIn:
#         lines = fileIn.readlines()
#         tileMap = {}
#         for line in lines:
#             line = line.strip('\n')
#             line = line.split(',')
#             #load image and imagerect
#             newImgTuple = load_image(line[1], scale=3)
#             #store image and imagerect in the map at the character specified
#             tileMap[line[0]] = newImgTuple
#         return tileMap


# def loadMap(name):
#     '''
#     takes file name and loads csv map into grid
#     '''
#     mapPath = os.path.join(data_dir, name)
#     with open(mapPath) as file_in:
#         grid = []
#         for line in file_in.readlines():
#             line = line.strip('\n')
#             line = line.split(",")
#             grid.append(line)
#     return grid