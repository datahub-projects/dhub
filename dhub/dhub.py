import os, sys, argparse, datetime
from dateutil.parser import parse as parsedate
import get_pip

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(help='are available commands (first position, no hyphens)')

    reqs_args = subparsers.add_parser('reqs')
    reqs_args.add_argument("--package")
    reqs_args.add_argument("--importname")
    reqs_args.add_argument("--file")
    reqs_args.add_argument("--date", default="3000-1-1")

    sync_args = subparsers.add_parser('sync')
    sync_args.add_argument("--insist")

    args = parser.parse_args()
    cmd=sys.argv[1]                          #really? is this the only way?

    if cmd=="reqs":
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

    elif cmd=="sync":
        print("Coming soon: sync to remote")
