#!/usr/bin/env python3

# Program for my noticeboard hardware

# See README.md for details

import contextlib
import datetime
import functools
import io
import os
import subprocess
import re
import sched
import select
import socket
import sys
import time
import yaml

from timetable_announcer import announce
from noticeboardhardware import NoticeBoardHardware

# This is overwritten from /etc/noticeboard.conf if it's available
config = {
    'delays': {
        'fast': 0.01,
        'slow': 1.0,
        'shine': 2,
        'quench': 10,
        'photo': 3,
        'extend': 4,
        'retract', 15,
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
    'pir_log_file': "/var/log/pir",
    'port': 10101
}

camera = None

def convert_interval(interval_string):
    """Convert a string giving start and end times into a tuple of minutes after midnight.
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

def read_config_file(config, config_file_name):
    if os.path.isfile(config_file_name):
        with open(os.path.expanduser(os.path.expandvars(config_file_name))) as config_file:
            rec_update(config, yaml.safe_load(config_file))

def main():
    """Interface to the hardware of my noticeboard.
    This is meant for my noticeboard Emacs software to send commands to."""
    read_config_file(config, "/etc/noticeboard.conf")
    global expected_at_home_times
    expected_at_home_times = {day: [convert_interval(interval_string)
                                    for interval_string in interval_string_list]
                              for day, interval_string_list in config['expected_occupancy'].items()}
    print('(message "noticeboard hardware controller starting")')
    global photographing
    global photographing_duration
    photographing_duration = datetime.timedelta(0, config['camera']['duration'])

    scheduler = sched.scheduler(time.time, time.sleep)
    controller = NoticeBoardHardware(config=config,
                                     scheduler=scheduler,
                                     expected_at_home_times=expected_at_home_times)
    announcer = announce.Announcer(scheduler=scheduler,
                                   announce=lambda contr, message, **kwargs: contr.do_say(message),
                                   playsound=lambda contr, sound, **kwargs: controller.do_play(sound),
                                   chimes_dir=os.path.expandvars("$SYNCED/music/chimes"))

    for on_action in ['shine', 'photo', 'extend']:
        controller.add_pir_on_action(config['delays'][on_action], on_action)
    for off_action in ['quench', 'retract']:
        controller.add_pir_off_action(config['delays'][off_action], off_action)

    previous_date = datetime.date.today()
    announcer.reload_timetables(os.path.expandvars ("$SYNCED/timetables"), previous_date)

    incoming = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    incoming.setblocking(0)
    incoming.bind(('localhost', int(config['port'])))
    incoming.listen()

    print('(message "noticeboard hardware controller started")')
    running = True
    active = False
    watch_on = [sys.stdin, incoming]
    while running:
        active = controller.step(active)
        rec_update(config, controller.settings_updates)
        controller.settings_updates = {}
        # if we're stepping through an activity, ignore commands for now:
        if active:
            time.sleep(config['delays']['fast'])
        else:
            ready, _, _ = select.select(watch_on,
                                        [],
                                        [],
                                        config['delays']['slow'])
            for channel in ready:
                if channel == incoming:
                    conn, new_address = incoming.accept()
                    print("new connection from", new_address)
                    watch_on.append(conn)
                elif sys.stdin in ready:
                    try:
                        if controller.onecmd(sys.stdin.readline().strip()):
                            running = False
                    except Exception as e:
                        print('(message "Exception in running command: %s")' % e)
                else:
                    data, address = channel.recvfrom(1024)
                    print("got", str(data), "from", address)
                    if data:
                        command = data.decode('utf-8')
                        try:
                            with contextlib.redirect_stdout(io.StringIO()) as captured:
                                if controller.onecmd(command):
                                    # logout:
                                    watch_on.remove(channel)
                                    channel.shutdown(socket.SHUT_RDWR)
                            output = captured.getvalue()
                            if output:
                                channel.sendall(str(output))
                        except Exception as e:
                            print("Exception in running command from socket:", e)
                    else: # channel is closed
                        watch_on.remove(channel)
            today = datetime.date.today()
            if previous_date != today:
                announcer.reload_timetables(os.path.expandvars("$SYNCED/timetables"), today)
                previous_date = today
            announcer.tick()

    controller.onecmd("quiet")
    controller.onecmd("quench")
    controller.onecmd("off")

    print('(message "noticeboard hardware controller stopped")')

if __name__ == "__main__":
    main()
