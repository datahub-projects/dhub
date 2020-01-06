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
            sub = r.split()[:1]
            sub.reverse()
            subs.append(sub)
    return subs

def get_branch():
    out, err = git("git rev-parse --abbrev-ref HEAD")
    return out