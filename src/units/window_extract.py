#!/usr/bin/env python3

"""
Tool for learning DPAs using alergia (including evaluation).

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
import ast
import math
import itertools
from collections import defaultdict
from enum import Enum

import learning.fpt as fpt
import learning.alergia as alergia
import parser.core_parser as core_parser
import wfa.core_wfa_export as core_wfa_export
import wfa.matrix_wfa as matrix_wfa
import parser.IEC104_parser as con_par
import detection.distr_comparison as distr

rows_filter_normal = ["asduType", "cot"]
DURATION = 300

"""
Abstraction on messages
"""
def abstraction(item):
    return tuple([item[k] for k in rows_filter_normal])

"""
Print help message
"""
def print_help():
    print("Extract conversations of a given window range")
    print()
    print("./window_extract <csv> <first window> <last window>")


"""
Extracting conversations in given range of window
"""
def main():
    argc = len(sys.argv)
    if argc < 4:
        sys.stderr.write("Error: bad parameters\n")
        print_help()
        sys.exit(1)

    normal_file = sys.argv[1]
    normal_fd = open(normal_file, "r")
    normal_msgs = con_par.get_messages(normal_fd)

    window_first = int(sys.argv[2])
    window_last = int(sys.argv[3])
    normal_parser = con_par.IEC104Parser(normal_msgs)

    i = 0
    test_com = normal_parser.split_communication_pairs()
    for item in test_com:
        i = 0
        [(fip, fp), (sip, sp)] = list(item.compair)
        print("{0}:{1} -- {2}:{3}".format(fip, fp, sip, sp))
        for window in item.split_to_windows(DURATION):
            window.parse_conversations()

            if i >= window_first and i <= window_last:
                conv = window.get_all_conversations(abstraction)
                print("{0}:".format(i))
                for c in conv:
                    print(c)
                print()
            i += 1

    normal_fd.close()


if __name__ == "__main__":
    main()
