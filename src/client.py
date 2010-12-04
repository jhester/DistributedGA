import socket
import sys
import os
import random
import time
import pickle
import math

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

class client_class:
    def __init__(self, map, conn):
        self.map = map
        self.conn = conn
        self.AI = AI_class()
        
    #if a main packet is recieved
    def modeMain(self, ((xpos, ypos, health), localplayers)):
        dir = 4
    
        #unpickle localplayers
        localplayers = pickle.loads(localplayers)
    
        #find the closest player
        closestX = 0
        closestY = 0
        closestDist = 9999
        for (x,y,h) in localplayers:
            thisDist = getDist(xpos,ypos,x,y)
            if closestDist > thisDist:
                closestDist = thisDist
                closestX = x
                closestY = y
            
        #did not find a player close enough
        if closestDist > 10:
            dir = random.randint(0,4)
        else:
            #found a player to go to
            #run away
            if random.randint(0,100) > self.AI.courage:
                if randBool():
                    if closestX > xpos:
                        dir = 3
                    elif closestX < xpos:
                        dir = 1
                    elif closestY > ypos:
                        dir = 0
                    elif closestY < ypos:
                        dir = 2
                else:
                    if closestY > ypos:
                        dir = 0
                    elif closestY < ypos:
                        dir = 2
                    elif closestX > xpos:
                        dir = 3
                    elif closestX < xpos:
                        dir = 1                    
            #attack
            else:
                if closestX == xpos and closestY == ypos:
                    dir = 4
                elif randBool():
                    if closestX > xpos:
                        dir = 1
                    elif closestX < xpos:
                        dir = 3
                    elif closestY > ypos:
                        dir = 2
                    elif closestY < ypos:
                        dir = 0
                else:
                    if closestY > ypos:
                        dir = 2
                    elif closestY < ypos:
                        dir = 0
                    elif closestX > xpos:
                        dir = 1
                    elif closestX < xpos:
                        dir = 3
                
        #wait a little or we will generate too much traffic
        time.sleep(random.random())
        self.conn.send(str(dir))    
    
    #if a heartbeat packet is recieved
    def modeHeartbeat(self,(delay)):
        self.conn.send(str(constant_class.packet_heartbeat))
        time.sleep(delay)

    #if a spawn packet is recieved
    def modeSpawn(self,vars):
        print "AI: "+str(vars)
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
        print "ERROR: Try to connect to server FAILED"
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
        (pk_code, data) = pickle.loads(sock.recv(4096))

        #these modes process the data and respond to the server accordingly
        if pk_code == constant_class.packet_main:
            client.modeMain(data)
        elif pk_code == constant_class.packet_heartbeat:
            client.modeHeartbeat(data)
        elif pk_code == constant_class.packet_spawn:
            client.modeSpawn(data)
                                                                   
    sock.close()
