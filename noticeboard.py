#!/usr/bin/env python3

# Program for my noticeboard hardware

# See README.md for details

import datetime
import functools
import os
import subprocess
import re
import select
import shlex
import sys
import time
import yaml

from noticeboardhardware import NoticeBoardHardware

# This is overwritten from /etc/noticeboard.conf if it's available
config = {
    'delays': {
        'lamp': 0.01,
        'motor': 0.01,
        'main_loop': 1.0,
        'pir_delay': 2.0,
        'step_max': 200},
    'expected_occupancy': {
        # default for a 9-5 worker who stays in at weekends
        'Monday': ["06:00--08:30",
                   "17:30--23:30"],
        'Tuesday': ["06:00--08:30",
                    "17:30--23:30"],
        'Wednesday': ["06:00--08:30",
                      "17:30--23:30"],
        'Thursday': ["06:00--08:30",
                     "17:30--23:30"],
        'Friday': ["06:00--08:30",
                   "17:30--23:30"],
        'Saturday': ["08:00--23:30"],
        'Sunday': ["08:00--23:30"]},
    'camera': {
        'duration': 180,
        'directory': "/var/spool/camera"},
    'pir_log_file': "/var/log/pir"
}

camera = None

def convert_interval(interval_string):
    """Convert a string giving start and end times into a tuple.
    For the input "07:30--09:15" the output would be (450, 555)."""
    matched = re.match("([0-2][0-9]):([0-5][0-9])--([0-2][0-9]):([0-5][0-9])", interval_string)
    return (((int(matched.group(1))*60 + int(matched.group(2))),
             (int(matched.group(3))*60 + int(matched.group(4))))
            if matched
            else None)

manual_at_home = False
manual_away = False

def expected_at_home():
    """Return whether there is anyone expected to be in the house."""
    # todo: use key-hook sensor
    # todo: see whether desktop computer is responding
    # todo: see whether users' phone is in range
    if manual_at_home:
        return True
    if manual_away:
        return False
    when = datetime.datetime.now()
    what_time = when.hour * 60 + when.minute
    for interval in expected_at_home_times[['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'][when.weekday()]]:
        if interval is None:
            continue
        if what_time >= interval[0] and what_time <= interval[1]:
            return True
    return False

photographing_duration = None
photographing = False

def handle_possible_intruder():
    """Actions to be taken when the PIR detects someone when no-one is expected to be in the house."""
    global photographing
    when = datetime.datetime.now()
    photographing = when + photographing_duration
    with open(config['pir_log_file'], 'w+') as logfile:
        logfile.write(datetime.datetime.now().isoformat() + "\n")
    # todo: send a remote notification e.g. email with the picture

def quit():
    """Tell the main loop to quit."""
    global running
    running = False

def show_help():
    """List the commands."""
    maxlen = 1 + functools.reduce(max, map(len, actions.keys()))
    for command_name in sorted(actions.keys()):
        docstring = actions[command_name].__doc__
        if docstring is None:
            docstring = "Undocumented"
        print(command_name + ' '*(maxlen - len(command_name)), docstring)

actions = {
    "auto",
    "away",
    "extend",
    "help",
    "home",
    "off",
    "on",
    "photo",
    "play",
    "quench",
    "quit",
    "report",
    "retract",
    "say",
    "shine"
    }

# based on https://stackoverflow.com/questions/3232943/update-value-of-a-nested-dictionary-of-varying-depth
def rec_update(d, u, i=""):
    for k, v in u.items():
        if isinstance(v, dict):
            d[k] = rec_update(d.get(k, {}), v, "  ")
        elif isinstance(v, list):
            d[k] = d.get(k, []) + [(ve if ve != 'None' else None) for ve in v]
        elif v == 'None':
            d[k] = None
        else:
            d[k] = v
    return d

enable_pir = False
running = True

def main():
    """Interface to the hardware of my noticeboard.
    This is meant for my noticeboard Emacs software to send commands to."""
    config_file_name = "/etc/noticeboard.conf"
    if os.path.isfile(config_file_name):
        with open(os.path.expanduser(os.path.expandvars(config_file_name))) as config_file:
            more_config = yaml.safe_load(config_file)
            rec_update(config, more_config)
    global expected_at_home_times
    expected_at_home_times = { day: [convert_interval(interval_string)
                                     for interval_string in interval_string_list]
                               for day, interval_string_list in config['expected_occupancy'].items()}
    print("noticeboard hardware controller starting")
    global photographing
    global photographing_duration
    photographing_duration = datetime.timedelta(0, config['camera']['duration'])

    controller = NoticeBoardHardware(config)

    print("noticeboard hardware controller started")
    while running:
        active = controller.step()
        # if we're stepping through an activity, ignore commands for now:
        if active:
            time.sleep(self.config['delays']['motor'])
        else:
            ready, _, _ = select.select([sys.stdin], [], [], main_loop_delay)
            if sys.stdin in ready:
                command = shlex.parse(sys.stdin.readline().strip())
                if command[0] in actions:
                    getattr(controller, command)(command)
                else:
                    print('(error "Unknown noticeboard command" ', command, ')')

        # if photographing:
        #     take_photo()
        #     if datetime.datetime.now() >= photographing:
        #         photographing = False
    print("noticeboard hardware controller stopped")

if __name__ == "__main__":
    main()
