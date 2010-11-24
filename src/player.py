#python library
import random

#our library
from mapgen import mapgen_class
from constant import *

class player_class:
    def __init__(self, x, y, id):
        self.x = x
        self.y = y
        self.id = id

    #update the players position based on a direction
    def moveByDirection(self, direction, map):
        nextposx = self.x+constant_class.directionconvert[direction][0]
        nextposy = self.y+constant_class.directionconvert[direction][1]

        #make sure our new position is reachable        
        if map.isWalkable(nextposx,nextposy):
            self.x = nextposx
            self.y = nextposy

#class to manage all players, creation/deletion etc
class playerManager_class:
    def __init__(self, map):
        self.playerdict = {}
        self.map = map
        self.prevID = 0

    #creates and returns a new player object
    #also store this player in this manager
    def addPlayer(self):
        #start by finding a walkable position
        while True:
            x = int(random.random()*self.map.width)
            y = int(random.random()*self.map.height)        
            if self.map.isWalkable(x,y):
                break

        #create the player at this position
        self.prevID += 1
        newplayer = player_class(x,y,self.prevID)
        self.playerdict[self.prevID] = newplayer
        
        return newplayer

    def movePlayerDir(self, player, direction):
        player.moveByDirection(direction, self.map)

    #return the map surrounding the player
    def getLocalGrid(self, player):
        return self.map.localGrid(player, 5)

    #return a dictionary of player IDs and what has changed
    def getDictionary(self):
        #we should be building a dictionary of player IDs that
        #have changed ONLY (much smaller)
        return self.playerdict

    def mergeDictionary(self, dict):
        for (id, player) in dict.items():
            self.playerdict[id] = player
            
