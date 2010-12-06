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
from constant import constant_class
from maploader import mapLoader_class
from player import *

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
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption('DIstributed Genetic Algorithm (DIGA) - Observer')

#recv map level
maplvl = s.recv(64).strip()[0]
print maplvl
map = mapLoader_class('level'+maplvl)
mapscene = TileMap.TileMap("level"+maplvl)

#setup playermanager
playermanager = playerManager_class(map)

#add overlord
overlord = OverlordSprite.OverlordSprite(utils.load_sliced_sprites(32, 32, 'characters/alien.png'), 6,6, 0, 3, 3, mapscene) 
mapscene.setOverlord(overlord)

#main loop
time = 0
running = True
while running:
    #recv player id/position
    data = s.recv(4048).strip()
    playermanager.loadSmall(data)

    # Update all the players on the map
    # This will add players if they havent been added
    players = playermanager.getPlayerList()
    for player in players:
        mapscene.updatePlayer(player)
      
    # Handle map rendering and updating with movement    
    for evt in pygame.event.get():
        if evt.type == pygame.QUIT:
            running = False
        mapscene.update(screen, evt)
    
    pygame.display.flip()
        
s.close()
