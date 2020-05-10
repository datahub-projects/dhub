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
    return git("log -1 --pretty=format:'%an'")

def get_username():
    return git("config --get user.name")

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


if __name__ == "__main__":
    print("test run.py")
    cmd = sys.argv[1:]
    s, err = run(cmd, timeout=10, showoutput=False)
    print("output----------\n", s)
    print("end output------")
    print("completed:", err)
