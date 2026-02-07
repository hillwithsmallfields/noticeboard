#!/usr/bin/env python3

# Program for my noticeboard hardware

# See README.md for details

import contextlib
import datetime
import io
import os
import re
import sched
import select
import socket
import sys
import time
import traceback

from timetable_announcer import announce
from noticeboardhardware import NoticeBoardHardware
from lifehacking_config import config, update_config
import archive
import managed_directory
import motion

camera = None

def convert_interval(interval_string):
    """Convert a string giving start and end times into a tuple of minutes after midnight.
    For the input "07:30--09:15" the output would be (450, 555)."""
    matched = re.match("([0-2][0-9]):([0-5][0-9])--([0-2][0-9]):([0-5][0-9])", interval_string)
    return (((int(matched.group(1))*60 + int(matched.group(2))),
             (int(matched.group(3))*60 + int(matched.group(4))))
            if matched
            else None)

def convert_intervals(intervals):
    """Convert a dictionary of intervals."""
    return {k: convert_interval(v) for k, v in intervals.items()}

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
    with open(config('noticeboard', 'pir_log_file'), 'w+') as logfile:
        logfile.write(datetime.datetime.now().isoformat() + "\n")
    # todo: send a remote notification e.g. email with the picture

def main():
    """Interface to the hardware of my noticeboard.
    This is meant for my noticeboard Emacs software to send commands to."""
    global expected_at_home_times
    expected_at_home_times = {day: [convert_interval(interval_string)
                                    for interval_string in interval_string_list]
                              for day, interval_string_list in config('house', 'expected_occupancy').items()}
    print('(message "noticeboard hardware controller starting")')
    global photographing
    global photographing_duration
    photographing_duration = datetime.timedelta(0, config('noticeboard', 'camera', 'duration'))

    scheduler = sched.scheduler(time.time, time.sleep)
    controller = NoticeBoardHardware(scheduler=scheduler,
                                     expected_at_home_times=expected_at_home_times)
    announcer = announce.Announcer(scheduler=scheduler,
                                   announce=lambda contr, message, **kwargs: controller.do_say(message),
                                   playsound=lambda contr, sound, **kwargs: controller.do_play(sound),
                                   chiming_times=convert_intervals(config('noticeboard', 'chiming_times')),
                                   chimes_dir=os.path.expandvars("$SYNCED/music/chimes"))

    for on_action in ['shine', 'photo', 'extend']:
        controller.add_pir_on_action(config('noticeboard', 'delays', on_action), on_action)
    for off_action in ['quench', 'retract']:
        controller.add_pir_off_action(config('noticeboard', 'delays', off_action), off_action)

    previous_date = datetime.date.today()
    announcer.reload_timetables(os.path.expandvars("$SYNCED/timetables"),
                                convert_intervals(config('noticeboard', 'chiming_times')),
                                previous_date)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as incoming:
        incoming.setblocking(0)
        incoming.bind(('localhost', int(config('noticeboard', 'command_port'))))
        incoming.listen()

        print('(message "noticeboard hardware controller started")')
        running = True
        active = False
        watch_on = [sys.stdin, incoming]
        while running:
            active = controller.step(active)
            update_config (controller.config_updates)
            controller.config_updates = {}
            # if we're stepping through an activity, ignore commands for now:
            if active:
                time.sleep(config('noticeboard', 'delays', 'fast'))
            else:
                ready, _, _ = select.select(watch_on,
                                            [],
                                            [],
                                            config('noticeboard', 'delays', 'slow'))
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
                            traceback.print_exception(e)
                    else:
                        data, address = channel.recvfrom(1024)
                        if data:
                            try:
                                command = data.decode('utf-8')
                            except UnicodeDecodeError as dce:
                                print("Could not decode input from socket:", dce, data)
                                continue
                            try:
                                with contextlib.redirect_stdout(io.StringIO()) as captured, contextlib.redirect_stderr(io.StringIO()) as capturederr:
                                    if controller.onecmd(command):
                                        # logout:
                                        watch_on.remove(channel)
                                        channel.shutdown(socket.SHUT_RDWR)
                                output = captured.getvalue() + capturederr.getvalue()
                                print("Captured output", output)
                                if output:
                                    channel.sendall(bytes(output, encoding='utf-8'))
                            except Exception as e:
                                print("Exception in running command from socket:", e)
                                traceback.print_tb(e.__traceback__)
                        else: # channel is closed
                            watch_on.remove(channel)
                today = datetime.date.today()
                if previous_date != today:
                    announcer.reload_timetables(os.path.expandvars("$SYNCED/timetables"),
                                                convert_intervals(config('noticeboard', 'chiming_times')),
                                                today)
                    previous_date = today
                announcer.tick()

        controller.onecmd("quiet")
        controller.onecmd("quench")
        controller.onecmd("off")

    print('(message "noticeboard hardware controller stopped")')

if __name__ == "__main__":
    main()
