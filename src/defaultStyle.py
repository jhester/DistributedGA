import pygame


def init(gui):
    #Surface Loading
    buttonsurf = pygame.image.load("../data/gui/button.png").convert_alpha()
    closesurf = pygame.image.load('../data/gui/closebutton.png').convert_alpha()
    shadesurf = pygame.image.load('../data/gui/shadebutton.png').convert_alpha()
    checksurf = pygame.image.load('../data/gui/checkbox.png').convert_alpha()
    optionsurf = pygame.image.load('../data/gui/optionbox.png').convert_alpha()
    combosurf = pygame.image.load('../data/gui/combobox.png').convert_alpha()
    
    #Default gui font
    gui.defaultFont = pygame.font.SysFont("Arial", 12)
    
    #Label Style
    gui.defaultLabelStyle = {'font-color': (255,255,255),
                          'font': gui.defaultFont,
                          'autosize': True,
                          "antialias": True,
                          'border-width': 0,
                          'border-color': (255,255,255),
                          'wordwrap': False}
    
    #Button style
    gui.defaultButtonStyle = gui.createButtonStyle(gui.defaultFont, (0,0,0), buttonsurf,
                                                   4,1,4,4,1,4,4,1,4,4,1,4)
    
    #Close button style
    closeButtonStyle = gui.createImageButtonStyle(closesurf, 20)
    
    #Close button style
    shadeButtonStyle = gui.createImageButtonStyle(shadesurf, 20)
    
    #Window style
    gui.defaultWindowStyle = {'font': gui.defaultFont,
                            'font-color': (255,255,255),
                            'bg-color' : (0,0,0,255),
                            'shaded-font-color': (255,200,0),
                            'shaded-bg-color' : (100,0,0,100),
                            'border-width': 1,
                            'border-color': (150,150,150, 255),
                            'offset': (5,5),
                            'close-button-style': closeButtonStyle,
                            'shade-button-style': shadeButtonStyle
                            }
    
    #TextBox style
    gui.defaultTextBoxStyle = {'font': gui.defaultFont,
                               'font-color':(255,255,255),
                               'bg-color-normal':(55,55,55),
                               'bg-color-focus': (70,70,80),
                               'border-color-normal': (0,0,0),
                               'border-color-focus': (0,50,50),
                               'border-width': 1,
                               'appearence': gui.APP_3D,
                               'antialias': True,
                               'offset':(4,4)}
    
    #CheckBox style
    gui.defaultCheckBoxStyle = gui.createCheckBoxStyle(gui.defaultFont, checksurf, 12, (255,255,255),
                                                       (100,100,100), autosize = True)
    
    #Optionbox style
    gui.defaultOptionBoxStyle = gui.createOptionBoxStyle(gui.defaultFont, optionsurf, 12, (255,255,255),
                                                     (100,100,100), autosize = True)
    
    #ListBox style
    gui.defaultListBoxStyle = {'font': gui.defaultFont,
                               'font-color': (255,255,255),
                               'font-color-selected': (0,0,0),
                               'bg-color': (55,55,55),
                               'bg-color-selected': (160,180,200),
                               'bg-color-over': (60,70,80),
                               'border-width': 1,
                               'border-color': (0,0,0),
                               'item-height': 18,
                               'padding': 2,
                               'autosize': False}
    
    #ComboBox style
    gui.defaultComboBoxStyle = gui.createComboBoxStyle(gui.defaultFont, combosurf, 15, (255,255,255),
                                                       borderwidth = 1, bordercolor = (31,52,78),
                                                       bgcolor = (55,55,55))
    
