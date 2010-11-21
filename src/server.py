import socket
import threading
import pickle
import sys
import os
import time

from mapgen import *
from player import *
import constant

#a way to convert from direction to position
#0-up  1-right 2-down 3-left
global directionConvert
directionConvert = [(0,-1),(1,0),(0,1),(-1,0)]

#a class to handle all connections coming into this server
class genericConnection_class(threading.Thread):
    def __init__(self, conn):
        threading.Thread.__init__(self)
        self.conn = conn

    def run(self):
        #we are expecting this conn to send identification (player/observer)
        self.data = int(self.conn.recv(1024))
        self.handleClient(conn, self.data)

    #function to handle creating a client thread
    def handleClient(self, conn, data):
        #handle player clients
        if data == constant.constant_class.clientcode:
            print "GenericConnection starting player"
            connthread = playerConnectionHandler(len(playerthreadlist), conn)
            connthread.start()
            playerthreadlist.append(connthread)
            
            #handle observer clients
        elif data == constant.constant_class.observercode:
            print "GenericConnection starting observer"
            (observerConnectionHandler(conn, playerthreadlist)).start()

            #unknown clients
        else:
            print "ERROR: Recieved unknown code from client '"+str(data)+"'"

class playerConnectionHandler(threading.Thread):
    #start with thread with a unique id and the connection for the client
    def __init__(self, id, conn):
        threading.Thread.__init__(self)
        self.id = id
        self.conn = conn
        
    def run(self):
        global playerManager
        
        #create a new player for this connection
        self.player = playerManager.addPlayer()

        while 1:
            #send local map info
            self.conn.send(pickle.dumps(playerManager.getLocalGrid(self.player)))

            #we should be reciving a direction
            self.data = int(self.conn.recv(1024))
            playerManager.movePlayerDir(self.player, self.data)

    #getter for id
    def getId(self):
        return self.id

    #getter for player positions (should this be done by the thread??)
    def getPlayerPos(self):
        return (self.player.x, self.player.y)

class observerConnectionHandler(threading.Thread):
    #start with thread with a unique id and the connection for the client
    def __init__(self, conn, playerlist):
        threading.Thread.__init__(self)
        self.conn = conn
        self.playerlist = playerlist
        
    def run(self):
        global map

        #send the map
        self.conn.send(pickle.dumps(map.map))
        
        while 1:
            time.sleep(0.25)
            for thread in self.playerlist:
                #send player id/positions
                data = pickle.dumps((thread.getId(), thread.getPlayerPos()))
                self.conn.send(data)
            
if __name__ == "__main__":
    #make sure we didn't forget any commandline arguments
    if len(sys.argv) < 2:
        print "ERROR: Usage python server.py <port>"
        sys.exit()
    
    #initlize
    map = mapgen_class(40,40)
    playerManager = playerManager_class(map)
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
        (genericConnection_class(conn)).start()

    s.close()
    
                
