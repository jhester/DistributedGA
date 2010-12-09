import pygame
from pygame import display
from pygame import font
from pygame import draw
from pygame import Rect
from pygame import mouse

## COSTANTS ##
APP_FLAT = 1
APP_3D = 2

## ATTRIBUTES ##
defaultFont = None
defaultButtonStyle = None
defaultWindowStyle = None
defaultImageButtonStyle = None
defaultLabelStyle = None
defaultTextBoxStyle = None
defaultCheckBoxStyle = None
defaultOptionBoxStyle = None
defaultListBoxStyle = None
defaultComboBoxStyle = None

events = None

## FUNCTIONS ##
def setEvents(eventList):
    import gui
    gui.events = eventList
    return eventList

### STYLE CREATION ###
def createButtonStyle(font, fontcolor,  surface, *spaces):  
    if len(spaces) < 3:
        raise GuiException("Must pass 3 integers as spaces at least for the normal state button appearence.")
    
    w, h = surface.get_size()  
    
    style = {'font': font,
             'font-color': fontcolor,
             'left-normal': surface.subsurface(Rect(0,0,spaces[0],h)),
             'middle-normal': surface.subsurface(Rect(spaces[0],0,spaces[1],h)),
             'right-normal': surface.subsurface(Rect(sum(spaces[:2]),0,spaces[2],h))  
            }
    
    #Over
    if len(spaces) >= 6:
        style['do-over'] = True
        style['left-over'] = surface.subsurface(Rect(sum(spaces[:3]),0,spaces[3],h))
        style['middle-over'] = surface.subsurface(Rect(sum(spaces[:4]),0,spaces[4],h))
        style['right-over'] = surface.subsurface(Rect(sum(spaces[:5]),0,spaces[5],h))
    else:
        style['do-over'] = False
    
    #Down
    if len(spaces) >= 9:
        style['do-down'] = True
        style['left-down'] = surface.subsurface(Rect(sum(spaces[:6]),0,spaces[6],h))
        style['middle-down'] = surface.subsurface(Rect(sum(spaces[:7]),0,spaces[7],h))
        style['right-down'] = surface.subsurface(Rect(sum(spaces[:8]),0,spaces[8],h))
    else:
        style['do-down'] = False
    
    #Enabled
    if len(spaces) == 12:
        style['do-disabled'] = True
        style['left-disabled'] = surface.subsurface(Rect(sum(spaces[:9]),0,spaces[9],h))
        style['middle-disabled'] = surface.subsurface(Rect(sum(spaces[:10]),0,spaces[10],h))
        style['right-disabled'] = surface.subsurface(Rect(sum(spaces[:11]),0,spaces[11],h))
    else:
        style['do-disabled'] = False
    return style

def createImageButtonStyle(image, buttonWidth):
    if image.get_width() < buttonWidth:
        raise GuiException("The button width must be less or equal than image width.")
    
    style = {}
        
    h = image.get_height()
    
    style['image-normal'] = image.subsurface(Rect(0,0,buttonWidth,h))
    
    if image.get_width() >= buttonWidth * 2:
        style['do-over'] = True
        style['image-over'] = image.subsurface(Rect(buttonWidth,0,buttonWidth,h))
    else:
        style['do-over'] = False
    
    if image.get_width() >= buttonWidth * 3:
        style['do-down'] = True
        style['image-down'] = image.subsurface(Rect(buttonWidth*2,0,buttonWidth,h))
    else:
        style['do-down'] = False
    
    if image.get_width() >= buttonWidth * 4:
        style['do-disabled'] = True
        style['image-disabled'] = image.subsurface(Rect(buttonWidth*3,0,buttonWidth,h))
    else:
        style['do-disabled'] = False
    
    return style

def createCheckBoxStyle(font, image, singleImageWidth, font_color = (0,0,0), disabled_font_color = (150,150,150), spacing = 2, borderwidth = 0, bordercolor = (0,0,0), autosize = False, wordwrap = True, antialias = True ):
    if image.get_width() < singleImageWidth * 8:
        raise GuiException("The image of the CheckBox must contain 8 pictures for the four states (normal, mouse-over, pressed and disabled) for each CheckBox value Checked or Unchecked.")
    
    style = {'font':font, 'font-color': font_color, 'disabled-font-color': disabled_font_color,
             'antialias':antialias, 'autosize':autosize,
             'wordwrap':wordwrap, 'border-width':borderwidth, 'border-color':bordercolor,
             'spacing':spacing}
        
    h = image.get_height()
    
    style['unchecked-normal'] = image.subsurface(Rect(0,0,singleImageWidth,h))
    style['unchecked-over'] = image.subsurface(Rect(singleImageWidth,0,singleImageWidth,h))
    style['unchecked-down'] = image.subsurface(Rect(singleImageWidth*2,0,singleImageWidth,h))
    style['unchecked-disabled'] = image.subsurface(Rect(singleImageWidth*3,0,singleImageWidth,h))
    style['checked-normal'] = image.subsurface(Rect(singleImageWidth*4,0,singleImageWidth,h))
    style['checked-over'] = image.subsurface(Rect(singleImageWidth*5,0,singleImageWidth,h))
    style['checked-down'] = image.subsurface(Rect(singleImageWidth*6,0,singleImageWidth,h))
    style['checked-disabled'] = image.subsurface(Rect(singleImageWidth*7,0,singleImageWidth,h))    

    return style

