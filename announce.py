#!/usr/bin/python3

import argparse
import csv
import datetime
import sched
import talkey                   # https://pypi.org/project/talkey/
import time

def announce(tts, text):
    print(text)
    tts.say(text)

def announce_day_slots(time_slots, day, args):
    s = sched.scheduler(time.time, time.sleep)
    t = talkey.Talkey(preferred_languages=[args.language],
                      engine_preference=[args.engine])
    now = datetime.datetime.now()
    for start in sorted(time_slots.keys()):
        when = datetime.datetime.combine(day,
                                         start.timestamp())
        if when > now:
            s.enterabs(when, 1,
                       announce, (t, time_slots[start]))
    s.run()

def announce_from_file(inputfile, args):
    with open (inputfile) as instream:
        announce_day_slots(
            {datetime.time.fromisoformat(row['Start']): row['Activity']
             for row in csv.DictReader(instream)},
            datetime.date.today(),
            args)

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
