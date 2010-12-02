import socket
import threading
import pickle
import utils
import time

from maploader import *
from player import *
from constant import *

#a class to handle all connections coming into this server
class genericConnection_class(threading.Thread):
    def __init__(self, conn):
        threading.Thread.__init__(self)
        self.conn = conn

    def run(self):
        global playerthreadlist
        
        #we are expecting this conn to send identification (player/observer)
        data = int(self.conn.recv(1024))

        #handle player clients
        if data == constant_class.clientcode:
            print "GenericConnection starting player"
            connthread = playerConnectionHandler(len(playerthreadlist), conn)
            connthread.start()
            playerthreadlist.append(connthread)
            
            #handle observer clients
        elif data == constant_class.observercode:
            print "GenericConnection starting observer"
            (observerConnectionHandler(conn)).start()

            #unknown clients
        else:
            print "ERROR: Recieved unknown code from client '"+str(data)+"'"

class playerConnectionHandler(threading.Thread):
    #start with thread with a unique id and the connection for the client
    def __init__(self, id, conn):
        threading.Thread.__init__(self)
        self.id = id
        self.conn = conn
        self.player = None
        
    def run(self):
        print "Player started - " + str(self.id)
        global playermanager
        global maplvl
        
        #create a new player for this connection
        self.player = playermanager.addPlayer()

        #send maplvl
        self.conn.send(str(maplvl))

        ##################################
        #New server to client protocal
        #Send in this format....
        #  (Packet code, (Info))
        #
        # if packet code is heartbeat then (Info) = None
        # if packet code is spawn then (Info) = player.packAI()    <-- All the AI data
        # if packet code is main then (Info) = (player.packSmall(), playermanager.packLocal(player))
        ##################################        

        #This is just a basic frame work simmilar to end product
        while 1:
            #start in main mode            
            self.modeMain()
            #if bumped out of main wait in heartbeat
            self.modeHeartbeat()

    def modeHeartbeat(self):
        global heartbeatDelay
        
        print "Thread ("+str(self.id)+") with player ("+str(self.player.id)+") enterting heatbeat mode"
        while self.player.isDead():
            #send a heart beat
            self.conn.send(pickle.dumps((constant_class.packet_heartbeat, heartbeatDelay)))

            try:
                pk_code = int(self.conn.recv(1024))
            except:
                print "PlayerThread lost connection self.id="+str(self.id)+" player.id="+str(self.player.id)
                playermanager.removePlayer(self.player)
                sys.exit()
                                                            
            #client should be sending heartbeat back
            if not pk_code == constant_class.packet_heartbeat:
                print "Error: client not in same mode as server!"

            #wait until next heartbeat
            time.sleep(heartbeatDelay)


    def modeMain(self):
        print "Thread ("+str(self.id)+") with player ("+str(self.player.id)+") enterting main mode"
        global playermanager

        #stay in this mode as long as we are alive
        while not self.player.isDead():
            #send (playerdata,localplayers)
            self.conn.send(pickle.dumps((constant_class.packet_main,(self.player.packSmall(),playermanager.packLocal(self.player)))))
            
            #we should be reciving a direction
            try:
                self.data = int(self.conn.recv(1024))
            except:
                print "PlayerThread lost connection self.id="+str(self.id)+" player.id="+str(self.player.id)
                playermanager.removePlayer(self.player)
                sys.exit()

            #move the player
            playermanager.movePlayerDir(self.player, self.data)            

    #getter for id
    def getId(self):
        return self.id

    #getter for player positions (should this be done by the thread??)
    def getPlayerPos(self):
        return (self.player.x, self.player.y, self.player.health)

    #attack all players on the same tile
    def doDamage(self):
        if self.player == None:
            return

        global playermanager
        playermanager.attack(self.player)

class observerConnectionHandler(threading.Thread):
    #start with thread with a unique id and the connection for the client
    def __init__(self, conn):
        threading.Thread.__init__(self)
        self.conn = conn
        
    def run(self):
        global playermanager
        global maplvl

        #send the map
        self.conn.send(str(maplvl))
        
        while 1:
            time.sleep(0.1)
            #send player id/positions
            try:
                self.conn.send(playermanager.packSmall())
            except:
                print "Observer disconnected"
                return

#responcible for the game as a whole
#spawning new players, determining game end,
#doing damage
class gameMaster(threading.Thread):
    def __init__(self, playermanager, playerthreadlist):
        threading.Thread.__init__(self)
        self.playermanager = playermanager
        self.playerthreadlist = playerthreadlist
        
        self.minPlayers = 7 #number of players required to start round
        self.endCount = 10 #number of players alive to end round

    def run(self):
        #main loop where we pause movement and do damage
        while 1:
            #prevent players from moving while we do damage
            time.sleep(0.5)
            self.playermanager.pause()

            #tell all threads to 'attack'
            for thread in self.playerthreadlist:
                thread.doDamage()            

            #allow movement again
            self.playermanager.resume()

            if len(self.playermanager.getPlayerList()) > self.minPlayers:
                if len(self.playermanager.getPlayerList()) - len(self.playermanager.getDeadList()) < self.endCount:
                    print "GameMaster: End count ("+str(self.endCount)+") reached, starting new game!"
                    self.newGame()

    #start a new game
    def newGame(self):
        #respawn all players
        for thread in self.playerthreadlist:
            self.playermanager.respawn(thread.player)
            
if __name__ == "__main__":
    #make sure we didn't forget any commandline arguments
    if len(sys.argv) < 2:
        print "ERROR: Usage python server.py <port>"
        sys.exit()
    
    #initlize variables
    maplvl = 1
    map = mapLoader_class('level'+str(maplvl)+'_col.lvl')
    playermanager = playerManager_class(map)
    playerthreadlist = []
    heartbeatDelay = 5

    #startup the game master
    gamemaster = gameMaster(playermanager, playerthreadlist)
    gamemaster.start()

    #initlize socket
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
    
                
