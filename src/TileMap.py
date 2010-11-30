#! /usr/bin/env python

import math
import pygame
import utils
import AnimatedSprite
from pygame.locals import *

if not pygame.font: print 'Warning, fonts disabled'
if not pygame.mixer: print 'Warning, sound disabled'

BLOCK_SIZE = 32

class TileMap:
    
    def __init__(self, map_file):
        # this sets up a list (dynamic array) where tiles[N] corresponds to TiledScrolling_Tile{N}.jpg
        
        self.tiles = [pygame.image.load('../data/images/tile%d.png' % n).convert_alpha() for n in range(6)]
        self.tileWidth, self.tileHeight = self.tiles[0].get_size()
        self.map_file = map_file
        
        # Load tiles
        self.tileData1 = utils.load_map(self.map_file+'_layer1.txt')
        self.tileData2 = utils.load_map(self.map_file+'_layer2.txt')
        
        # Setup the offset and viewport coordinates and dimensions
        self.vpRenderOffset = (80, 60)
        self.vpStatsOffset = (80, 540)
         
        self.xvpCoordinate = 0
        self.yvpCoordinate = 0
        self.vpDimensions = (640, 480)
        
        # Set up the boundaries
        self.minHorzScrollBounds = 0
        self.maxHorzScrollBounds = len(self.tileData1[0]) * self.tileWidth - 640 - self.tileWidth
        
        self.minVertScrollBounds = 0
        self.maxVertScrollBounds = len(self.tileData1) * self.tileHeight - 480 - self.tileHeight
        
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
       
    def addPlayer(self, player):
            self.players[player.id] = AnimatedSprite.AnimatedSprite(utils.load_sliced_sprites(32, 32, 'zeldamove.png'), player.x,player.y) 
    
    def setOverlord(self, sprite):
        self.overlord = sprite
    
    def turnOverlordOn(self, truefalse):
        self.overlordOn = truefalse
          
    def updatePlayer(self, player):
        if self.players[player.id] is not None:
            self.players[player.id].gotoTile(player.x, player.y)
        else:
            self.players[player.id] = AnimatedSprite.AnimatedSprite(utils.load_sliced_sprites(32, 32, 'zeldamove.png'), player.x,player.y) 

        
    def inView(self, tileX, tileY):
        startXTile = math.floor(float(self.xvpCoordinate) / self.tileWidth)
        startYTile = math.floor(float(self.yvpCoordinate) / self.tileHeight)
        if tileX >= startXTile and tileX < startXTile+self.numXTiles and tileY >= startYTile and tileY < startYTile+self.numYTiles:
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
                
     
        # render
        screen.fill((0, 0, 0))
        startXTile = math.floor(float(self.xvpCoordinate) / self.tileWidth)
        startYTile = math.floor(float(self.yvpCoordinate) / self.tileHeight)
        
        for x in range(startXTile, startXTile + self.numXTiles):
            for y in range(startYTile, startYTile + self.numYTiles):
                self.tileLayer.blit(self.tiles[self.tileData1[y][x]], ((x - startXTile) * self.tileWidth, (y - startYTile) * self.tileHeight))
                if self.tileData2[y][x] is not 1:
                    self.tileLayer.blit(self.tiles[self.tileData2[y][x]], ((x - startXTile) * self.tileWidth, (y - startYTile) * self.tileHeight))
    
        screen.blit(self.tileLayer, self.vpRenderOffset, (self.xvpCoordinate - (startXTile * self.tileWidth), self.yvpCoordinate - (startYTile * self.tileHeight)) + self.vpDimensions)
        
        # Update the sprites
        self.time += 1000.0 / 30
        list = []
        for key in self.players.keys():
            list.append(self.players[key])
        for player in list:
            if self.inView(player.tileX, player.tileY):
                player.update(self.time, screen, self.xvpCoordinate, self.yvpCoordinate, self.vpRenderOffset, self.tileWidth, self.vpDimensions)
       
        # Update overlord if applicable
        if self.overlord is not None and self.overlordOn is True:
            if self.inView(self.overlord.tileX, self.overlord.tileY):
                self.overlord.update(self.time, screen, self.xvpCoordinate, self.yvpCoordinate, self.vpRenderOffset, self.tileWidth, self.vpDimensions)
