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
import os
import csv
import math

import learning.fpt as fpt
import learning.alergia as alergia
import parser.IEC104_parser as con_par

rows_filter = ["asduType", "cot"]
TRAINING = 0.33


"""
Abstraction on messages
"""
def abstraction(item):
    return tuple([item[k] for k in rows_filter])



"""
Print help message
"""
def print_help():
    print("./pa_learning <csv file>")


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

    normal_msgs = con_par.get_messages(csv_fd)
    parser = con_par.IEC104Parser(normal_msgs)
    parser.parse_conversations()
    lines = parser.get_all_conversations(abstraction)

    index = int(len(lines)*TRAINING)
    training, testing = lines[:index], lines[index:]

    tree = fpt.FPT()
    for line in training:
        tree.add_string(line)

    alpha = 0.05
    t0 = int(math.log(index, 2))

    aut = alergia.alergia(tree, alpha, t0)
    aut.rename_states()
    fa = aut.normalize()

    store_filename = os.path.splitext(os.path.basename(csv_file))[0]
    store_filename = "{0}a{1}t{2}".format(store_filename, alpha, t0)

    fa_fd = open("{0}.fa".format(store_filename), "w")
    fa_fd.write(fa.to_fa_format(True))
    fa_fd.close()

    legend = "File: {0}, alpha: {1}, t0: {2}".format(csv_file, alpha, t0)
    dot_fd = open("{0}.dot".format(store_filename), "w")
    dot_fd.write(fa.to_dot(aggregate=False, legend=legend))
    dot_fd.close()

    miss = 0
    for line in testing:
        prob = fa.string_prob_deterministic(line)
        if prob is None:
            miss += 1

    print("File: {0}".format(csv_file))
    print("alpha: {0}, t0: {1}".format(alpha, t0))
    print("States {0}".format(len(aut.get_states())))
    print("Testing: {0}/{1} (missclassified/all)".format(miss, len(testing)))
    if len(testing) > 0:
        print("Accuracy: {0}".format((len(testing)-miss)/float(len(testing))))

    csv_fd.close()


if __name__ == "__main__":
    main()