def createOptionBoxStyle(font, image, singleImageWidth, font_color = (0,0,0), disabled_font_color = (150,150,150), spacing = 2, borderwidth = 0, bordercolor = (0,0,0), autosize = False, wordwrap = True, antialias = True ):
    if image.get_width() < singleImageWidth * 7:
        raise GuiException("The image of the CheckBox must contain 7 pictures for the four states (normal, mouse-over and pressed) for each CheckBox value Checked or Unchecked plus one, the last, for the disabled appearence.")
    
    style = {'font':font, 'font-color': font_color, 'disabled-font-color': disabled_font_color,
             'antialias':antialias, 'autosize':autosize,
             'wordwrap':wordwrap, 'border-width':borderwidth, 'border-color':bordercolor,
             'spacing':spacing}
        
    h = image.get_height()
    
    style['unchecked-normal'] = image.subsurface(Rect(0,0,singleImageWidth,h))
    style['unchecked-over'] = image.subsurface(Rect(singleImageWidth,0,singleImageWidth,h))
    style['unchecked-down'] = image.subsurface(Rect(singleImageWidth*2,0,singleImageWidth,h))
    style['checked-normal'] = image.subsurface(Rect(singleImageWidth*3,0,singleImageWidth,h))
    style['checked-over'] = image.subsurface(Rect(singleImageWidth*4,0,singleImageWidth,h))
    style['checked-down'] = image.subsurface(Rect(singleImageWidth*5,0,singleImageWidth,h))
    style['disabled'] = image.subsurface(Rect(singleImageWidth*6,0,singleImageWidth,h))    

    return style

def createListBoxStyle(font, fontcolor, fontcolorover, fontcolorselected, bgcolor,bgcolorselected, itemheight = None, padding = 3, antialias = True):
    if not itemheight:
        itemheight = font.get_ascent()
        
    style = {'font' : font, 'font-color-over':fontcolorover,'font-color-selected': fontcolorselected,
             'bg-color':bgcolor, 'bg-color-selected' : bgcolorselected,
             'item-height':itemheight, 'padding': padding, 'antialias' : antialias}
    
    return style

def createComboBoxStyle(font, image, singleImageWidth, font_color = (0,0,0), borderwidth = 0, bordercolor = (0,0,0), bgcolor = (255,255,255), antialias = True ):
    if image.get_width() < singleImageWidth * 4:
        raise GuiException("The image of the CheckBox must contain 7 pictures for the four states (normal, mouse-over and pressed) for each CheckBox value Checked or Unchecked plus one, the last, for the disabled appearence.")
    
    style = {'font':font, 'font-color': font_color,
             'antialias':antialias, 'bg-color': bgcolor,
             'border-width':borderwidth, 'border-color':bordercolor,
             }
        
    h = image.get_height()
    
    style['normal'] = image.subsurface(Rect(0,0,singleImageWidth,h))
    style['over'] = image.subsurface(Rect(singleImageWidth,0,singleImageWidth,h))
    style['down'] = image.subsurface(Rect(singleImageWidth*2,0,singleImageWidth,h))
    style['disabled'] = image.subsurface(Rect(singleImageWidth*3,0,singleImageWidth,h))    

    return style

### UTILS ###

def wrapText(text, font, width):
    lineWidth = font.size(text)[0]
    if lineWidth > width:
        words = text.split(' ')
        i = 1
        while i < len(words):
            currLine = ' '.join(words[:-i]) 
            if font.size(currLine)[0] <= width:
                return currLine + "\n" + wrapText(' '.join(words[len(words)-i:]),font,width)
            i += 1
    else:
        return text

def drawHTiled(frm, lenght, source, dest):
    "Draws a surface onto another horizontally tiling it"
    sw = source.get_width()
    
    k = lenght // sw
    exceed = lenght - k * sw
    
    for i in xrange(k):
        dest.blit(source, (frm[0] + i * sw, frm[1]))
    
    #Draws exceeding part
    dest.blit(source, (frm[0] + k * sw, frm[1]), pygame.Rect(0,0, exceed , source.get_height()))

def colorLuminosity(color, delta):
    r,g,b = color
    
    a = 255
    
    if len(color) == 4:
        a = color[3]
        
    r += delta
    g += delta
    b += delta
    
    if r < 0 : r = 0
    if g < 0: g = 0
    if b < 0 : b = 0
    if r > 255: r = 255
    if g> 255: g = 255
    if b> 255: b = 255
    
    return r,g,b,a

def mixColors(colorA, colorB):
    
    r1,g1,b1 = colorA
    r2,g2,b2 = colorB
    
    if len(colorA) > 3:
        a1 = colorA[1]
    else:
        a1 = 255
        
    if len(colorB) > 3:
        a2 = colorA[1]
    else:
        a2 = 255            
    
    r3 = min((r1+r2)/2.,  255)
    g3 = min((g1+g2)/2., 255)
    b3 = min((b1+b2)/2., 255)
    a3 = min((a1+a2)/2., 255)
    
    return (r3,g3,b3) if a3 != 255 else (r3,g3,b3,a3)


def center(positionHost, sizeHost, sizeClient):
    return (positionHost[0] + sizeHost[0] / 2 - sizeClient[0] / 2,
            positionHost[1] + sizeHost[1] / 2 - sizeClient[1] / 2)

def renderText(text, font, antialias, color, size, autosize, wordwrap):
    lines = text.split('\n')
    
    #Wordwrapping
    if wordwrap and not autosize:
        for i in xrange(len(lines)):
            line = lines[i]
            del lines[i]
            lines[i:i] = wrapText(line, font, size[0]).split('\n')
    
    #Text Rendering       
    if len(lines) == 1:
        #Single line text
        return font.render(text, antialias, color)
        
    else:
        #Multi line text
        lineHeight = font.get_linesize()
        
        height = lineHeight * len(lines)
        
        width = 0
        lineSurfs = []
        
        for line in lines:
            linesurf = font.render(line, antialias, color)
            lineSurfs.append(linesurf) 
            if linesurf.get_width() > width:
                width = linesurf.get_width()
        
        surf = pygame.Surface((width,height), pygame.SRCALPHA)
        
        for i in xrange(len(lineSurfs)):
            surf.blit(lineSurfs[i], (0,i * lineHeight))
    
        return surf

