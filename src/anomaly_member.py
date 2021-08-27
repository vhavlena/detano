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
from dataclasses import dataclass
from collections import defaultdict
from enum import Enum

import learning.fpt as fpt
import learning.alergia as alergia
import parser.IEC104_parser as con_par
import detection.member as mem

rows_filter_normal = ["asduType", "cot"]
DURATION = 300

"""
Program parameters
"""
class Algorithms(Enum):
    PA = 0
    PTA = 1


@dataclass
class Params:
    alg : Algorithms
    normal_file : str
    test_file : str
    reduced : float



"""
Abstraction on messages
"""
def abstraction(item):
    return tuple([item[k] for k in rows_filter_normal])


"""
PA learning
"""
def learn_proc_pa(training):
    tree = fpt.FPT()
    tree.add_string_list(training)
    alpha = 0.05
    if len(training) > 0:
        t0 = int(math.log(len(training), 2))
    else:
        t0 = 1
    aut = alergia.alergia(tree, alpha, t0)
    aut.rename_states()
    return aut.normalize()


"""
PTA learning
"""
def learn_proc_pta(training):
    tree = fpt.FPT()
    tree.add_string_list(training)
    aut = tree
    aut.rename_states()
    return aut.normalize()


"""
Learn a golden model from the given dataset
"""
def learn_golden(parser, learn_proc):
    ret = defaultdict(lambda: [None])
    parser_com = parser.split_communication_pairs()

    for item in parser_com:
        item.parse_conversations()
        training = item.get_all_conversations(abstraction)

        fa = learn_proc(training)
        ret[item.compair] = [fa]

    return ret


"""
Print help message
"""
def print_help():
    print("Anomaly detection based on membership test")
    print()
    print("./anomaly_member <valid traffic csv> <anomaly csv> <opts>")
    print("<opts> are from the following:")
    print("  --pa detection based on PAs")
    print("  --pta detection based on PTAs")


"""
Distribution-comparison-based anomaly detection
"""
def main():
    argc = len(sys.argv)
    if argc < 3:
        sys.stderr.write("Error: bad parameters\n")
        print_help()
        sys.exit(1)

    par = Params(Algorithms.PA, sys.argv[1], sys.argv[2], None)
    learn_proc = None
    try:
        opts, args = getopt.getopt(sys.argv[3:], "h", ["help", "pa", "pta"])
    except getopt.GetoptError as err:
        sys.stderr.write("Error: bad parameters\n")
        print_help()
        sys.exit(1)
    for o, a in opts:
        if o == "--pa":
            par.alg = Algorithms.PA
            learn_proc = learn_proc_pa
        elif o == "--pta":
            par.alg = Algorithms.PTA
            learn_proc = learn_proc_pta
        elif o in ("-h", "--help"):
            print_help()
            sys.exit()
        else:
            sys.stderr.write("Error: bad parameters\n")
            print_help()
            sys.exit(1)

    normal_fd = open(par.normal_file, "r")
    normal_msgs = con_par.get_messages(normal_fd)

    test_fd = open(par.test_file, "r")
    test_msgs = con_par.get_messages(test_fd)

    normal_parser = con_par.IEC104Parser(normal_msgs)
    test_parser = con_par.IEC104Parser(test_msgs)

    golden_map = learn_golden(normal_parser, learn_proc)
    anom = mem.AnomMember(golden_map, learn_proc)

    res = defaultdict(lambda: [])
    test_com = test_parser.split_communication_pairs()
    for item in test_com:
        for window in item.split_to_windows(DURATION):
            window.parse_conversations()
            r = anom.detect(window.get_all_conversations(abstraction), item.compair)
            res[item.compair].append(r)

    #Printing results
    for k, v in res.items():
        print(k)
        for i in range(len(v)):
            print("{0}: {1}".format(i, [ it for its in v[i] for it in its ]))

    normal_fd.close()
    test_fd.close()


if __name__ == "__main__":
    main()
