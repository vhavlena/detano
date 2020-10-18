#!/usr/bin/env python3

"""
Tool for approximate reductions of finite automata used in network traffic
monitoring. Taken and modified from https://github.com/vhavlena/appreal

Copyright (C) 2017  Vojtech Havlena, <xhavle03@stud.fit.vutbr.cz>

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

def convert_to_pritable(dec, dot=False):
    """Convert string containing also non-printable characters to printable hexa
    number. Inspired by the Netbench tool.

    Return: Input string with replaced nonprintable symbols with their hexa numbers.
    Keyword arguments:
    dec -- Input string.
    dot -- Use the result for converting to dot format.
    """
    esc_str = str()
    for ch in dec:
        if (ord(ch) < 30) or (ord(ch) > 127) or (ch == '\'') or (ch == '"') or (ch == '\\' and not dot):
            esc_str += "\\{0}".format(hex(ord(ch)))
        elif (ch == '\\') and (not dot):
            esc_str += "\\"
        else:
            esc_str += ch
    return esc_str
