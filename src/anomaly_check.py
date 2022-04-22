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
import copy
from dataclasses import dataclass
from collections import defaultdict
from enum import Enum

from typing import List, Tuple, FrozenSet, Callable, Union

import learning.fpt as fpt
import learning.alergia as alergia
import wfa.core_wfa as core_wfa
import wfa.core_wfa_export as core_wfa_export
import wfa.matrix_wfa as matrix_wfa
import parser.IEC104_parser as con_par
import parser.conversation_parser_base as con_base
import detection.distr_comparison as distr
import detection.member as mem
import parser.IEC104_conv_parser as iec_prep_par

SPARSE = False

rows_filter_normal = ["asduType", "cot"]
DURATION = 300
AGGREGATE = True
ACCELERATE = False


ComPairType = FrozenSet[Tuple[str,str]]
AutListType = List[Union[core_wfa_export.CoreWFAExport,None]]

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


class InputFormat(Enum):
    IPFIX = 0
    CONV = 1


"""!
Details about the anomalies
"""
@dataclass
class AnomDetails:
    bad_conv : List
    test_aut : core_wfa.CoreWFA
    model_aut : core_wfa.CoreWFA


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
    file_format : InputFormat
    threshold : float


"""
Abstraction on messages
"""
def abstraction(item: dict[str, str]) -> Tuple[str, ...]:
    return tuple([item[k] for k in rows_filter_normal])


"""
PA learning
"""
def learn_proc_pa(training: List) -> core_wfa_export.CoreWFAExport:
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
def learn_proc_pta(training: List) -> core_wfa_export.CoreWFAExport:
    tree = fpt.FPT()
    tree.add_string_list(training)
    aut = tree
    aut.rename_states()
    return aut.normalize()


"""
Communication entity string format
"""
def ent_format(k: ComPairType) -> str:
    [(fip, fp), (sip, sp)] = list(k)
    return "{0}:{1} -- {2}:{3}".format(fip, fp, sip, sp)


def conv_format(conv: List) -> str:
    return "".join([str(elem) for elem in conv])


"""
Convert a list of conversations into a string
"""
def conv_list_format(l: List) -> str:
    ret = str()
    for num, sym in enumerate(l):
        ret += "{0}. {1}\n".format(num+1, conv_format(sym))
    return ret


"""
Learn a golden model (for distr detection) from the given dataset
"""
def learn_golden_distr(parser: con_base.ConvParserBase, learn_proc: Callable, par: Params) -> dict[ComPairType, AutListType]:
    ret: dict[ComPairType, AutListType] = defaultdict(lambda: [None])
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
def learn_golden_member(parser: con_base.ConvParserBase, learn_proc: Callable, par: Params) -> dict[ComPairType, AutListType]:
    ret: dict[ComPairType, AutListType] = defaultdict(lambda: [None])
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
    print("\t--format=conv/ipfix\tformat of input data: conversations (conv) or csv data in ipfix format (ipfix)")
    print("\t--smoothing\t\tuse smoothing (for distr only)")
    print("\t--reduced=val\t\tremove similar automata with the error upper-bound val [0,1] (for distr only)")
    print("\t--threshold=val\t\tdetect anomalies with a given threshold (for distr only)")
    print("\t--help\t\t\tprint this message")


"""
Distribution-comparison-based anomaly detection
"""
def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hr:t:a:sf:", ["help", "reduced=", "atype=", "alg=", "smoothing", "format=", "threshold="])
        if len(args) > 1:
            opts, _ = getopt.getopt(sys.argv[3:], "hr:t:a:sf:", ["help", "reduced=", "atype=", "alg=", "smoothing", "format=", "threshold="])
    except getopt.GetoptError as err:
        sys.stderr.write("Error: bad parameters (try --help)\n")
        sys.exit(1)

    par = Params(Algorithms.DISTR, None, None, AutType.PA, None, False, InputFormat.IPFIX, None)
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
        elif o in ("--threshold"):
            par.threshold = float(a)
        elif o == "--smoothing":
            par.smoothing = True
        elif o in ("-h", "--help"):
            print_help()
            sys.exit()
        elif o in ("-r", "--reduced"):
            par.reduced = float(a)
        elif o in ("-f", "--format"):
            if a == "conv":
                par.file_format = InputFormat.CONV
            elif a == "ipfix":
                par.file_format = InputFormat.IPFIX
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

    if par.file_format == InputFormat.IPFIX:
        normal_parser = con_par.IEC104Parser(normal_msgs)
        test_parser = con_par.IEC104Parser(test_msgs)
    elif par.file_format == InputFormat.CONV:
        normal_parser = iec_prep_par.IEC104ConvParser(normal_msgs)
        test_parser = iec_prep_par.IEC104ConvParser(test_msgs)

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


    anomalies = defaultdict(lambda: dict())
    if (par.alg == Algorithms.DISTR) and (par.threshold is not None):
        golden_map_member = learn_golden_member(normal_parser, learn_proc, par)
        anom_member = mem.AnomMember(golden_map_member, learn_proc)
    res = defaultdict(lambda: [])
    test_com = test_parser.split_communication_pairs()
    last = 0
    acc = par.threshold if ACCELERATE and par.threshold is not None else 0.0

    for item in test_com:
        cnt = 0
        wns = item.split_to_windows(DURATION)
        for window in wns:
            window.parse_conversations()
            r = anom.detect(window.get_all_conversations(abstraction), item.compair, acc)
            res[item.compair].append(r)
            last = max(cnt, last)
            if (par.alg == Algorithms.DISTR) and (par.threshold is not None):
                if min(r) > par.threshold:
                    ind = r.index(min(r))
                    model = anom.golden_map[item.compair][ind]
                    mem_det = anom_member.apply_detection(model, window.get_all_conversations(abstraction), item.compair)
                    anomalies[item.compair][cnt] = AnomDetails(mem_det, copy.deepcopy(anom.test_fa), copy.deepcopy(anom.golden_map[item.compair][ind]))
            cnt += 1

    print("Detection results: ")
    #Printing results
    print("{0} {1}".format(par.normal_file, par.test_file))
    for k, v in res.items():
        print("\n"+ent_format(k))

        if par.alg == Algorithms.DISTR:
            for i in range(len(v)):
                if i == last:
                    continue
                if AGGREGATE:
                    print("{0};{1}".format(i, min(v[i])))
                else:
                    print("{0};{1}".format(i, v[i]))
        elif par.alg == Algorithms.MEMBER:
            for i in range(len(v)):
                if i == last:
                    continue
                print("{0};{1}".format(i, [ it for its in v[i] for it in its ]))

    if (par.alg == Algorithms.DISTR) and (par.threshold is not None):
        print("\nPossibly problematic conversations: ")
        for ent, windows in anomalies.items():
            for i, det in windows.items():
                if i == last:
                    continue
                print("Communicating: {0}; Window: {1}".format(ent_format(ent), i))

                print("Bad conversations:")
                tmp = [k for k,v in itertools.groupby(sorted(det.bad_conv))]
                print(conv_list_format(tmp))

                #aut = det.model_aut
                #aut.__class__ = core_wfa_export.CoreWFAExport
                #print(aut.to_dot())

                print("Missing conversation:")
                if det.model_aut is None:
                    print("empty model")
                else:
                    word, pr = det.model_aut.difference_dwfa(det.test_aut).get_most_probable_string()
                    print(conv_format(word), pr)

                print()


if __name__ == "__main__":
    main()
