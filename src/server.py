import socket
import threading
import pickle
import sys
import os
import Queue

from mapgen import mapgen_class
import constant

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

#a class to handle all connections coming into this server
class genericConnection_class(threading.Thread):
    def __init__(self, conn, dataqueue):
        threading.Thread.__init__(self)
        self.conn = conn
        self.dataqueue = dataqueue
        print "genericConnection_class created"

    def run(self):
        #we are expecting this conn to send identification (player/observer)
        self.data = int(self.conn.recv(1024))
        self.dataqueue.put((conn, self.data))
        print "genericConnection_class data added to queue"
    
class playerConnectionHandler(threading.Thread):
    #start with thread with a unique id and the connection for the client
    def __init__(self, id, conn):
        threading.Thread.__init__(self)
        self.id = id
        self.conn = conn
        print "playerConnectionHandler created id="+str(id)
        
    def run(self):
        print "["+str(self.id)+"] Connection thread started"

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
    connDataQueue = Queue.Queue(10) #Queue is self locking (safe for threads)

    HOST = ''
    PORT = int(sys.argv[1])
    s=socket.socket()
    s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
    s.bind((HOST,PORT))
    s.listen(5)

    #create new player connection threads for any new connections
    while 1:
        conn, addr = s.accept()
        (genericConnection_class(conn, connDataQueue)).start()

        while not connDataQueue.empty():
            conn, data = connDataQueue.get()
            print "Data found in connDataQueue = "+str((conn, data))
            
            if data == constant.constant_class.clientcode:                
                connthread = playerConnectionHandler(len(playerthreadlist), conn)
                connthread.start()
                playerthreadlist.append(connthread)
            elif data == constant.constant_class.observercode:
                print "Observercode"
            else:
                print "ERROR: Recieved unknown code from client '"+str(data)+"'"
        
    s.close()
    
                
