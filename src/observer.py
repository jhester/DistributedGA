#this is the observer it handles the drawing 
#and calculation of some player factors

import socket
import sys
import os
import time
import pickle

from constant import constant_class
from mapgen import mapgen_class
from player import playerManager_class

#don't be hatin
if not len(sys.argv) == 3:
    print "Usage python client.py <host> <port>"
    sys.exit()

#store host and port from command line
host = sys.argv[1]
port = int(sys.argv[2])

#try and connect to our server
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host,port))
print "Observer Connected on "+str(host)+":"+str(port)

#send observer code to server
s.send(str(constant_class.observercode))

#recv map data
mapdata = s.recv(8096).strip()
mapdata = pickle.loads(mapdata)
map = mapgen_class(40,40)
map.map = mapdata

#create player manager
playermanager = playerManager_class(map)

#main loop
s.settimeout(5)
while 1:
    #recv player id/position
    data = s.recv(4048).strip()
    playermanager.loadSmall(data)

    #convert dictionary to position list
    players = playermanager.getDictionary()
    list = []
    for key in players.keys():
        list.append((players[key].x, players[key].y))

    #display
    time.sleep(0.1)
    os.system('clear')

    #display list...
    map.printGrid(list)
        
s.close()