### CLASSES ###

class GuiException(Exception):
    def __init__(self, message):
        Exception.__init__(self, message)

## WIDGETS ##
class Widget(object):
    #This is default for widgets: by default, every widget is passive to focus, it means
    #it won't be placed in front of others if clicked (like windows).
    
    #General Widget Properties
    HIGH_PRIORITY = False
    
    REFRESH_ON_MOUSE_OVER = True
    REFRESH_ON_MOUSE_DOWN = True
    REFRESH_ON_MOUSE_CLICK = True
    REFRESH_ON_MOUSE_LEAVE = True
    
    GETS_TAB = False
    
    dynamicAttributes = []
    
    def __init__(self, position = (0,0), size = (100,20), parent = None, style = None, enabled = True):
        if not parent:
            raise GuiException("Could not create a new widget with None parent")        
        self.position = position
        self.size = size        
        self.style = style       
        self.enabled = enabled
        self._parent = None
        
        #Sets the desktop in which the widget is
        self.desktop = parent.desktop
    
        self.visible = True
        
        #Logic attributes
        self.mouseover = False
        self.mousedown = False
        self.mouseclick = False
        
        #Callbacks
        self.onMouseOver = None
        self.onMouseDown = None
        self.onMouseLeave = None
        
        self.onClick = None
            
        #Finally refreshes the widget
        self.refresh()
        
        #I don't need a refresh!
        self.needsRefresh = False
        
        self.dynamicAttributes.extend(("size", "style", 'enabled'))
        
        #After refreshing my self for the first time, I add myself to my parent
        self._set_parent(parent)
    
    
    def __setattr__(self, attr, value):
        object.__setattr__(self, attr, value)
        
        if attr in self.dynamicAttributes:
            #Must refresh then
            self.needsRefresh = True
        
    def update(self, topmost):
        if self.enabled:
            
            if self.mouseclick:
                self.mouseclick = False
            
            #Updates informations about mouse
            if not pygame.mouse.b1:
                if self == topmost and not self.mouseover:
                    self._getMouseOver()
                elif self != topmost and self.mouseover:
                    self._loseMouseOver()
            
            #Checks if mouse is over and button is pressed   
            if self.mouseover and mouse.b1 and not self.mousedown:
                #Sets the button is pressed
                self.mousedown = True
                
                #Calls on mouse down event if present
                if self.onMouseDown:
                    self.onMouseDown(self)
                
                #Refreshes if he wants
                if self.REFRESH_ON_MOUSE_DOWN:
                    self.needsRefresh = True
            
            #In this case, button is not pressed but the mouse was pressed before
            elif not mouse.b1 and self.mousedown:
                self.mousedown = False
                
                #If the mouse is on it too, it means widget has been clicked
                if self.mouseover:
                    self.mouseclick = True
                    
                    if self.onClick:
                        self.onClick(self)
                
                if self.REFRESH_ON_MOUSE_CLICK:
                    self.needsRefresh = True
        
        #Refreshes if needed
        if self.needsRefresh:
            self.refresh()
            self.needsRefresh = False
        
    def _getMouseOver(self):
        if self.enabled:
            self.mouseover = True    
            
            if self.onMouseOver:
                self.onMouseOver(self)
            
            if self.REFRESH_ON_MOUSE_OVER:
                    self.needsRefresh = True
    
    def _loseMouseOver(self):
        if self.enabled:
            self.mouseover = False
            
            if self.onMouseLeave:
                self.onMouseLeave(self)
            
            if self.REFRESH_ON_MOUSE_LEAVE:
                    self.needsRefresh = True
            
    def refresh(self):
        pass
    
    #Properties
    def _set_parent(self, parent):
        if self._parent:
            self._parent.remove(self)
        
        self._parent = parent
        
        self._parent.add(self)
        
    parent = property(lambda self: self._parent, _set_parent)
    rect = property(lambda self: Rect(self.position,self.size))
    hasFocus = property(lambda self: self.desktop.focused == self)
    
class Container():    
    def __init__(self):
        self.widgets = []
        self.surf = None
        
        #Explained later
        self._nextPosition = (0,0)
        
        #Contains the optionbox currently checked as true
        self.selectedOptionBox = None
        
    def add(self, widget):       
        self.widgets.append(widget)
        
        #Updates the next free position for widgets
        self._nextPosition = widget.position[0], widget.position[1] + widget.size[1]
    
    def remove(self, widget):
        self.widgets.remove(widget)
    
    def update(self, topmost):
        for widget in self.widgets:
            widget.update(topmost)
        
    def draw(self, surf):
        #Supposing method update was called before this, all widgets have redrawn their
        #private surfaces so they are ready to be drawn on the screen.
        
        #If the widget is cropped by the left or top edge of the screen-container,
        #I copy its surface and let child widgets draw on it, the blit it on screen, otherwise
        #I take the subsurface from the screen and let widgets draw on it which is faster.       
        if self.visible:
            if self.position[0] < 0 or self.position[1] < 0:
                temp_surf = self.surf.copy()
                
                for widget in self.widgets:
                    widget.draw(temp_surf)
                
                surf.blit(temp_surf, self.position)
            else:
                surf.blit(self.surf, self.position)
                
                subsurfrect = self.rect.clip(surf.get_rect())
                
                if subsurfrect.size != (0,0):
                    subsurf = surf.subsurface(subsurfrect)
                           
                    for widget in self.widgets:
                        widget.draw(subsurf)       
    
    def nextPosition(self, spacing):
        return self._nextPosition[0], self._nextPosition[1] + spacing
    
    def findTopMost(self, point):
        topmost = self
        
        for widget in self.widgets:
            if widget.enabled and widget.visible:
                if widget.rect.collidepoint(point):
                    topmost = widget
        
        if hasattr(topmost, 'findTopMost') and topmost != self:
            return topmost.findTopMost( (point[0] - topmost.position[0], point[1] - topmost.position[1]))
        else:
            return topmost
    
    def getCenterPoint(self, size):
        return self.size[0] / 2 - size[0] / 2, self.size[1] / 2 - size[1] / 2
    
    def getScreenPosition(self, position):
        parentPos = self.parent.getScreenPosition(self.position)
        return position[0] + parentPos[0], position[1] + parentPos[1] 
    
