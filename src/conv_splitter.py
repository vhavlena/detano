#!/usr/bin/env python3

"""
Tool dividing a csv file containing a list of messages into conversations.

Copyright (C) 2020  Vojtech Havlena, <ihavlena@fit.vutbr.cz>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License.
If not, see <http://www.gnu.org/licenses/>.
"""

import sys
import getopt
import os
import os.path
import csv
import collections

import parser.conversation_parser as con_par

DELIMITER = ";"

def print_help():
    print("Usage: ")
    print("./conv_splitter.py <csv>")


def print_row(row):
    print(DELIMITER.join(row.values()))


def main():
    argc = len(sys.argv)
    if argc != 2:
        sys.stderr.write("Bad parameters\n")
        print_help()
        sys.exit(1)

    csv_file = sys.argv[1]
    csv_fd = open(csv_file, "r")

    reader = csv.DictReader(csv_fd, delimiter=DELIMITER)
    buffer = collections.deque([], 4)
    print(DELIMITER.join(reader.fieldnames))

    parser = con_par.ConvParser(list(reader))
    conv = parser.get_conversation()
    while conv is not None:
        for row in conv:
            print_row(row)
        print(DELIMITER*(14))
        conv = parser.get_conversation()

    csv_fd.close()


if __name__ == "__main__":
    main()
