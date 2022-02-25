#!/usr/bin/env python3

import argparse
import csv

def make_table(filename, colname, nformat):
    """Make a renumbering table."""
    with open(filename) as instream:
        return {row[colname]: nformat % rownum
                for rownum, row in enumerate(csv.DictReader(instream))}

def renumber_file(filename, renumbering_table):
    """Renumber entries in a file."""
    with open(filename) as instream:
        rows = list(csv.reader(instream))
    with open(filename, 'w') as outstream:
        writer = csv.writer(outstream)
        for row in rows:
            writer.writerow([renumbering_table.get(cell, cell) for cell in row])

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--renumber", "-r", default="Wire")
    parser.add_argument("--format", "-f", default="w%d")
    parser.add_argument("--verbose", "-v", action='store_true')
    parser.add_argument("--dry-run", "-n", action='store_true')
    parser.add_argument("inputfiles", nargs='*')
    args = parser.parse_args()
    renumbering_table = make_table(args.inputfiles[0],
                                   args.renumber,
                                   args.format)
    if args.verbose:
        for k in sorted(renumbering_table.keys()):
            print(k, renumbering_table[k])
    if not args.dry_run:
        for filename in args.inputfiles:
            renumber_file(filename, renumbering_table)

if __name__ == "__main__":
    main()
