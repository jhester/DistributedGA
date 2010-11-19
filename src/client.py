import socket
import sys
import os
import random
import time
import pickle

import constant

#don't be hatin
if not len(sys.argv) == 3:
    print "Usage python client.py <host> <port>"
    sys.exit()

#store host and port from command line
host = sys.argv[1]
port = int(sys.argv[2])

#try and connect to our server
try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host,port))
    print "Connected on "+str(host)+":"+str(port)
except:
    print "ERROR: Try to connect to server FAILED"

#send client code
s.send(str(constant.constant_class.clientcode))

#main loop
s.settimeout(10)
while 1:
    data = s.recv(4048).strip()
    data = pickle.loads(data)
    
    time.sleep(0.25)
    s.send(str(int(random.random()*4)))

    os.system('clear')

    print "---------------------------"
    for i in data:
        line = ""
        for j in i:
            if j == 0:
                line += "\033[30m" #black
                    
            line += " " + str(j)
            line += "\033[0m" #white
        print line
    print "---------------------------"
                                                                   
s.close()
