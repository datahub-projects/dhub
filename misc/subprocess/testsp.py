import subprocess as sp
from threading import Thread
from queue import Queue, Empty
import time


def getabit(o, q):
    for c in iter(lambda:o.read(1), b''):
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


def run_interactive(cmd, input_func):
    pobj = sp.Popen(cmd, stdin=sp.PIPE, stdout=sp.PIPE, shell=True)
    q = Queue()
    t = Thread(target=getabit, args=(pobj.stdout, q))
    t.daemon = True
    t.start()

    while True:
        # print('Sleep for 1 second...')
        time.sleep(.4)#to ensure that the data will be processed completely
        o_dat = getdata(q).decode()
        # print('Data received:' + o_dat)
        if not t.isAlive():
            break
        in_dat = input_func(o_dat)
        pobj.stdin.write(bytes(in_dat, 'utf-8'))
        pobj.stdin.write(b'\n')
        pobj.stdin.flush()
    time.sleep(1)
    pobj.wait(15)


def test_func(s):
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


if __name__=="__main__":
    cmd = "python testri.py"
    print (cmd)
    run_interactive(cmd, test_func)

    print ("DONE")