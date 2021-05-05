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

import parser.IEC104_parser as con_par

DELIMITER = ";"

"""
Abstraction on messages
"""
def abstraction(item):
    return tuple([item[k] for k in rows_filter])


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

    normal_msgs = con_par.get_messages(csv_fd)
    parser = con_par.IEC104Parser(normal_msgs)
    parser.parse_conversations()
    lines = parser.get_all_conversations()

    for line in lines:
        for row in line:
            print_row(row)
        print(DELIMITER*(14))

    csv_fd.close()


if __name__ == "__main__":
    main()
