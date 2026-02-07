#!/usr/bin/python3

import argparse
import os
import yaml

source_dir = os.path.dirname(os.path.realpath(__file__))

CONFIGURATION = {}

# based on https://stackoverflow.com/questions/3232943/update-value-of-a-nested-dictionary-of-varying-depth
def rec_update(basedict, u):
    """Update a dictionary recursively."""
    for k, v in u.items():
        if isinstance(v, dict):
            basedict[k] = rec_update(basedict.get(k, {}), v)
        elif isinstance(v, list):
            base = basedict.get(k, [])
            basedict[k] = base + [(ve if ve != 'None' else None)
                                  for ve in v
                                  if ve not in base]
        elif v == 'None':
            basedict[k] = None
        else:
            basedict[k] = v
    return basedict

def load_yaml_files(target_dict, yaml_files):
    """Load several YAML files, merging the data from them."""
    if yaml_files:
        for yaml_file in yaml_files:
            if yaml_file is None:
                continue
            if os.path.exists(yaml_file):
                with open(yaml_file) as yaml_handle:
                    rec_update(target_dict, yaml.safe_load(yaml_handle))

HARDCODED_DEFAULT_CONFIG = {
    'finance': {
        'accounts-config': "accounts.yaml",
        'accumulated-bank-statements-file': "$SYNCED/finances/handelsbanken/handelsbanken-full.csv",
        'bank-statement-template': "$HOME/Downloads/Transaction*.csv",
        'budgeting-classes-file': "budgetting-classes.yaml",
        'configdir': "$HOME/open-projects/github.com/hillwithsmallfields/qs/conf",
        'conversions-config': "conversions.yaml",
        'conversions-dir': "$SYNCED/finances",
        'finances-completions': "$SYNCED/var/finances-completions.el",
        'main-account': "$SYNCED/finances/finances.csv",
        'merge-results-dir': "$HOME/scratch/auto-merge-results",
        'merge-results-file': "merged-with-unmatched-all.csv",
        'thresholds-file': "budgetting-thresholds.yaml"},

    'inventory': {
        'books-file': "$SYNCED/org/books.csv",
        'inventory-file': "$SYNCED/org/inventory.csv",
        'project-parts-file': "$SYNCED/org/project-parts.csv",
        'stock-file': "$SYNCED/org/stock.csv",
        'storage-file': "$SYNCED/org/storage.csv"},

    'physical': {
        'running-filename': "$SYNCED/health/garmin-running.csv",
        'cycling-filename': "$SYNCED/health/garmin-cycling.csv",
        'garmin-incoming-pattern': "$HOME/Downloads/Activities*.csv",
        'mfp-filename': "$SYNCED/health/mfp-accum.csv",
        'omron-filename': "$SYNCED/health/blood-pressure.csv",
        'omron-incoming-pattern': "$HOME/Downloads/*BP-Logbook*.csv",
        'oura-filename': "$SYNCED/health/sleep.csv",
        'physical-filename': "$SYNCED/health/physical.csv",
        'weight-filename': "$SYNCED/health/weight.csv",
        'temperature-file': "$SYNCED/health/temperature.csv"},

    'start-page': {
        'start-page-generator': 'make_link_table.py',
        'startpage': "$HOME/private_html/startpage.html",
        'startpage-source': "$SYNCED/org/startpage.yaml",
        'startpage-style': "$SYNCED/org/startpage.css"},

    'travel': {
        'travel-filename': "$SYNCED/travel/travel.csv",
        'places-filename': "$SYNCED/travel/places/places.csv"},

    'contacts': {
        'contacts-file': "$SYNCED/org/contacts.csv"},

    'weather': {
        'weather-filename': "$SYNCED/var/weather.csv"},

    'general': {
        'org-directory': "$ORG",
        'sync-directory': "$SYNCED",
        'charts': "$HOME/private_html/dashboard",
        'default-timetable': "timetable.csv",
        'projects-dir': "$HOME/open-projects/github.com",
        'projects-user': "hillwithsmallfields",
        'reflections-dir': os.path.expandvars("$SYNCED/texts/reflection"),
        'timetables-dir': "$SYNCED/timetables"},

    'archive': {
        'org-archive-directory': "$HOME/org-snapshots",
        'org-archives-size': "8Gb",
        'sync-archive-directory': "$HOME/Sync-snapshots",
        'sync-archives-size': "32Gb",
        'archive': "$ARCHIVE",
        'backup-iso-format': "backup-%s.iso",
        'backup-isos-directory': "$ISOS/backups",
        'write-iso-to-dvd': True,
        'synced-snapshots': "$SYNCEDSNAPSHOTS",
        'daily-backup-template': "org-%s.tgz",
        'gpg-recipient': "jcg.sturdy@gmail.com",
        'projects-dir': "$HOME/open-projects/github.com",
        'projects-user': "hillwithsmallfields",
        'monthly-backup-day': 1,
        'weekly-backup-day': "Wednesday",
        'weekly-backup-template': "Sync-%s.tgz"
    },

    'house': {
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
    },

    'motion': {
        'retain': "8Gb",
        'days': 31,
    },

    'noticeboard': {
        'chiming_times': {
            'Default': "05:30--22:00",
            'Saturday': "08:30--22:00",
            'Sunday': "06:00--22:00",
        },
        'pir_log_file': "/var/log/pir",
        'command_port': 10101,
        'camera': {
            'duration': 180,
            'directory': "/var/spool/camera"},
        'delays': {
            'fast': 0.01,
            'slow': 1.0,
            'shine': 2,
            'quench': 10,
            'photo': 3,
            'extend': 4,
            'retract': 15,
            'step_max': 200},
    },
}

