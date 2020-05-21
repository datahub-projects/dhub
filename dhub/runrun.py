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

def get_repo():
    out, err = git("remote -v")
    return out.split()[1]

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
    def getchar():
        return o.read(1)

    for c in iter(getchar, b''):
        q.put(c)
    o.close()


def getdata(q):
    r = b''
    while True:
        try:
            c = q.get(False)
        except Empty:
            # print ("   EMPTY")
            break
        else:
            # print ("   DATA")
            r += c
    return r


def test_func(s):
    if not s:
        return ""
    # print ("----------PARSE------------")
    # print (s)
    # print ("~~~~~~~~~~~~~~~~~")
    N = 7
    for L in s.split():
        try:
            N = int(L.strip())
        except:
            pass
    # print ("RESULT:", N)
    # print ("----------/PARSE------------")
    return "BOOM " * N


class runner:
    def __init__(self, cmd):
        self.pobj = sp.Popen(cmd.split(), stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.STDOUT)
        self.q = Queue()
        self.t = Thread(target=getabit, args=(self.pobj.stdout, self.q))
        self.t.daemon = True
        self.t.start()
        self.in_dat = ''
    #
    # call interact with user input, returns next process text+prompt
    #
    def interact(self, cmd=None):
        trip = 3
        if cmd:                                         #typically None for first interaction to get prompt
            # print ("===%s==="%cmd)
            self.pobj.stdin.write(bytes(cmd, 'utf-8'))
            self.pobj.stdin.write(b'\n')
            try:
                self.pobj.stdin.flush()
            except:
                return ''
            self.in_dat = cmd
        o_dat = getdata(self.q).decode('utf8')
        print("                                         O_DAT",o_dat.replace("\n","|").replace("\r",']'))
        while not o_dat:
            o_dat = getdata(self.q).decode('utf8')
            print("                                         O_DAT", o_dat.replace("\n","|").replace("\r",']'))
            time.sleep(1.1)
            if not self.t.isAlive():
                trip-=1
                if trip==0:
                    return ''
            # else:
            #     print("-",trip)

        if o_dat.find(self.in_dat+"\r\n")==0:
            print ("                                    YEP")
            o_dat=o_dat[len(self.in_dat)+2:]
        else:
            print ("                                    NOPE", "-->%s<--"%self.in_dat)
        return o_dat


if __name__=="__main__":
    cmd = "cd"
    # cmd = "echoz foo"
    print (cmd, end="\n\n")
    run = runner(cmd)
    o = run.interact()                                  #get initial startup spam + prompt
    print (o, end='')
    for i in range(44):
        resp = test_func(o)
        cmd = "Response %s %s" % (i, resp)
        print ("--> %s" % cmd)
        o = run.interact(cmd)                           #respond to process output+prompt with next command
        if not o:
            break
        print(o, end='')
    print ("DONE")

# if __name__ == "__main__":
#     print("test run.py")
#     cmd = sys.argv[1:]
#     s, err = run(cmd, timeout=10, showoutput=False)
#     print("output----------\n", s)
#     print("end output------")
#     print("completed:", err)