class Desktop(Container):
    def __init__(self):
        Container.__init__(self)
        
        #Tricky: TODO
        self.desktop = self
        
        self.size = pygame.display.get_surface().get_size()
        
    def add(self, widget):
        "Adds a widget on the desktop. If it \"gets the focus\", it will be placed on top of present widgets, otherwise behind them."        
        self.focused = widget
        
        if widget.HIGH_PRIORITY:
            self.widgets.append(widget)
        else:
            self.widgets.insert(0, widget)
            
            #Updates the next free position for widgets
            self._nextPosition = widget.position[0], widget.position[1] + widget.size[1]


    def update(self):
        #Checks all the events occurred in last frame
        #Mouse over / click
        pygame.mouse.b1,pygame.mouse.b2,pygame.mouse.b3 = pygame.mouse.get_pressed()
        
        topmost = self.findTopMost(mouse.get_pos())
               
        if pygame.mouse.b1:                    
            if self.focused and self.focused != self:
                if topmost != self.focused.parent:
                    if hasattr(self.focused, 'lostFocus'):
                        self.focused.lostFocus()
                    self.focused = topmost
            else: 
                self.focused = topmost
            topmost = None        
        
        Container.update(self, topmost)
        
        

    def draw(self):
        #Desktop draws directly on screen
        
        #Supposing method update was called before this, all widgets have redrawn their
        #private surfaces so they are ready to be drawn on the screen.
        for widget in self.widgets:
            widget.draw(display.get_surface())
    
    def bringToFront(self, window):
        self.widgets.remove(window)
        self.widgets.append(window)
        
    def getScreenPosition(self, position):   
        return position
    
### WIDGETS ###
class Label(Widget):
    
    REFRESH_ON_MOUSE_OVER  = False
    REFRESH_ON_MOUSE_DOWN = False
    REFRESH_ON_MOUSE_CLICK = False
    REFRESH_ON_MOUSE_LEAVE = False
    
    def __init__(self,  position = (0,0), size = (120,20), parent = None, style = None, text = "Label"):
        #Custom attributes
        self.text = text
        
        self.dynamicAttributes.append("text")
        
        if not style:
            if not defaultLabelStyle:
                import gui
                gui.defaultLabelStyle = {'font-color': (0,0,0), 'font': font.Font(None,18), 'autosize': True, "antialias": True,
                          'border-width': False, 'border-color': (0,0,0), 'wordwrap': False}

            style = defaultLabelStyle            
        
        Widget.__init__(self,position,size,parent,style,enabled = False)
    
    def refresh(self):
        self.surf = renderText(self.text, self.style['font'], self.style['antialias'], self.style['font-color'],
                   self.size, self.style['autosize'], self.style['wordwrap'])
        
        if self.style['autosize']:
            self.size = self.surf.get_size()
            
    def draw(self, surf):
        if self.visible:
            surf.blit(self.surf, self.position, Rect((0,0), self.size))
            if self.style['border-width']:
                draw.rect(surf, self.style['border-color'], self.rect, self.style['border-width'])

class Button(Widget):
    def __init__(self,  position = (0,0), size = (120,20), parent = None, style = None, enabled = True, text = "Button"):
        #Custom attributes
        self.text = text
        
        #Private button attributes
        self.suffix = ""
        
        self.dynamicAttributes.append("text")
        
        if not style:
            if defaultButtonStyle:
                style = defaultButtonStyle
            else:
                raise GuiException("Buttons must have a style.")
        
        #Finally lets the base init
        Widget.__init__(self,position,size,parent,style,enabled)
        
    def refresh(self):
        if not self.enabled and self.style['do-disabled']:
            suffix = '-disabled'
        elif self.mousedown and self.style['do-down']:
            suffix = "-down"
        elif self.mouseover and self.style['do-over']:
            suffix = "-over"
        else:
            suffix = "-normal" 
        
        if suffix != self.suffix:
            self.suffix = suffix
            
            left = self.style['left' + suffix]
            middle = self.style['middle' + suffix]
            right = self.style['right' + suffix]
            
            self.size = (max(self.size[0], left.get_width() + middle.get_width() +
                             right.get_width()), left.get_height())
            
            self.surf = pygame.Surface(self.size, pygame.SRCALPHA)
            
            self.surf.blit(left, (0,0))
            
            drawHTiled((left.get_width(), 0),
                       self.size[0] - left.get_width() - right.get_width(),
                       middle, self.surf)
            
            self.surf.blit(right, (self.size[0] - right.get_width(), 0))
        
        self.textsurf = self.style['font'].render(self.text, True, self.style['font-color'])
        
        
    def draw(self, surf):
        if self.visible:
            surf.blit(self.surf, self.position)
            surf.blit(self.textsurf, (self.position[0] + self.size[0] / 2 - self.textsurf.get_size()[0]/2,
                                      self.position[1] + self.size[1] / 2 - self.textsurf.get_size()[1]/2))

