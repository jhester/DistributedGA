#this is the observer it handles the drawing 
#and calculation of some player factors

import socket
import sys
import os
import pickle
import time

from constant import constant_class
from mapgen import mapgen_class

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

#main loop
s.settimeout(5)
while 1:
    #recv player id/position
    data = s.recv(4048).strip()
    players = pickle.loads(data)    

    #convert dictionary to list
    list = []
    for key in players.keys():
        list.append(players[key])

    #display
    time.sleep(0.1)
    os.system('clear')

    #display list...
    map.printGrid(list)
        
s.close()
