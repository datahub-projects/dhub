import subprocess as sp
from threading import Thread
from queue import Queue, Empty
import time
import random

# def getabit(o, q):
#     for c in iter(lambda:o.read(1), b''):
#         q.put(c)
#     o.close()

t0=time.time()
def getline(o, q):
    for c in iter(lambda:o.readline(), b''):
        print ("---%s %s---" % (c, time.time()-t0))
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

pobj = sp.Popen('python3 called.py', stdin=sp.PIPE, stdout=sp.PIPE, shell=True)
q = Queue()
t = Thread(target=getline, args=(pobj.stdout, q))
t.daemon = True
t.start()

def parse_output(s):
    print ("----------PARSE------------")
    print (s)
    print ("~~~~~~~~~~~~~~~~~")
    for L in s.split():
        try:
            N = int(L.strip())
        except:
            pass
    print ("RESULT:", N)
    print ("----------/PARSE------------")
    return "BOOM " * N

while True:
    # print('Sleep for 1 second...')
    time.sleep(.4)#to ensure that the data will be processed completely
    o_dat = getdata(q).decode()
    # print('Data received:' + o_dat)
    if not t.isAlive():
        break
    in_dat = parse_output(o_dat)
    pobj.stdin.write(bytes(in_dat, 'utf-8'))
    pobj.stdin.write(b'\n')
    pobj.stdin.flush()
