#!/usr/bin/env python3

import argparse
import datetime
import json
import os
import prefixed
import psutil
import re
import socket
import sys
import subprocess
import time

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--list-files", "-l", action='store_true')
    parser.add_argument("--keep-days", "-k", type=int)
    parser.add_argument("--wipeout", "-w", action='store_true')
    parser.add_argument("--trim", "-t", default="2G")
    return vars(parser.parse_args())

def get_live_command_lines_matching(matching):
    """Get the command lines for current processes running a given program."""
    return [cmdline
            for cmdline in (proc.cmdline()
                            for proc in (psutil.Process(pid) for pid in psutil.pids())
                            if proc.status() != 'zombie')
            if cmdline and cmdline[0].endswith(matching)]

def get_option_value(cmdline, option):
    """Get the value for a selected command-line option."""
    pattern = "--%s=(.+)" % option
    for i, v in enumerate(cmdline):
        if v == option:
            return (cmdline[i+1] if i < len(cmdline) else None)
        if (m := re.match(pattern, v)):
            return m.group(1)
    return None

def get_motion_config_filename():
    """Get the filename in current use as a motion config."""
    motions = get_live_command_lines_matching("motion")
    if len(motions) > 1:
        raise RuntimeError("More than one motion process")
    if len(motions) == 0:
        raise RuntimeError("No motion process")
    return get_option_value(motions[0], "-c")

def get_config_value(filename, key):
    """Get a value from a motion config filename."""
    with open(filename) as instream:
        for line in instream:
            parts = line.split()
            if parts:
                if parts[0] == key:
                    return parts[1]
    return None

def get_clips_dir():
    """Get the clips directory in current use."""
    return get_config_value(get_motion_config_filename(), "target_dir")

def run_on_host(hostname, command):
    """Run a command on a specified host."""
    if socket.gethosthame() == hostname:
        return subprocess.run(command).stdout
    else:
        return subprocess.run(["ssh", hostname, command]).stdout

def file_details(filename):
    """Return some details of a file as a dictionary."""
    stat = os.stat(filename)
    return {'filename': filename,
            'size': stat.st_size,
            'created': datetime.datetime.fromtimestamp(stat.st_mtime).isoformat()}

def full_filenames(directory):
    """Return the full names of all the regular files in a directory."""
    return [s for s in (os.path.join(directory, r)
                        for r in os.listdir(directory))
            if os.path.isfile(s)]

def get_files_details(directory):
    """Return the details of all the regular files in a directory."""
    return [file_details(s) for s in full_filenames(directory)]

def keep_days_in_dir(keep_days=7, clips_dir=None):
    """Keep only a given number of days back in a clips directory."""
    cutoff = time.time() - keep_days*24*60*60
    deleted = 0
    kept = 0
    failed = 0
    for name in full_filenames(clips_dir or get_clips_dir()):
        if os.stat(name).st_mtime < cutoff:
            try:
                os.remove(name)
                deleted += 1
            except Exception as e:
                failed += 1
        else:
            kept += 1
    return {'deleted': deleted,
            'failed_to_delete': failed,
            'kept': kept}

def directory_size(directory):
    return (prefixed.Float(subprocess.run(["du", "-s", directory],
                                          capture_output=True,
                                          encoding='utf8')
                           .stdout
                           .split('\t')
                           [0]))

def trim_dir(directory, trim_to="4Gb"):
    """Trim a clips directory to a given size."""
    limit = prefixed.Float(trim_to.removesuffix("b"))
    filenames = sorted(full_filenames(directory),
                       key=lambda filename: os.stat(filename).st_ctime,
                       reverse=True)
    while (filenames and (directory_size(directory) > limit)):
        try:
            filename = filenames.pop()
            os.remove(filename)
        except:
            print("Could not delete", filename, "while trimming directory", directory, "to", trim_to)

def motion_main(list_files, keep_days, wipeout, trim):
    clips_dir = get_config_value(get_motion_config_filename(),
                                 "target_dir")
    if list:
        json.dump(get_files_details(clips_dir),
                  sys.stdout)
    if wipeout:
        deleted = 0
        failed = 0
        for filename in full_filenames(clips_dir):
            try:
                os.remove(filename)
                deleted += 1
            except:
                failed += 1
        json.dump({'deleted': deleted,
                   'failed_to_delete': failed}, sys.stdout)
    if keep_days:
        json.dump(keep_days_in_dir(keep_days, clips_dir),
                  sys.stdout)
    if trim:
        trim(trim, clips_dir)

if __name__ == "__main__":
    motion_main(**get_args())
