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
    time.sleep(td.total_seconds if isinstance(td, datetime.timedelta) else td)

def announce(announcer, slot):
    print(slot.activity)
    announcer.talker.say(slot.activity)
    if any((os.stat(inputfile).st_mtime > lastread
            for inputfile, lastread in announcer.last_read.items())):
        announcer.empty_queue()
        for inputfile in announcer.last_read.keys():
            announcer.load(inputfile)

def as_timedelta(duration):
    """Convert anything that might be a duration to a timedelta."""
    if isinstance(duration, datetime.timedelta):
        return duration
    if isinstance(duration, numbers.Number):
        return datetime.timedelta(minutes=duration)
    hours_minutes = duration.split(':')
    return (datetime.timedelta(minutes=int(hours_minutes[0]))
            if len(hours_minutes) == 1
            else datetime.timedelta(hours=int(hours_minutes[0]),
                                    minutes=int(hours_minutes[1])))

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
                 link=None,
                 sound=None):
        self.start = as_datetime(start)
        self.end = (self.start + as_timedelta(duration)) if duration else None
        self.activity = activity
        self.link = link

    def __repr__(self):
        return "<Activity from %s to %s doing %s>" % (self.start, self.end, self.activity)

    def __str__(self):
        return "<%s--%s: %s>" % (self.start, self.end, self.activity)

    def duration(self):
        return self.end - self.start

    def in_progress_at(self, when):
        return when >= self.start and when < self.end

    def starts_during(self, other):
        return other.in_progress_at(self.start)

    def ends_during(self, other):
        return self.end > other.start and self.end <= other.end

    def clashes_with(self, other):
        return (self.starts_during(other)
                or self.ends_during(other)
                or other.starts_during(self)
                or other.ends_during(self))

class Day():

    pass

    def __init__(self, inputfile=None, verbose=False):
        self.slots = {}
        self.last_read = {}
        if inputfile:
            self.load(inputfile, verbose)

    def add_slot(self, slot):
        """Add a timeslot.
        If it overlaps with existing ones, they are split as necessary."""
        for when, existing in slots.items():
            if existing.starts_during(slot) and existing.ends_during(slot):
                # we overlap it completely, so supersede it:
                del slots.items[when]
            elif slot.starts_during(existing):
                if slot.ends_during(existing):
                    # split the existing slot into before and after parts
                    self.slots[slot.end] = TimeSlot(start=slot.end,
                                                    duration=existing.end-slot.end,
                                                    activity=existing.activity,
                                                    link=existing.link)
                    existing.duration = slot.start - existing.start
                else:
                    # keep the beginning of the existing one
                    existing.duration = slot.start - existing.start
            elif slot.ends_during(existing):
                # but we already know it doesn't start during it
                # keep the end of the existing one
                existing.duration = (existing.start + existing.duration) - (slot.start + slot.duration)
                existing.start = slot.start + slot.duration
        self.slots[slot.start] = slot

    def load(self, input_file, verbose=False):
        """Load a one-day timetable file.
        The file is expected to have columns ['Start', 'Duration', and 'Activity']
        where the start time is HH:MM and the duration is M or H:MM."""
        if input_file is None:
            return
        self.last_read[input_file] = os.stat(input_file).st_mtime
        print("loading", input_file)
        today = datetime.date.today()
        with open (input_file) as instream:
            # When a start but no duration is given, hold it here
            # until we have the start of the next entry:
            pending = None
            incoming = []
            for row in csv.DictReader(instream):
                if 'Start' not in row:
                    print("Warning: no Start in row", row, "from file", input_file)
                    continue
                start = datetime.datetime.combine(today, as_time(row['Start']))
                if pending:
                    prev_start, prev_activity = pending
                    prev_duration = as_time(start) - prev_start
                    incoming.append(TimeSlot(prev_start, prev_activity, prev_duration))
                    pending = None
                activity = row['Activity']
                duration = row.get('Duration')
                link = row.get('URL')
                if duration:
                    incoming.append(TimeSlot(start, activity,
                                             duration=duration,
                                             link=link or None))
                else:
                    pending = (start, activity)
            if pending:
                prev_start, prev_activity = pending
                prev_duration = as_time("23:59") - as_time(prev_start)
                incoming.append(TimeSlot(prev_start, prev_activity, prev_duration))
            for what in sorted(incoming, key=lambda slot: slot.start):
                self.add_slot(what)

