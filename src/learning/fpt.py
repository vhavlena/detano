#!/usr/bin/env python3

"""
Class for frequency prefix tree automata.

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

import learning.ffa as ffa
import learning.dffa as dffa
from collections import defaultdict


class FPT(dffa.DFFA):

    def __init__(self, states, trans, ini, fin):
        super(FPT, self).__init__(states, trans, ini, fin)


    def __init__(self):
        rt = tuple([])
        ini = defaultdict(lambda: 0)
        ini[rt] = 0
        super(FPT, self).__init__(set([rt]), defaultdict(lambda: dict()), ini, defaultdict(lambda: 0), rt)


    def __str__(self):
        return self.show()


    def show(self):
        ret = str()
        ret += "Initials: \n"
        for state, weight in self._ini.items():
            ret += "{0}: {1}\n".format(state, weight)
        ret += "Finals: \n"
        for state, weight in self._fin.items():
            ret += "{0}: {1}\n".format(state, weight)
        ret += "Transitions: \n"
        for src, dct in self._trans.items():
            for sym, tr in dct.items():
                ret += "{0} -{1}-> {2}: {3}\n".format(tr.src, tr.symbol, tr.dest, tr.weight)
        return ret


    def _create_branch(self, state, string):
        act = state
        dest = None
        for ch in string:
            dest = act + tuple([ch])
            self._states.add(dest)
            self._trans[act][ch] = ffa.FFATrans(act, dest, 1, ch)
            act = dest
        self._fin[act] = self._fin[act] + 1


    """
    Add string to frequency prefix tree
    """
    def add_string(self, string):
        act = self._root
        self._ini[act] = self._ini[act] + 1
        for i in range(len(string)):
            try:
                trans = self._trans[act][string[i]]
                trans.weight = trans.weight + 1
                act = trans.dest
            except KeyError:
                self._create_branch(act, string[i:])
                return
        self._fin[act] = self._fin[act] + 1


    def add_string_list(self, lst):
        for item in lst:
            self.add_string(item)
