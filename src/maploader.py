import sys
import utils

class mapLoader_class:
    floor = 0
    wall = 1
    fillPrecentage = 0.75

    def __init__(self, map_file=''):
        if map_file == '':
            print "No map file name supplied with map_class"
            sys.exit()
            
        self.map = utils.load_map('level1_layer1.txt')
        self.height = len(self.map)
        self.width = len(self.map[0])

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
        if x > self.width-1 or x < 0 or y > self.height-1 or y < 0:
            return 0
        return 1

    #return if the location is 'walkable'
    def isWalkable(self, x, y):
        if not self.isWithin(x,y):
            return 0

        if self.map[x][y] == self.floor:
            return 1
        return 0

    #print the map out in a 2d style
    #TODO this is very slow, but only here for debugging
    #until we get an observer up, try to find a better way for the observer
    def printGrid(self, playerlist):
        for (x, y) in playerlist:
            self.map[x][y] = 2
            
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
            self.map[x][y] = 0
                            