class ImageButton(Widget):      
    def __init__(self,  position = (0,0), parent = None, style = None, enabled = True):
        #Private button attributes
        self.suffix = ""  
        
        if not style:
            if defaultImageButtonStyle:
                style = defaultImageButtonStyle
            else:
                raise GuiException("ImageButtons must have a style.")
        
        size = style['image-normal'].get_size()  
        
        Widget.__init__(self,position,size,parent,style,enabled)
        
    def refresh(self):
        self.size = self.style['image-normal'].get_size()
    
    def draw(self,surf):
        if self.visible:
            if not self.enabled and self.style['do-disabled']:
                suffix = '-disabled'
            elif self.mousedown and self.style['do-down']:
                suffix = "-down"
            elif self.mouseover and self.style['do-over']:
                suffix = "-over"
            else:
                suffix = "-normal"
            
            surf.blit(self.style['image' + suffix], self.position)
    
class OnImageButton(Widget):      
    def __init__(self, img,  position = (0,0), parent = None, style = None, enabled = True):
        #Private button attributes
        self.suffix = ""  
        self.img = img
        
        
        size = self.img.get_size()  
        
        Widget.__init__(self,position,size,parent,style,enabled)
        
    def refresh(self):
        self.size = self.img.get_size()
    
    def draw(self,surf):
        if self.visible:            
            surf.blit(self.img, self.position)
                       
class Window(Widget, Container):
    
    #Widget attributes
    HIGH_PRIORITY = True #Yes, it's a window
    
    REFRESH_ON_MOUSE_OVER  = False
    REFRESH_ON_MOUSE_DOWN = False
    REFRESH_ON_MOUSE_CLICK = False
    REFRESH_ON_MOUSE_LEAVE = False
    
    def __init__(self,  position = None , size = (140,50), parent = None, style = None, text = "Window", closeable = True, shadeable = True):
        if parent.desktop != parent:
            #Parent is not a desktop, wrong way
            raise GuiException("Windows can belong only to Desktops (the parent must be a Desktop)")
        
        #For windows I have to set it before Widget.__init__, most important thing
        self._parent = parent
        self.desktop = parent
        
        if not style:
            if defaultWindowStyle:
                style = defaultWindowStyle
            else:
                raise GuiException("Windows must have a style.")
            
        Container.__init__(self)
        
        #Custom attributes
        if not position:
            position = self.parent.getCenterPoint(size)
            
        self.text = text
        self.shaded = None
        self.surf = None
        self.closeable = closeable
        self.shadeable = shadeable
        self.moving = None
        
        self.dynamicAttributes.extend(["text", "closeable", "shadeable"])
        
        self.closebutton = ImageButton(parent = self, style = style['close-button-style'])
        self.shadebutton = ImageButton(parent = self, style = style['shade-button-style'])
        
        #Callbacks
        self.onClose=None
        self.onMove=None
        self.onMoveStop=None
        self.onShade=None
        self.onUnshade=None
        
        #Creates the image buttons
        ## Close
        self.closebutton.onClick = lambda button:self.close()
        
        ## Shade
        def shadeWindow(button):
            if self.shaded:
                self.unshade()
            else:
                self.shade()
            
        self.shadebutton.onClick = shadeWindow
        
        Widget.__init__(self, position, size, parent, style, text)
        
    def close(self):
        self.parent.remove(self)
        if self.onClose: self.onClose(self)
          
    def shade(self):
        if self.onShade: self.onShade(self)
        if self.shaded: return
        self.shaded = self.size[1]
        self.size = (self.size[0],2*self.style['offset'][0] + self.shadebutton.size[1])
        self.needsRefresh = True
        
    def unshade(self):
        if self.onUnshade: self.onUnshade(self)
        if not self.shaded: return 
        self.size = (self.size[0],self.shaded)
        self.shaded = None
        self.needsRefresh = True
        
    def refresh(self):
        #Reposition of the closebutton if visible
        if self.closeable:
            self.closebutton.visible = True
            self.closebutton.position = (self.size[0] - self.style['offset'][0] - self.closebutton.size[0],
                                     self.style['offset'][1])
        else:
            self.closebutton.visible = False
            
        if self.shadeable:
            self.shadebutton.visible = True
            self.shadebutton.position = (self.size[0] - 2*(self.style['offset'][0] + self.shadebutton.size[0]),
                                     self.style['offset'][1])
        else:
            self.shadebutton.visible = False
        
        #If I don't have a surface or surface size is different from my size, i create a new one
        temp='shaded-' if self.shaded else ''
        if not self.surf or self.size != self.surf.get_size():
            del self.surf
            self.surf = pygame.Surface(self.size, pygame.SRCALPHA)
        
        if self.style[temp+'bg-color']:
            self.surf.fill(self.style[temp+'bg-color'])
        
        if self.style['border-width']:
            draw.rect(self.surf, self.style['border-color'], Rect((0,0), self.size), self.style['border-width'])
            
        self.surf.blit(self.style['font'].render(self.text, True, self.style[temp+'font-color']), self.style['offset'])

    def update(self, topmost):
        
        oldMousedown = self.mousedown
        
        Container.update(self, topmost)
        Widget.update(self, topmost)
        
        if self.moving:
            mx,my = mouse.get_pos()
            mx = mx - self.moving[0]
            my = my - self.moving[1]
             
            self.position = (self.position[0] + mx, self.position[1] + my)
            
            self.moving = mouse.get_pos()
                    
        if not oldMousedown and self.mousedown and self.enabled:
            #Start moving
            self.moving = mouse.get_pos()
            if self.onMove: self.onMove(self)
            
        elif oldMousedown and not self.mousedown:
            #Stop moving
            self.moving = False
            if self.onMoveStop: self.onMoveStop(self)
        
        if self.mousedown and self.enabled:
            self.parent.bringToFront(self)

