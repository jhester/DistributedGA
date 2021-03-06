import os, sys

#we have to surround with try statements... pygame is not on condor
try:
    import pygame
except:
    print "No pygame!!"

def load_image(name, colorkey=None):
    fullname = os.path.join('../data', 'images')
    fullname = os.path.join(fullname, name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error, message:
        print 'Cannot load image:', fullname
        raise SystemExit, message
    image = image.convert_alpha()
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0,0))
        image.set_colorkey(colorkey, RLEACCEL)
    return image

def load_sliced_sprites(w, h, filename):
    '''
    Specs :
        Master can be any height.
        Sprites frames width must be the same width
        Master width must be len(frames)*frame.width
    '''
    images = []
    master_image = pygame.image.load(os.path.join('../data/images', filename)).convert_alpha()

    master_width, master_height = master_image.get_size()
    for i in xrange(int(master_width/w)):
        images.append(master_image.subsurface((i*w,0,w,h)))
    return images


# Note that the map loaded by this puts its y before x, access it like map[y][x]
def load_map(map_file):
    print 'Loading map file: ', map_file
    #try to open from the correct directory, if can't try a local version
    try:
        tileData1 = open('../data/maps/'+map_file).readlines()
    except:
        try:
            tileData1 = open(map_file).readlines()
        except:
            sys.stderr.write("Could not open map_file: " + map_file + "\n")
            sys.exit()

    # strip off all the newlines in the strings in tileData1
    tileData1 = [line.rstrip() for line in tileData1]
    tileData1 = [[int(c) for c in s] for s in tileData1]
    return tileData1

# Note that the map loaded by this puts its y before x, access it like map[y][x]
def load_char_map(map_file):
    #try to open from the correct directory, if can't try a local version
    try:
        tileData1 = open('../data/maps/'+map_file).readlines()
    except:
        try:
            tileData1 = open(map_file).readlines()
        except:
            sys.stderr.write("Could not open map_file: " + map_file)

    # strip off all the newlines in the strings in tileData1
    tileData1 = [line.rstrip() for line in tileData1]
    tileData1 = [[c for c in s] for s in tileData1]
    return tileData1

#nifty bit of code to read all data from a socket
#taken from the website...
#http://appi101.wordpress.com/2007/12/01/recv-over-sockets-in-python/
def getDataFromSocket(sck):
    data = ""
    sck.settimeout(None)
    data = sck.recv(1024)
    sck.settimeout(0.1)
    
    while 1:
        line = ""
        try:
            line = sck.recv(1024)
        except:
            break
        
        if line == "":
            break
        
        data += line
    return data

def printErr(s):
    sys.stderr.write("\033[31mERROR:" + str(s) + "\033[37m\n")

def printConn(s):
    sys.stderr.write("\033[33m" + str(s) + "\033[37m\n")

def printGM(s):
    sys.stderr.write("\033[32m" + str(s) + "\033[37m\n")
