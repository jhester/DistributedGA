import socket
import sys
import os
import random
import time
import pickle

import constant
from maploader import mapLoader_class

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
map = mapLoader_class('level'+maplvl+'_layer1.txt')

#main loop
while 1:
    #recieve our position
    (xpos, ypos) = pickle.loads(s.recv(2048))

    #wait a little or we will generate too much traffic
    time.sleep(0.1)
    s.send(str(int(random.random()*4)))

    os.system('clear')

    print "---------------------------"
    data = map.localGrid(xpos, ypos, 5)
    for i in data:
        line = ""
        for j in i:
            if j == 0:
                line += "\033[30m" #black
                    
            line += " " + str(j)
            line += "\033[0m" #white
        print line
    print "---------------------------"
                                                                   
s.close()
