#this is the observer it handles the drawing 
#and calculation of some player factors

import socket
import sys
import os
import pickle
import time
import pygame
import TileMap
import AnimatedSprite
import utils
from constant import constant_class
from maploader import mapLoader_class

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

#Setup pygame
pygame.init()
screen = pygame.display.set_mode((800, 600))

#recv map level
maplvl = s.recv(64).strip()[0]
map = mapLoader_class('level'+maplvl+'_layer1.txt')
mapscene = TileMap.TileMap("level"+maplvl)

#setup playermanager
playermanager = playerManager_class(map)

#add overlord
overlord = AnimatedSprite.AnimatedSprite(utils.load_sliced_sprites(32, 32, 'alien.png'), 6,6) 
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
    players = playermanager.getDictionary()
    for key in players.keys():
        mapscene.updatePlayer(players[key])
      
    # Handle map rendering and updating with movement    
    for evt in pygame.event.get():
        if evt.type == pygame.QUIT:
            running = False
        mapscene.update(screen, evt)
    
    pygame.display.flip()
        
s.close()
