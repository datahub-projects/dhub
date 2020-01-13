import os
from ver_run import run
from blessings import Terminal
bless_term = Terminal()


def print_red(s, **kw):
    print (bless_term.red(s), **kw)
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

#
# get full pathnames of active subdirectories
#
def get_subs():
    out, err = git("submodule status")
    subs = []
    for r in out.split("\n"):
        if r.strip():
            sub = r.split()[:2]
            sub.reverse()
            sub[1] = sub[1].replace("+", "").replace("-", "")
            subs.append(sub)
    return subs

def get_branch():
    out, err = git("rev-parse --abbrev-ref HEAD")
    return out

def is_ver_project():
    opath = os.path.abspath(".")
    cur = opath
    while True:
        if os.path.exists(".ver_root"):
            os.chdir(opath)
            return True
        os.chdir("..")
        up1 = os.path.abspath(".")
        if up1 == cur:
            os.chdir(opath)
            return False
        cur = up1

def chdir_root():
    opath = os.path.abspath(".")
    cur = opath
    top = None
    while True:
        if os.path.exists(".ver_root"):
            top = cur
            break
        os.chdir("..")
        up1 = os.path.abspath(".")
        if up1 == cur:
            break
        cur = up1
    if top:
        os.chdir(top)
    else:
        print ("Not a ver project")
        os.chdir(opath)
        raise Exception("ERROR -- not a ver project")