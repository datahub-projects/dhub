import  subprocess, time, os, sys, re
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


def stdout_thread(o, q):
    def getchar():
        return o.read(1)

    for c in iter(getchar, b''):
        q.put(c)
    o.close()


def get_sub_stdout(q):
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

def escape_ansi(line):
    ansi_escape = re.compile(r'(\x9B|\x1B\[)[0-?]*[ -/]*[@-~]')
    return ansi_escape.sub('', line)

def parse_prompt(out):
    if out:
        return escape_ansi(out).replace("\r", '').strip().split("\n")[-1]
    return out

class runner:
    def __init__(self, cmd):
        self.pobj = sp.Popen(cmd.split(), stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.STDOUT)
        self.q = Queue()
        self.t = Thread(target=stdout_thread, args=(self.pobj.stdout, self.q))
        self.t.daemon = True
        self.t.start()
        self.in_dat = ''
        self.prompt = ''
    #
    # call interact with user input, returns next process text+prompt
    #
    def interact(self, cmd=None):
        if cmd != None:                                   #typically None for first interaction to get prompt
                                                          #if '', still need to write to stdin to keep rolling ball
            # print ("===%s==="%cmd)
            self.pobj.stdin.write(bytes(cmd, 'utf-8'))
            self.pobj.stdin.write(b'\n')
            try:
                self.pobj.stdin.flush()
            except:
                return ''
            self.in_dat = cmd
        o_dat = get_sub_stdout(self.q).decode('utf8')
        # print ("                                      O_DAT(0)-->%s<--" % o_dat.replace("\r",']').replace("\n",'|'))
        p = parse_prompt(o_dat)
        # print("                                       LOOP(0):", "->%s<-->%s<-" % (p, self.prompt), p != self.prompt)
        lastdat = time.time()
        ptry = 42
        # print ("WHILE"); sys.stdout.flush()
        while ptry and (not o_dat or p.find(self.prompt)==0):
            # print ("                     TIME: %s PTRY: %s" % (time.time()-lastdat,ptry))
            #Use advanced machine learning algorithms to ascertain if we have a prompt:
            # print(" " * 80 + "CHECK: |%s| p=%s self=%s p[-1]=%s t=%s" % (
            #         not not p and not self.prompt and p[-1] in '$#>:' and time.time() - lastdat > .6,
            #         not not p, not self.prompt, p[-1:], time.time() - lastdat > .6))
            if p and not self.prompt and p[-1] in '$#>:' and time.time()-lastdat > .6:  # Does it quack AND oink?
                self.prompt = p
                # print ("                                   SET:", p)
                break
            else:
                ptry -= 1
                if not ptry:
                    # print("                                   GIVE UP capturing prompt-->%s<--" % p)
                    break
            o_new = get_sub_stdout(self.q).decode('utf8')
            o_dat += o_new
            if o_new:
                lastdat = time.time()
            # print ("                                      O_DAT(1)-->%s<--" % o_dat.replace("\r", ']').replace("\n", '|'))
            time.sleep(.1)
            p = parse_prompt(o_dat)
            # print ("                                       LOOP:(1)", "->%s<-->%s<-" % (p, self.prompt),p!=self.prompt)
        if p==self.prompt:
            # print("                                   PROMPT:", p)
            pass
        # remove echo:
        # if o_dat.find(self.in_dat+"\r\n")==0:
        #     o_dat=o_dat[len(self.in_dat)+2:]
        if self.prompt=='':
            return o_dat, "NO_PROMPT"
        return o_dat


if __name__=="__main__":
    cmd = "cd"
    # cmd = "echoz foo"
    print (cmd, end="\n\n")
    run = runner(cmd)
    o = run.interact()                                  #get initial startup spam + prompt
    print (o, end='')
    while True:
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
