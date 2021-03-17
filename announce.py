#!/usr/bin/python3

import argparse
import calendar
import csv
import datetime
import os
import sched
import talkey                   # https://pypi.org/project/talkey/
import time

def sleep_timedelta(td):
    time.sleep(td.seconds if isinstance(td, datetime.timedelta) else td)
        
def announce(announcer, text):
    print(text)
    announcer.talker.say(text)
    if os.stat(announcer.inputfile).st_mtime > announcer.last_read:
        print("Reloading events file")
        announcer.empty_queue()
        announcer.load()

class Announcer():

    pass

    def __init__(self, inputfile,
                 engine, language):
        self.slots = None
        self.engine = engine
        self.language = language
        self.inputfile = inputfile
        self.last_read = None
        self.scheduler = sched.scheduler(datetime.datetime.now, sleep_timedelta)
        self.talker = talkey.Talkey(preferred_languages=[self.language],
                                    engine_preference=[self.engine])
        self.load()

    def load(self):
        self.last_read = os.stat(self.inputfile).st_mtime
        print("loading", self.inputfile)
        with open (self.inputfile) as instream:
            self.announce_day_slots(
                {datetime.time.fromisoformat(row['Start']): row['Activity']
                 for row in csv.DictReader(instream)},
                datetime.date.today())

    def announce_day_slots(self, time_slots, day):
        now = datetime.datetime.now()
        for start in sorted(time_slots.keys()):
            when = datetime.datetime.combine(day, start)
            if when > now:
                print("scheduling", time_slots[start], "at", when)
                self.scheduler.enterabs(when, 1,
                                        announce, (self, time_slots[start]))

    def run(self):
        self.scheduler.run()

    def empty_queue(self):
        for event in self.scheduler.queue():
            self.scheduler.cancel(event)

def find_dayfile(directory, dayname):
    for dayfile in [
            dayname,
            dayname.lower(),
            "Timetable", "timetable", "Daily", "daily", "Default", "default"]:
        dayfile = os.path.join(directory, dayfile + ".csv" )
        if os.path.isfile(dayfile):
            return dayfile
    return None
            
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--language', '-l',
                        default='en',
                        help="""The default language for Talkey""")
    parser.add_argument('--engine', '-e',
                        default='espeak',
                        help="""The engine to use for Talkey""")
    parser.add_argument("--verbose", "-v",
                        action='store_true')
    parser.add_argument('inputfile')
    args = parser.parse_args()

    Announcer((find_dayfile(args.inputfile,
                            calendar.day_name[datetime.datetime.now().weekday()])
                           if os.path.isdir(args.inputfile)
                           else args.inputfile),
              args.engine, args.language).run()

if __name__ == '__main__':
    main()
