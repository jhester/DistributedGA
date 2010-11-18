import socket
import threading
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
        
class playerConnectionHandler(threading.Thread):
    #start with thread with a unique id and the connection for the client
    def __init__(self, id, conn):
        threading.Thread.__init__(self)
        self.id = id
        self.conn = conn
        print "playerConnectionHandler created id="+str(id)
        
    def run(self):
        #global map

        print "New conn started"

        #create a new player for this connection
        player = player_class(2,2,map)

        while 1:
            #send local map info
            self.conn.send(pickle.dumps(map.localGrid(player, 5)))

            #we should be reciving a direction
            self.data = int(self.conn.recv(1024))
            player.moveByDirection(self.data)
            #print "["+str(self.id)+"] Player ("+str(player.x)+","+str(player.y)+")"
            #os.system('clear')
            #map.printGrid(player)        
            
            
if __name__ == "__main__":
    #make sure we didn't forget any commandline arguments
    if len(sys.argv) < 2:
        print "ERROR: Usage python server.py <port>"
        sys.exit()
    
    #initlize
    map = mapgen_class(40,40)
    playerthreadlist = []

    HOST = ''
    PORT = int(sys.argv[1])
    s=socket.socket()
    s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
    s.bind((HOST,PORT))
    s.listen(5)

    #create new player connection threads for any new connections
    while 1:
        conn, addr = s.accept()
        connthread = playerConnectionHandler(len(playerthreadlist), conn)
        connthread.start()
        playerthreadlist.append(connthread)        
        
    s.close()
    
                
