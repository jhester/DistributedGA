import socket
import sys
import os
import random
import time
import pickle

#don't be hatin
if not len(sys.argv) == 3:
    print "Usage python client.py <host> <port>"
    sys.exit()

#store host and port from command line
host = sys.argv[1]
port = int(sys.argv[2])

#try and connect to our server
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host,port))
print "Connected on "+str(host)+":"+str(port)

#main loop
s.settimeout(2)
while 1:
    data = s.recv(4048).strip()
    data = pickle.loads(data)
    
    time.sleep(0.25)
    s.send(str(int(random.random()*4)))

    os.system('clear')

    for i in data:
        print i
        
s.close()
