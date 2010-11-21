#python library
import random

#our library
from mapgen import mapgen_class
import constant

#a way to convert from direction to position
#0-up  1-right 2-down 3-left
global directionConvert
directionConvert = [(0,-1),(1,0),(0,1),(-1,0)]

class player_class:
    def __init__(self, x, y, map):
        self.x = x
        self.y = y
        self.map = map

    #update the players position based on a direction
    def moveByDirection(self, direction):
        global direcitonConvert
        nextposx = self.x+directionConvert[direction][0]
        nextposy = self.y+directionConvert[direction][1]

        #make sure our new position is reachable        
        if self.map.isWalkable(nextposx,nextposy):
            self.x = nextposx
            self.y = nextposy

#class to manage all players, creation/deletion etc
class playerManager_class:
    def __init__(self, map):
        self.playerlist = []
        self.map = map

    #creates and returns a new player object
    #also store this player in this manager
    def addPlayer(self):
        #start by finding a walkable position
        while True:
            x = random.random()
            y = random.random()        
            if self.map.isWalkable(x,y):
                break

        #create the player at this position
        newplayer = player_class(x,y, map)
        self.playerlist.append(newplayer)
        
        return newplayer

    def movePlayer(self, player, direction):
        player.moveByDirection(direction)
