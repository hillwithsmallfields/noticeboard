#!/usr/bin/env python3

import argparse
import os
import sys

from lifehacking_config import config
import managed_directory
import backup_and_archive
import motion

# my_projects = os.path.dirname(sys.path[0])
# sys.path.append(os.path.join(my_projects, "qs/update"))
# import update

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--charts-dir", default=os.path.expanduser("~/private_html/dashboard"),
                        help="""Directory to write charts into.""")
    parser.add_argument("--begin",
                        help="""Earliest date to chart.""")
    parser.add_argument("--end",
                        help="""Latest date to chart.""")
    parser.add_argument("--read-externals", "-x", action='store_true',
                        help="""Read data from external servers""")
    parser.add_argument("--force", "-f", action='store_true',
                        help="""Do the updates even if the files have been updated
                        within the last day.""")
    parser.add_argument("--nightly", action='store_true')
    parser.add_argument("--weekly", action='store_true')
    parser.add_argument("--no-updates", action='store_true')
    parser.add_argument("--no-backup", action='store_true')
    parser.add_argument("--testing", action='store_true',
                        help="""Use an alternate directory which can be reset.""")
    parser.add_argument("--verbose", "-v", action='store_true',
                        help="""Be more verbose.""")
    return vars(parser.parse_args())

def nightly_chores():
    """Do some nightly tasks."""
    backup_and_archive.nightly_archive()
    clips_directory = motion.get_clips_directory()
    removed = managed_directory.trim_directory(clips_directory,
                                               config('motion', 'retain'))
    keeping = managed_directory.keep_days_in_directory(clips_directory,
                                                       config('motion', 'days'))
    print('(message "Removed %d files to keep clips directory down to %s and %d because older than %d days")'
          % (len(removed), config('motion', 'retain'), keeping['deleted'], config('motion', 'days')))

def weekly_chores():
    """Do some weekly tasks."""
    backup_and_archive.weekly_archive()
    
def chores(charts_dir,
           begin, end,
           read_externals,
           nightly, weekly,
           no_updates,
           no_backup,
           verbose, force, testing):

    """Do various daily 'admin' tasks: merge incoming quantification data
    from various sources, prepare a dashboard page with charts on it, and
    do some backups."""

    if nightly:
        nightly_chores()
    if weekly:
        weekly_chores()

    if not no_updates:
        update.updates(charts_dir,
                       begin,
                       end,
                       read_externals,
                       verbose=verbose,
                       force=force,
                       testing=testing)

    # TODO: recursive listing of directories, or tar and md5sum them, to detect damage

    if not no_backup:
        backup_and_archive.backup_and_archive()

if __name__ == '__main__':
    chores(**get_args())
