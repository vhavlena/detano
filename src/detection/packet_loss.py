"""!
\brief Packet-loss detection.

\details
    Language-based approach for a detection of packet losses. It computes edit
    distance (assuming only the delete operation) between two strings.

\author Vojtěch Havlena

\copyright
    Copyright (C) 2020  Vojtech Havlena, <ihavlena@fit.vutbr.cz>\n
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

class PacketLoss:
    """!
    Language-based approach for a detection of packet losses
    """

    @staticmethod
    def compatible_strings(str1: str, str2: str) -> bool:
        """!
        Compute edit distance (assuming only the delete operation) between two
        strings

        @param str1: First string
        @param str2: Second string

        @return edit distance of str1 and str2 (can be used to compute the
        number of lost packets)
        """
        m, n = len(str1), len(str2)
        mat = [ [0]*(n+1) for i in range((m+1))]
        for j in range(n+1):
            mat[0][j] = 1
        for i in range(1,m+1):
            for j in range(1,n+1):
                if mat[i][j-1] == 1:
                    mat[i][j] = 1
                if mat[i-1][j-1] == 1 and str1[i-1] == str2[j-1]:
                    mat[i][j] = 1
        return mat[m][n] == 1
