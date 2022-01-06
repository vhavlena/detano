#!/usr/bin/env python3

"""!
\brief Class for frequency prefix tree automataa

\details Class providing operations for frequency prefix tree automata

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

import learning.ffa as ffa
import learning.dffa as dffa
from collections import defaultdict
from typing import Set, Tuple, Any, List


class FPT(dffa.DFFA):
    """!
    Frequency prefix tree (FPT)
    """

    def __init__(self, states: Set[ffa.StateType], trans: ffa.TransFuncDetType, ini: ffa.StateWeightType, fin: ffa.StateWeightType):
        """!
        Constructor

        @param states: States of the DFFA
        @param trans: Transitions of the DFFA
        @param ini: Initial states
        @param fin: Final states
        """
        super(FPT, self).__init__(states, trans, ini, fin)
        self.flanguages: dict[ffa.StateType, dict[Tuple, float]] = defaultdict(lambda: defaultdict(lambda: 0))


    def __init__(self):
        """!
        Default constructor
        """
        rt = tuple([])
        ini = defaultdict(lambda: 0)
        ini[rt] = 0
        super(FPT, self).__init__(set([rt]), defaultdict(lambda: dict()), ini, defaultdict(lambda: 0), rt)
        self.flanguages: dict[ffa.StateType, dict[Tuple, float]] = defaultdict(lambda: defaultdict(lambda: 0))


    def __str__(self) -> str:
        """!
        Convert to a string representation
        """
        return self.show()


    def _partition_set(self, st: ffa.StateType, mp: dict[ffa.StateType, Any]) -> List[Set[ffa.StateType]]:
        """!
        Partition given set to equivalent classes according to a relation

        @param st: Set of states
        @param mp: Relation

        @return: Partitioning of the set st
        """
        act: List[List[ffa.StateType]] = []
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


    def _normalize_flanguages(self) -> None:
        """!
        Normalize flanguages for each state
        """
        for st in self._states:
            s = sum(self.flanguages[st].values())
            nd = {}
            for k, v in self.flanguages[st].items():
                nd[k] = v/float(s)
            self.flanguages[st] = nd


    def show(self) -> str:
        """!
        Convert the FPT to a string representation

        @return String representation of the FPT
        """
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


    def _create_branch(self, state: ffa.StateType, string: str, label: int) -> None:
        """!
        Create new branch in the FPT for the string string

        @param state: First state
        @param string: String to be added to the FPT
        @param label: Label of the new added string
        """
        act = state
        dest = None
        for i in range(len(string)):
            dest = act + tuple([string[i]])
            self.flanguages[dest][tuple(string[i+1:])] += 1
            self._states.add(dest)
            self._trans[act][string[i]] = ffa.FFATrans(act, dest, 1, string[i], label)
            act = dest
        self._fin[act] = self._fin[act] + 1


    def get_leaves(self) -> Set[ffa.StateType]:
        """!
        Get leaves (states without outgoing transitions)

        @return Set of leaves
        """
        lv = set()
        for st in self.get_states():
            if len(self.successors(st)) == 0:
                lv.add(st)
        return lv


    def suffix_minimize(self) -> None:
        """!
        Merge equivalent backward deterministic states
        """
        inv = self.inverse_ffa()
        fin = self._fin.keys()

        self._normalize_flanguages()
        classes = self._partition_set(self.get_states(), self.flanguages)
        self.merge_equivalent(classes)
        self.merge_states(self.get_leaves())


    def count_label_edges(self, label: int) -> int:
        """!
        Count edges with labels corresponding to label

        @param label: Label of an edge

        @return Number of edge labelled by label
        """
        cnt = 0
        for tr in self.get_transition_list():
            if tr.label == label:
                cnt += 1
        return cnt


    def add_string(self, string: str, label: int=0) -> None:
        """!
        Add string to the frequency prefix tree

        @param string: String to be added to the FPT
        @param label: Label of the new added string
        """
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


    def add_string_list(self, lst: List[str], label: int=0) -> None:
        """!
        Add a list of strings to frequency prefix tree

        @param lst: List of strings to be added to the FPT
        @param label: Label of the new added string
        """
        for item in lst:
            self.add_string(item, label)
