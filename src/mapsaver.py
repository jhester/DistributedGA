import sys
import random
import time
import os
import utils

class mapgen_class:
    floor = 0
    wall = 1
    fillPrecentage = 0.75

    def __init__(self, width, height, maplvl):
        self.maplvl = maplvl
        self.width = width
        self.height = height
        self.totalArea = width*height
        self.map = []
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
    def printGrid(self):
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
    
    #add floor to make rooms TODO CLEAN UGLY
    def fillGrid(self):
        #create a initial room
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
                        if self.isFloor(j+x,y) == 1:
                            connected = True
                        else:
                            self.map[j+x][y] = self.floor
                            floorArea += 1
                            
                    if self.isWithin(j+x, y+h):
                        if  self.isFloor(j+x,y+h) == 1:
                            connected = True
                        else:
                            self.map[j+x][y+h] = self.floor
                            floorArea += 1
                            
                for k in range(1,h):
                    if self.isWithin(x, k+y):
                        if self.isFloor(x, k+y) == 1:
                            connected = True
                        else:
                            self.map[x][k+y] = self.floor
                            floorArea += 1

                    if self.isWithin(x+w, k+y):
                        if self.isFloor(x+w,k+y) == 1:                        
                            connected = True
                        else:
                            self.map[x+w][k+y] = self.floor
                            floorArea += 1

        for x in range(self.width):
            self.map[x][0] = self.wall 
            self.map[x][self.height-1] = self.wall
            
        for y in range(self.height):
            self.map[0][y] = self.wall
            self.map[self.width-1][y] = self.wall

    def isFloor(self, x, y):
        if self.map[x][y] == self.floor:
            return True
        return False
        
    #return if in index range
    def isWithin(self, x, y):
        if x > self.width-1 or x < 0 or y > self.height-1 or y < 0:
            return 0
        return 1

    def save(self):
        pass

width = int(raw_input("Input width: "))
height = int(raw_input("Input height: "))
lvl = int(raw_input("Input lvl: "))

yn = 'n'
while not yn == 'y':
    map = mapgen_class(width, height, lvl)
    map.printGrid()

    yn = raw_input("Acceptable? (y/n): ")

map.save()
