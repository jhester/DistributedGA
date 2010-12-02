#python library
import random
import pickle
import threading

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

    #determine if the player is currently dead
    def isDead(self):
        if self.health <= 0:
            return True
        return False

class blockManager_class:
    def __init__(self, map):
        self.blockWidth = 5

        self.mapsize = map.width+1
        self.blocksPerSide = int(self.mapsize/self.blockWidth)
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
        self.playerlist = []
        self.map = map
        self.prevID = 0
        self.blockManager = blockManager_class(map)
        self.running = threading.Event()
        self.running.set() #initially true for now

    def pause(self):
        self.running.clear()

    def resume(self):
        self.running.set()

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
        self.playerlist.append(newplayer)

        #add to block manager
        self.blockManager.addPlayer(newplayer)
        
        return newplayer

    def removePlayer(self, player):
        self.blockManager.removePlayer(player)
        self.playerlist.remove(player)

    def movePlayerDir(self, player, direction):
        #don't allow movement while paused
        self.running.wait()

        #record initial position
        oldx = player.x
        oldy = player.y

        #move player
        player.moveByDirection(direction, self.map)

        #update blocks
        self.blockManager.updatePlayer(oldx, oldy, player)

    #do damage to other players on the same tile
    def attack(self, p1):
        if p1.health <= 0:
            return
        
        locallist = self.blockManager.getBlock(p1.x, p1.y)
        for p2 in locallist:
            if not p2 == p1 and p2.health > 0:
                if p2.x == p1.x and p2.y == p1.y:
                    p2.health -= 1
                    if p2.health <= 0:
                        print "Player ("+str(p2.id)+") died!"

    #return a list of player IDs and what has changed
    def getPlayerList(self):
        return self.playerlist

    def mergePlayerList(self, list):
        for newPlayer in list:
            for oldPlayer in self.playerlist:
                if newPlayer.id == oldPlayer.id:
                    oldPlayer = newPlayer
                    break

    #convert our changed data to a string
    def packSmall(self):
        list = []
        for player in self.playerlist:
            list.append((player.id, player.packSmall()))
            
        return pickle.dumps(list)

    def loadSmall(self, str):
        list = pickle.loads(str)
        for (id, data) in list:
            found = False
            for player in self.playerlist:
                if player.id == id:
                    player.loadSmall(data)
                    found = True

            #we should be sending info on player spawns and deaths...
            if not found:
                player = player_class(0, 0, id)
                player.loadSmall(data)
                self.playerlist.append(player)

    def packLocal(self, player):
        blocks = self.blockManager.getSurroundingBlocks(player.x, player.y)
        locallist = []

        #convert the list of lists of players into
        #a list of player data (pos, health)
        #the clients don't need to keep track of the player after it leaves view
        #so we don't need to include IDs        
        for i in blocks:
            for j in i:
                if not j == player:
                    locallist.append(j.packSmall())

        return pickle.dumps(locallist)
