#!/usr/bin/env python3

"""
Anomaly detection based on a single conversation inspection.

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

import parser.core_parser as core_parser
import parser.wfa_parser as wfa_parser
import wfa.core_wfa_export as core_wfa_export
import parser.conversation_parser as con_par

import wfa.aux_functions as aux

rows_filter = ["asduType", "cot"]

def print_help():
    print("Usage: ")
    print("./anomaly_detector.py <aut.fa> <csv-conversations>")


def main():
    argc = len(sys.argv)
    if argc != 3:
        sys.stderr.write("Bad parameters\n")
        print_help()
        sys.exit(1)

    fa_file = sys.argv[1]
    csv_file = sys.argv[2]

    fa_fd = open(fa_file, "r")
    csv_fd = open(csv_file, "r")

    wfa = wfa_parser.WFAParser.fa_to_wfa(fa_fd)
    wfa.map_symbols(lambda s: ast.literal_eval("{0}".format(s)))

    if not wfa.is_deterministic():
        sys.stderr.write("Automaton is not deterministic.\n")
        sys.exit(1)

    reader = csv.DictReader(csv_fd, delimiter=";")
    lines = con_par.filter_to_conversations(reader, rows_filter)
    for line in lines:
        prob = wfa.string_prob_deterministic(line)
        if prob is None:
            print("String is not accepted: {0}".format(line))
            continue

if __name__ == "__main__":
    main()