class Announcer():

    pass

    def __init__(self,
                 speech_engine="espeak",
                 language="en",
                 chimes_dir,
                 day=None):
        self.speech_engine = speech_engine
        self.language = language
        self.day = day or Day()
        self.scheduler = sched.scheduler()
        self.talker = talkey.Talkey(preferred_languages=[self.language],
                                    engine_preference=[self.speech_engine])
        self.chimes_dir = chimes_dir

    def load(self, input_file, verbose=False):
        """Load one timetable file.
        The slots from the file will be merged with the existing slots."""
        self.day.load(input_file, verbose)

    def reload_timetables(self, timetables_directory, day):
        """Load the timetables for the given day.
        Any previous entries will be cleared out."""
        self.empty_queue()
        self.load(os.path.join(timetables_directory, "timetable.csv"))
        if os.path.exists(dayfile := os.path.join(timetables_directory,
                                                  day.strftime("%A")+".csv")):
            self.load(dayfile)
        self.schedule_chimes()

    def show(self):
        for slot in sorted(self.day.slots.keys()):
            print(self.day.slots[slot])

    def ordered(self):
        return [self.day.slots[slot] for slot in sorted(self.day.slots.keys())]

    def schedule_announcements(self):
        now = datetime.datetime.now()
        for start, slot in sorted(self.day.slots.items()):
            if start > now:
                print("scheduling", self.day.slots[start], "at", start)
                self.scheduler.enterabs(start, 2,
                                        announce, (self, slot))

    def schedule_sound(self, when, what):
        """Schedule a sound to be played at a time."""
        self.scheduler.enterabs(when, 1, play_sound, (self, what))

    def schedule_chimes(self):
        """Add chimes to the schedule."""
        for hour in range(6, 22):
            self.schedule_sound()

    def start(self):
        self.scheduler.run()

    def tick(self):
        self.scheduler.run(blocking=False)

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

def unit_tests():
    today = datetime.date.today()
    ten = TimeSlot(datetime.datetime.combine(today, as_time("10:00")), "Activity A", duration=60)
    ten_thirty = TimeSlot(datetime.datetime.combine(today, as_time("10:30")), "Activity B", duration=60)
    eleven = TimeSlot(datetime.datetime.combine(today, as_time("11:00")), "Activity C", duration=60)
    eleven_thirty = TimeSlot(datetime.datetime.combine(today, as_time("11:00")), "Activity D", duration=60)
    if ten.starts_during(ten_thirty):
        print("fail: ten.starts_during(ten_thirty)")
    if not ten_thirty.starts_during(ten):
        print("fail: not ten_thirty.starts_during(ten)")

    if ten.starts_during(eleven):
        print("fail: ten.starts_during(eleven)")
    if eleven.starts_during(ten):
        print("fail: not eleven.starts_during(ten)")

    if ten.clashes_with(eleven):
        print("fail: ten.clashes_with(eleven)")
        print("      ten.starts_during(eleven):", ten.starts_during(eleven))
        print("      ten.ends_during(eleven):", ten.ends_during(eleven))
        print("      eleven.starts_during(ten):", eleven.starts_during(ten))
        print("      eleven.ends_during(ten):", eleven.ends_during(ten))
    if eleven.clashes_with(ten):
        print("fail: eleven.clashes_with(ten)")

    if ten.clashes_with(eleven_thirty):
        print("fail: ten.clashes_with(eleven_thirty)")
    if eleven_thirty.clashes_with(ten):
        print("fail: eleven_thirty.clashes_with(ten)")

    if not ten.clashes_with(ten_thirty):
        print("fail: ten.clashes_with(ten_thirty)")
    if not ten_thirty.clashes_with(ten):
        print("fail: not ten_thirty.clashes_with(ten)")

def get_day_data(inputfile,
                 verbose=False):

    my_day = Day()

    if os.path.isdir(inputfile):
        my_day.load(find_default_file(inputfile), verbose)
        my_day.load(find_day_file(inputfile,
                                  calendar.day_name[datetime.date.today().weekday()]),
                    verbose)
    else:
        my_day.load(inputfile, verbose)

    return my_day

def get_day_announcer(inputfile,
                      extra_files=[],
                      language='en',
                      engine='espeak',
                      verbose=False):
    day = Day(inputfile,
              verbose=verbose)
    for extra in extra_files:
        day.load(extra)
    return Announcer(engine, language, day=day)

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--language', '-l',
                        default='en',
                        help="""The default language for Talkey""")
    parser.add_argument('--engine', '-e',
                        default='espeak',
                        help="""The engine to use for Talkey""")
    parser.add_argument("--verbose", "-v",
                        action='store_true')
    parser.add_argument("--run-tests", "-u",
                        action='store_true')
    parser.add_argument('inputfile')
    return vars(parser.parse_args())

def main(language, engine, verbose, run_tests, inputfile):

    if run_tests:
        unit_tests()
        return

    my_announcer = Announcer(
        speech_engine=engine,
        language=language,
        get_day_data(
            inputfile,
            verbose=verbose))

    if args.verbose:
        my_announcer.show()

    my_announcer.schedule_announcements()
    my_announcer.start()

if __name__ == '__main__':
    main(**get_args())
