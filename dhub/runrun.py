import  subprocess, time, os, sys
from blessings import Terminal
bless_term = Terminal()

MAXLINES=100

def print_red(s, **kw):
    print (bless_term.red(s), **kw)

def run(*args, **kw):
    # print ("DBG", args, kw)
    if 'showoutput' in kw:
        showoutput = kw['showoutput']
        # print("showoutput:", showoutput)
        del kw['showoutput']
    else:
        showoutput = False
    if 'timeout' in kw:
        timeout = float(kw['timeout'])
        if showoutput:
            print("running", args[0], "with timeout:", timeout, end=' ')
        del kw['timeout']
    else:
        timeout = 0
    try:
        if not timeout:
            timeout = 10**10
        # print ("args:", args)
        proc = subprocess.Popen(*args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        t0 = time.time()
        out = ""
        complete = False
        while time.time() < t0 + timeout:
            line = proc.stdout.readline().decode('utf8')
            # print ("DBG", type(out), type(line))
            out += line
            i = 0
            while line != "":
                if showoutput:
                    sys.stdout.write(line)
                i += 1
                if i >= MAXLINES:
                    break
                line = proc.stdout.readline().decode('utf8')
                out += line
            if proc.poll() != None:
                complete = True
                #get all output
                line = proc.stdout.readline().decode('utf8')
                out += line
                while line != "":
                    if showoutput:
                        sys.stdout.write(line)
                    sys.stdout.write(line)
                    line = proc.stdout.readline().decode('utf8')
                    out += line
                sys.stdout.flush()
                break
##                sys.stdout.write(".")
##                sys.stdout.flush()
            time.sleep(0.2)
        if not complete:
            proc.kill()

    except subprocess.CalledProcessError as e:
        out = e.output
    return out, complete

#
# run a git command, capture the output
#
def git(cmd, show=False, debug=False):
    if debug:
        print_red ("git %s" % cmd)
    if hasattr(cmd, "lower"):
        cmd = cmd.split()
    out, good = run(["git"] + cmd, showoutput=show)
    if not good:
        err = "ERROR -- git command did not complete"
        print (err, file=sys.stderr)
        out += "\n\n" + err
    return out, not good


def get_branch():
    out, err = git("rev-parse --abbrev-ref HEAD")
    return out.strip()

def get_author():
    return git("log -1 --pretty=format:'%an'")[0].strip().replace("'", "")

def get_username():
    return git("config --get user.name")[0].strip()

def git_status(show=False, debug=False):
    out, err = git("status --porcelain", show=show, debug=debug)
    changes=0
    for row in out.split("\n"):
        row = row.strip()
        if not row:
            continue
        if row[:2] != "??":
            changes += 1
    return changes

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
    in_dat=""
    while True:
        # print('Sleep for 1 second...')
        time.sleep(.4)#to ensure that the data will be processed completely
        o_dat = getdata(q).decode()
        if not o_dat:
            break
        # print("~%s~" % o_dat)
        if o_dat.find(in_dat+"\n")==0:
            o_dat=o_dat[len(in_dat)+1:]
        # print ("LEN:", len(in_dat))
        rows = o_dat.split("\n")
        rows = "\n$ ".join(rows)
        print(rows, end='')
        if t.isAlive():
            in_dat = input_func(o_dat)
            print ("> %s"%in_dat)
            pobj.stdin.write(bytes(in_dat, 'utf-8'))
            pobj.stdin.write(b'\n')
            pobj.stdin.flush()
    time.sleep(1)
    pobj.wait(15)


def test_func(s):
    # print ("----------PARSE------------")
    # print (s)
    # print ("~~~~~~~~~~~~~~~~~")
    for L in s.split():
        try:
            N = int(L.strip())
        except:
            pass
    # print ("RESULT:", N)
    # print ("----------/PARSE------------")
    return "BOOM " * N


if __name__=="__main__":
    cmd = "python testri.py"
    print (cmd)
    run_interactive(cmd, test_func)

    print ("DONE")

# if __name__ == "__main__":
#     print("test run.py")
#     cmd = sys.argv[1:]
#     s, err = run(cmd, timeout=10, showoutput=False)
#     print("output----------\n", s)
#     print("end output------")
#     print("completed:", err)