def recursive_expand(value):
    return (os.path.expanduser(os.path.expandvars(value))
            if isinstance(value, str)
            else ({k: recursive_expand(v) for k, v in value.items()}
                  if isinstance(value, dict)
                  else ([recursive_expand(v) for v in value]
                        if isinstance(value, list)
                        else value)))

def load_config(no_hardcoded_default=False,
                no_main_config=False,
                main_config_file=os.path.join(source_dir, "config.yaml"),
                config_files=[]):

    global CONFIGURATION

    config = {} if no_hardcoded_default else HARDCODED_DEFAULT_CONFIG

    if not no_main_config:
        with open(main_config_file) as yaml_stream:
            rec_update(config, yaml.safe_load(yaml_stream))

    load_yaml_files(config, config_files)

    CONFIGURATION = recursive_expand(config)

    return CONFIGURATION

def lookup(config, *keys):
    for key in keys:
        if key not in config:
            return None
        config = config[key]
    return config

def override(config, keys, value):
    for key in keys[:-1]:
        if key in config:
            config = config[key]
        else:
            config[key] = {}
    config[keys[-1]] = value

def config(*keys):
    if not CONFIGURATION:
        load_config()
    return lookup(CONFIGURATION, *keys)

def update_config(incoming):
    rec_update(CONFIGURATION, incoming)

def file_config(*keys):
    return os.path.expanduser(os.path.expandvars(config(*keys)))

def main():
    """Look up and output a config element.
    Alternatively, show all of them, for debugging."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-main-config", action='store_true')
    parser.add_argument("--no-hardcoded-default", action='store_true')
    parser.add_argument("--main-config-file", "-m",
                        default=os.path.join(source_dir, "config.yaml"))
    parser.add_argument("--config-file", "-c",
                        action='append')
    parser.add_argument("--show-all", "-a", action='store_true')
    parser.add_argument("--override", "-o", nargs=2, action='append',
                        help="""Override a value.  The parts of the key are colon-separated.""")
    parser.add_argument("keys", nargs='*')
    args = parser.parse_args()

    config = load_config(args.no_hardcoded_default,
                         args.no_main_config,
                         args.main_config_file,
                         args.config_file)

    if args.override:
        for overrider in args.override:
            override(config, overrider[0].split(':'), overrider[1])

    if args.show_all:
        print(config)
    else:
        print(lookup(config, *args.keys))

if __name__ == '__main__':
    main()
