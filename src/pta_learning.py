#!/usr/bin/env python3

"""
Tool for learning DPAs using prefix tree acceptor construction (including
evaluation).

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
import sys
import getopt
import os
import os.path
import csv
import math
import random

import learning.fpt as fpt
import learning.alergia as alergia
import parser.core_parser as core_parser
import parser.wfa_parser as wfa_parser
import wfa.core_wfa_export as core_wfa_export
import parser.IEC104_parser as con_par

import wfa.aux_functions as aux

rows_filter = ["asduType", "cot"]
TRAINING = 0.33


def create_fpt(ln, ren_dict):
    tree = fpt.FPT()
    lines = con_par.rename_values(ln, ren_dict)
    tree.add_string_list(ln)
    return tree


"""
Abstraction on messages
"""
def abstraction(item):
    return tuple([item[k] for k in rows_filter])


"""
Print help message
"""
def print_help():
    print("./pta_learning <csv file>")


"""
Main
"""
def main():
    argc = len(sys.argv)
    if argc < 2:
        sys.stderr.write("Error: bad parameters\n")
        print_help()
        sys.exit(1)

    csv_file = sys.argv[1]
    csv_fd = open(csv_file, "r")
    csv_file = os.path.basename(csv_file)

    ############################################################################
    # Preparing the learning data
    ############################################################################
    normal_msgs = con_par.get_messages(csv_fd)
    parser = con_par.IEC104Parser(normal_msgs)
    parser.parse_conversations()
    lines = parser.get_all_conversations(abstraction)

    ren_dict = con_par.values_bidict(lines)
    index = int(len(lines)*TRAINING)
    training, testing = lines[:index], lines[index:]

    tree = create_fpt(training, ren_dict)
    tree.rename_states()
    fa = tree.normalize()

    store_filename = os.path.splitext(os.path.basename(csv_file))[0]
    store_filename = "{0}".format(store_filename)

    fa_fd = open("{0}-pta.fa".format(store_filename), "w")
    fa_fd.write(fa.to_fa_format(True))
    fa_fd.close()

    legend = "File: {0} PTA".format(csv_file)
    dot_fd = open("{0}-pta.dot".format(store_filename), "w")
    dot_fd.write(fa.to_dot(aggregate=False, legend=legend))
    dot_fd.close()

    miss = 0
    for line in testing:
        prob = fa.string_prob_deterministic(line)
        if prob is None:
            miss += 1

    print("File: {0}".format(csv_file))
    print("States {0}".format(len(tree.get_states())))
    print("Testing: {0}/{1} (missclassified/all)".format(miss, len(testing)))
    print("Accuracy: {0}".format((len(testing)-miss)/float(len(testing))))

    csv_fd.close()


if __name__ == "__main__":
    main()
