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
import parser.wfa_parser as wfa_parser
import wfa.core_wfa_export as core_wfa_export
import wfa.matrix_wfa as matrix_wfa
import parser.conversation_parser as con_par
import detection.distr_comparison as distr

SPARSE = False

rows_filter_normal = ["asduType", "cot"]
DURATION = 300

"""
Program parameters
"""
class Params(Enum):
    PA = 0
    PTA = 1


"""
Get all messages from a csv file
"""
def get_messages(fd):
    reader = csv.DictReader(fd, delimiter=";")
    ret = []
    for item in reader:
        ret.append(item)
    return ret


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
    ret = defaultdict(lambda: None)
    parser_com = parser.split_communication_pairs()

    for item in parser_com:
        item.parse_conversations()
        training = item.get_all_conversations(abstraction)

        fa = learn_proc(training)
        ret[item.compair] = fa

    return ret


"""
Distribution-comparison-based anomaly detection
"""
def main():
    argc = len(sys.argv)
    if argc < 4:
        sys.stderr.write("Bad parameters\n")
        sys.exit(1)

    alg = Params.PA
    learn_proc = None
    if sys.argv[1] == "--pa":
        alg = Params.PA
        learn_proc = learn_proc_pa
    elif sys.argv[1] == "--pta":
        alg = Params.PTA
        learn_proc = learn_proc_pta

    normal_file = sys.argv[2]
    normal_fd = open(normal_file, "r")
    normal_msgs = get_messages(normal_fd)

    test_file = sys.argv[3]
    test_fd = open(test_file, "r")
    test_msgs = get_messages(test_fd)

    normal_parser = con_par.ConvParser(normal_msgs)
    test_parser = con_par.ConvParser(test_msgs)

    golden_map = learn_golden(normal_parser, learn_proc)
    anom = distr.AnomDistrComparison(golden_map, learn_proc)

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
            print("{0}: {1}".format(i, v[i]))

    normal_fd.close()
    test_fd.close()


if __name__ == "__main__":
    main()
