from run import run

def git(cmd, show=False, debug=False):
    if debug:
        print ("--> git", cmd)
    out, good = run(["git"] + cmd.split(), showoutput=show)
    if not good:
        err = "ERROR -- git command did not complete"
        print (err, file=sys.stderr)
        out += "\n\n" + err
    return out, not good