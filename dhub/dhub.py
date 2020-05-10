import os, sys, argparse, datetime
from dateutil.parser import parse as parsedate
import get_pip
from mod_sync import sync, mod
from runrun import git_status
from blessings import Terminal
bless_term = Terminal()

def print_green(s, **kw):
    print (bless_term.green(s), **kw)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(help='are available commands (first position, no hyphens)')

    reqs_args = subparsers.add_parser('reqs')
    reqs_args.add_argument("--package")
    reqs_args.add_argument("--importname")
    reqs_args.add_argument("--file")
    reqs_args.add_argument("--date", default="3000-1-1")

    sync_args = subparsers.add_parser('sync')
    sync_args.add_argument("--debug", action="store_true")
    # sync_args.add_argument("--insist")

    mod_args = subparsers.add_parser('mod')
    mod_args.add_argument("--debug", action="store_true")
    # mod_args.add_argument("--insist")
    mod_args.add_argument("--message")

    args = parser.parse_args()

    command=None
    if len(sys.argv)>1:
        command=sys.argv[1]                          #really? is this the only way?

    if command=="reqs":
        b4 = parsedate(args.date)
        # print ("REQS", args, b4)
        if args.package:
            version, date = get_pip.get_latest(args.package, b4)
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
                pkg=pkg.split("==")[0]
                version, date = get_pip.get_latest(pkg, b4)
                print("{0: <40} #released {1}".format("{0}=={1}".format(pkg, version), date.ctime()))
        elif args.importname:
            print ("Coming soon: cv2 implies openCV")

        else:
            print ("Coming soon: use pipreqs to create requirements list from scratch")

    elif command=="mod":
        if not(args.message or git_status()):
            print_green("Nothing to do")
        else:
            print_green("Rewriting tip (most recent) commit & pushing to remote")
            mod(message=args.message, show=args.debug, debug=args.debug)

    elif command=="sync":
        print_green("Synchronizing local git repository and working tree to remote/origin")
        sync(show=args.debug, debug=args.debug)