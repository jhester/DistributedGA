import socket
import sys
import os
import random
import time
import pickle
import math

import constant
from maploader import mapLoader_class
from player import *

def getDist(x1,y1,x2,y2):
    x = x1-x2
    y = y1-y2
    d = math.sqrt(x*x + y*y)
    return d

#don't be hatin
if not len(sys.argv) == 3:
    print "Usage python client.py <host> <port>"
    sys.exit()

#store host and port from command line
host = sys.argv[1]
port = int(sys.argv[2])

#try and connect to our server
try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host,port))
    s.settimeout(10)
    print "Connected on "+str(host)+":"+str(port)
except:
    print "ERROR: Try to connect to server FAILED"
    sys.exit()

#send client code
s.send(str(constant.constant_class.clientcode))

#recieve and load map lvl
maplvl = s.recv(64)
map = mapLoader_class('level'+maplvl+'_layer1.lvl')

#main loop
while 1:
    #recieve position and local players
    ((xpos, ypos), localplayers) = pickle.loads(s.recv(4096))
    localplayers = pickle.loads(localplayers)

    #find the closest player, move toward it
    closestX = 0
    closestY = 0
    closestDist = 9999
    for (x,y,h) in localplayers:
        thisDist = getDist(xpos,ypos,x,y)        
        if closestDist > thisDist:            
            closestDist = thisDist
            closestX = x
            closestY = y

    if x > xpos:
        dir = 1
    elif x < xpos:
        dir = 3
    elif y > ypos:
        dir = 2
    elif y < ypos:
        dir = 0
    else:
        dir = 4

    #wait a little or we will generate too much traffic
    time.sleep(0.1)
    s.send(str(dir))
                                                                   
s.close()
