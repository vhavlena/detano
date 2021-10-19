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
import parser.core_parser as core_parser
import parser.wfa_parser as wfa_parser
import wfa.core_wfa_export as core_wfa_export
import wfa.matrix_wfa as matrix_wfa
import parser.IEC104_parser as con_par
import detection.distr_comparison as distr
import detection.member as mem

SPARSE = False

rows_filter_normal = ["asduType", "cot"]
DURATION = 300
AGGREGATE = True

"""
Program parameters
"""
class Algorithms(Enum):
    DISTR = 0
    MEMBER = 1


"""
Program parameters
"""
class AutType(Enum):
    PA = 0
    PTA = 1


"""
Program parameters
"""
@dataclass
class Params:
    alg : Algorithms
    normal_file : str
    test_file : str
    aut_type : AutType
    reduced : float
    smoothing : bool


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
Communication entity string format
"""
def ent_format(k):
    [(fip, fp), (sip, sp)] = list(k)
    return "{0}:{1} -- {2}:{3}".format(fip, fp, sip, sp)


"""
Learn a golden model (for distr detection) from the given dataset
"""
def learn_golden_distr(parser, learn_proc, par):
    ret = defaultdict(lambda: [None])
    parser_com = parser.split_communication_pairs()

    for item in parser_com:
        if par.smoothing:
            ret[item.compair] = list()
            wins1 = item.split_to_windows(1*DURATION)
            wins2 = item.split_to_windows(2*DURATION)
            for window in wins1 + wins2:
                window.parse_conversations()
                training = window.get_all_conversations(abstraction)

                fa = learn_proc(training)
                ret[item.compair].append(fa)
        else:
            item.parse_conversations()
            training = item.get_all_conversations(abstraction)
            fa = learn_proc(training)
            ret[item.compair] = [fa]

    return ret


"""
Learn a golden model (for member detection) from the given dataset
"""
def learn_golden_member(parser, learn_proc, par):
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
    print("./anomaly_distr <valid traffic csv> <anomaly csv> [OPT]")
    print("OPT are from the following: ")
    print("\t--atype=pa/pta\t\tlearning based on PAs/PTAs (default PA)")
    print("\t--alg=distr/member\tanomaly detection based on comparing distributions (distr) or single message reasoning (member) (default distr)")
    print("\t--smoothing\t\tuse smoothing (for distr only)")
    print("\t--reduced=val\t\tremove similar automata with the error upper-bound val [0,1] (for distr only)")
    print("\t--help\t\t\tprint this message")


"""
Distribution-comparison-based anomaly detection
"""
def main():
    # if len(sys.argv) < 3:
    #     sys.stderr.write("Error: bad parameters (try --help)\n")
    #     sys.exit(1)

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hr:t:a:s", ["help", "reduced=", "atype=", "alg=", "smoothing"])
        if len(args) > 1:
            opts, _ = getopt.getopt(sys.argv[3:], "hr:t:a:s", ["help", "reduced=", "atype=", "alg=", "smoothing"])
    except getopt.GetoptError as err:
        sys.stderr.write("Error: bad parameters (try --help)\n")
        sys.exit(1)

    par = Params(Algorithms.DISTR, None, None, AutType.PA, None, False)
    learn_proc = learn_proc_pa
    golden_proc = learn_golden_distr

    for o, a in opts:
        if o in ("--atype", "-t"):
            if a == "pa":
                par.aut_type = AutType.PA
                learn_proc = learn_proc_pa
            elif a == "pta":
                par.aut_type = AutType.PTA
                learn_proc = learn_proc_pta
        elif o in ("--alg", "-a"):
            if a == "distr":
                par.alg = Algorithms.DISTR
                golden_proc = learn_golden_distr
            elif a == "member":
                par.alg = Algorithms.MEMBER
                golden_proc = learn_golden_member
        elif o == "--smoothing":
            par.smoothing = True
        elif o in ("-h", "--help"):
            print_help()
            sys.exit()
        elif o in ("-r", "--reduced"):
            par.reduced = float(a)
        else:
            sys.stderr.write("Error: bad parameters (try --help)\n")
            sys.exit(1)

    if len(args) < 3:
        sys.stderr.write("Missing input files (try --help)\n")
        sys.exit(1)
    par.normal_file = sys.argv[1]
    par.test_file = sys.argv[2]

    try:
        normal_fd = open(par.normal_file, "r")
        normal_msgs = con_par.get_messages(normal_fd)
        test_fd = open(par.test_file, "r")
        test_msgs = con_par.get_messages(test_fd)
        normal_fd.close()
        test_fd.close()
    except FileNotFoundError:
        sys.stderr.write("Cannot open input files\n")
        sys.exit(1)

    normal_parser = con_par.IEC104Parser(normal_msgs)
    test_parser = con_par.IEC104Parser(test_msgs)
    try:
        golden_map = golden_proc(normal_parser, learn_proc, par)
    except KeyError as e:
        sys.stderr.write("Missing column in the input csv: {0}\n".format(e))
        sys.exit(1)

    if par.alg == Algorithms.DISTR:
        anom = distr.AnomDistrComparison(golden_map, learn_proc)
        anom.remove_identical()
        if par.reduced is not None:
            anom.remove_euclid_similar(par.reduced)
        print("Automata counts: ")
        for k,v in anom.golden_map.items():
            print("{0} | {1}".format(ent_format(k), len(v)))
        print()
    elif par.alg == Algorithms.MEMBER:
        anom = mem.AnomMember(golden_map, learn_proc)

    res = defaultdict(lambda: [])
    test_com = test_parser.split_communication_pairs()
    for item in test_com:
        for window in item.split_to_windows(DURATION):
            window.parse_conversations()
            r = anom.detect(window.get_all_conversations(abstraction), item.compair)
            res[item.compair].append(r)

    print("Detection results: ")
    #Printing results
    print("{0} {1}".format(par.normal_file, par.test_file))
    for k, v in res.items():
        print(ent_format(k))

        if par.alg == Algorithms.DISTR:
            for i in range(len(v)):
                if AGGREGATE:
                    print("{0};{1}".format(i, min(v[i])))
                else:
                    print("{0};{1}".format(i, v[i]))
        elif par.alg == Algorithms.MEMBER:
            for i in range(len(v)):
                print("{0};{1}".format(i, [ it for its in v[i] for it in its ]))


if __name__ == "__main__":
    main()