class TextBox(Widget):
    
    GETS_TAB = True
    
    REFRESH_ON_MOUSE_OVER = False
    REFRESH_ON_MOUSE_LEAVE = False
    REFRESH_ON_MOUSE_DOWN = False
    
    def __init__(self,  position = (0,0), size = (120,20), parent = None, style = None, enabled = True, text = ""):
        if not style:
            if not defaultTextBoxStyle:
                import gui
                gui.defaultTextBoxStyle = {'font': font.SysFont(None, 16), 'font-color':(0,0,0),
                                       'bg-color-normal':(255,255,255), 'bg-color-focus': (230,255,255),
                                       'border-color-normal': (0,0,0),'border-color-focus': (0,50,50),
                                       'border-width': 1, 'appearence': APP_3D, 'antialias': True,
                                       'offset':(4,4)}
            style = defaultTextBoxStyle
            
        self.text = text
        self.currpos = len(text)
        self._textStartX = 0
        self.surf = None
        self.textWidth = 0
        
        pygame.key.set_repeat(250, 40)
                              
        self.dynamicAttributes.extend(["text", "currpos"])
        
        Widget.__init__(self,position,size,parent,style,enabled)
        
    def refresh(self):           
        #Save this information coz it's frequently used
        self.offset = self.style['offset']
        
        if self.size[1] < self.style['font'].get_ascent() + self.offset[1]* 2:
            self.size = self.size[0], self.style['font'].get_ascent() + self.offset[1]* 2
                
        #Creates the surface with the rendered text
        self.textsurf = self.style['font'].render(self.text, self.style['antialias'], self.style['font-color'])
        
        #Creates a new widget surface if None or different size from widget size
        if not self.surf or self.surf.get_size() != self.size:
            self.surf = pygame.Surface(self.size, pygame.SRCALPHA)
        
        if self.hasFocus:
            suffix = "-focus"
        else:
            suffix = "-normal"
        
        #Background
        self.surf.fill(self.style['bg-color' + suffix])
                
        #Calculates the position of the text surface
        textpos =  self.offset[0], self.size[1] / 2. - self.textsurf.get_height() / 2
        
        #Width of the text until the cursor
        cursorWidth = self.style['font'].size(self.text[:self.currpos])[0]
        #X coordinate of the cursor 
        cursorx = cursorWidth + self.offset[0]
        #Total width of the text
        self.textWidth = self.textsurf.get_width()
        
        if cursorWidth - self._textStartX < self.size[0] - self.offset[0] * 2 :
            if cursorx - self._textStartX < 0:
                self._textStartX = max(0, cursorx - (self.size[0] - self.offset[0] * 2))
        else:
            self._textStartX = cursorWidth - (self.size[0] - self.offset[0] * 2)
            
        #Blits the text surface in the appropriate position
        self.surf.blit(self.textsurf, textpos, Rect(self._textStartX ,0, self.size[0] - self.offset[0] * 2, self.textsurf.get_height()))
        
        #Draws the cursor
        cursorx -= self._textStartX
        draw.line(self.surf, (255,255,255), (cursorx ,self.offset[1]),(cursorx , self.size[1] - self.offset[1]))

        #Renders the border
        if self.style['appearence'] == APP_FLAT:
            draw.rect(self.surf, self.style['border-color' + suffix], Rect((0,0), self.size), self.style['border-width'])
        else:
            bgcolor = self.style['bg-color' + suffix]
            color_dark = colorLuminosity(bgcolor,-50)
            color_light = colorLuminosity(bgcolor,+30)
            #color_corner = mixColors(color_dark, color_light)
            
            draw.line(self.surf,color_dark, (0,0), (self.size[0]-2,0)) #TOP
            draw.line(self.surf,color_dark, (0,0), (0,self.size[1]-2)) #LEFT
            draw.line(self.surf,color_light, (1,self.size[1]-1), (self.size[0],self.size[1]-1)) #LEFT
            draw.line(self.surf,color_light, (self.size[0]-1,1), (self.size[0]-1,self.size[1]-1)) #LEFT
                                                   
    def update(self, topmost):
        #Letter entry
        if self.currpos > len(self.text):
            self.currpos = len(self.text)
            
        if self.hasFocus:           
            for e in events:
                if e.type == pygame.KEYDOWN:  
                    if e.key == pygame.K_BACKSPACE:
                        if self.currpos == 0:
                            continue
                        self.text = self.text[:self.currpos-1] + self.text[self.currpos:]
                        self.currpos -= 1
                        if self.currpos < 0:
                            self.currpos = 0
                    elif e.key == pygame.K_DELETE:
                        self.text = self.text[:self.currpos] + self.text[self.currpos+1:]
                    elif e.key == pygame.K_LEFT:
                        self.currpos -= 1
                        if self.currpos < 0:
                            self.currpos = 0
                    elif e.key == pygame.K_RIGHT:
                        self.currpos += 1
                        if self.currpos > len(self.text):
                            self.currpos = len(self.text)
                    elif e.key == pygame.K_HOME:
                        self.currpos = 0
                    elif e.key == pygame.K_END:
                        self.currpos = len(self.text)
                    elif e.key in (pygame.K_RSHIFT, pygame.K_LSHIFT, pygame.K_RETURN):
                        pass
                    else:
                        self.text = self.text[:self.currpos] +  e.unicode + self.text[self.currpos:]
                        self.currpos += 1                   
                    
        Widget.update(self, topmost)
        
    def draw(self, surf):
        if self.visible:
            surf.blit(self.surf, self.position)
    
    def lostFocus(self):
        self.needsRefresh = True
        


