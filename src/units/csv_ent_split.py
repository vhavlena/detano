#!/usr/bin/env python3

"""
Divide a csv file containing a list of messages into conversation and
communication entities.

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
HEAD = "TimeStamp;srcIP;dstIP;srcPort;dstPort;ipLen;len;fmt;uType;asduType;numix;cot;oa;addr;ioa"
DELIMITER = ";"

def format_row(row):
    return DELIMITER.join(row.values())

def main():
    argc = len(sys.argv)
    if argc != 2:
        sys.stderr.write("Bad parameters\n")
        print_help()
        sys.exit(1)

    csv_file = sys.argv[1]
    csv_fd = open(csv_file, "r")

    bname = os.path.basename(csv_file)
    store_filename = os.path.splitext(os.path.basename(bname))[0]

    normal_msgs = con_par.get_messages(csv_fd)
    distict_dict = dict()
    fnames = None
    all_cnt = 0
    for row in normal_msgs:
        if fnames is None:
            fnames = row.keys()
        fd = None
        items = []
        for flt in rows_filters:
            items.append(tuple([row[k] for k in flt]))
        key = frozenset(items)
        if not key in distict_dict:
            distict_dict[key] = open("{0}-part{1}.csv".format(store_filename, all_cnt), "w")
            distict_dict[key].write(DELIMITER.join(fnames) + "\n")
            all_cnt += 1
        fd = distict_dict[key]
        fd.write("{0}\n".format(format_row(row)))

    csv_fd.close()


if __name__ == "__main__":
    main()
