import os

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
    image = image.convert()
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

def load_map(map_file):
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
    tileData1 = [[int(c) for c in s] for s in tileData1]
    return tileData1
        
