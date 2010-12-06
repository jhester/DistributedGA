import threading
import os
import time

class launcher(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
    
    def run(self):
        os.system('cd ~/362/DistributedGA/src\npython client.py gecko1.cs.clemson.edu 5555')

list = []
for i in range(15):
    j = launcher()
    j.start()
    list.append(j)
    time.sleep(0.5)
