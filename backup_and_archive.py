#!/usr/bin/python3

import argparse
import datetime
import glob
import os
import time

import lifehacking_config

CONFIGURATION = {}

def CONF(*keys):
    return lifehacking_config.lookup(CONFIGURATION, *keys)

def make_tarball(tarball, parent_directory, of_directory):
    if not os.path.isfile(tarball):
        command = "tar cz -C %s %s > %s" % (parent_directory, of_directory, tarball)
        print("backup command is", command)
        os.system(command)

def latest_file_matching(template):
    files = glob.glob(template)
    return files and sorted(files, key=os.path.getmtime)[-1]

def backup_and_archive(force=False):
    global CONFIGURATION
    CONFIGURATION = lifehacking_config.load_config()
    common_backups = CONF('backups', 'common-backups')
    print("common_backups", common_backups)
    if common_backups == "" or common_backups.startswith("$"):
        common_backups = os.path.expandvars("$HOME/common-backups")
        print("common_backups now", common_backups)
    daily_backup_template = CONF('backups', 'daily-backup-template')
    weekly_backup_template = CONF('backups', 'weekly-backup-template')
    today = datetime.date.today()
    make_tarball(os.path.join(common_backups, daily_backup_template % today.isoformat()),
                 os.path.expandvars("$COMMON"),
                 "org")
    weekly_backup_day = CONF('backups', 'weekly-backup-day')
    if not isinstance(weekly_backup_day, int):
        try:
            weekly_backup_day = time.strptime(weekly_backup_day, "%A").tm_wday
        except ValueError:
            weekly_backup_day = time.strptime(weekly_backup_day, "%a").tm_wday
    if force or today.weekday() == weekly_backup_day:
        make_tarball(os.path.join(common_backups, weekly_backup_template % today.isoformat()),
                     os.path.expandvars("$HOME"), "common")
    if force or today.day == int(CONF('backups', 'monthly-backup-day')):
        backup_isos_directory = CONF('backups', 'backup_isos_directory')
        if backup_isos_directory == "" or backup_isos_directory.startswith("$"):
            backup_isos_directory = os.path.expandvars("$HOME/isos")
        monthly_backup_name = os.path.join(backup_isos_directory, CONF('backups', 'backup-iso-format') % today.isoformat())
        if not os.path.isfile(monthly_backup_name):
            # make_tarball("/tmp/music.tgz", os.path.expandvars("$HOME"), "Music")
            make_tarball("/tmp/github.tgz",
                         CONF('backups', 'projects-dir'),
                         CONF('backups', 'projects-user'))
            files_to_backup = [
                latest_file_matching(os.path.join(common_backups, daily_backup_template % "*")),
                latest_file_matching(os.path.join(common_backups, weekly_backup_template % "*")),
                # too large for genisoimage:
                # "/tmp/music.tgz",
                "/tmp/github.tgz"]
            # prepare a backup of my encrypted partition, if mounted
            if os.path.isdir(os.path.expandvars("/mnt/crypted/$USER")):
                os.system("backup-confidential")
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
            print("Time to take a monthly backup of", files_to_backup, "into", monthly_backup_name)
            os.system("genisoimage -o %s %s" % (monthly_backup_name, " ".join(files_to_backup)))
            print("made backup in", monthly_backup_name)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", "-f",
                        action='store_true',
                        help="""Make a backup even if it's not backup day.""")
    args = parser.parse_args()

    backup_and_archive(args.force)

if __name__ == "__main__":
    main()
