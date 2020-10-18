#!/usr/bin/env python3

"""
Tool computing Euclid distance of two DPAs.

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

import parser.core_parser as core_parser
import parser.wfa_parser as wfa_parser
import wfa.core_wfa_export as core_wfa_export
import wfa.matrix_wfa as matrix_wfa
import parser.conversation_parser as con_par

SPARSE = False

def main():
    argc = len(sys.argv)
    if argc < 3:
        sys.stderr.write("Wrong parameters\nUsage: ./euclid_distance aut1.fa aut2.fa\n")
        sys.exit(1)

    aut1_file = sys.argv[1]
    aut2_file = sys.argv[2]
    aut1_fd = open(aut1_file, "r")
    aut2_fd = open(aut2_file, "r")

    wfa1 = wfa_parser.WFAParser.fa_to_wfa(aut1_fd)
    wfa1.map_symbols(lambda s: ast.literal_eval("{0}".format(s)))

    wfa2 = wfa_parser.WFAParser.fa_to_wfa(aut2_fd)
    wfa2.map_symbols(lambda s: ast.literal_eval("{0}".format(s)))

    if not wfa1.is_deterministic() or not wfa2.is_deterministic():
        sys.stderr.write("Automaton is not deterministic.\n")
        aut1_fd.close()
        aut2_fd.close()
        sys.exit(1)

    pr1 = wfa1.product(wfa1).get_trim_automaton()
    pr2 = wfa1.product(wfa2).get_trim_automaton()
    pr3 = wfa2.product(wfa2).get_trim_automaton()

    pr1.rename_states()
    pr2.rename_states()
    pr3.rename_states()

    pr1.__class__ = matrix_wfa.MatrixWFA
    pr2.__class__ = matrix_wfa.MatrixWFA
    pr3.__class__ = matrix_wfa.MatrixWFA

    res1 = pr1.compute_language_probability(matrix_wfa.ClosureMode.inverse, SPARSE)
    res2 = pr2.compute_language_probability(matrix_wfa.ClosureMode.inverse, SPARSE)
    res3 = pr3.compute_language_probability(matrix_wfa.ClosureMode.inverse, SPARSE)
    dist = math.sqrt(res1 - 2*res2 + res3)

    print(dist)

    aut1_fd.close()
    aut2_fd.close()


if __name__ == "__main__":
    main()
