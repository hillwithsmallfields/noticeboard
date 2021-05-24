#!/usr/bin/python3

import os
import sys

my_projects = os.path.dirname(sys.path[0])

for project in ("noticeboard", "JCGS-emacs", "JCGS-org-mode", "qs"):
    print("updating", project)
    os.chdir(os.path.join(my_projects, project))
    os.system("git pull")

print("updated lifehacking projects")
