#! /usr/bin/env python

import os, glob, math
import pygame
import utils
import AnimatedSprite, OverlordSprite
from pygame.locals import *

if not pygame.font: print 'Warning, fonts disabled'
if not pygame.mixer: print 'Warning, sound disabled'

BLOCK_SIZE = 32

class TileMap:
    
    def __init__(self, map_file):
        #self.tiles = [pygame.image.load('../data/images/tiles/tile%d.png' % n).convert_alpha() for n in range(6)]
        # Load the tiles
        self.tiles = {}
        self.loadMapFile(map_file)
        
        # Setup the offset and viewport coordinates and dimensions
        self.vpRenderOffset = (0, 0)
        self.vpStatsOffset = (80, 540)
         
        self.xvpCoordinate = 0
        self.yvpCoordinate = 0
        self.vpDimensions = (800, 600)
        
        # Set up the boundaries
        self.minHorzScrollBounds = 0
        self.maxHorzScrollBounds = len(self.tileData1[0]) * self.tileWidth - self.vpDimensions[0] - self.tileWidth
        
        self.minVertScrollBounds = 0
        self.maxVertScrollBounds = len(self.tileData1) * self.tileHeight - self.vpDimensions[1] - self.tileHeight
        
        # Velocity set and reset during update loops
        self.xadvanceVelocity = 0
        self.yadvanceVelocity = 0
        
        self.scrollVelocity = 10
         
        self.numXTiles = int(math.ceil(float(self.vpDimensions[0]) / self.tileWidth)) + 1
        self.numYTiles = int(math.ceil(float(self.vpDimensions[1]) / self.tileHeight)) + 1
        self.tileLayer = pygame.Surface((self.numXTiles * self.tileWidth, self.numYTiles * self.tileHeight)).convert()
        
        # Custom event for updating the map view
        self.UPDATE = pygame.USEREVENT
        pygame.time.set_timer(self.UPDATE, int(1000.0 / 30))
        self.time = 0
        
        # The player dictionary
        self.players = {}
        # The overlord, invincible user man
        self.overlord = None
        self.overlordOn = False
        
        # Add the mini-map
        self.minimap = utils.load_image('minimap.png')
        self.movebx = utils.load_image('movebx.png')
        self.deadbx = utils.load_image('deadbx.png')
        self.atkbx = utils.load_image('atkbx.png')
        self.ovbx = utils.load_image('ovbx.png')
        self.ratio = self.minimap.get_height()/self.map_size
        
        # Generate the mini-map background image
        

    def loadMapFile(self, map_file):
        # Load the tile images
        for infile in glob.glob( os.path.join('../data/images/tiles', '*.*') ):
            self.tiles[infile[len(infile)-5]] = pygame.image.load(infile).convert_alpha()   
        
        # Load the sprite images
        self.map_sprites = [pygame.image.load('../data/images/sprites/sprite%d.png' % n).convert_alpha() for n in range(6)]
        self.map_sprites_rd = [53, 0, 128, 128, 0, 0]
        self.map_sprites_list = []
        self.tileWidth, self.tileHeight = self.tiles['0'].get_size()
        
        # Load tiles
        self.map_file = map_file
        self.tileData1 = utils.load_char_map(self.map_file+'_layer1.lvl')
        self.tileData2 = utils.load_char_map(self.map_file+'_layer2.lvl')
        self.col_data = utils.load_map(self.map_file+'_col.lvl')
        self.map_size = len(self.tileData1[0])-1
        
        # Load up sprites
        self.spriteData = utils.load_map(self.map_file+'_sprites.lvl')
        for x in range(self.map_size):
            for y in range(self.map_size):
                if self.spriteData[y][x] is not 1: self.map_sprites_list.append((x,y,self.spriteData[y][x]))
    
    def addPlayer(self, player):
        self.players[player.id] = AnimatedSprite.AnimatedSprite(utils.load_sliced_sprites(32, 32, 'characters/zelda_move.png'), player.x,player.y) 
    
    def setOverlord(self, sprite):
        self.overlord = sprite
    
    def turnOverlordOn(self, truefalse):
        self.overlordOn = truefalse
    
    def isPlayerAttacking(self, player):
        p1 = self.players[player.id]
        list = self.players.keys()
        for key in list:
            p2 = self.players[key]
            if not p2 == p1 and not p2.dead:
                if p2.tileX == p1.tileX and p2.tileY == p1.tileY:
                        return True
        return False
    
    def updatePlayer(self, player):
        if self.players.has_key(player.id):
            # Check to see if were dying 
            if player.isDead():
                self.players[player.id].die()
           # if self.isPlayerAttacking(player):
            #    self.players[player.id].attack()
            
            self.players[player.id].gotoTile(player.x, player.y)
                                    
        else:
            self.players[player.id] = AnimatedSprite.AnimatedSprite(utils.load_sliced_sprites(32, 32, 'characters/zelda_move.png'), player.x,player.y) 
            # Add the death and attacking images
            self.players[player.id].addAttackImages(utils.load_sliced_sprites(32, 32, 'characters/zelda_atk.png'))
            self.players[player.id].addDeathImages(utils.load_sliced_sprites(32, 32, 'characters/zelda_dead.png'))
    
    def reset(self):
        for (key, player) in self.players.items():
            player.live()
            
    def inView(self, tileX, tileY):
        startXTile = math.floor(float(self.xvpCoordinate) / self.tileWidth)
        startYTile = math.floor(float(self.yvpCoordinate) / self.tileHeight)
        if tileX >= startXTile and tileX < startXTile+self.numXTiles and tileY >= startYTile and tileY < startYTile+self.numYTiles:
            return True
        return False
    
    def isWithin(self, x, y):
        if x > self.map_size or x < 0 or y > self.map_size or y < 0:
            return 0
        return 1
    
    def isWalkable(self, x, y):
        if not self.isWithin(x,y):
            return False

        if self.col_data[y][x] == 0:
            return True
        return False   
    
    def update(self, screen, evt):
        if evt.type == pygame.KEYDOWN:
            if evt.key == pygame.K_LEFT:
                self.xadvanceVelocity += -self.scrollVelocity
            elif evt.key == pygame.K_RIGHT:
                self.xadvanceVelocity += self.scrollVelocity
            elif evt.key == pygame.K_UP:
                self.yadvanceVelocity += -self.scrollVelocity
            elif evt.key == pygame.K_DOWN:
                self.yadvanceVelocity += self.scrollVelocity
 
            elif evt.key == pygame.K_ESCAPE:
                pygame.event.post(pygame.event.Event(pygame.QUIT, {}))
 
        elif evt.type == pygame.KEYUP:
            if evt.key == pygame.K_LEFT:
                self.xadvanceVelocity += self.scrollVelocity
            elif evt.key == pygame.K_RIGHT:
                self.xadvanceVelocity += -self.scrollVelocity
            elif evt.key == pygame.K_UP:
                self.yadvanceVelocity += self.scrollVelocity
            elif evt.key == pygame.K_DOWN:
                self.yadvanceVelocity += -self.scrollVelocity
            elif evt.key == pygame.K_o and self.overlord is not None:
                self.overlordOn = True
            elif evt.key == pygame.K_l:
                self.loadMapFile(self.map_file)
            if self.overlord is not None and self.overlordOn is True:
                self.overlord.handleKeyUp(evt)
                
        elif evt.type == self.UPDATE:
            self.xvpCoordinate += self.xadvanceVelocity
            self.yvpCoordinate += self.yadvanceVelocity
            if self.xvpCoordinate < self.minHorzScrollBounds:
                self.xvpCoordinate = self.minHorzScrollBounds
            if self.xvpCoordinate > self.maxHorzScrollBounds:
                self.xvpCoordinate = self.maxHorzScrollBounds
            if self.yvpCoordinate < self.minVertScrollBounds:
                self.yvpCoordinate = self.minVertScrollBounds
            if self.yvpCoordinate > self.maxVertScrollBounds:
                self.yvpCoordinate = self.maxVertScrollBounds
                
     
        # Render the tiles
        screen.fill((0, 0, 0))
        startXTile = math.floor(float(self.xvpCoordinate) / self.tileWidth)
        startYTile = math.floor(float(self.yvpCoordinate) / self.tileHeight)
        
        for x in range(int(startXTile), int(startXTile + self.numXTiles)):
            for y in range(int(startYTile), int(startYTile + self.numYTiles)):
                self.tileLayer.blit(self.tiles[self.tileData1[y][x]], ((x - startXTile) * self.tileWidth, (y - startYTile) * self.tileHeight))
                if self.tileData2[y][x] is not '1':
                    self.tileLayer.blit(self.tiles[self.tileData2[y][x]], ((x - startXTile) * self.tileWidth, (y - startYTile) * self.tileHeight))
 
        screen.blit(self.tileLayer, self.vpRenderOffset, (self.xvpCoordinate - (startXTile * self.tileWidth), self.yvpCoordinate - (startYTile * self.tileHeight)) + self.vpDimensions)
        
        # Now render the bottom part of the sprite layer which is impassable
        xdiff = self.xvpCoordinate-startXTile*self.tileHeight
        ydiff = self.yvpCoordinate-startYTile*self.tileHeight
        for item in self.map_sprites_list:
            screen.blit(self.map_sprites[item[2]]
                        .subsurface((0,self.map_sprites_rd[item[2]], self.map_sprites[item[2]].get_width(), self.map_sprites[item[2]].get_height()-self.map_sprites_rd[item[2]])), 
                        (self.vpRenderOffset[0]-xdiff+(item[0]-startXTile)*32,self.vpRenderOffset[1]-ydiff+(item[1]-startYTile)*32))
        
        # Update the player sprites
        self.time += 1000.0 / 30
        list = []
        for key in self.players.keys():
            list.append(self.players[key])
        for player in list:
                player.update(self.time, screen, self.xvpCoordinate, self.yvpCoordinate, self.vpRenderOffset, self.tileWidth, self.vpDimensions)
       
        # Update overlord if applicable, make sure of collisions
        if self.overlord is not None and self.overlordOn is True:
            if self.inView(self.overlord.tileX, self.overlord.tileY):
                self.overlord.update(self.time, screen, self.xvpCoordinate, self.yvpCoordinate, self.vpRenderOffset, self.tileWidth, self.vpDimensions)
                
        # Render the passable part of the sprites
        for item in self.map_sprites_list:
            screen.blit(self.map_sprites[item[2]]
                        .subsurface((0,0, self.map_sprites[item[2]].get_width(), self.map_sprites_rd[item[2]])), 
                        (self.vpRenderOffset[0]-xdiff+(item[0]-startXTile)*32,self.vpRenderOffset[1]-ydiff+(item[1]-startYTile)*32-self.map_sprites_rd[item[2]]))

        # Now update the mini-map
        screen.blit(self.minimap,  (self.vpRenderOffset[0]+580,self.vpRenderOffset[1]+385))
        # Blit overlord
        if self.overlordOn is True:
            screen.blit(self.ovbx, (self.vpRenderOffset[0]+580+self.overlord.tileX*self.ratio+4, self.vpRenderOffset[1]+385+self.overlord.tileY*self.ratio+4))
        for player in list:
            # Determine status
            img = self.movebx
            if player.attack is True:
                img = self.atkbx
            elif player.dead is True:
                img = self.deadbx
            screen.blit(img, (self.vpRenderOffset[0]+580+player.tileX*self.ratio+4, self.vpRenderOffset[1]+385+player.tileY*self.ratio+4))
        pygame.draw.rect(screen, (0,255,255), (self.vpRenderOffset[0]+580+startXTile*self.ratio+4,self.vpRenderOffset[1]+385+startYTile*self.ratio+4,self.numXTiles*self.ratio,self.numYTiles*self.ratio-4), 1) 
        
        #screen.blit(surf, (self.vpRenderOffset[0]+426+player.tileX*ratio, self.vpRenderOffset[1]+264+player.tileY*ratio))