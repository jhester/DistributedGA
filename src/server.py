#!/usr/bin/env python
import SocketServer
import pickle
import sys
import os
from mapgen import mapgen_class

#a way to convert from direction to position
#0-up  1-right 2-down 3-left
global directionConvert
directionConvert = [(0,-1),(1,0),(0,1),(-1,0)]

class player_class:
    def __init__(self, x, y, map):
        self.x = x
        self.y = y
        self.map = map

    #update the players position based on a direction
    def moveByDirection(self, direction):
        global direcitonConvert
        nextposx = self.x+directionConvert[direction][0]
        nextposy = self.y+directionConvert[direction][1]

        #make sure our new position is reachable        
        if self.map.isWalkable(nextposx,nextposy):
            self.x = nextposx
            self.y = nextposy
        
class MyTCPHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        global map
        global player

        while 1:
            #send local map info
            self.request.send(pickle.dumps(map.localGrid(player, 5)))

            #we should be reciving a direction
            self.data = int(self.request.recv(1024))
            player.moveByDirection(self.data)
            os.system('clear')
            map.printGrid(player)        
            
if __name__ == "__main__":
    #initlize
    map = mapgen_class(40,40)
    player = player_class(2,2,map)

    HOST = ''
    PORT = int(sys.argv[1])
    server = SocketServer.TCPServer((HOST, PORT), MyTCPHandler)
    
    server.serve_forever()
    
                
