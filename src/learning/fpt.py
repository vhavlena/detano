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
        self.flanguages = defaultdict(lambda: defaultdict(lambda: 0))


    def __init__(self):
        rt = tuple([])
        ini = defaultdict(lambda: 0)
        ini[rt] = 0
        super(FPT, self).__init__(set([rt]), defaultdict(lambda: dict()), ini, defaultdict(lambda: 0), rt)
        self.flanguages = defaultdict(lambda: defaultdict(lambda: 0))


    def __str__(self):
        return self.show()


    """
    Partition given set to equivalent classes according to a relation
    """
    def _partition_set(self, st, mp):
        act = []
        for item in st:
            found = False
            for eq in act:
                if mp[item] == mp[eq[0]]:
                    eq.append(item)
                    found = True
                    break
            if not found:
                act.append([item])
        return [set(u) for u in act]


    """
    Normalize flanguages for each state
    """
    def _normalize_flanguages(self):
        for st in self._states:
            s = sum(self.flanguages[st].values())
            nd = {}
            for k, v in self.flanguages[st].items():
                nd[k] = v/float(s)
            self.flanguages[st] = nd


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


    def _create_branch(self, state, string, label):
        act = state
        dest = None
        for i in range(len(string)):
            dest = act + tuple([string[i]])
            self.flanguages[dest][tuple(string[i+1:])] += 1
            self._states.add(dest)
            self._trans[act][string[i]] = ffa.FFATrans(act, dest, 1, string[i], label)
            act = dest
        self._fin[act] = self._fin[act] + 1


    """
    Get leaves (states without outgoing transitions)
    """
    def get_leaves(self):
        lv = set()
        for st in self.get_states():
            if len(self.successors(st)) == 0:
                lv.add(st)
        return lv



    """
    Merge equivalent backward deterministic states
    """
    def suffix_minimize(self):
        inv = self.inverse_ffa()
        fin = self._fin.keys()

        self._normalize_flanguages()
        classes = self._partition_set(self.get_states(), self.flanguages)
        self.merge_equivalent(classes)
        self.merge_states(self.get_leaves())



    """
    Count edges with labels corresponding to label
    """
    def count_label_edges(self, label):
        cnt = 0
        for tr in self.get_transition_list():
            if tr.label == label:
                cnt += 1
        return cnt


    """
    Add string to frequency prefix tree
    """
    def add_string(self, string, label=0):
        act = self._root
        self._ini[act] = self._ini[act] + 1
        for i in range(len(string)):
            try:
                self.flanguages[act][tuple(string[i:])] += 1
                trans = self._trans[act][string[i]]
                trans.weight = trans.weight + 1
                trans.label = min(trans.label, label)
                act = trans.dest
            except KeyError:
                self._create_branch(act, string[i:], label)
                return
        self.flanguages[act][()] += 1
        self._fin[act] = self._fin[act] + 1


    def add_string_list(self, lst, label=0):
        for item in lst:
            self.add_string(item, label)
