from run import run

def git(cmd):
    print ("--> git", cmd)
    return run("git", cmd)