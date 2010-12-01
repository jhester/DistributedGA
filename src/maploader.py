import sys
import utils

class mapLoader_class:
    def __init__(self, map_file=''):
        if map_file == '':
            print "No map file name supplied with map_class"
            sys.exit()
            
        self.map = utils.load_map('level1_col.lvl')
        self.height = len(self.map)-1
        self.width = len(self.map[0])-1

        self.floor = 0

    #create a matrix of the local map
    def localGrid(self, xpos, ypos, radius):
        #get a center position, ajust for map edges
        #TODO clean this bit up
        if self.width < radius*2 or self.height < radius*2:
            print "ERROR: Attempting to get localgrid 'radius' is greater than map size"
            sys.exit()
            
        gridx = xpos-radius
        gridy = ypos-radius
        if gridx < 0:
            gridx = 0
        if gridy < 0:
            gridy = 0
        if gridx+radius*2 > self.width-1:
            gridx = self.width-1-radius*2
        if gridy+radius*2 > self.height-1:
            gridy = self.height-1-radius*2
        
        localmap = []
        for x in range(radius*2):
            localmap.append([])
            for y in range(radius*2):
                localmap[x].append(self.map[gridx+x][gridy+y])
        return localmap
        
    #return if in index range
    def isWithin(self, x, y):
        if x > self.width or x < 0 or y > self.height or y < 0:
            return 0
        return 1

    #return if the location is 'walkable'
    def isWalkable(self, x, y):
        if not self.isWithin(x,y):
            return 0

        if self.map[y][x] == self.floor:
            return 1
        return 0

    #print the map out in a 2d style
    #TODO this is very slow, but only here for debugging
    #until we get an observer up, try to find a better way for the observer
    def printGrid(self, playerlist):
        for (x, y) in playerlist:
            self.map[y][x] = 2
            
        for i in self.map:
            line = ""
            for j in i:
                if j == 0:
                    line += "\033[30m" #black
                elif j == 2:
                    line += "\033[31m" #red
                    
                line += " " + str(j)
                line += "\033[0m" #white
            print line

        for (x, y) in playerlist:
            self.map[y][x] = 0
                            
