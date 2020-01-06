import os
from run import run
#
# run a git command, capture the output
#
def git(cmd, show=False, debug=False):
    if debug:
        print ("--> git", cmd)
    out, good = run(["git"] + cmd.split(), showoutput=show)
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

def chdir_root():
    opath = os.path.abspath(".")
    cur = opath
    top = None
    while True:
        if os.path.exists(".git"):
            top = cur
        os.chdir("..")
        up1 = os.path.abspath(".")
        if up1 == cur:
            break
        cur = up1
    if top:
        os.chdir(top)
    else:
        print ("Not a ver path")
        os.chdir(opath)