#!/usr/bin/python3

"""Pull updates of the noticeboard system.

This should be run under an "ssh-agent" shell,
hence it not being part of the main noticeboard chores system.

In the "daily" mode, it waits until between 2 and 3 a.m. to do the
update, does the update, and then execs the python interpreter running
the same program, thus forcing a reload in case of this program having
been updated by the "git pull".

"""

import argparse
import datetime
import os
import random
import sys
import time

LAST_PULLED_FILE = "/tmp/last_pulled"
UPDATE_INTERVAL = 2 * 60 * 60

def updated_lately(filename, recentness=3600):
    now = datetime.datetime.now()
    recent = (os.path.isfile(filename)
              and (now - datetime.datetime.fromtimestamp(os.stat(filename).st_mtime)).total_seconds() < recentness)
    with open(filename, 'w') as f:
        f.write(now.isoformat() + "\n")
    return recent

script_dir = sys.path[0]
script = os.path.join(script_dir, sys.argv[0])
my_projects = os.path.dirname(script_dir)

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--daily", action='store_true')
    parser.add_argument("--force", "-f", action='store_true')
    return vars(parser.parse_args())

def do_update(force=False):
    if force or not updated_lately(LAST_PULLED_FILE, UPDATE_INTERVAL):
        for project in ("noticeboard", "JCGS-emacs", "JCGS-org-mode", "qs", "coimealta"):
            print("updating", project)
            os.chdir(os.path.join(my_projects, project))
            os.system("git pull")
        os.chdir(script_dir)
        os.system("cat *.crontab | crontab -")
        print("Updated lifehacking projects")
    else:
        print("Skipped updating lifehacking projects, as was done within the past period")

def main(daily=False, force=False):
    if daily:
        now = datetime.datetime.now()
        time.sleep(((now
                     # tomorrow
                     + datetime.timedelta(days=1))
                    # between 2 and 3 a.m.
                    .replace(hour=2, minute=random.randint(0, 59), second=random.randint(0, 59))
                    - now)
                   .total_seconds())
        do_update()
        os.execlp(script, "--daily")
    else:
        do_update(force)

if __name__ == "__main__":
    main(**get_args())
