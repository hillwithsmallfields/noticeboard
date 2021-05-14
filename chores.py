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

    file_locations = {
        # backups and archives
        'archive': "~/archive",
        'backup-iso-format': "backup-%s.iso",
        'backup_isos_directory': "~/isos/backups",
        'common-backups': "~/common-backups",
        'daily-backup-template': "org-%s.tgz",
        'projects-dir': "~/open-projects/github.com",
        'projects-user': "hillwithsmallfields",
        'weekly-backup-template': "common-%s.tgz",
    }
    file_locations = {k: os.path.expanduser(os.path.expandvars(v))
                      for k, v in file_locations.items()}

    update.updates(args.charts,
                   args.begin,
                   args.end,
                   not args.no_externals,
                   args.verbose)
    backup_and_archive.backup_and_archive(file_locations)

if __name__ == '__main__':
    main()
