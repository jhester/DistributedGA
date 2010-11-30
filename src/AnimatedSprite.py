import pygame
import constant
import math

class AnimatedSprite(pygame.sprite.Sprite):
    
    def __init__(self, images, tileX, tileY, start_direction = 0, frames_per_direction = 3, fps = 3):
        pygame.sprite.Sprite.__init__(self)
        self._images = images
        #Animations: 0-up  1-right 2-down 3-left
        self.UP=0
        self.RIGHT=1
        self.DOWN=2
        self.LEFT=3
        
        # Track the time we started, and the time between updates.
        # Then we can figure out when we have to switch the image.
        self._start = pygame.time.get_ticks()
        self._delay = 1000 / fps
        self._last_update = 0
        self.frames_per_direction = frames_per_direction
        self.direction = start_direction
        self.directionChanged = False
        self.velocity = 3
        self.tileX = tileX
        self.tileY = tileY
        self.moving = False
        self.rect = pygame.Rect(tileX*32, tileY*32, 32, 32)
        
        # Set our first image.
        self._frame = self.direction*self.frames_per_direction
        self.image = self._images[self._frame]

    def goDirection(self, direction):
        self.moving = True
        self.direction = direction
        self.directionChanged = True
        if direction == self.UP:
            self.tileY += -1
        if direction == self.DOWN:
            self.tileY += 1
        if direction == self.LEFT:
            self.tileX += -1
        if direction == self.RIGHT:
            self.tileX += 1
    
    def gotoTile(self, tileX, tileY):
        # Figure out what general direction were going
        diffX = tileX - self.tileX
        diffY = tileY - self.tileY
        if diffY >= diffX:
            if diffY > 0: self.direction = self.UP
            else: self.direction = self.DOWN
        else:
            if diffX > 0: self.direction = self.RIGHT
            else: self.direction = self.LEFT

        # Set the destination
        self.moving = True
        self.directionChanged = True
        self.tileX = tileX
        self.tileY = tileY;
        
    def handleKeyUp(self, evt):
        if evt.key == pygame.K_a:
            self.goDirection(self.LEFT)
        elif evt.key == pygame.K_d:
            self.goDirection(self.RIGHT)
        elif evt.key == pygame.K_w:
            self.goDirection(self.UP)
        elif evt.key == pygame.K_s:
            self.goDirection(self.DOWN)
        
        
    def update(self, t, screen, xvpCoordinate, yvpCoordinate, screenOffset, tileHeight, vpDimensions):
        # Note that this doesn't work if it's been more that self._delay
        # time between calls to update(); we only update the image once
        # then, but it really should be updated twice.
        
        
        #Start moving to our destination, if we are moving. 
        # If we have made it to our location stop
      
        # Were moving so update taking into account velocity and direction
        
            
        # Now animate
        if self.directionChanged is True:
            self._frame = self.direction*self.frames_per_direction
            self.directionChanged = False
            
        if t - self._last_update > self._delay:
            self._frame += 1
            if self._frame >= len(self._images) / 4 + self.direction*self.frames_per_direction: self._frame = self.direction*self.frames_per_direction
            self.image = self._images[self._frame]
            self._last_update = t
            
        # go ahead and draw right here
        # So we know were in the view, now calculate where we are
        startXTile = math.floor(float(xvpCoordinate) / tileHeight)
        startYTile = math.floor(float(yvpCoordinate) / tileHeight)
        xdiff = xvpCoordinate-startXTile*tileHeight
        ydiff = yvpCoordinate-startYTile*tileHeight

        #screen.blit(self.image, (screenOffset[0]+xvpCoordinate - (startXTile * tileHeight), screenOffset[1]+yvpCoordinate - (startYTile * tileHeight)))
        #screen.blit(self.image, screenOffset, (xvpCoordinate - (startXTile * tileHeight), yvpCoordinate - (startYTile * tileHeight)) + vpDimensions)
        screen.blit(self.image, (screenOffset[0]-xdiff+(self.tileX-startXTile)*32,screenOffset[1]-ydiff+(self.tileY-startYTile)*32))
        #screen.blit(self.image, self.rect.topleft)
        #print startXTile, startYTile, xdiff, ydiff, self.tileX, self.tileY, xvpCoordinate, yvpCoordinate
