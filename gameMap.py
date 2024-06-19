from utility import *

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
                newImgTuple = load_image(line[1], scale=3)
                #store image and imagerect in the map at the character specified
                textureMap[line[0]] = newImgTuple
                navMap[line[0]] = line[2]
            # contains map of {tileSymbol -> (imageSurface, imageRect)}
            self.textureMap = textureMap
            # contains map from {tileSymbol -> (yes/no navigable)}
            self.navMap = navMap

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
            self.tileMap = grid
            # get height and width from the tilemap we just made
            print("we still need to validate csv inputs. height, width, and map may be broken")
            self.height = len(self.tileMap)
            self.width = len(self.tileMap[0])

        print(self.tileMap)
        print(self.textureMap)

        '''
        create the adjacency list
        '''
        self.adjList = {}
        for rowNum, row in enumerate(self.tileMap):
            for colNum, tile in enumerate(row):
                tileAdjacencies = [] # this dict maps from coord tuple, to list of adjacencies for each tile.
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