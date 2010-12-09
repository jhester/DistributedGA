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
            utils.printErr("Recieved unknown code from client '"+str(data)+"'")

class playerConnectionHandler(threading.Thread):
    #start with thread with a unique id and the connection for the client
    def __init__(self, id, conn):
        threading.Thread.__init__(self)
        self.id = id
        self.conn = conn
        self.player = None
        self.runState = constant_class.game_wait
        
    def run(self):
        global playermanager
        global maplvl
        
        #create a new player for this connection
        self.player = playermanager.addPlayer()

        #send maplvl
        self.trySend(str(maplvl))
        
        #This is just a basic frame work simmilar to end product
        while 1:
            self.modeHeartbeat()
            self.modeSpawn()
            self.modeMain()      
            
    def modeHeartbeat(self):
        global heartbeatDelay

        #if we are not supposed to be waiting
        if not self.runState == constant_class.game_wait:
            return
        
        self.player.isPlaying = False        
        while self.runState == constant_class.game_wait:
            #send a heart beat
            self.trySend(pickle.dumps((constant_class.packet_heartbeat, heartbeatDelay)))
        
            try:
                pk_code = int(self.conn.recv(1024)[0])
            except:
                utils.printConn("Client lost conn, heartbeat")
                playermanager.removePlayer(self.player)
                sys.exit()
            
            #wait until next heartbeat
            time.sleep(heartbeatDelay)

    def modeMain(self):
        global playermanager
        global moveevent
        global moveevent2
        
        #if we are not supposed to be playing
        if not self.runState == constant_class.game_main:
            return

        self.player.isPlaying = True

        #stay in this mode as long as we are alive
        while self.runState == constant_class.game_main:
            #send (playerdata,localplayers)
            self.trySend(pickle.dumps((constant_class.packet_main,(self.player.packSmall(),playermanager.packLocal(self.player)))))
            
            #we should be reciving a direction
            try:
                self.data = int(self.conn.recv(1024)[0])
            except:
                #if we recved nothing then int will fail
                utils.printConn("Client lost conn, main mode")
                playermanager.removePlayer(self.player)
                self.conn.close()
                sys.exit()
                
            #if the client had an error assume they aren't going to move
            if self.data == constant_class.packet_err:
                self.data = 4

            #wait for second move flag
            moveevent2.wait()

            #set the next direction
            self.player.nextdir = self.data

            #wait for move flag
            moveevent.wait()
            
            #check for player death
            if self.player.isDead():
                self.runState = constant_class.game_wait
                self.player.isPlaying = False
                print "Player "+str(self.player.id)+" died!"

    #send the player a spawn packet then go into play mode
    def modeSpawn(self):
        if not self.runState == constant_class.game_spawn:
            return

        #send the players current AI
        self.trySend(pickle.dumps((constant_class.packet_spawn,self.player.getAI())))

        #client recved AI
        if not self.conn.recv(64)[0] == str(constant_class.packet_err):
            self.runState = constant_class.game_main

    #getter for id
    def getId(self):
        return self.id

    #getter for player positions (should this be done by the thread??)
    def getPlayerPos(self):
        return (self.player.x, self.player.y, self.player.health)

    def trySend(self, s):
        try:
            self.conn.sendall(s)
        except:
            utils.printConn("Client lost conn, trySend")
            playermanager.removePlayer(self.player)
            sys.exit()
                                                
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
            time.sleep(0.25)
            
            #send player id/positions
            try:
                self.conn.sendall(playermanager.packSmall())
            except:
                utils.printConn("Observer disconnected")
                return

#responcible for the game as a whole
#spawning new players, determining game end,
#doing damage
class gameMaster(threading.Thread):
    def __init__(self, playermanager, playerthreadlist, moveevent, moveevent2):
        threading.Thread.__init__(self)
        self.playermanager = playermanager
        self.playerthreadlist = playerthreadlist
        self.AImanager = AIManager_class()
        self.moveevent = moveevent
        self.moveevent2 = moveevent2
        
        self.startCount = 20 #number of players required to start round
        self.minCount = 10 #min number of connected players (dead or alive) for valid round
        self.winCount = 10 #number of players alive to end round

    def run(self):
        while 1:
            self.modeWait() #wait until we have enough players
            self.modeSpawn() #give life to players
            self.modeMain() #let the game play out

    #wait mode is ised to wait for additional players to connect if we don't have enough
    def modeWait(self):
        #if we have enough players to start already
        if len(self.playermanager.getPlayerList()) >= self.startCount:
            return

        #not enough players, put anyone connected into wait mode, then wait for more players
        print "\033[32mGameMaster: Not enough players connected\033[37m"
        for thread in self.playerthreadlist:
            thread.runState = constant_class.game_wait

        while len(self.playermanager.getPlayerList()) < self.startCount:
            time.sleep(5)

    def modeSpawn(self):
        #make sure we have enough players to start a round
        if len(self.playermanager.getPlayerList()) < self.startCount:
            return
        
        utils.printGM("GameMaster: Spawning players")
        
        #respawn all players
        self.playermanager.respawnPlayers(self.AImanager)

        #tell threads to do spawn
        for thread in playerthreadlist:
            thread.runState = constant_class.game_spawn
                                        
    def modeMain(self):
        global moveevent
        global moveevent2

        if self.roundIsValid():
            utils.printGM("GameMaster: Round started")

        while self.roundIsValid():
            #allow movement
            moveevent.clear()
            moveevent2.set()

            #slow the game down a bit
            time.sleep(constant_class.game_speed)

            #stop movement
            moveevent2.clear()
            moveevent.set()

            #update the positions
            self.playermanager.movePlayers()

            #deal out damage/death etc
            self.playermanager.attackPlayers()

            #check for round win
            if self.playermanager.getPlayingCount() < self.winCount:
                print "\033[32mGameMaster: End count ("+str(self.winCount)+") reached, starting new game!\033[37m"
                for thread in playerthreadlist:
                    thread.runState = constant_class.game_wait
                self.AImanager.set(self.playermanager.getLiveList())
                break

            time.sleep(0.1)

        moveevent.set()
        moveevent2.set()

    #function to check if the current round is vail (enough players etc)
    def roundIsValid(self):
        if self.playermanager.getDeadCount()+self.playermanager.getPlayingCount() > self.minCount:
            return True
        return False
    
if __name__ == "__main__":
    #make sure we didn't forget any commandline arguments
    if len(sys.argv) < 3:
        print "\033[31mERROR: Usage python server.py <port> <map level number>\033[37m"
        sys.exit()
    
    #initlize variables
    maplvl = sys.argv[2]
    map = mapLoader_class('level'+str(maplvl))
    playermanager = playerManager_class(map)
    playerthreadlist = []
    heartbeatDelay = 1

    moveevent = threading.Event()
    moveevent2 = threading.Event()
    gamemaster = gameMaster(playermanager, playerthreadlist, moveevent, moveevent2)
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
    
                
