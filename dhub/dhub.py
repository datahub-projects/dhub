#!/usr/bin/env python3
import os, sys, argparse, json, datetime, subprocess
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
from dhub.runrun import git_status, get_author, get_username, get_branch, get_repo, runner

os.chdir(opath)

bless_term = Terminal()

def _print_green(s, **kw):
    print (bless_term.green(s), **kw)

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
proc_args.add_argument("--sync", action="store_true")
proc_args.add_argument("--dumb", action="store_true")
proc_args.add_argument("--debug", action="store_true")


args = parser.parse_args()

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
        sshopts = '-tt -4'
        if args.port:
            sshopts += ' -p {0}'.format(args.port)
        shell = "ssh {0} {1}".format(sshopts, url)
    else:
        shell = "ssh -tt -4 localhost"
    print ("CMD", shell)

    if args.source:
        f = open(args.source)
        sub = runner(shell)
        out = sub.interact()
        if "Permission denied" in out:
            print ("Problem logging in to %s" % url)
        else:
            print(out, end='')
            for row in f.readlines():
                row = row.rstrip()
                print (row, end='')
                out = sub.interact(row)
                print (out, end='')
        f.close()

    elif args.dumb:
        sub = runner(shell)
        out = sub.interact()
        while True:
            rows = out.split("\n")
            for row in rows[:-1]:
                print (row)
            for row in rows[-1:]:
                print (row.upper(), end='')
            inp = input('')
            out = sub.interact(inp)

    elif args.sync:
        repo = get_repo()
        branch = get_branch()
        home = os.path.expanduser('~')
        cwd = os.getcwd()
        if cwd.find(home) != 0:
            print ("Home directory mismatch: {0} does not start with {1}".format(cwd, home))
        else:
            rwd = cwd[len(home):]
            if rwd[0]=='/':
                rwd = rwd[1:]
            print(repo, branch, rwd)
            sub = runner(shell)
            out = sub.interact()
            if "Permission denied" in out:
                print ("Problem logging in to %s" % url)
            else:
                out = sub.interact("cd %s; pwd" % rwd)
                print (out, end='')
                out = sub.interact("source ./venv/bin/activate; pwd")
                print (out, end='')
                out = sub.interact("pip install -r requirements.txt")
                print (out, end='')
                out = sub.interact("git checkout {0}".format(branch))
                if not out.find('fatal')==0:
                    print (out, end='')
                    out = sub.interact("git pull")
                    print (out, end='')
                    out = sub.interact("git log -n 1")
                    print (out, end='')
                    out = sub.interact("python3 dhub/dhub.py reqs --package mido")
                    print (out, end='')

    else:
        subprocess.call(shell.replace("-T", '').split())
    print ("Exit dhub")

else:
    parser.print_help()