import os, sys, argparse, datetime
from dateutil.parser import parse as parsedate
import get_pip

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(help='commands')

    reqs_args = subparsers.add_parser('reqs')
    reqs_args.add_argument("--_reqs_", default=True)
    reqs_args.add_argument("--package")
    reqs_args.add_argument("--import")
    reqs_args.add_argument("--file")
    reqs_args.add_argument("--date", default="3000-1-1")

    args = parser.parse_args()

    if hasattr(args, "_reqs_"):
        b4 = parsedate(args.date)
        print ("REQS", args, b4)
        if args.package:
            version, date = get_pip.get_latest(args.package, b4)
            print ("{0}=={1}   #released {2}".format(args.package, version, date.ctime()))
        elif args.file:
            f=open(args.file)
            for row in f.readlines():
                row=row.strip()
                if not row:
                    continue
                if row[0]=='#':
                    continue
                if row[0]=='-':
                    print ("Skipping", row)
                row=row.split("==")[0]
                version, date = get_pip.get_latest(row, b4)
                print("{0}=={1}   #released {2}".format(args.package, version, date.ctime()))