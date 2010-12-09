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
            print "\033[31mERROR: Recieved unknown code from client '"+str(data)+"'\033[37m"

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
        
        # Block till we get the response back
        data = int(self.conn.recv(1024))
        if data != constant_class.clientcode:
            print "\033[32mClient Disconnected\033[37m" 
            sys.exit()
        print "\033[32mClient communicating with GameMaster. Waiting\033[37m"
        
        #This is just a basic frame work simmilar to end product
        while 1:
            self.modeHeartbeat()
            self.modeSpawn()
            self.modeMain()      
            
            # Now we need to block until we get a response saying the observer
            # has done everything it needs to do
            # Block till we get the response back
            data = int(self.conn.recv(1024))
            if data != constant_class.clientcode:
                print "\033[32mClient Disconnected\033[37m" 
                sys.exit()      

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
                print "\033[33mClient lost conn, heartbeat\033[37m"
                playermanager.removePlayer(self.player)
                sys.exit()
            
            #wait until next heartbeat
            time.sleep(heartbeatDelay)

    def modeMain(self):
        global playermanager

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
                print "\033[33mClient lost conn, main\033[37m"
                playermanager.removePlayer(self.player)
                sys.exit()
                
            #if the client had an error assume they aren't going to move
            if self.data == constant_class.packet_err:
                self.data = 4

            #move the player
            playermanager.movePlayerDir(self.player, self.data)            

            #check for player death
            if self.player.isDead():
                self.runState = constant_class.game_wait

    #send the player a spawn packet then go into play mode
    def modeSpawn(self):
        if not self.runState == constant_class.game_spawn:
            return

        #send the players current AI
        self.trySend(pickle.dumps((constant_class.packet_spawn,self.player.getAI())))

        #client recved AI
        if not self.conn.recv(64)[0] == str(constant_class.packet_err):
            self.runState = constant_class.game_main

    #respawn our player
    def respawn(self, AImanager):
        #don't try to respawn if we don't have a player
        if self.player == None:
            return

        global playermanager
        playermanager.respawn(self.player)
        self.player.setAI(AImanager.get())
        self.runState = constant_class.game_spawn

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
        
    def trySend(self, s):
        try:
            self.conn.sendall(s)
        except:
            print "\033[33mClient lost conn, trySend\033[37m"
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
        
        # Block till we get the response back
        data = int(self.conn.recv(1024))
        if data != constant_class.observercode:
            print "\033[32mObserver Disconnected\033[37m" 
            sys.exit()
        print "\033[32mObserver communicating with GameMaster. Starting\n\n\033[37m"
            
        while 1:
            #send player id/positions
            try:
                self.conn.send(playermanager.packSmall())

                # Now we need to block until we get a response saying the observer
                # has done everything it needs to do
                # Block till we get the response back
                data = int(self.conn.recv(1024))
                if data != constant_class.observercode:
                    print "\033[32mObserver Disconnected\033[37m" 
                    sys.exit()
                
            except:
                print "\033[32mObserver disconnected\033[37m"
                return

#responcible for the game as a whole
#spawning new players, determining game end,
#doing damage
class gameMaster(threading.Thread):
    def __init__(self, playermanager, playerthreadlist):
        threading.Thread.__init__(self)
        self.playermanager = playermanager
        self.playerthreadlist = playerthreadlist
        self.AImanager = AIManager_class()
        
        self.startCount = 4 #number of players required to start round
        self.minCount = 1 #min number of connected players (dead or alive) for valid round
        self.winCount = -1 #number of players alive to end round

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
        
        print "\033[32mGameMaster: Spawning players\033[37m"
        
        #respawn all players
        self.playermanager.emptyDeadList()
        for thread in self.playerthreadlist:
            thread.respawn(self.AImanager)

        #wait until atleast the minimum # of players have spawned
        while self.playermanager.getPlayingCount() < self.minCount:
            time.sleep(1)
                                        
    def modeMain(self):
        if self.roundIsValid():
            print "\033[32mGameMaster: Round started\033[37m"

        self.roundWon = False
        while self.roundIsValid():
            #prevent players from moving while we do damage
            time.sleep(0.5)
            self.playermanager.pause()
            
            #tell all threads to 'attack'
            for thread in self.playerthreadlist:
                thread.doDamage()
            
            #allow movement again
            self.playermanager.resume()

            #check for round win
            if self.roundWon:
                return

    #check for win conditions
    def playerDied(self):
        if self.playermanager.getPlayingCount() < self.winCount:
            print "\033[32mGameMaster: End count ("+str(self.winCount)+") reached, starting new game!\033[37m"
            self.AImanager.empty()
            self.AImanager.set(self.playermanager.getLiveList())
            self.roundWon = True
                                                                        

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
    heartbeatDelay = 5

    gamemaster = gameMaster(playermanager, playerthreadlist)
    playermanager.gamemaster = gamemaster
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
    
                
