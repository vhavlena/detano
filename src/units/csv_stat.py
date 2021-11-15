#!/usr/bin/env python3

"""
Tool computing statistics about a csv file containing conversations.

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

rows_filters = [["srcIP", "srcPort"], ["dstIP", "dstPort"]]
DELIMITER = ";"

"""
Abstraction on messages
"""
def abstraction(item):
    return tuple([item[k] for k in rows_filter])

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

    distict_set = set()
    inform_cnt = 0
    all_cnt = 0
    for row in normal_msgs:
        for flt in rows_filters:
            item = tuple([row[k] for k in flt])
            distict_set.add(item)
        if con_par.IEC104Parser.is_inform_message(row):
            inform_cnt += 1
        all_cnt += 1

    print("#messages: {0}".format(all_cnt))
    print("#i-messages: {0}".format(inform_cnt))
    print("#entities: {0}".format(len(distict_set)))
    print("entities: {0}".format(distict_set))
    print("#conversations: {0}".format(len(lines)))

    csv_fd.close()


if __name__ == "__main__":
    main()
