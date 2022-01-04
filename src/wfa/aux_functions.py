#!/usr/bin/env python3

"""!
\brief Auxiliary functions for WFAs

\details
    Auxiliary functions for printing WFAs. Taken and modified from
    <https://github.com/vhavlena/appreal>

\author Vojtěch Havlena

\copyright
    Copyright (C) 2017  Vojtech Havlena, <xhavle03@stud.fit.vutbr.cz>\n
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 2 of the License, or
    (at your option) any later version.\n
    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.\n
    You should have received a copy of the GNU General Public License.
    If not, see <http://www.gnu.org/licenses/>.
"""

def convert_to_pritable(dec: str, dot: bool=False) -> str:
    """!
    Convert string containing also non-printable characters to printable hexa
    number. Inspired by the Netbench tool.

    @param dec: Input string.
    @param dot: Use the result for converting to dot format.

    @return Input string with replaced nonprintable symbols with their hexa numbers.
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
