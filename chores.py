#!/usr/bin/python3

import argparse
import os
import sys

import backup_and_archive

my_projects = os.path.dirname(sys.path[0])
print("my_projects is", my_projects)
sys.path.append(os.path.join(my_projects, "qs/update"))
import update

def main():

    """Do various daily 'admin' tasks: merge incoming quantification data
    from various sources, prepare a dashboard page with charts on it, and
    do some backups."""

    parser = argparse.ArgumentParser()
    parser.add_argument("--charts", default=os.path.expanduser("~/private_html/dashboard"),
                        help="""Directory to write charts into.""")
    parser.add_argument("--begin",
                        help="""Earliest date to chart.""")
    parser.add_argument("--end",
                        help="""Latest date to chart.""")
    parser.add_argument("--no-externals", action='store_true',
                        help="""Don't pester external servers""")
    parser.add_argument("--force", action='store_true',
                        help="""Do the updates even if the files have been updated
                        within the last day.""")
    parser.add_argument("--testing", action='store_true',
                        help="""Use an alternate directory which can be reset.""")
    parser.add_argument("--verbose", "-v", action='store_true',
                        help="""Be more verbose.""")
    args = parser.parse_args()

    update.updates(args.begin,
                   args.end,
                   not args.no_externals,
                   verbose=args.verbose,
                   force=args.force,
                   testing=args.testing)

    # TODO: recursive listing of directories, or tar and md5sum them, to detect damage

    backup_and_archive.backup_and_archive()

if __name__ == '__main__':
    main()
