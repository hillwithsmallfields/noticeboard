#!/usr/bin/python3

import datetime
import os
import sys

LAST_PULLED_FILE = "/tmp/last_pulled"
# a day, but allow for a bit of clock jitter:
UPDATE_INTERVAL = 23.5 * 60 * 60

def updated_lately(filename, recentness=3600):
    now = datetime.datetime.now()
    recent = (os.path.isfile(filename)
              and (now - datetime.datetime.fromtimestamp(os.stat(filename).st_mtime)).total_seconds() < recentness)
    with open(filename, 'w') as f:
        f.write(now.isoformat() + "\n")
    return recent

my_projects = os.path.dirname(sys.path[0])

if not updated_lately(LAST_PULLED_FILE, UPDATE_INTERVAL):
    for project in ("noticeboard", "JCGS-emacs", "JCGS-org-mode", "qs"):
        print("updating", project)
        os.chdir(os.path.join(my_projects, project))
        os.system("git pull")
    print("Updated lifehacking projects")
else:
    print("Skipped updating lifehacking projects, as was done within the past period")
