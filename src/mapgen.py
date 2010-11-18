import sys

class mapgen_class:
    floor = 0
    wall = 1
    map = []

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.buildGrid(self.floor)
        self.fillGrid()
        
    #fill the map with 1 tile type
    def buildGrid(self, tile):
        for i in range(self.width):
            self.map.append([])
            for j in range(self.height):
                self.map[i].append(tile)
                                            
    #print the map out in a 2d style
    #TODO this is very slow, but only here for debugging
    #until we get an observer up, try to find a better way for the observer
    def printGrid(self, playerlist):
        for player in playerlist:
            self.map[player.x][player.y] = 2

        for i in self.map:
            print i

        for player in playerlist:
            self.map[player.x][player.y] = 0

    #create a matrix of the local map
    def localGrid(self, player, radius):
        #get a center position, ajust for map edges
        #TODO clean this bit up
        if self.width < radius*2 or self.height < radius*2:
            print "ERROR: Attempting to get localgrid 'radius' is greater than map size"
            sys.exit()            
        gridx = player.x-radius
        gridy = player.y-radius
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
        
    #add walls to the map
    def fillGrid(self):
        for x in range(self.width):
            self.map[x][0] = self.wall 
            self.map[x][self.height-1] = self.wall
            
            for y in range(self.height):
                self.map[0][y] = self.wall
                self.map[self.width-1][y] = self.wall

    #return if the location is 'walkable'
    def isWalkable(self, x, y):
        if x > self.width-1 or x < 0 or y > self.height-1 or y < 0:
            return 0

        if self.map[x][y] == self.floor:
            return 1
        return 0
