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
    def __init__(self, x, y):
        self.x = x
        self.y = y

    #update the players position based on a direction
    def moveByDirection(self, direction, map):
        global direcitonConvert
        nextposx = self.x+directionConvert[direction][0]
        nextposy = self.y+directionConvert[direction][1]

        #make sure our new position is reachable        
        if map.isWalkable(nextposx,nextposy):
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
            x = int(random.random()*self.map.width)
            y = int(random.random()*self.map.height)        
            if self.map.isWalkable(x,y):
                break

        #create the player at this position
        newplayer = player_class(x,y)
        self.playerlist.append(newplayer)
        
        return newplayer

    def movePlayerDir(self, player, direction):
        player.moveByDirection(direction, self.map)

    #return the map surrounding the player
    def getLocalGrid(self, player):
        return self.map.localGrid(player, 5)
