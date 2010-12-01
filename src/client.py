import socket
import sys
import os
import random
import time
import pickle

import constant
from maploader import mapLoader_class
from player import *

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

    #wait a little or we will generate too much traffic
    time.sleep(0.1)
    s.send(str(int(random.random()*4)))
                                                                   
s.close()
