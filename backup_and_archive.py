#!/usr/bin/python3

import argparse
import datetime
import glob
import os
import subprocess
import time

from lifehacking_config import config
import managed_directory

DVD_FULL = 4700000000

def make_tarball(tarball, of_directory):
    if not os.path.isfile(tarball):
        subprocess.run(["tar", "--create", "--gzip",
                        "--dereference",
                        "--directory", os.path.dirname(of_directory),
                        "--file", tarball,
                        os.path.basename(of_directory),
                        ])

def archive_and_trim_archives(directory,
                              template,
                              archives,
                              archives_size):
    archive_directory = os.path.expandvars(archives)
    archive_filename = os.path.join(archive_directory,
                                    template % (datetime.date.today().isoformat()))
    print("archive filename is", archive_filename, "and archive directory is", archive_directory, "and directory being archived is", directory)
    make_tarball(archive_filename, os.path.expandvars(directory))
    managed_directory.trim_directory(archive_directory,
                                     archives_size)

def nightly_archive():
    archive_and_trim_archives(
        config('general', 'org-directory'),
        config('archive', 'daily-backup-template'),
        config('archive', 'org-archive-directory'),
        config('archive', 'org-archives-size'))

def weekly_archive():
    archive_and_trim_archives(
        config('general', 'sync-directory'),
        config('archive', 'weekly-backup-template'),
        config('archive', 'sync-archive-directory'),
        config('archive', 'sync-archives-size'))
    
def write_iso_to_dvd(iso):
    """Write a DVD image to the drive if there's a blank disk in it."""
    if os.path.exists("/dev/dvdrw"):
        command = "wodim " + iso
        if ("""wodim: Cannot read TOC header"""
            in subprocess.run(["wodim", "-toc"],
                              check=False, # suppress exception
                              text=True,
                              capture_output=True).stderr):
            os.system(command)
        else:
            print("Please put a blank DVD in the drive and run:", command)
    else:
        print("Writable DVD drive not found")

def latest_file_matching(template):
    """Return the name of the most recently modified file matching the glob template."""
    files = glob.glob(template)
    return files and sorted(files, key=os.path.getmtime)[-1]

def get_next_backup_file():
    """Stub for working through a round-robin of extra files to back up."""
    return None

def backup_to_dvd(synced_snapshots,
                  daily_backup_template, weekly_backup_template):
    """Prepare an ISO image of my latest backups."""
    backup_isos_directory = os.path.expandvars(config('backups', 'backup-isos-directory'))
    if backup_isos_directory == "":
        backup_isos_directory = os.path.expandvars("$HOME/isos")
    os.makedirs(backup_isos_directory, exist_ok=True)
    monthly_backup_name = os.path.join(
        backup_isos_directory,
        config('backups', 'backup-iso-format') % datetime.date.today().isoformat())
    # this assumes it's a different filename each time:
    if os.path.isfile(monthly_backup_name):
        print("Backup file", monthly_backup_name, "already exists")
    else:
        # make_tarball("/tmp/music.tgz", os.path.expandvars("$HOME/Music"))
        make_tarball("/tmp/github.tgz",
                     os.path.join(config('backups', 'projects-dir'),
                                  config('backups', 'projects-user')))
        files_to_backup = [
            latest_file_matching(os.path.join(synced_snapshots, daily_backup_template % "*")),
            latest_file_matching(os.path.join(synced_snapshots, weekly_backup_template % "*")),
            # too large for genisoimage:
            # "/tmp/music.tgz",
            "/tmp/github.tgz"]
        # prepare a backup of my encrypted partition, if mounted
        if os.path.isdir(os.path.expandvars("/mnt/crypted/$USER")):
            os.system("backup-confidential " + config('backups', 'gpg-recipient'))
        # look for the output of https://github.com/hillwithsmallfields/JCGS-scripts/blob/master/backup-confidential
        confidential_backup = latest_file_matching("/tmp/personal-*.tgz.gpg")
        if confidential_backup:
            files_to_backup.append(confidential_backup)
            digest = confidential_backup.replace('gpg', 'sha256sum')
            if os.path.isfile(digest):
                files_to_backup.append(digest)
            sig = digest + ".sig"
            if os.path.isfile(sig):
                files_to_backup.append(sig)
        # We might have room to back up some more files:
        stuffed = False
        while True:
            os.system("genisoimage -o %s %s" % (monthly_backup_name, " ".join(files_to_backup)))
            if stuffed:
                # we exceeded the limit last time, and have now
                # removed the file that took us over the limit, so
                # now we're full:
                break
            if os.path.getsize(monthly_backup_name) >= DVD_FULL:
                # we have just exceeded the limit this time, so back off one file:
                files_to_backup = files_to_backup[:-1]
                stuffed = True
            else:
                # pick something else to include in the backup,
                # maybe on a round robin system:
                next_file_to_backup = get_next_backup_file()
                if next_file_to_backup:
                    files_to_backup.append(next_file_to_backup)
                else:
                    # we couldn't find anything else to include in
                    # the backup:
                    break
        backup_size = os.path.getsize(monthly_backup_name)
        print("made backup in", monthly_backup_name,
              "with size", backup_size,
              "bytes which is", backup_size / (1024 * 1024), "Mib")
    return monthly_backup_name

def backup_and_archive(force=False):
    """Take backups, and make an archive, if today is one of the specified days."""
    nightly_archive()
    weekly_backup_day = config('backups', 'weekly-backup-day')
    if not isinstance(weekly_backup_day, int):
        try:
            weekly_backup_day = time.strptime(weekly_backup_day, "%A").tm_wday
        except ValueError:
            weekly_backup_day = time.strptime(weekly_backup_day, "%a").tm_wday
    if force or today.weekday() == weekly_backup_day:
        weekly_archive()
    if force or today.day == int(config('backups', 'monthly-backup-day')):
        if 'ISOS' not in os.environ:
            os.environ['ISOS'] = os.path.expandvars("$HOME/isos")
        iso = backup_to_dvd(synced_snapshots, daily_backup_template, weekly_backup_template)
        print("backup writing flag is", config('backups', 'write-iso-to-dvd'))
        if config('backups', 'write-iso-to-dvd'):
            write_iso_to_dvd(iso)

def main():
    """Make snapshots and archives."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", "-f",
                        action='store_true',
                        help="""Make a backup even if it's not backup day.""")
    args = parser.parse_args()

    backup_and_archive(args.force)

if __name__ == "__main__":
    main()
