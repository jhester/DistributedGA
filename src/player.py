#python library
import random
import pickle
import threading

#our library
from maploader import mapLoader_class
from constant import *

class player_class:
    def __init__(self, x, y, id):
        self.x = x #starting x
        self.y = y #starting y
        self.health = constant_class.maxHealth #starting health
        self.id = id #unique player id
        self.isPlaying = False #is player playing current round?
        self.AI = AI_class()
        self.nextdir = -1
        
    #update the players position based on a direction
    def move(self, map):
        #-1 could be set if we try to move before thinking
        if self.nextdir == -1:
            return
        
        nextposx = self.x+constant_class.directionconvert[self.nextdir][0]
        nextposy = self.y+constant_class.directionconvert[self.nextdir][1]

        #make sure our new position is reachable        
        if map.isWalkable(nextposx,nextposy):
            self.x = nextposx
            self.y = nextposy

        #reset our nextdir
        self.netdir = -1

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
        self.health = constant_class.maxHealth
        self.nextdir = -1

    def getAI(self):
        return self.AI.get()

    def setAI(self,vars):
        self.AI.set(vars)
        
    def __str__( self ) :
        status = 'Alive'
        if self.isDead(): status = 'Slain'
        return "Player (id:" + str(self.id)+"): Status - "+status

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
        except:
            pass

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
        self.lock = threading.Lock()

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
        self.lock.acquire()
        self.prevID += 1
        newplayer = player_class(x,y,self.prevID)
        self.playerlist.append(newplayer)

        #add to block manager
        self.blockManager.addPlayer(newplayer)
        self.lock.release()
        
        return newplayer

    #bring players back to life
    def respawnPlayers(self, aimanager):
        self.lock.acquire()
        self.deadlist = []

        #spawn all players currently in existance
        for player in self.playerlist:
            #find a starting position
            while True:
                x = int(random.random()*self.map.width)
                y = int(random.random()*self.map.height)
                if self.map.isWalkable(x,y):
                    break

            #set the player to new condition
            player.respawn(x,y)
            player.setAI(aimanager.get())

            #set player as playing
            player.isPlaying = True
        self.lock.release()

    #remove a player from all lists
    def removePlayer(self, player):
        self.lock.acquire()
        self.blockManager.removePlayer(player)
        self.playerlist.remove(player)
        self.removeFromDeadList(player)
        self.lock.release()

    def movePlayers(self):
        self.lock.acquire()
        for player in self.playerlist:
            if player.isPlaying and not player.isDead():
                self.movePlayerDir(player)
                
        self.lock.release()
        
    def movePlayerDir(self, player):
        #record initial position
        oldx = player.x
        oldy = player.y

        #move player
        player.move(self.map)

        #update blocks
        self.blockManager.updatePlayer(oldx, oldy, player)

    #handle players attacking eachother
    def attackPlayers(self):
        print "a"
        self.lock.acquire()
        print "b"
        for p1 in self.playerlist:
            if not p1.isDead() and p1.isPlaying:
                locallist = self.blockManager.getBlock(p1.x, p1.y)
                for p2 in locallist:
                    if not p2 == p1 and p2.isPlaying:
                        if p2.x == p1.x and p2.y == p1.y:
                            self.damagePlayer(p2)
        print "c"
        self.lock.release()
        print "d"

    #deal damage to a player
    def damagePlayer(self, player):        
        if not player.isDead() and player.isPlaying:
            player.health -= 1
            if player.isDead():
                self.addPlayerToDeadList(player)

    #a list to keep track of dead players
    def addPlayerToDeadList(self, player):
        if not player.isDead():
            print "Warning: Adding living player("+str(player.id)+") to dead list!"
            
        if self.deadlist.count(player) == 0:
            self.deadlist.append(player)

        self.blockManager.removePlayer(player)

    def removeFromDeadList(self, player):
        #is there a better way than try statements?
        try:
            self.deadlist.remove(player)
        except:
            pass

    def getDeadList(self):
        return self.deadlist
    
    def getDeadCount(self):
        return len(self.deadlist)

    def getLiveList(self):
        result = []
        for p in self.playerlist:
            if not p.isDead() and p.isPlaying:
                result.append(p)

        return result

    #get the number of players playing in current round
    def getPlayingCount(self):
        count = 0
        for p in self.playerlist:
            if p.isPlaying:
                count += 1

        return count

    #return a list of player IDs and what has changed
    def getPlayerList(self):
        return self.playerlist

    #convert our changed data to a string
    #in a way that gives us the shortest pickle
    def packSmall(self):
        list = []
        for player in self.playerlist:
            if player.isPlaying:
                list.append((player.id, player.packSmall()))

        return pickle.dumps(list)

    #convert from string to data
    def loadSmall(self, str):
        list = pickle.loads(str)

        self.lock.acquire()

        #TEMP this is a horrid way of removing old players that are gone
        self.playerlist = []

        
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

        self.lock.release()
        
    def packLocal(self, player):
        blocks = self.blockManager.getSurroundingBlocks(player.x, player.y)
        locallist = []

        #convert the list of lists of players into
        #a list of player data (pos, health)
        #the clients don't need to keep track of the player after it leaves view
        #so we don't need to include IDs        
        for i in blocks:
            for j in i:
                if not j == player and j.isPlaying: #TEMP here j should not be in the block manager if its not playing!!!
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

        f = open('aioutput.txt','w')
        f.write("---- New Round ----\n")
        f.write("Count="+str(len(players))+"\n")
        for a in self.AIlist:
            f.write(str(a)+"\n")
        f.close()

    #return an AI var list
    def get(self):
        result = []
        
        #if there are no AIs to draw from just make a random one
        if len(self.AIlist) == 0:
            for i in range(AI_class.AIvarcount):
                result.append(random.randint(0,100))
            return result

        #create an AI from our list
        for i in range(AI_class.AIvarcount):
            #get random source AI
            AI = self.AIlist[random.randint(0,len(self.AIlist)-1)]
            result.append(AI[i])
        return result

class AI_class:
    #AI stuffs
    AIvarcount = 4

    def __init__(self):
        self.courage = 0
        self.camper = 0
        self.clingy = 0
        self.stack = 0

    #return a list of AI variables
    def get(self):
        return (self.courage, self.camper, self.clingy, self.stack)

    #set the AI vars, should be in same order as get
    def set(self, vars):
        (self.courage, self.camper, self.clingy, self.stack) = vars
