import os, sys, argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(help='commands')

    reqs_args = subparsers.add_parser('reqs')
    reqs_args.add_argument("--_reqs_", default=True)
    reqs_args.add_argument("--print")

    args = parser.parse_args()

    if hasattr(args, "_reqs_"):
        print ("REQS", args)
