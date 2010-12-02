import pygame
import os, sys
import TileMap
import AnimatedSprite
import utils
import player

# Setup pygame
pygame.init()
screen = pygame.display.set_mode((800, 600))

# Map scene
mapscene = TileMap.TileMap('level1')

# main loop
time = 0
running = True
mapscene.addPlayer(player.player_class(1, 20, 1))
#mapscene.addPlayer(player.player_class(1, 2, 2))
overlord = AnimatedSprite.AnimatedSprite(utils.load_sliced_sprites(32, 32, 'characters/alien.png'), 6,6, 0, 3, 3, mapscene) 
mapscene.setOverlord(overlord)

while running:
      
    # Handle map rendering and updating with movement    
    for evt in pygame.event.get():
        if evt.type == pygame.QUIT:
            running = False
        mapscene.update(screen, evt)
    
    pygame.display.flip()
        