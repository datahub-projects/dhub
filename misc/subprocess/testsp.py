import subprocess as sp
from threading import Thread
from queue import Queue,Empty
import time
import random

def getabit(o,q):
    for c in iter(lambda:o.read(1),b''):
        q.put(c)
    o.close()

def getdata(q):
    r = b''
    while True:
        try:
            c = q.get(False)
        except Empty:
            break
        else:
            r += c
    return r

pobj = sp.Popen('python3 called.py',stdin=sp.PIPE,stdout=sp.PIPE,shell=True)
q = Queue()
t = Thread(target=getabit,args=(pobj.stdout,q))
t.daemon = True
t.start()

while True:
    print('Sleep for 1 second...')
    time.sleep(1)#to ensure that the data will be processed completely
    print('Data received:' + getdata(q).decode())
    if not t.isAlive():
        break
    in_dat = "BOOM" if random.random()>.5 else "BOOM BOOM"
    pobj.stdin.write(bytes(in_dat,'utf-8'))
    pobj.stdin.write(b'\n')
    pobj.stdin.flush()
