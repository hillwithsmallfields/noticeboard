#!/usr/bin/env python3

import argparse
import csv
import sys

PREAMBLE="""<html>
<head>
<title>%s</title>
<style>
pre {
  font-size: %d;
}
</style>
</head>
<body>
<h1>%s</h1>
<pre>
"""

POSTAMBLE="""
</pre></body></html>
"""

def read_table(filename, begin, end):
    """Read a CSV file and optionally trim by rows."""
    with open(filename, encoding='utf-8') as instream:
        rows = list(csv.reader(instream))
    return rows[begin:end or len(rows)]

def adjust_cell(cell, width, padding, extend):
    if extend and cell == extend:
        cell = cell[0] * width
    return cell.ljust(width, padding)

def align_cells(table, padding, vgrid, extend=None):
    """Align the cells of a table for display as monospaced character graphics.
    The input is a list of lists of strings, and the result is a list of strings."""
    widths = [max([len(cell) for cell in column])
              for column in zip(*table)]
    return "\n".join([vgrid.join([adjust_cell(cell, widths[icol], padding, extend)
                                  for icol, cell in enumerate(row)])
                      for row in table]) + "\n"

def write_table(table, output_filename, htmlize, title, font_size):
    """Write a table provided as a list of strings."""
    with (open(output_filename, 'w', encoding='utf-8')
          if output_filename
          else sys.stdout) as outstream:

        if htmlize:
            outstream.write(PREAMBLE % (title, font_size, title))

        outstream.write(table)

        if htmlize:
            outstream.write(POSTAMBLE)

def main():
    """Convert a CSV file into an 'ASCII graphics' table.
    Optionally make a web page of it.
    Intended for laying out stripboard circuitry.
    The column order can be flipped."""
    parser = argparse.ArgumentParser()
    parser.add_argument("inputfile")
    parser.add_argument("--begin", "-b",
                        type=int,
                        default=0,
                        help="""Start at this row.""")
    parser.add_argument("--end", "-e",
                        type=int,
                        default=0,
                        help="""End at this row.""")
    parser.add_argument("--pad", "-p",
                        type=str, default=" ",
                        help="""Pad cells with this character.""")
    parser.add_argument("--extend", "-x",
                        default="---",
                        help="""Stretch cells equal to this string.""")
    parser.add_argument("--vgrid", "-V",
                        type=str, default=" ",
                        help="""Use this character between columns.""")
    parser.add_argument("--reversed", "-r",
                        action='store_true',
                        help="""Reverse the column order.""")
    parser.add_argument("--html",
                        action='store_true',
                        help="""Wrap the output to make an HTML page.""")
    parser.add_argument("--font-size",
                        type=int,
                        default=8,
                        help="""The font size to use for HTML output.""")
    parser.add_argument("--title",
                        default="",
                        help="""The title to set for HTML output.""")
    parser.add_argument("--output", "-o")
    args = parser.parse_args()

    table = read_table(args.inputfile, args.begin, args.end)

    write_table(align_cells(([list(reversed(row)) for row in table]
                             if args.reversed
                             else table),
                            args.pad[0],
                            args.vgrid[0],
                            args.extend),
                args.output, args.html,
                args.title, args.font_size)

if __name__ == "__main__":
    main()
