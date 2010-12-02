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
        self.health = 25
        self.id = id

        #Important!!!! MAKE SURE TO UPDATE AI COUNT IN CONSTANT
        self.TEMP_aiVar1 = 1
        self.TEMP_aiVar2 = 2
        
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

    #a function to restore a player to brand new condition
    def respawn(self, x, y):
        self.x = x
        self.y = y
        self.health = 25

    #return a list of AI variables
    def getAI(self):
        return (self.TEMP_aiVar1, self.TEMP_aiVar2)

    #set the AI vars, should be in same order as getAI
    def setAI(self, vars):
        (self.TEMP_aiVar1, self.TEMP_aiVar2) = vars

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
        try:
            oldBlock.remove(player)
        except:
            pass
        
        newBlock.append(player)        

    def addPlayer(self, player):
        self.getBlock(player.x, player.y).append(player)

    def removePlayer(self, player):
        try:
            self.getBlock(player.x, player.y).remove(player)
            print "Player ("+str(player.id)+") removed from block manager"        
        except:
            print "Player ("+str(player.id)+") could noe be removed from block"

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
        self.deadlist = []
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

    #bring a player back to life
    def respawn(self, player):
        #find a starting position
        while True:
            x = int(random.random()*self.map.width)
            y = int(random.random()*self.map.height)
            if self.map.isWalkable(x,y):
                break

        #set the player to new condition
        player.respawn(x,y)

        #make undead
        self.removeFromDeadList(player)
        
                                                    
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

    #handle a players attack
    def attack(self, p1):
        if p1.isDead():
            return
        
        locallist = self.blockManager.getBlock(p1.x, p1.y)
        for p2 in locallist:
            if not p2 == p1 and not p2.isDead():
                if p2.x == p1.x and p2.y == p1.y:
                    self.damagePlayer(p2)

    #deal damage to a player
    def damagePlayer(self, player):        
        if not player.isDead():
            player.health -= 1
            if player.isDead():
                print "Player ("+str(player.id)+") died!"
                self.addPlayerToDeadList(player)

    #a list to keep track of dead players
    def addPlayerToDeadList(self, player):
        if not player.isDead():
            print "Warning: Adding living player("+str(player.id)+") to dead list!"
            
        if self.deadlist.count(player) == 0:
            self.deadlist.append(player)

        self.blockManager.removePlayer(player)

    def removeFromDeadList(self, player):
        if player.isDead():
            print "Warning: Removing dead player ("+str(player.id)+") from dead list!"

        #is there a better way than try statements?
        try:
            self.deadlist.remove(player)
        except:
            pass

    def clearDeadList(self):
        self.deadlist = []

    def getDeadList(self):
        return self.deadlist

    def getLiveList(self):
        result = []
        for p in self.playerlist:
            if not p.isDead():
                result.append(p)

        return result

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

#a manager for AI
class AIManager_class:
    def __init__(self):
        self.AIlist = []        

    def empty(self):
        self.AIlist = []

    #populate our list of AIs using the players we were given
    def set(self, players):
        self.empty()
        for player in players:
            self.AIlist.append(player.getAI())

    #return an AI var list
    def get(self):
        result = []
        
        #if there are no AIs to draw from just make a random one
        if len(self.AIlist) == 0:
            for i in range(constant_class.AIvarcount):
                result.append(random.randint(0,100))

            return result

        #create an AI from our list
        for i in range(constant_class.AIvarcount):
            #get random source AI
            AI = self.AIlist[random.randint(0,len(self.AIlist)-1)]
            result.append(AI[i])

        return result
