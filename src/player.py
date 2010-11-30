#python library
import random
import struct
import pickle

#our library
from maploader import mapLoader_class
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

    #only pack the stuff that could change
    def packSmall(self):
        return (self.x, self.y)
    def loadSmall(self, data):
        self.x = data[0]
        self.y = data[1]

    #include AI (everything needed to recreate player)
    def packAll(self):
        return (self.x, self.y)
    def loadAll(self, data):
        self.x = data[0]
        self.y = data[1]    

class blockManager_class:
    def __init__(self, map):
        self.blocks = []
        self.blocksize = int(map.width/10) + 1

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

    def removePlayer(self, player):
        for (id, p) in dict.items():
            if p == player:
                del self.playerdict[id]
                pass

    def movePlayerDir(self, player, direction):
        player.moveByDirection(direction, self.map)

    #return a dictionary of player IDs and what has changed
    def getDictionary(self):
        #we should be building a dictionary of player IDs that
        #have changed ONLY (much smaller)
        return self.playerdict

    def mergeDictionary(self, dict):
        for (id, player) in dict.items():
            self.playerdict[id] = player    

    #convert our changed data to a string
    def packSmall(self):
        list = []
        for (id, player) in self.playerdict.items():
            list.append((id, player.packSmall()))
            
        return pickle.dumps(list)

    def loadSmall(self, str):
        list = pickle.loads(str)
        for (id, data) in list:
            if self.playerdict.has_key(id):
                self.playerdict[id].loadSmall(data)

            #new players should not appear unexpectedly
            else:
                self.playerdict[id] = player_class(0, 0, id)
                self.playerdict[id].loadSmall(data)
