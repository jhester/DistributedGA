# This is the observer it handles the drawing 
# and calculation of some player factors

import socket
import sys
import os
import pickle
import time
import pygame
import TileMap
import AnimatedSprite
import OverlordSprite
import utils
import gui
import defaultStyle
from constant import constant_class
from maploader import mapLoader_class
from player import *                                                            

class ObserverGUI:
    
    def __init__(self):
        # Setup GUI
        self.playerselection = 0
        defaultStyle.init(gui)
        
        self.desktop = gui.Desktop()
        self.win = gui.Window(position = (800,0), size = (200,600), parent = self.desktop, text = 'Statistics and Help')
        self.lbl = gui.Label(position = (2, 30), text = '---- Mini-map Key ----', parent = self.win)
        
        self.movbtn = gui.OnImageButton(utils.load_image('movebx.png'), position = (15, 50), parent = self.win)
        self.mvlbl = gui.Label(position = (25, 45), text = 'Moving / Living Player', parent = self.win)
        
        self.atkbtn = gui.OnImageButton(utils.load_image('atkbx.png'), position = (15, 70), parent = self.win)
        self.atklbl = gui.Label(position = (25, 65), text = 'Attacking Player', parent = self.win)
        
        self.deadbtn = gui.OnImageButton(utils.load_image('deadbx.png'), position = (15, 90), parent = self.win)
        self.deadlbl = gui.Label(position = (25, 85), text = 'Slain Player', parent = self.win)
        
        self.ovbtn = gui.OnImageButton(utils.load_image('ovbx.png'), position = (15, 110), parent = self.win)
        self.ovlbl = gui.Label(position = (25, 105), text = 'Overlord Player', parent = self.win)
        
        self.statslbl = gui.Label(position = (2, 130), text = '---- Player List ----', parent = self.win)
        self.playerstats = gui.ListBox(position = (2, 150), size = (196, 200), parent = self.win)
        self.playerstats.onItemSelected = self.itemSelected
        
        self.lbl_title_pos = gui.Label(position = (5, 350), text='Player (id:#): Status - ', parent = self.win)
        self.lbl_pos = gui.Label(position = (5, 365), text='Location: ( #, # )', parent = self.win)
        self.lbl_health = gui.Label(position = (5, 380), text='Health: # / 25', parent = self.win)
        self.lbl_ai_courage = gui.Label(position = (5, 395), text='AI Courage: #', parent = self.win)
        self.lbl_ai_camper = gui.Label(position = (5, 410), text='AI Camper: #', parent = self.win)
        self.lbl_ai_clingy = gui.Label(position = (5, 425), text='AI Clingy: #', parent = self.win)
        self.lbl_ai_stack = gui.Label(position = (5, 440), text='AI Stack: #', parent = self.win)
        self.player_img_alive = gui.OnImageButton(utils.load_sliced_sprites(32, 32, 'characters/zelda_atk.png')[0], position = (100,420), parent = self.win, enabled = False)
        self.player_img_dead = gui.OnImageButton(utils.load_sliced_sprites(32, 32, 'characters/zelda_dead.png')[0], position = (100,420), parent = self.win, enabled = False)
        
        
    def itemSelected(self, widget):
        self.playerselection = widget.selectedIndex
        
        
    def updatePlayerStats(self, players):
        player = players[self.playerselection]
        stat = 'Alive'
        self.player_img_dead.visible = False
        self.player_img_alive.visible = True
        if player.isDead(): 
            stat = 'Slain'
            self.player_img_dead.visible = True
            self.player_img_alive.visible = False
        self.lbl_title_pos.text='Player(id:'+str(player.id)+'): Status - '+str(stat)
        self.lbl_pos.text='Location: ( '+str(player.x)+', '+str(player.y)+' )'
        self.lbl_health.text='Health: '+str(player.health)+' / '+str(constant_class.maxHealth)
        AI = player.getAI()
        self.lbl_ai_courage.text='AI Courage: '+str(AI[0])
        self.lbl_ai_camper.text='AI Camper: '+str(AI[1])
        self.lbl_ai_clingy.text='AI Clingy: '+str(AI[2])
        self.lbl_ai_stack.text='AI Stack: '+str(AI[3])
        
    def draw(self):
        self.desktop.draw()
        
    def update(self, players):
        self.desktop.update()
        self.playerstats.items = players


if __name__ == "__main__":    
    #don't be hatin
    if not len(sys.argv) == 3:
        print "Usage python observer.py <host> <port>"
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
    
    #Setup pygame
    pygame.init()
    screen = pygame.display.set_mode((1000, 600))
    pygame.display.set_caption('DIstributed Genetic Algorithm (DIGA) - Observer')
    
    #recv map level
    maplvl = s.recv(64).strip()[0]
    print maplvl
    map = mapLoader_class('level'+maplvl)
    mapscene = TileMap.TileMap("level"+maplvl)
    
    # Confirm reception
    s.send(str(constant_class.observercode))
    
    #setup playermanager
    playermanager = playerManager_class(map)
    
    #add overlord
    overlord = OverlordSprite.OverlordSprite(utils.load_sliced_sprites(32, 32, 'characters/alien.png'), 6,6, 0, 3, 3, mapscene) 
    mapscene.setOverlord(overlord)
    
    # Setup GUI
    ogui = ObserverGUI()
    
    #main loop
    time = 0
    code = -1
    running = True
    while running:
        #recv player id/position
        try: 
            data = utils.getDataFromSocket(s)
            (code, data) = pickle.loads(data)
            if not data == None:
                playermanager.loadBig(data)
        except: 
            utils.printConn('Couldnt load round of player data.')
    
        if code == constant_class.game_spawn:
            mapscene.reset()
    
        # Update all the players on the map
        # This will add players if they havent been added
        players = playermanager.getPlayerList()
        for player in players:
            mapscene.updatePlayer(player)
            
        # Update the GUI
        if len(players) > 0:
            ogui.update(players)
            ogui.updatePlayerStats(players)
        
        # Handle map rendering and updating with movement    
        for evt in gui.setEvents(pygame.event.get()):
            if evt.type == pygame.QUIT:
                running = False
            mapscene.update(screen, evt)
        
        # Render the GUI info screen
        ogui.draw()
        
        # Flip the display buffer
        pygame.display.flip()
            
    s.close()