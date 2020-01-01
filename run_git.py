from run import run

def git(cmd):
    print ("--> git", cmd)
    out, good = run(["git"] + cmd.split())
    if not good:
        err = "ERROR -- git command did not complete"
        print (err, file=sys.stderr)
        out += "\n\n" + err
    return out, not good