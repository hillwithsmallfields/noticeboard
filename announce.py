#!/usr/bin/python3

import argparse
import calendar
import csv
import datetime
import numbers
import os
import sched
import talkey                   # https://pypi.org/project/talkey/
import time

def sleep_timedelta(td):
    time.sleep(td.seconds if isinstance(td, datetime.timedelta) else td)
        
def announce(announcer, slot):
    print(slot.activity)
    announcer.talker.say(slot.activity)
    if any((os.stat(inputfile).st_mtime > lastread
            for inputfile, lastread in announcer.last_read.items())):
        announcer.empty_queue()
        for inputfile in announcer.last_read.keys():
            announcer.load(inputfile)

def as_duration(duration):
    if isinstance(duration, datetime.timedelta):
        return duration
    if isinstance(duration, numbers.Number):
        return datetime.timedelta(minutes=duration)
    hours_minutes = duration.split(':')
    return (datetime.timedelta(minutes=int(hours_minutes[0]))
            if len(hours_minutes) == 1
            else datetime.timedelta(hours=int(hours_minutes[-2]), minutes=int(hours_minutes[-1])))

def as_time(when):
    return (when
            if isinstance(when, datetime.time)
            else (when.time()
                  if isinstance(when, datetime.datetime)
                  else (datetime.time.fromisoformat(when))))

def as_datetime(when):
    return (when
            if isinstance(when, datetime.datetime)
            else (datetime.datetime.combine(datetime.date.today(),
                                            when.time())
                  if isinstance(when, datetime.time)
                  else (datetime.time.fromisoformat(when))))

class TimeSlot():

    pass

    def __init__(self,
                 start, activity,
                 duration=None,
                 sound=None):
        self.start = as_datetime(start)
        self.end = (self.start + as_duration(duration)) if duration else None
        self.activity = activity

    def __repr__(self):
        return "<Activity from %s to %s doing %s>" % (self.start, self.end, self.activity)

    def __str__(self):
        return "<%s--%s: %s>" % (self.start, self.end, self.activity)
        
    def in_progress_at(self, when):
        return when >= self.start and when < self.end

    def clashes_with(self, other):
        # TODO: I don't think this is right in practice
        return (self.in_progress_at(other.start)
                or self.in_progress_at(other.end)
                or other.in_progress_at(self.start)
                or other.in_progress_at(self.end))
        
class Announcer():

    pass

    def __init__(self, engine, language):
        self.engine = engine
        self.language = language
        self.slots = {}
        self.last_read = {}
        self.scheduler = sched.scheduler(datetime.datetime.now, sleep_timedelta)
        self.talker = talkey.Talkey(preferred_languages=[self.language],
                                    engine_preference=[self.engine])

    def load(self, input_file):
        if input_file is None:
            return
        self.last_read[input_file] = os.stat(input_file).st_mtime
        print("loading", input_file)
        today = datetime.date.today()
        with open (input_file) as instream:
            pending = None
            incoming = []
            for row in csv.DictReader(instream):
                start = datetime.datetime.combine(today, as_time(row['Start']))
                if pending:
                    prev_start, prev_activity = pending
                    prev_duration = as_time(start) - prev_start
                    incoming.append(TimeSlot(prev_start, prev_activity, prev_duration))
                    pending = None
                activity = row['Activity']
                duration = row.get('Duration')
                if duration:
                    incoming.append(TimeSlot(start, activity, duration))
                else:
                    pending = (start, activity)
            if pending:
                prev_start, prev_activity = pending
                prev_duration = as_time("23:59") - as_time(prev_start)
                incoming[prev_start] = TimeSlot(prev_start, prev_activity, prev_duration)
            print("merging", incoming, "into", self.slots)
            clashed = set()
            for what in incoming:
                print("  merging", what, "into", self.slots)
                for when, already in self.slots.items():
                    print("  checking", what, "against prior", already)
                    if what.clashes_with(already):
                        print("clash between", what, already)
                        clashed.add(when)
                self.slots[what.start] = what
            for clash in clashed:
                print("removing clash", self.slots[clash])
                del self.slots[clash]

    def show(self):
        for slot in self.slots:
            print(slot)
                
    def schedule_announcements(self):
        now = datetime.datetime.now()
        for start, slot in sorted(self.slots.items()):
            if start > now:
                print("scheduling", self.slots[start], "at", start)
                self.scheduler.enterabs(start, 1,
                                        announce, (self, slot))
        self.scheduler.run()

    def empty_queue(self):
        for event in self.scheduler.queue():
            self.scheduler.cancel(event)

def find_default_file(directory):
    for default_file in ["Timetable", "timetable", "Daily", "daily", "Default", "default"]:
        default_file = os.path.join(directory, default_file + ".csv" )
        if os.path.isfile(default_file):
            return default_file
    return None

def find_day_file(directory, dayname):
    for dayfile in [dayname, dayname.lower()]:
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

    my_day = Announcer(args.engine, args.language)
    if os.path.isdir(args.inputfile):
        my_day.load(find_default_file(args.inputfile))
        my_day.load(find_day_file(args.inputfile,
                                  calendar.day_name[datetime.datetime.now().weekday()]))
    else:
        my_day.load(args.inputfile)

    if args.verbose:
        my_day.show()
        
    my_day.schedule_announcements()

if __name__ == '__main__':
    main()
