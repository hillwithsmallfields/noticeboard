"""Archive a directory."""

import datetime
import os
import subprocess

import managed_directory

def archive(directory, 
            archives,
            archives_size):
    archive_directory = os.path.expandvars(archives)
    archive_filename = os.path.join(archive_directory,
                                     (os.path.basename(directory)
                                      + "-"
                                      + (datetime.datetime.now(timespec='seconds')
                                         .replace(':', '-')
                                         .replace('T', '-'))
                                      + ".tgz"))
    subprocess.run(["tar", "czf",
                    archive_filename,
                    os.path.expandvars(directory)])
    managed_directory.trim_directory(archive_directory,
                                     archives_size)
                   
