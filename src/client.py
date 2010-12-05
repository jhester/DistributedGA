import socket
import sys
import os
import random
import time
import pickle
import math
from collections import deque

from constant import *
from maploader import mapLoader_class
from player import AI_class

def randBool():
    return random.choice((1, 0))

def getDist(x1,y1,x2,y2):
    x = x1-x2
    y = y1-y2
    d = math.sqrt(x*x + y*y)
    return d

#a class to keep info on other players
class target_class:
    def __init__(self, vars):
        (self.x, self.y, self.health) = vars
        self.attackPcnt = -1

class client_class:
    def __init__(self, map, conn):
        self.x = -1
        self.y = -1
        self.health = -1
        
        self.map = map
        self.conn = conn
        self.AI = AI_class()

    #how likely are we to attack based on courage alone
    #if we are at 0 courage but greatest health advantage then
    #we have .50 attack percent
    #if we are at the same health as the other guy
    #with 50 courage then percent is .50
    def courageAttackPcnt(self, other):
        healthPcnt = (other.health-self.health)+constant_class.maxHealth
        healthPcnt /= (constant_class.maxHealth*2.0)
        couragePcnt = self.AI.courage/100.0
        attackPcnt = couragePcnt-healthPcnt
        attackPcnt += 1
        attackPcnt /= 2.0
        return attackPcnt

    #this is based on distance, campers don't like to move
    def camperAttackPcnt(self, other):
        dist = getDist(self.x,self.y,other.x,other.y)
        if dist > 15: #15+ is all really far
            dist = 15

        distPcnt = dist/15.0
        distPcnt = 1-distPcnt
        camperPcnt = self.AI.camper/100.0
        attackPcnt = camperPcnt-distPcnt
        attackPcnt += 1
        attackPcnt /= 2.0
        return attackPcnt

    #if they are touching a wall return clingypcnt otherwise return inverse
    def clingyAttackPcnt(self, other):
        isTouching = False
        if not self.map.isWalkable(other.x-1,other.y):
            isTouching = True
        elif not self.map.isWalkable(other.x+1, other.y):
            isTouching = True
        elif not self.map.isWalkable(other.x, other.y-1):
            isTouching = True
        elif not self.map.isWalkable(other.x, other.y+1):
            isTouching = True

        clingyPcnt = self.AI.clingy/100.0
        if not isTouching:
            return 1-clingyPcnt
        return clingyPcnt

    #if they are stacked return stackpcnt otherwise return inverse
    def stackAttackPcnt(self, other, others):
        isStacked = False
        for target in others:
            if not other == target:
                if other.x == target.x and other.y == target.y:
                    isStacked = True
                    break

        stackPcnt = self.AI.stack/100.0
        if not isStacked:
            return 1-stackPcnt
        return stackPcnt                        

    #the percent chance we attack this guy
    def overallAttackPcnt(self, other, others):
        #percentage of attack
        attackPcnt = 0.0

        #get a percent of attack for each AI variable
        attackPcnt += self.courageAttackPcnt(other)
        attackPcnt += self.camperAttackPcnt(other)
        attackPcnt += self.clingyAttackPcnt(other)
        attackPcnt += self.stackAttackPcnt(other, others)

        #get it in range 0.0-1.0
        attackPcnt /= 4.0
        return attackPcnt

    #determine the best player to attack out of list 'others'
    def getBestTarget(self, others):
        highestPcnt = -1
        target = None
        for other in others:
            pcnt = self.overallAttackPcnt(other, others)
            other.attackPcnt = pcnt

            if pcnt > highestPcnt:
                highestPcnt = pcnt
                target = other

        return target

    #flood fill pathfinding
    def getBestDir(self, target):
        #if no target then just random
        if target == None:
            return random.randint(0,4)

        #create a move dist map
        tiles = []
        for i in range(self.map.width):
            tiles.append([])
            for j in range(self.map.height):
                tiles[i].append(-1)

        #recursively check tiles untile find the target
        checkList = deque()
        tiles[self.x][self.y] = 0
        checkList.appendleft((self.x,self.y))
        while len(checkList) > 0:
            (x,y) = checkList.pop()

            #if this tile is our target then we are done
            if x == target.x and y == target.y:
                dir = self.traceBack(tiles, target.x, target.y)
                return dir
            
            #add ajacent tiles to checkList
            if self.map.isWalkable(x-1,y):
                if tiles[x-1][y] == -1:
                    tiles[x-1][y] = tiles[x][y]+1
                    checkList.appendleft((x-1,y))
            if self.map.isWalkable(x+1,y):
                if tiles[x+1][y] == -1:
                    tiles[x+1][y] = tiles[x][y]+1
                    checkList.appendleft((x+1,y))
            if self.map.isWalkable(x,y-1):
                if tiles[x][y-1] == -1:
                    tiles[x][y-1] = tiles[x][y]+1
                    checkList.appendleft((x,y-1))
            if self.map.isWalkable(x,y+1):
                if tiles[x][y+1] == -1:
                    tiles[x][y+1] = tiles[x][y]+1
                    checkList.appendleft((x,y+1))
                                                            
        #target is unreachable
        return random.randint(0,4)

    def traceBack(self, tiles, x, y):
        l = []
        nextPos = (x,y)
        lastPos = nextPos
        while not tiles[nextPos[0]][nextPos[1]] == 0:
            lastPos = nextPos
            (x,y) = nextPos
            l.append(nextPos)

            if self.map.isWalkable(x-1,y):
                v = tiles[x-1][y]
                if v < tiles[x][y] and v > -1:
                    nextPos = (x-1,y)
            if self.map.isWalkable(x+1,y):
                v = tiles[x+1][y]
                if v < tiles[x][y] and v > -1:
                    nextPos = (x+1,y)
            if self.map.isWalkable(x,y-1):
                v = tiles[x][y-1]
                if v < tiles[x][y] and v > -1:
                    nextPos = (x,y-1)
            if self.map.isWalkable(x,y+1):
                v = tiles[x][y+1]
                if v < tiles[x][y] and v > -1:
                    nextPos = (x,y+1)
                        
        #lastPos is where we should move next
        if lastPos[0] == self.x and lastPos[1] == self.y:
            return 4
        elif lastPos[0] == self.x-1:
            return 3
        elif lastPos[0] == self.x+1:
            return 1
        elif lastPos[1] == self.y-1:
            return 0
        elif lastPos[1] == self.y+1:
            return 2
        else:
            sys.stderr.write("Pathfinding error 1")
            sys.exit()                

    #store data about ourself from server
    def loadData(self, vars):
        (self.x, self.y, self.health) = vars
        
    #if a main packet is recieved
    def modeMain(self, (vars, localplayers)):
        #store data about ourself
        self.loadData(vars)
        
        #unpickle localplayers and convert to list of targets
        localplayers = pickle.loads(localplayers)
        others = []
        for player in localplayers:
            others.append(target_class(player))

        #determine best player to attack
        target = self.getBestTarget(others)

        #determine best direction to move
        dir = self.getBestDir(target)
    
        #wait a little or we will generate too much traffic
        time.sleep(random.random()/2.0)
        self.conn.send(str(dir))    
    
    #if a heartbeat packet is recieved
    def modeHeartbeat(self,(delay)):
        self.conn.send(str(constant_class.packet_heartbeat))
        time.sleep(delay)

    #if a spawn packet is recieved
    def modeSpawn(self,vars):
        self.AI.set(vars)

if __name__ == "__main__":  
    #don't be hatin
    if not len(sys.argv) == 3:
        print "Usage python client.py <host> <port>"
        sys.exit()

    #store host and port from command line
    host = sys.argv[1]
    port = int(sys.argv[2])

    #try and connect to our server
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host,port))
        sock.settimeout(10)
        print "Connected on "+str(host)+":"+str(port)
    except:
        sys.stderr.write("ERROR: Try to connect to server FAILED")
        sys.exit()

    #send client code
    sock.send(str(constant_class.clientcode))

    #recieve and load map lvl
    maplvl = sock.recv(64)
    map = mapLoader_class('level'+maplvl+'_col.lvl')

    #create a client
    client = client_class(map, sock)

    #main loop
    while 1:
        #recieve and process packet
        (pk_code, data) = pickle.loads(sock.recv(6144))

        #these modes process the data and respond to the server accordingly
        if pk_code == constant_class.packet_main:
            client.modeMain(data)
        elif pk_code == constant_class.packet_heartbeat:
            client.modeHeartbeat(data)
        elif pk_code == constant_class.packet_spawn:
            client.modeSpawn(data)
                                                                   
    sock.close()
