import sys
import random
import time
import os

class mapgen_class:
    floor = 0
    wall = 1
    map = []
    fillPrecentage = 0.75

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.totalArea = width*height
        self.buildGrid(self.wall)
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
        for (x, y) in playerlist:
            print "Player at:" + str((x,y))
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
        
    #add floor to the map
    def fillGrid(self):
        #create an initial room
        x = int(random.random()*self.width)
        y = int(random.random()*self.height)
        w = int(random.random()*15)+5
        h = int(random.random()*15)+5
        floorArea = 0
        
        #fill it
        for j in range(w):
            for k in range(h):
                if self.isWithin(j+x,k+y):
                    if not self.map[j+x][k+y] == self.floor:
                        self.map[j+x][k+y] = self.floor
                        floorArea += 1
                    
        #'cut' away rooms until we reach our precentage of floor space
        while (floorArea/float(self.totalArea)) < self.fillPrecentage:
            #room init
            x = int(random.random()*self.width)
            y = int(random.random()*self.height)
            w = int(random.random()*15)+5
            h = int(random.random()*15)+5

            #fill it
            for j in range(w):
                for k in range(h):                    
                    if self.isWithin(j+x,k+y):
                        if not self.map[j+x][k+y] == self.floor:
                            self.map[j+x][k+y] = self.floor
                            floorArea += 1
                        
            #expand the room until you make contact with another room
            #this is so we don't have isloated rooms
            w -= 1
            h -= 1
            connected = False
            while not connected:
                #expand the borders
                w += 2
                h += 2
                x -= 1
                y -= 1
                
                #fill in just the new edges looking for
                #a floor tile that is already down
                for j in range(w+1):
                    if self.isWithin(j+x, y):
                        if self.map[j+x][y] == self.floor:
                            connected = True
                        else:
                            self.map[j+x][y] = self.floor
                            floorArea += 1
                            
                    if self.isWithin(j+x, y+h):
                        if self.map[j+x][y+h] == self.floor:
                            connected = True
                        else:
                            self.map[j+x][y+h] = self.floor
                            floorArea += 1
                            
                for k in range(1,h):
                    if self.isWithin(x, k+y):
                        if self.map[x][k+y] == self.floor:
                            connected = True
                        else:
                            self.map[x][k+y] = self.floor
                            floorArea += 1

                    if self.isWithin(x+w, k+y):
                        if self.map[x+w][k+y] == self.floor:                        
                            connected = True
                        else:
                            self.map[x+w][k+y] = self.floor
                            floorArea += 1

            print (floorArea,float(self.totalArea),floorArea/float(self.totalArea))

        for x in range(self.width):
            self.map[x][0] = self.wall 
            self.map[x][self.height-1] = self.wall
            
        for y in range(self.height):
            self.map[0][y] = self.wall
            self.map[self.width-1][y] = self.wall

        
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

