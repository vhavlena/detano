#!/usr/bin/env python3

"""!
\brief Class for general frequency automata.

\details Class providing operations for general (nondeterministic) frequency automata.

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

import copy
from dataclasses import dataclass
from collections import defaultdict
import wfa.core_wfa as core_wfa
import wfa.core_wfa_export as core_wfa_export

@dataclass(eq=True, unsafe_hash=True)
class FFATrans:
    """!
    Class representing a transtion of the FFA
    """
    ## Source state
    src: str
    ## Destination state
    dest: str
    ## Weight
    weight: int
    ## Symbol
    symbol: int
    ## Label
    label: int


class FFA:
    """!
    General frequency automata (FFA)
    """

    def __init__(self, states, trans, ini, fin):
        """!
        Constructor

        @param states: States of the DFFA
        @param trans: Transitions of the DFFA
        @param ini: Initial states
        @param fin: Final states
        """
        self._states = states
        self._trans = trans
        self._ini = ini
        self._fin = fin
        self._states_dict = None


    def _find_eq_trans(self, val, trans):
        """!
        Find transition with equal structure (except weight and label)

        @param val: Given transition
        @param trans: Collection of all transitions

        @return Transition corresponding to val
        """
        for tr in trans:
            if tr.src == val.src and tr.dest == val.dest and tr.symbol == val.symbol:
                return tr
        return None


    def _create_tr_func(self, tr_list):
        """!
        Create transition function from a list of transitions

        @param tr_list: List of transitions

        @return Transitions represented by a dictionary (transition function)
        """
        tr_func = defaultdict(lambda: dict())
        for tr in tr_list:
            try:
                tmp = tr_func[tr.src][tr.symbol]
                tr_m = self._find_eq_trans(tr, tmp)
                if tr_m is None:
                    tr_func[tr.src][tr.symbol].add(tr)
                    continue
                tr_m.weight += tr.weight
                tr_m.label = min(tr_m.label, tr.label)
            except KeyError:
                tr_func[tr.src][tr.symbol] = set([tr])
        return tr_func



    def _merge_in_dict(self, states, id, dct):
        """!
        Merge states in initial/final state vector

        @param states: Collection of states
        @param id: Identifier
        @param dct: Dictionary

        @return Dictionary with merged values
        """
        new_dict = defaultdict(lambda: 0)
        tw = 0
        for st, weight in dct.items():
            if st in states:
                tw += weight
            else:
                new_dict[st] = weight
        if tw > 0:
            new_dict[id] = tw
        return new_dict


    def get_transition_list(self):
        """!
        Get list of transitions from the transition function

        @return List of transitions
        """
        lst = []
        for src, tr_dest in self._trans.items():
            for sym, dst in tr_dest.items():
                if isinstance(dst, set):
                    lst = lst + list(copy.deepcopy(dst))
                else:
                    lst.append(dst)
        return lst


    def inverse_ffa(self):
        """!
        Get the inverse FFA

        @return FFA with the inverse transition function
        """
        lst = copy.deepcopy(self.get_transition_list())
        for tr in lst:
            tr.src, tr.dest = tr.dest, tr.src

        trs = self._create_tr_func(lst)
        return FFA(self.get_states(), trs, self._fin, self._ini)


    def _get_inits(self):
        """!
        Get initial states

        @return Initial states of the FFA
        """
        return list(self._ini.items())


    def get_states(self):
        """!
        Get all states

        @return All states of the FFA
        """
        return self._states


    def get_finals(self):
        """!
        Get final states

        @return Final states of the FFA
        """
        return self._fin


    def get_transitions(self):
        """!
        Get transitions

        @return Transitions of the FFA
        """
        return self._trans


    def successors(self, state, sym=None):
        """!
        Get all successors from state over sym

        @param state: State
        @param sym: Symbol

        @return Set of all successors
        """
        succ = set()
        for s, tr_dest in self._trans[state].items():
            if sym is not None and s != sym:
                continue
            if isinstance(tr_dest, set):
                succ = succ | set(map(lambda x: x.dest, tr_dest))
            else:
                succ.add(tr_dest.dest)
        return succ


    def successors_set(self, states, sym=None):
        """!
        Get all successors from the set states over sym

        @param states: State
        @param sym: Symbol

        @return Set of all successors
        """
        succ = set()
        for st in states:
            succ = succ | self.successors(st, sym)
        return succ


    def reachable_states(self, st_set):
        """!
        Get all reachable states from st_set

        @param st_set: Set of states

        @return Set of reachable states
        """
        new_set = self.successors_set(st_set)
        if new_set <= st_set:
            return st_set
        return self.reachable_states(new_set | st_set)


    def merge_states(self, states):
        """!
        Merge a set of states (remove those states and replace with one in the set)

        @param states: States to be merged
        """
        id = next(iter(states))
        self._states = self._states - states
        deterministic = False
        tr_lst = self.get_transition_list()

        if len(tr_lst) == 0:
            return
        deterministic = isinstance(self._trans[tr_lst[0].src][tr_lst[0].symbol], set)
        for tr in tr_lst:
            if tr.src in states:
                tr.src = id
            if tr.dest in states:
                tr.dest = id

        self._trans = self._create_tr_func(tr_lst)
        self._states.add(id)
        self._ini = self._merge_in_dict(states, id, self._ini)
        self._fin = self._merge_in_dict(states, id, self._fin)
        self._states_dict = None


    def merge_equivalent(self, classes):
        """!
        Merge equivalent states according to the equivalent classes

        @param classes: Partitioning of the states
        """
        for item in classes:
            self.merge_states(item)


    def path_length(self, st1, st2):
        """!
        Get length of a shortest path between st1 and st2

        @param st1: Source state
        @param st2: Destination state

        @return Length of a shortest path
        """
        new_set = set([st1])
        ln = 0
        all = set()
        while not new_set <= all:
            if st2 in new_set:
                return ln
            all = all | new_set
            new_set = self.successors_set(new_set)
            ln += 1
        return None


    def trim(self):
        """
        Remove unreachable states from the automaton.
        """
        reach = self.reachable_states(set(self._ini.keys()))
        new_tran = defaultdict(lambda: dict())
        st_rem = self._states - reach

        for st in reach:
            try:
                new_tran[st] = self._trans[st]
            except KeyError:
                continue

        for st in st_rem:
            del self._fin[st]
        self._states = reach
        self._trans = new_tran


    def rename_states(self):
        """
        Rename states to consecutive numbers (from 0)
        """
        self._states_dict = dict()
        new_transitions = []
        new_states = set()
        new_finals = defaultdict(lambda: 0)
        new_starts = defaultdict(lambda: 0)
        count = 0

        for st in self.get_states():
            self._states_dict[st] = count
            new_states.add(count)
            count += 1

        for state, prob in self._fin.items():
            dest = self._states_dict[state]
            new_finals[dest] = prob

        for state, prob in self._ini.items():
            dest = self._states_dict[state]
            new_starts[dest] = prob

        new_tran = defaultdict(lambda: dict())
        for src, tr_dest in self._trans.items():
            for sym, dst in tr_dest.items():
                n_dst = None
                if isinstance(dst, set):
                    n_dst = set()
                    for tr in dst:
                        n_dst.add(FFATrans(self._states_dict[tr.src], \
                            self._states_dict[tr.dest], tr.weight, tr.symbol, tr.label))
                else:
                    n_dst = FFATrans(self._states_dict[dst.src], \
                        self._states_dict[dst.dest], dst.weight, dst.symbol, dst.label)
                new_tran[self._states_dict[src]][sym] = n_dst

        self._trans = new_tran
        self._fin = new_finals
        self._ini = new_starts
        self._states = new_states


    def to_graphiwiz(self, legend=None):
        """!
        Convert the WFA to graphwiz format (for graphical visualization).

        @param legend: Legend to be print in the figure
        @return Graphwiz format of the automaton
        """
        dot = str()
        dot += "digraph \" Automat \" {\n    rankdir=LR;\n"
        if legend is not None:
            dot += "{{ rank = LR\n Legend [shape=none, margin=0, label=\"{0}\"] }}\n".format(legend)
        dot += "node [shape = doublecircle];\n"
        if len(self._fin) > 0:
            for state, weight in self._fin.items():
                dot += "\"" + str(state) + "\"" + " [label=\"" \
                    + str(state) + ", " \
                    + str(weight) + "\"]"
                dot += ";\n"

        dot += "node [shape = circle];\n"
        for state in self._states:
            if state not in self._fin:
                dot += "\"" + str(state) + "\"" + " [label=\"" \
                    + str(state) + "\"]"
                dot += ";\n"

        for state, weight in self._ini.items():
            dot += "\"init{0}\" [label=\"{1}\",shape=plaintext];".format(state, weight)
            dot += "\"init{0}\" -> \"{1}\";\n".format(state, state)

        for _, tr_dest in self._trans.items():
            for sym, dst in tr_dest.items():
                if isinstance(dst, set):
                    for tr in dst:
                        dot += self._print_transition(tr.src, tr.dest, tr.symbol, tr.weight)
                else:
                    dot += self._print_transition(dst.src, dst.dest, dst.symbol, dst.weight)

        dot += "}"
        return dot


    def _print_transition(self, src, dest, sym, weight):
        """!
        Convert a transition to graphwiz format

        @param src: Source state
        @param dest: Destination state
        @oaram sym: Symbol
        @param weight: Weight

        @return Graphwiz format
        """
        dot = str()
        dot += "\"" + str(src) + "\""
        dot += " -> "
        dot += "\"" + str(dest) + "\""
        dot += " [ label = \"" + str(sym) + " : " + str(weight)
        dot += "\" ];\n"
        return dot


    def to_wfa(self):
        """!
        Converts FFA to WFA (weighted finite automaton)

        @return FFA represented as WFA
        """
        trs = []
        for _, tr_dest in self._trans.items():
            for sym, dst in tr_dest.items():
                if isinstance(dst, set):
                    for tr in dst:
                        trs.append(core_wfa.Transition(tr.src, tr.dest, \
                            tr.symbol, tr.weight))
                else:
                    trs.append(core_wfa.Transition(dst.src, dst.dest, \
                        dst.symbol, dst.weight))
        return core_wfa_export.CoreWFAExport(trs, self._fin, self._ini)
