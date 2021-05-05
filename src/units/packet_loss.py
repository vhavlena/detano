#!/usr/bin/env python3

"""
Tool for packet loss detection based on adding symbol distance.

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

from collections import defaultdict
import learning.fpt as fpt
import learning.alergia as alergia
import FAdo.fa
import detection.packet_loss as pl
import parser.IEC104_parser as con_par


rows_filter = ["asduType", "cot"]
THR = 1

"""
Abstraction on messages
"""
def abstraction(item):
    return tuple([item[k] for k in rows_filter])


"""
Main
"""
def main():
    argc = len(sys.argv)
    if argc < 2:
        sys.stderr.write("Bad parameters\n")
        sys.exit(1)

    obs_file = sys.argv[1]
    obs_fd = open(obs_file, "r")

    normal_msgs = con_par.get_messages(obs_fd)
    parser = con_par.IEC104Parser(normal_msgs)
    parser.parse_conversations()
    lines = parser.get_all_conversations(abstraction)

    strings = defaultdict(lambda: 0)
    for line in lines:
        strings[tuple(line)] += 1

    significant = dict(filter(lambda e: e[1] > 1, strings.items()))
    suspicious = dict(filter(lambda e: e[1] <= 1, strings.items()))
    for orig, _ in significant.items():
        for sus, _ in suspicious.items():
            if pl.PacketLoss.compatible_strings(sus, orig) and len(orig) - len(sus) <= THR:
                print(orig, sus, len(orig) - len(sus))


    obs_fd.close()


if __name__ == "__main__":
    main()