class CheckBox(Widget):
        def __init__(self,  position = (0,0), size = (120,20), parent = None, style = None, enabled = True, text = "CheckBox", value = False):
            if not style:
                if defaultCheckBoxStyle:
                    style = defaultCheckBoxStyle
                else:
                    raise GuiException("CheckBoxes must have a style!")

            self.text = text
            self.value = value 
            self.surf = None
                            
            self.dynamicAttributes.extend(["text","value"])
            
            #Callbacks
            self.onValueChanged = None
            
            Widget.__init__(self,position,size,parent,style,enabled)
            
        def update(self, topmost):           
            Widget.update(self, topmost)
            
            if self.mouseclick:
                self.value = not self.value
                self.refresh()
                
                if self.onValueChanged:
                    self.onValueChanged(self)
            
        def refresh(self):           
            if self.enabled:
                prefix = ""
            else:
                prefix = "disabled-"
            
            self.textsurf = renderText(self.text, self.style['font'], self.style['antialias'], self.style[prefix + 'font-color'],
                   (self.size[0], self.size[1]), self.style['autosize'], self.style['wordwrap'])
        
            if self.style['autosize']:
                self.size = (self.textsurf.get_width() + self.style['spacing'] + self.style['checked-normal'].get_width(), max (self.textsurf.get_height(), self.style['checked-normal'].get_height()))
        
        def draw(self, surf):
            if self.visible:
                if not self.enabled:
                    suffix = '-disabled'
                elif self.mousedown:
                    suffix = "-down"
                elif self.mouseover:
                    suffix = "-over"
                else:
                    suffix = "-normal"
                
                if self.value:
                    prefix = "checked"
                else:
                    prefix = "unchecked"
                    
                centerPoint = self.style['spacing'] * 1 + self.position[0]+ self.style['checked-normal'].get_width(), center(self.position, self.size, self.textsurf.get_size())[1]
                
                image = self.style[prefix + suffix]
                imagePoint = self.position[0], center(self.position,self.size, image.get_size())[1]
                
                #Draws the image
                surf.blit(image, imagePoint)
                surf.blit(self.textsurf, centerPoint, Rect((0,0), self.size))
                
                if self.style['border-width']:
                    draw.rect(surf, self.style['border-color'], self.rect, self.style['border-width'])

class OptionBox(Widget):
        def __init__(self,  position = (0,0), size = (120,20), parent = None, style = None, enabled = True, text = "CheckBox", value = False):
            if not style:
                if defaultOptionBoxStyle:
                    style = defaultOptionBoxStyle
                else:
                    raise GuiException("OptionBoxes must have a style!")

            self._parent = None
            self.text = text
            self._value = False
            self.value = value 
            self.surf = None
                            
            self.dynamicAttributes.extend(["text","value"])
            
            #Callbacks
            self.onValueChanged = None
            
            Widget.__init__(self,position,size,parent,style,enabled)
            
        def update(self, topmost):           
            Widget.update(self, topmost)
            
            if self.mouseclick:
                self.value = True

                self.refresh()
                
                if self.onValueChanged:
                    self.onValueChanged(self)
            
        def refresh(self):           
            if self.enabled:
                prefix = ""
            else:
                prefix = "disabled-"
            
            self.textsurf = renderText(self.text, self.style['font'], self.style['antialias'], self.style[prefix + 'font-color'],
                   (self.size[0], self.size[1]), self.style['autosize'], self.style['wordwrap'])
        
            if self.style['autosize']:
                self.size = (self.textsurf.get_width() + self.style['spacing'] + self.style['checked-normal'].get_width(), max(self.textsurf.get_height(), self.style['checked-normal'].get_height()))
        
        def draw(self, surf):
            if self.visible:
                if self.enabled:
                    if self.value:
                        prefix = "checked"
                    else:
                        prefix = "unchecked"
                    
                    if self.mousedown:
                        suffix = "-down"
                    elif self.mouseover:
                        suffix = "-over"
                    else:
                        suffix = "-normal"
                        
                    image = self.style[prefix + suffix]
                else:
                    image = self.style["disabled"]
                    
                centerPoint = self.style['spacing'] * 1 + self.position[0] + self.style['checked-normal'].get_width(), center(self.position, self.size, self.textsurf.get_size())[1]
                
                imagePoint = self.position[0], center(self.position,self.size, image.get_size())[1]
                
                #Draws the image
                surf.blit(image, imagePoint)
                surf.blit(self.textsurf, centerPoint, Rect((0,0), self.size))
                
                if self.style['border-width']:
                    draw.rect(surf, self.style['border-color'], self.rect, self.style['border-width'])

        def _set_value(self, val):
            self._value = val
            
            if val == True:
                if self._parent:
                    self._parent.selectedOptionBox = self
            
            if self._parent:
                for widget in self._parent.widgets:
                    if type(widget) == type(self) and widget != self:
                        widget._value = not self._value
                        if not self._value:
                            self._parent.selectedOptionBox = widget                    
                            break
            
        value = property(lambda self: self._value, _set_value)       
        
