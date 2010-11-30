#! /usr/bin/env python

import os, sys, math
import pygame
import Tile

from pygame.locals import *

if not pygame.font: print 'Warning, fonts disabled'
if not pygame.mixer: print 'Warning, sound disabled'

BLOCK_SIZE = 32

class TileMap:
    
    def __init__(self, map_file):
        # this sets up a list (dynamic array) where tiles[N] corresponds to TiledScrolling_Tile{N}.jpg
        #
        self.tiles = [pygame.image.load('../data/images/tile%d.png' % n).convert_alpha() for n in range(6)]
        self.tileWidth, self.tileHeight = self.tiles[0].get_size()
        self.map_file = map_file
        
        # the following is roughly equivalent to
        # outer_temp = []
        # for s in file('TiledScrolling_Tiledata.txt'): # line-by-line
        #     inner_temp = []
        #     for c in s:
        #         inner_temp.append(int(c))
        #     outer_temp.append(inner_temp)
        # tileData1 = outer_temp
        #
        # List comprehensions are a fantastic thing. Learn them if you use Python!
        #
        self.tileData1 = open('../data/maps/'+self.map_file+'_layer1.txt').readlines()
        # strip off all the newlines in the strings in tileData1
        self.tileData1 = [line.rstrip() for line in self.tileData1]
        self.tileData1 = [[int(c) for c in s] for s in self.tileData1]
        
        self.tileData2 = open('../data/maps/'+self.map_file+'_layer2.txt').readlines()
        self.tileData2 = [line.rstrip() for line in self.tileData2]
        self.tileData2 = [[int(c) for c in s] for s in self.tileData2]
        
        self.vpRenderOffset = (80, 60)
        self.vpStatsOffset = (80, 540)
         
        self.xvpCoordinate = 0
        self.yvpCoordinate = 0
        
        self.vpDimensions = (640, 480)
        self.minHorzScrollBounds = 0
        self.maxHorzScrollBounds = len(self.tileData1[0]) * self.tileWidth - 640 - self.tileWidth
        
        self.minVertScrollBounds = 0
        self.maxVertScrollBounds = len(self.tileData1) * self.tileHeight - 480 - self.tileHeight
        
        self.xadvanceVelocity = 0
        self.yadvanceVelocity = 0
        
        self.scrollVelocity = 10
         
        self.numXTiles = int(math.ceil(float(self.vpDimensions[0]) / self.tileWidth)) + 1
        self.numYTiles = int(math.ceil(float(self.vpDimensions[1]) / self.tileHeight)) + 1
        self.tileLayer = pygame.Surface((self.numXTiles * self.tileWidth, self.numYTiles * self.tileHeight)).convert()
        
        
        self.UPDATE = pygame.USEREVENT
        pygame.time.set_timer(self.UPDATE, int(1000.0 / 30))
        self.time = 0
        
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
