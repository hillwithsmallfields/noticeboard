#!/usr/bin/python3

import argparse
import os
import sys

my_projects = os.path.dirname(sys.path[0])
print("my_projects is", my_projects)
sys.path.append(os.path.join(my_projects, "qs/qs"))
import update

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--charts", default=os.path.expanduser("~/private_html/dashboard"),
                        help="""Directory to write charts into.""")
    parser.add_argument("--begin",
                        help="""Earliest date to chart.""")
    parser.add_argument("--end",
                        help="""Latest date to chart.""")
    parser.add_argument("--no-externals", action='store_true',
                        help="""Don't pester external servers""")
    parser.add_argument("--verbose", "-v", action='store_true',
                        help="""Be more verbose.""")
    args = parser.parse_args()

    update.updates(args.charts,
                   args.begin,
                   args.end,
                   not args.no_externals,
                   args.verbose)

if __name__ == '__main__':
    main()
