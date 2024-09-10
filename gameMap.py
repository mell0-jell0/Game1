from collections import deque
from utility import *

IMG_SCALE = 3
DEBUG = False
tile = tuple[int, int]
tileId = str
class GameMap:
    '''
    reads the manifest and csv, loads in tile textures, and handles the underlying pathing of the map
    '''
    def __init__(self, manifestName: str, mapName: str):
        '''
        reads in list of number that correspond to different tiles
        creates one image for each tile type
        maps
        '''

        manifestPath = os.path.join(data_dir, manifestName)
        with open(manifestPath) as fileIn:
            lines = fileIn.readlines()
            textureMap = {}
            navMap = {}
            self.fullCoverTiles = set()
            self.halfCoverTiles = set()
            for line in lines:
                line = line.strip('\n')
                line = line.split(',')
                #load image and imagerect
                newImgTuple = load_image(line[1], scale=IMG_SCALE)
                self.TILE_WIDTH = newImgTuple[1].width

                #store image and imagerect in the map at the character specified
                textureMap[line[0]] = newImgTuple
                navMap[line[0]] = line[2]

                #get list of all cover tiles
                match line[3]:
                    case "full":
                        self.fullCoverTiles.add(line[0])
                    case "half":
                        self.halfCoverTiles.add(line[0])
                    case _:
                          pass
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
            self.tileMap: list[list[tileId]] = grid
            # get height and width from the tilemap we just made
            print("we still need to validate csv inputs. height, width, and map may be broken")
            self.height: int = len(self.tileMap)
            self.width: int = len(self.tileMap[0])

        self.rect = pg.Rect(0, 0, self.width * self.TILE_WIDTH, self.height * self.TILE_WIDTH) #rect containing map area
        if DEBUG:
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
        if DEBUG: print(self.adjList)

        self.offset: tuple[float, float] = (0,0)
    
    def getTile(self, pos) -> tuple[int, int]:
        '''
        takes an xy pixel position and returns a row,col of the tile that location resides in
        '''
        tileRow = (pos[1] + self.offset[1]) // self.TILE_WIDTH
        tileCol = (pos[0] + self.offset[0]) // self.TILE_WIDTH
        return (tileRow, tileCol)

    def tileToPixel(self, tileCoord, center=False) -> tuple[int, int]:
        '''
        takes a tile row,col and spits out a pixel x,y for the top left of that tile
        '''
        pixelx = (tileCoord[1] * self.TILE_WIDTH) - self.offset[0]
        pixely = (tileCoord[0] * self.TILE_WIDTH) - self.offset[1]
        if center:
            return (pixelx + (self.TILE_WIDTH//2), pixely + (self.TILE_WIDTH//2))
        else:
            return (pixelx, pixely)
    
    def draw(self, screen: pg.Surface):
         '''
         takes pygame screen as parameter
         uses texturemap and tilemap to blit all tiles to screen
         '''
         for rowNum, row in enumerate(self.tileMap):
              for colNum, tile in enumerate(row):
                   pos = (colNum*self.TILE_WIDTH - self.offset[0], rowNum*self.TILE_WIDTH - self.offset[1])
                   screen.blit(self.textureMap[tile][0], pos)
    
    def drawDebug(self, screen: pg.Surface):
        #this is just a stopgap measure. Should not be loading images every call.
        redX = load_image("redX.png", scale=IMG_SCALE)
        greenMarker = load_image("greenMarker.png", scale=IMG_SCALE)

        for rowNum, row in enumerate(self.tileMap):
              for colNum, tile in enumerate(row):
                    pos = (colNum*self.TILE_WIDTH - self.offset[0], rowNum*self.TILE_WIDTH - self.offset[1])
                    if self.navMap[tile] == "no":
                        screen.blit(redX[0], pos)
                    elif self.navMap[tile] == "yes":
                        screen.blit(greenMarker[0], pos)
    
    def drawAdjTile(self, screen, target: tuple[int, int]):
        greenMarker = load_image("greenMarker.png", scale=IMG_SCALE)
        for tile in self.adjList[target]:
            screen.blit(greenMarker[0], (tile[1]*self.TILE_WIDTH - self.offset[0], tile[0]*self.TILE_WIDTH - self.offset[1]))
    #write a bfs/dfs to find the shortest path to 1 points OR all points within a certain distance so that i can display them on screen
    
    def calcDistance(self, source: tuple[int, int], target: tuple[int, int]) -> int:
        '''
        uses BFS to calculate distance between source and target tiles. Handles non-navigable tiles but not cover yet
        returns 100 000 if no path is found'''
        toVisit = deque([source]) #basic bfs queue
        visited = set() #keep track of what we already visited
        parents = {} #track parent pointers for pathing later
        distance: dict[tuple[int, int], int] = {source: 0}

        while True:
            if len(toVisit) == 0: return 100000
            currTile = toVisit.pop() # get the next thing to visit
            for tile in self.adjList[currTile]: #update all the newly discovered tiles if applicable
                if tile not in visited:
                    parents[tile] = currTile
                    toVisit.appendleft(tile) #add the tile to the list if it hasn't been explored
                    distance[tile] = distance[currTile] + 1 #update the distance
            visited.add(currTile)
            if currTile == target: return distance[currTile]

    def getPath(self, source: tuple[int, int], target: tuple[int, int]) -> deque:
        '''
        Like calcDistance, uses bfs to find a shortest path between source and target. not accounting for cover/obstructions
        '''
        toVisit = deque([source]) #basic bfs queue
        visited = set() #keep track of what we already visited
        parents = {} #track parent pointers for pathing later
        distance: dict[tuple[int, int], int] = {source: 0}

        while True:
            if len(toVisit) == 0: return deque()
            currTile = toVisit.pop() # get the next thing to visit
            for tile in self.adjList[currTile]: #update all the newly discovered tiles if applicable
                if tile not in visited:
                    parents[tile] = currTile
                    toVisit.appendleft(tile) #add the tile to the list if it hasn't been explored
                    distance[tile] = distance[currTile] + 1 #update the distance
            visited.add(currTile)

            if currTile == target: #end protocol
                path = []
                currTile = target
                while True: #continually add tiles to path
                    path.append(currTile)
                    if currTile == source: break
                    currTile = parents[currTile]
                path.reverse()
                path = deque(path)
                #remove source from path
                path.popleft()
                return path
    
    def setOffset(self, newVal):
        self.offset = newVal
        self.rect.topleft = (-1*newVal[0], -1*newVal[1])
    
    def getFullCover(self) -> list[pg.rect.Rect]:
        '''
        yields a list of rects which are pieces of full cover
        '''
        outList = []
        for rowNum, row in enumerate(self.tileMap):
            for colNum, tile in enumerate(row):
                if tile in self.fullCoverTiles:
                    topleft = self.tileToPixel((rowNum, colNum))
                    width_Height = self.TILE_WIDTH, self.TILE_WIDTH
                    outList.append(pg.rect.Rect(topleft, width_Height))
        return outList
    
    def getHalfCover(self)  -> list[pg.rect.Rect]:
        '''
        yields a list of rects which are pieces of half cover
        '''
        outList = []
        for rowNum, row in enumerate(self.tileMap):
            for colNum, tile in enumerate(row):
                if tile in self.halfCoverTiles:
                    topleft = self.tileToPixel((rowNum, colNum))
                    width_Height = self.TILE_WIDTH, self.TILE_WIDTH
                    outList.append(pg.rect.Rect(topleft, width_Height))
        return outList
    
    def drawCoverDebug(self, screen):
        for rect in self.getFullCover():
            pg.draw.rect(screen, "red", rect)
        
        for rect in self.getHalfCover():
            pg.draw.rect(screen, "yellow", rect)
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