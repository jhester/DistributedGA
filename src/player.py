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
        self.health = 100
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
        return (self.x, self.y, self.health)
    def loadSmall(self, data):
        self.x = data[0]
        self.y = data[1]
        self.health = data[2]

class blockManager_class:
    def __init__(self, map):
        self.blockWidth = 5

        self.mapsize = map.width
        self.blocksPerSide = int(map.width/self.blockWidth)
        self.blockCount = self.blocksPerSide*self.blocksPerSide
        self.blocks = []
        self.createBlocks()

    def createBlocks(self):
        for i in range(self.blockCount):
            self.blocks.append([])

    #move the player from one block to another
    def updatePlayer(self, oldx, oldy, player):
        oldBlock = self.getBlock(oldx, oldy)
        newBlock = self.getBlock(player.x, player.y)

        #if the player didn't change blocks we are done
        if oldBlock == newBlock:
            return

        #remove from old block, add to new block
        oldBlock.remove(player)
        newBlock.append(player)        

    def addPlayer(self, player):
        self.getBlock(player.x, player.y).append(player)

    def removePlayer(self, player):
        self.getBlock(player.x, player.y).remove(player)

    def getBlock(self, x, y):
        x = int(x/self.blockWidth)
        y = int(y/self.blockWidth)

        b = int(self.blocksPerSide)*y + x
        return self.blocks[b]

    def addBlock(self, blockX, blockY, list):
        if blockX >= self.blocksPerSide or blockX < 0 or blockY >= self.blocksPerSide or blockY < 0:
            return

        list.append(self.blocks[int(self.blocksPerSide)*blockY + blockX])
    
    def getSurroundingBlocks(self, x, y):
        x = int(x/self.blockWidth)
        y = int(y/self.blockWidth)

        #add blocks to our list if they exist
        list = []
        self.addBlock(x,y,list)
        self.addBlock(x+1,y,list)
        self.addBlock(x,y+1,list)
        self.addBlock(x-1,y,list)
        self.addBlock(x,y-1,list)
        self.addBlock(x+1,y+1,list)
        self.addBlock(x-1,y-1,list)
        self.addBlock(x+1,y-1,list)
        self.addBlock(x-1,y+1,list)

        return list
        
#class to manage all players, creation/deletion etc
class playerManager_class:
    def __init__(self, map):
        self.playerdict = {}
        self.map = map
        self.prevID = 0
        self.blockManager = blockManager_class(map)

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

        #add to block manager
        self.blockManager.addPlayer(newplayer)
        
        return newplayer

    def removePlayer(self, player):
        self.blockManager.removePlayer(player)
        
        for (id, p) in self.playerdict.items():
            if p == player:
                del self.playerdict[id]
                pass

    def movePlayerDir(self, player, direction):
        #record initial position
        oldx = player.x
        oldy = player.y

        #move player
        player.moveByDirection(direction, self.map)

        #update blocks
        self.blockManager.updatePlayer(oldx, oldy, player)

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

    def packLocal(self, player):
        blocks = self.blockManager.getSurroundingBlocks(player.x, player.y)
        #blocks[0].remove(player) #remove this player from its own local player list
        locallist = []

        #convert the list of lists of players into
        #a list of player data (pos, health)
        #the clients don't need to keep track of the player after it leaves view
        #so we don't need to include IDs        
        for i in blocks:
            for j in i:
                locallist.append(j.packSmall())

        return pickle.dumps(locallist)
