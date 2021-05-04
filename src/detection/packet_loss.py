"""
Packet-loss detection.

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

class PacketLoss:

    @staticmethod
    def compatible_strings(str1, str2):
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
