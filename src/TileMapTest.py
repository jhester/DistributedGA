import pygame
import os, sys
import TileMap
import utils
import player
from OverlordSprite import OverlordSprite

# Get the map
if len(sys.argv) is not 2:
    print 'Usage: python TileMapTest.py <level number>'
    sys.exit()
        
# Setup pygame
pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption('DIstributed Genetic Algorithm (DIGA) - Map Viewer')

# Map scene
mapscene = TileMap.TileMap('level'+sys.argv[1])

# main loop
time = 0
running = True
mapscene.addPlayer(player.player_class(1, 20, 1))
#mapscene.addPlayer(player.player_class(1, 2, 2))
overlord = OverlordSprite(utils.load_sliced_sprites(32, 32, 'characters/alien.png'), 6,6, 0, 3, 3, mapscene) 
mapscene.setOverlord(overlord)

while running:
      
    # Handle map rendering and updating with movement    
    for evt in pygame.event.get():
        if evt.type == pygame.QUIT:
            running = False
        mapscene.update(screen, evt)
                
    pygame.display.flip()
        