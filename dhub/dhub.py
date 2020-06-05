#!/usr/bin/env python3
import os, sys, argparse, json, time, datetime, subprocess
from dateutil.parser import parse as parsedate
from blessings import Terminal

#
#the BDOL does not admire scripts which are also importable modules
#well frack him
#
#so absolute imports work in script mode, we need to import from the parent folder
opath = os.path.abspath(".")
abspath = os.path.abspath(__file__)
abspath = abspath[:abspath.rfind('/') + 1]
os.chdir(abspath)
abspath = os.path.abspath("..")
sys.path.insert(0, abspath)

from dhub import get_pip
from dhub.mod_sync import sync, mod
from dhub.runrun import git_status, get_author, get_username, get_branch, get_repo, run, runner

os.chdir(opath)

bless_term = Terminal()

def _print_green(s, **kw):
    print (bless_term.green(s), **kw)

def _print_purple(s, **kw):
    print (bless_term.magenta(s), **kw)

parser = argparse.ArgumentParser(description=__doc__)
subparsers = parser.add_subparsers(help='followed by --help for command-specific options')

reqs_args = subparsers.add_parser('reqs')
reqs_args.add_argument("--package")
reqs_args.add_argument("--importname")
reqs_args.add_argument("--file")
reqs_args.add_argument("--date", default="3000-1-1")
reqs_args.add_argument("--unstable", action="store_true")
reqs_args.add_argument("--debug", action="store_true")

sync_args = subparsers.add_parser('sync')
sync_args.add_argument("--debug", action="store_true")
# sync_args.add_argument("--insist")

mod_args = subparsers.add_parser('mod')
mod_args.add_argument("--message")
mod_args.add_argument("--debug", action="store_true")
mod_args.add_argument("--insist", action="store_true")

proc_args = subparsers.add_parser('process')
proc_args.add_argument("--ssh")
proc_args.add_argument("--name")
proc_args.add_argument("--port")
proc_args.add_argument("--source")
proc_args.add_argument("--sync")
proc_args.add_argument("--command", default="python entrypoint.py")
proc_args.add_argument("--git") #=path to proj or .
proc_args.add_argument("--wake") #instance ID
proc_args.add_argument("--dumb", action="store_true")
proc_args.add_argument("--debug", action="store_true")


args = parser.parse_args()

def wake_up(inst):
    if inst:
        cmd = ("aws ec2 start-instances --instance-ids %s" % inst).split()
        cmd2 = ("aws ec2 describe-instance-status --include-all-instances --instance-ids %s" % inst).split()
        _print_purple(' '.join(cmd))
        out, ok = run(cmd)
        print (out)
        print ("Waiting for %s to arise" % inst)
        while True:
            out, ok = run(cmd2)
            j = json.loads(out)
            print ("AWAIT:", j['InstanceStatuses'][0]['InstanceId']==inst, j['InstanceStatuses'][0]['InstanceState']['Name']=='running')
            if j['InstanceStatuses'][0]['InstanceId']==inst and j['InstanceStatuses'][0]['InstanceState']['Name']=='running':
                break

            time.sleep(5)
        time.sleep(20)
        print ("Instance %s is up & running" % inst)

#FIXME should be done solely on remote
def go_to_sleep(inst):
    cmd = "aws ec2 stop-instances --instance-ids %s" % inst
    _print_purple(cmd)
    sys.stdout.flush()
    os.system(cmd)

def subdo(sub, s, expect=None, show=True):
    _print_green("\n-~> %s" % s.rstrip())
    done = False
    ret = ""
    first = True
    while not done:
        out, done = sub.interact(s, expect)
        if done:
            if show:
                print(out, end='')
        elif out:
            if first:
                first = False               #first response==shi-tty echo
            else:
                if show:
                    print (out, end='')
        ret += out
        s = None
    return ret

def sync_to(base, paths, ssh):
    if not ssh:
        ssh = "localhost"
    for p in paths.strip().split(','):
        cmd = "rsync -vrltzu ./{1} {2}:{0}/".format(base, p, ssh)
        _print_purple("RSYNC_TO: " + cmd)
        os.system(cmd)

def sync_from(base, paths, ssh):
    if not ssh:
        ssh = "localhost"
    for p in paths.strip().split(','):
        cmd = "rsync -vrltzu {2}:{0}/{1} ./".format(base, p, ssh)
        _print_purple("RSYNC_FROM: " + cmd)
        os.system(cmd)

command=None
if len(sys.argv)>1:
    command=sys.argv[1]                          #really? is this the only way?

if command=="reqs":
    b4 = parsedate(args.date)
    # print ("REQS", args, b4)
    if args.package:
        version, date = get_pip.get_latest(args.package, b4, not args.unstable, args.debug)
        if not version:
            print ("# ERROR: package not found: {0}".format(args.package))
            exit()
            0/0
        print("{0: <40} #released {1}".format("{0}=={1}".format(args.package, version), date.ctime()))
    elif args.file:
        f=open(args.file)
        for pkg in f.readlines():
            pkg=pkg.strip()
            if not pkg:
                continue
            if pkg[0]=='#':
                continue
            if pkg[0]=='-':
                print ("Skipping", pkg)
                continue
            pkg=pkg.split("==")[0]
            version, date = get_pip.get_latest(pkg, b4, not args.unstable, args.debug)
            if not version:
                continue
            print("{0: <40} #released {1}".format("{0}=={1}".format(pkg, version), date.ctime()))
    elif args.importname:
        print ("Coming soon: cv2 implies openCV")

    else:
        print ("Coming soon: use pipreqs to create requirements list from scratch")

