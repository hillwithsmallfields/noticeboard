#!/usr/bin/python3

import argparse
import os
import yaml

source_dir = os.path.dirname(os.path.realpath(__file__))

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

def load_multiple_yaml(target_dict, yaml_files):
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
        'accumulated-bank-statements-file': "$COMMON/finances/handelsbanken/handelsbanken-full.csv",
        'bank-statement-template': "~/Downloads/Transaction*.csv",
        'budgeting-classes-file': "budgetting-classes.yaml",
        'configdir': "~/open-projects/github.com/hillwithsmallfields/qs/conf",
        'conversions-config': "conversions.yaml",
        'conversions-dir': "$COMMON/finances",
        'finances-completions': "$COMMON/var/finances-completions.el",
        'main-account': "$COMMON/finances/finances.csv",
        'merge-results-dir': "~/scratch/auto-merge-results",
        'merge-results-file': "merged-with-unmatched-all.csv",
        'thresholds-file': "budgetting-thresholds.yaml"},

    'inventory': {
        'books-file': "$COMMON/org/books.csv",
        'inventory-file': "$COMMON/org/inventory.csv",
        'project-parts-file': "$COMMON/org/project-parts.csv",
        'stock-file': "$COMMON/org/stock.csv",
        'storage-file': "$COMMON/org/storage.csv"},

    'physical': {
        'running-filename': "$COMMON/health/garmin-running.csv",
        'cycling-filename': "$COMMON/health/garmin-cycling.csv",
        'garmin-incoming-pattern': "~/Downloads/Activities*.csv",
        'mfp-filename': "$COMMON/health/mfp-accum.csv",
        'omron-filename': "$COMMON/health/blood-pressure.csv",
        'omron-incoming-pattern': "~/Downloads/*BP-Logbook*.csv",
        'oura-filename': "$COMMON/health/sleep.csv",
        'physical-filename': "$COMMON/health/physical.csv",
        'weight-filename': "$COMMON/health/weight.csv",
        'temperature-file': "$COMMON/health/temperature.csv"},

    'start-page': {
        'start-page-generator': 'make_link_table.py',
        'startpage': "~/private_html/startpage.html",
        'startpage-source': "$COMMON/org/startpage.yaml",
        'startpage-style': "$COMMON/org/startpage.css"},

    'travel': {
        'travel-filename': "$COMMON/travel/travel.csv",
        'places-filename': "$COMMON/travel/places/places.csv"},

    'contacts': {
        'contacts-file': "$COMMON/org/contacts.csv"},

    'weather': {
        'weather-filename': "$COMMON/var/weather.csv"},

    'general': {
        'archive': "~/archive",
        'charts': "~/private_html/dashboard",
        'default-timetable': "timetable.csv",
        'projects-dir': "~/open-projects/github.com",
        'projects-user': "hillwithsmallfields",
        'reflections-dir': os.path.expandvars("$COMMON/texts/reflection"),
        'timetables-dir': "$COMMON/timetables"}}

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
    config = {} if no_hardcoded_default else HARDCODED_DEFAULT_CONFIG

    if not no_main_config:
        with open(main_config_file) as yaml_stream:
            rec_update(config, yaml.safe_load(yaml_stream))

    load_multiple_yaml(config, config_files)

    config = recursive_expand(config)

    return config

def lookup(config, *keys):
    for key in keys:
        config = config[key]
    return config

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
    parser.add_argument("keys", nargs='*')
    args = parser.parse_args()

    config = load_config(args.no_hardcoded_default,
                         args.no_main_config,
                         args.main_config_file,
                         args.config_file)

    if args.show_all:
        print(config)
    else:
        print(lookup(config, *args.keys))

if __name__ == '__main__':
    main()
