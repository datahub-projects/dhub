#!/usr/bin/env python3
import os, sys, argparse, datetime
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
from dhub.runrun import git_status, get_author, get_username, get_branch

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

rem_args = subparsers.add_parser('remote')
rem_args.add_argument("url")
rem_args.add_argument("--debug", action="store_true")


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

elif command=="remote":
    print ("Connecting to", args.url)
    from subprocess import call, PIPE
    call(['ssh', args.url], stdin=sys.stdin, stdout=sys.stdout)

else:
    parser.print_help()