elif command=="mod":
    if get_author() != get_username() and not args.insist:
        _print_green("Different author --insist if you are sure")
        # print (get_author(), get_username())
    else:
        if get_branch()=="master" and not args.insist:
            _print_green("This operation will rebase the master branch --insist if you are sure")
        else:
            _print_green("Rewriting tip (most recent) commit & pushing to remote")
            mod(message=args.message, show=args.debug, debug=args.debug)

elif command=="sync":
    _print_green("Synchronizing local git repository and working tree to remote/origin")
    sync(show=args.debug, debug=args.debug)

elif command=="process":
    url = args.ssh
    #
    #  alias
    #
    if url:
        if args.name:
            fn = "{0}/.dhub/names/{1}".format(os.path.expanduser("~"), args.name)
            f = open(fn, 'w')               #FIXME create folders
            f.write(url)
            f.close()
        fn = "{0}/.dhub/names/{1}".format(os.path.expanduser("~"), url)
        if os.path.exists(fn):
            f = open(fn)
            url = f.read().strip()
            f.close()
        sshopts = '-tt -4 -o ConnectTimeout=10 -o BatchMode=yes -o ServerAliveInterval=60'
        if args.port:
            sshopts += ' -p {0}'.format(args.port)
        shell = "ssh {0} {1}".format(sshopts, url)
    else:
        shell = "ssh -tt -4 localhost"
    # print ("SHELL COMMAND:", shell)

    if args.source:
        f = open(args.source)
        wake_up(args.wake)
        sub = runner(shell)
        out, err = sub.first()
        print(out, end='')
        if not err:
            for row in f.readlines():
                row = row.rstrip()
                print (row, end='')
                out = sub.interact(row)
                print (out, end='')
        f.close()

    elif args.dumb:
        wake_up(args.wake)
        sub = runner(shell)
        out, err = sub.first()
        if err:
            print(out, end='')
        else:
            while True:
                rows = out.split("\n")
                for row in rows[:-1]:
                    print (row)
                for row in rows[-1:]:
                    print ("DUMB:", row, end='')
                inp = input('')
                if inp=='exit':
                    break
                out = sub.interact(inp)
        sub.exit()

    elif args.git:
        sub = None
        for i in range(1): #allows break
            repo = get_repo()
            if not repo:
                print ("Not a git repository")
                break
            proj = repo[repo.rfind('/')+1:] #FIXME make me smarter -- multi-folder project
            if args.git == '.':
                if not args.ssh:
                    print ("You probably don't want to remove your local checkout")
                    break
            else:
                proj = args.git
            branch = get_branch()
            home = os.path.expanduser('~')
            wake_up(args.wake)
            for tri in range(3):
                sub = runner(shell)
                _print_purple (shell)
                out, err = sub.first()
                if not err:
                    break
                print(out, end='')
                print ("failed connection on attempt %d of 3" % (tri+1))
            if err:
                break
            print ("Connection successful")
            subdo(sub, "rm -fr %s" % proj)
            out = subdo(sub, "git clone --single-branch --branch %s %s %s" % (branch, repo, proj), expect=["yes/no", "repository exists"])
            if "yes/no" in out:
                print ("\n\nDHUB: Must establish the legitimacy of the git repository's public key.")
                print("Log in to the remote server and try 'git fetch' to establish the key in known_hosts.")
                break
            if "repository exists" in out:
                print ("\n\nDHUB: Need to set up server's git public key for this repository.")
                print("Alternatively, use read-only publicly accessible repo.")
                break
            subdo(sub, "cd %s" % proj)
            if "fatal" in out:
                break
            print ()
            if args.sync:
                sync_to(proj, args.sync, args.ssh)
            print ("Checking for Dockerfile")
            out = subdo(sub, """python3 -uc 'import os; print(os.path.exists("Dockerfile"))'""", show=False)
            if "False" in out:
                print ("No docker file found; setting up virtualenv")
                subdo(sub, "virtualenv -p python3 venv")
                subdo(sub, "source ./venv/bin/activate")
                out = subdo(sub, "pip install -r requirements.txt")
                if out.find('ERROR')>=0:
                    print ("quitting on error", end='')
                    break
                subdo(sub, args.command)
            else:
                print("Dockerfile found; building docker image")
                subdo(sub, "docker build . -t %s" % proj)
                if args.sync:
                    # out, pr = sub.interact("""python3 -c 'import os; print(os.path.abspath("%s"))'""" % args.sync)
                    out = subdo(sub, """python3 -uc 'import os; print(os.path.abspath("%s"))'""" % args.sync, show=False)
                    # print ("\n\n\nRET:==>%s<==\n\n\n"%out.replace("\r","]"))
                    abs = out.strip().split("\n")[-2].strip()
                    print ("==>%s"%abs.replace("\r","]"))
                    subdo(sub, "docker run --rm -it -v {0}:/{1} {2}".format(abs, args.sync, proj))
                else:
                    subdo(sub, "docker run --rm -it %s" % proj)
            if args.sync:
                print()
                sync_from(proj, args.sync, args.ssh)
        if sub:
            sub.exit()
        if args.wake:
            go_to_sleep(args.wake)
    else:
        subprocess.call(shell.replace("-T", '').split())
    print ("\nExit dhub")

else:
    parser.print_help()
