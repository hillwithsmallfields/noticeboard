#!/usr/bin/python3

import argparse
import csv
import datetime
import os
import sched
import talkey                   # https://pypi.org/project/talkey/
import time

LAST_READ = None
FILE_NAME = None
PROG_ARGS = None

def sleep_timedelta(td):
    time.sleep(td.seconds if isinstance(td, datetime.timedelta) else td)

def announce(tts, text):
    print(text)
    tts.say(text)
    if os.stat(FILE_NAME).st_mtime > LAST_READ:
        print("Reloading events file")
        announce_from_file(FILE_NAME, PROG_ARGS)

def announce_day_slots(time_slots, day, args):
    s = sched.scheduler(datetime.datetime.now, sleep_timedelta)
    t = talkey.Talkey(preferred_languages=[args.language],
                      engine_preference=[args.engine])
    now = datetime.datetime.now()
    for start in sorted(time_slots.keys()):
        when = datetime.datetime.combine(day, start)
        if when > now:
            print("scheduling", time_slots[start], "at", when)
            s.enterabs(when, 1,
                       announce, (t, time_slots[start]))
    s.run()

def announce_from_file(inputfile, args):
    global LAST_READ
    LAST_READ = os.stat(inputfile).st_mtime
    global FILE_NAME
    FILE_NAME = inputfile
    global PROG_ARGS
    PROG_ARGS = args
    with open (inputfile) as instream:
        announce_day_slots(
            {datetime.time.fromisoformat(row['Start']): row['Activity']
             for row in csv.DictReader(instream)},
            datetime.date.today(),
            args)

def empty_queue(s):
    for event in s.queue():
        s.cancel(event)
        
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--language', '-l',
                        default='en',
                        help="""The default language for Talkey""")
    parser.add_argument('--engine', '-e',
                        default='espeak',
                        help="""The engine to use for Talkey""")
    parser.add_argument('inputfile')
    args = parser.parse_args()
    announce_from_file(args.inputfile, args)

if __name__ == '__main__':
    main()
