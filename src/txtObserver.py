#this is the observer it handles the drawing 
#and calculation of some player factors

import socket
import sys
import os
import pickle
import time
import TileMap
from constant import constant_class
from maploader import mapLoader_class
from player import *

#nifty bit of code to read all data from a socket
#taken from the website...
#http://appi101.wordpress.com/2007/12/01/recv-over-sockets-in-python/
def getDataFromSocket(sck):
    data = ""
    sck.settimeout(None)
    data = sck.recv(1024)
    sck.settimeout(0.1)
    
    while 1:
        line = ""
        try:
            line = sck.recv(1024)
        except:
            break
        
        if line == "":
            break
        
        data += line
    return data
    

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

#recv map level
maplvl = s.recv(1)
map = mapLoader_class("level"+maplvl)

#setup playermanager
playermanager = playerManager_class(map)

#main loop
time = 0
running = True
while running:
    #recv player id/position
    data = getDataFromSocket(s)
    playermanager.loadSmall(data)                

    #convert dictionary to list
    list = []
    for player in playermanager.getPlayerList():
        list.append((player.x, player.y))

    os.system('clear')
    map.printGrid(list)
    print "Total players: " + str(len(playermanager.getPlayerList()))
        
s.close()
