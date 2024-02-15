#!/usr/bin/python3

import argparse
import calendar
import csv
import datetime
import numbers
import os
import sched
import time

# TODO: flexible start and end times
first_hour = 6
last_hour = 22

def play_sound(announcer, sound):
    os.system("ogg123 %s" % sound)

def announce(announcer, slot):
    print(slot.activity)
    announcer.announce_function.say(slot.activity)
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

def time_now():
    return datetime.datetime.now().time()

def as_time(when):
    """Convert anything that might be a time to a time."""
    return (when
            if isinstance(when, datetime.time)
            else (when.time()
                  if isinstance(when, datetime.datetime)
                  else (datetime.time.fromisoformat(when))))

def as_datetime(when):
    """Convert anything that might be a datetime to a datetime."""
    return (when
            if isinstance(when, datetime.datetime)
            else (datetime.datetime.combine(datetime.date.today(),
                                            when)
                  if isinstance(when, datetime.time)
                  else (datetime.time.fromisoformat(when)
                        if isinstance(when, str)
                        else datetime.datetime.fromtimestamp(when))))

def as_time_number(when):
    return time.mktime(as_datetime(when).timetuple())

class TimeSlot():

    """A timeslot for an activity."""

    def __init__(self,
                 start, activity,
                 duration=None,
                 end=None,
                 link=None,
                 sound=None):
        self.start = as_time_number(start)
        self.end = as_time_number(end or ((self.start + as_timedelta(duration).total_seconds())
                                          if duration
                                          else None))
        self.activity = activity
        self.link = link
        print("made timeslot", self.__repr__(), type(self.start), type(self.end))

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

    """A timeslot manager."""

    def __init__(self, inputfile=None, verbose=False):
        self.slots = {}
        self.last_read = {}
        if inputfile:
            self.load(inputfile, verbose)

    def add_slot(self, slot):
        """Add a timeslot.
        If it overlaps with existing ones, they are split as necessary."""
        # iterate over a copy of the dictionary, as we will be
        # changing the original dictionary from inside the loop:
        for when, existing in {k: v for k, v in self.slots.items()}.items():
            if existing.starts_during(slot) and existing.ends_during(slot):
                # we overlap it completely, so supersede it:
                if when in self.slots: # might have been removed earlier
                    del self.slots[when]
            elif slot.starts_during(existing):
                if slot.ends_during(existing):
                    # split the existing slot into before and after parts
                    # make an "after" part:
                    self.slots[slot.end] = TimeSlot(start=slot.end,
                                                    end=existing.end,
                                                    activity=existing.activity,
                                                    link=existing.link)
                # the original one becomes the "before" part:
                existing.end = slot.start
            elif slot.ends_during(existing):
                # but we already know it doesn't start during it
                # keep the end of the existing one
                existing.duration = existing.end - slot.end
                existing.start = slot.end
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

    """A timeslotted day manager."""

    def __init__(self,
                 announce=None,
                 playsound=None,
                 chimes_dir="/usr/local/share/chimes",
                 day=None):
        self.announce_function = announce
        self.playsound_function = playsound
        self.day = day or Day()
        self.scheduler = sched.scheduler(time.time, time.sleep)
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
                self.scheduler.enterabs(as_time_number(start), 2,
                                        self.announce_function,
                                        (self, slot))

    def schedule_sound(self, when, what):
        """Schedule a sound to be played at a time."""
        self.scheduler.enterabs(as_time_number(when), 1,
                                self.playsound_function,
                                (self, what))

    def schedule_chimes(self):
        """Add chimes to the schedule."""
        for hour in range(max(datetime.datetime.now().time().hour,
                              first_hour),
                          last_hour - 1):
            self.schedule_sound(datetime.time(hour=hour),
                                os.path.join(self.chimes_dir, "Cambridge-chimes-hour-%02d.ogg" % hour))
            self.schedule_sound(datetime.time(hour=hour, minute=15),
                                os.path.join(self.chimes_dir, "Cambridge-chimes-first-quarter.ogg"))
            self.schedule_sound(datetime.time(hour=hour, minute=30),
                                os.path.join(self.chimes_dir, "Cambridge-chimes-second-quarter.ogg"))
            self.schedule_sound(datetime.time(hour=hour, minute=45),
                                os.path.join(self.chimes_dir, "Cambridge-chimes-third-quarter.ogg"))
        self.schedule_sound(datetime.time(hour=last_hour),
                            os.path.join(self.chimes_dir, "Cambridge-chimes-hour-%02d.ogg" % last_hour))

    def start(self):
        self.scheduler.run()

    def tick(self):
        self.scheduler.run(blocking=False)

    def empty_queue(self):
        for event in self.scheduler.queue:
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

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--verbose", "-v",
                        action='store_true')
    parser.add_argument("--display", "-d",
                        action='store_true')
    parser.add_argument("--timetables",
                        default="$SYNCED/timetables")
    parser.add_argument("--run-tests", "-u",
                        action='store_true')
    return vars(parser.parse_args())

def main(language, engine, verbose, run_tests, display, timetables):

    if run_tests:
        unit_tests()
        return

    my_announcer = Announcer()

    my_announcer.schedule_announcements()
    if display:
        my_announcer.reload_timetables(os.path.expandvars(timetables),
                                       datetime.date.today())
        my_announcer.show()
    else:
        my_announcer.start()

if __name__ == '__main__':
    main(**get_args())