class ListBox(Widget):
    
    REFRESH_ON_MOUSE_CLICK = False
    
    def __init__(self,  position = (0,0), size = (120,20), parent = None, style = None, enabled = True, items = []):
        #Custom attributes
        self.items = items
        self.selectedIndex = 0
        self.overedIndex = None
        
        self.dynamicAttributes.append('values')
        self._scrolling = 0
                
        self.surf = None
        
        if not style:
            import gui
            if not gui.defaultListBoxStyle:
                gui.defaultListBoxStyle = {'font':font.Font(None,15), 'font-color': (0,0,0),
                                       'font-color-selected': (0,0,0), 'bg-color': (255,255,255),
                                       'bg-color-selected': (155,155,155),'bg-color-over': (215,215,215),
                                        'border-width': 1,'border-color': (0,0,0), 'item-height': 18,
                                        'padding': 2, 'autosize': False}
            
            style = gui.defaultListBoxStyle
        
        #Callbacks
        self.onItemSelected = None
        
        #Finally lets the base init
        Widget.__init__(self,position,size,parent,style,enabled)

    def moveDown(self):
        temp = min(self.selectedIndex + 1, len(self.items)-1)
        
        if temp != self.selectedIndex:
            self.selectedIndex = temp
            self.needsRefresh = True
        
        if (self.selectedIndex +1)* self.style['item-height'] - self._scrolling > self.size[1] - self.style['padding']:
            #Moves the scrolling so the selected one is the last
            self._scrolling += (self.selectedIndex +1) * self.style['item-height'] - self._scrolling - (self.size[1] - self.style['padding']*2)
    
    def moveUp(self):
        temp = max(0, self.selectedIndex - 1)
        
        if temp != self.selectedIndex:
            self.selectedIndex = temp
            self.needsRefresh = True
            
        if (self.selectedIndex )* self.style['item-height'] - self._scrolling < self.style['padding']:
            #Moves the scrolling so the selected one is the last
            self._scrolling += (self.selectedIndex) * self.style['item-height'] - self._scrolling
                   
    def update(self, topmost):
        Widget.update(self, topmost)
        
        oldSelectedIndex = self.selectedIndex
        
        if self.mouseover:
            my = mouse.get_pos()[1]
            screenPos = self.parent.getScreenPosition(self.position)[1]
            
            tempIndex = max(0,((my - screenPos - self.style['padding'] + self._scrolling) / self.style['item-height']))
               
                
            if tempIndex != self.overedIndex:
                self.overedIndex = tempIndex
                self.needsRefresh = True
            
            if self.mousedown:
                if tempIndex != self.selectedIndex:
                    self.selectedIndex = self.overedIndex
                    self.needsRefresh = True                    
        
            
        if self.hasFocus:
            for e in events:
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_DOWN: self.moveDown()
                    elif e.key == pygame.K_UP: self.moveUp()
                    
                if e.type == pygame.MOUSEBUTTONDOWN:
                    if e.button == 4 and self.mouseover: #Wheel-UP
                        self._scrolling = max(0, self._scrolling - self.style['item-height'])
                        
                    if e.button == 5 and self.mouseover: #Wheel-down
                        self._scrolling = min(self.style['item-height'] * len(self.items) - self.size[1] + self.style['padding'] * 2,
                                              self._scrolling + self.style['item-height'])
                        
                    self.needsRefresh = True
                
        if self.needsRefresh:
            self.needsRefresh = False
            self.refresh()
          
        #Checks if selected index has changed
        if oldSelectedIndex != self.selectedIndex:
          if self.onItemSelected:
            self.onItemSelected(self)
            
    def refresh(self):    
        self._padding = self.style['padding']
        itemheight = self.style['item-height']
        
        maxItemWidth = self.size[0]
        for item in self.items:
            itemWidth = self.style['font'].size(str(item))[0]
            if itemWidth  > maxItemWidth:
                maxItemWidth = itemWidth 
        
        if self.style['autosize']:
            self.size = maxItemWidth, len(self.items) * itemheight 
        
        listsize = self.size[0], len(self.items) * itemheight
                
        if not self.surf or self.surf.get_size() != listsize:
            self.surf = pygame.Surface(listsize, pygame.SRCALPHA)
        
        self.surf.fill (self.style['bg-color'])
        
        for i in xrange(len(self.items)):
            drawRect = True
            if i== self.overedIndex ==self.selectedIndex and self.mouseover:
                fontcolor = self.style['font-color']
                bgcolor = mixColors(self.style['bg-color-over'],self.style['bg-color-selected'])
            if i == self.overedIndex and self.mouseover:
                fontcolor = self.style['font-color']
                bgcolor = self.style['bg-color-over']                
            elif i == self.selectedIndex:
                fontcolor = self.style['font-color-selected']
                bgcolor = self.style['bg-color-selected']
            else:
                fontcolor = self.style['font-color']
                bgcolor = self.style['bg-color']
                drawRect = False
                
            if drawRect:
                draw.rect(self.surf, bgcolor, Rect(0, i * itemheight, self.surf.get_width(), itemheight))
                
            render = self.style['font'].render(str(self.items[i]), True, fontcolor, bgcolor)
            self.surf.blit(render, (2,i * itemheight + itemheight / 2 - render.get_height() /2 ))
    
    
    def draw(self, surf):
        #Background
        draw.rect(surf, self.style['bg-color'] ,  self.rect)
        
        surf.blit(self.surf,(self.position[0] + self._padding, self.position[1]+ self._padding),
                  Rect( (0,self._scrolling), (self.size[0] - self._padding*2, self.size[1] - self._padding*2)))
        
        #Border
        if self.style['border-width']:
            draw.rect(surf, self.style['border-color'] ,  self.rect, self.style['border-width'])
