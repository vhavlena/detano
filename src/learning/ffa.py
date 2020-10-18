#!/usr/bin/env python3

"""
Class for general frequency automata.

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

from dataclasses import dataclass
from collections import defaultdict
import wfa.core_wfa as core_wfa
import wfa.core_wfa_export as core_wfa_export

@dataclass
class FFATrans:
    src: str
    dest: str
    weight: int
    symbol: int


class FFA:

    def __init__(self, states, trans, ini, fin):
        self._states = states
        self._trans = trans
        self._ini = ini
        self._fin = fin
        self._states_dict = None

    def _get_inits(self):
        return list(self._ini.items())


    def get_states(self):
        return self._states


    def get_transitions(self):
        return self._trans


    def successors(self, state):
        succ = set()
        for _, tr_dest in self._trans[state].items():
            if isinstance(tr_dest, set):
                succ = succ | set(map(lambda x: x.dest, tr_dest))
            else:
                succ.add(tr_dest.dest)
        return succ


    def successors_set(self, states):
        succ = set()
        for st in states:
            succ = succ | self.successors(st)
        return succ


    def reachable_states(self, st_set):
        new_set = self.successors_set(st_set)
        if new_set <= st_set:
            return st_set
        return self.reachable_states(new_set | st_set)


    """
    Remove unreachable states from the automaton.
    """
    def trim(self):
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


    """
    Rename states to consecutive numbers (from 0)
    """
    def rename_states(self):
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
                    for tr in tr_dest:
                        n_dst.add(FFATrans(self._states_dict[tr.src], \
                            self._states_dict[tr.dest], tr.weight, tr.symbol))
                else:
                    n_dst = FFATrans(self._states_dict[dst.src], \
                        self._states_dict[dst.dest], dst.weight, dst.symbol)
                new_tran[self._states_dict[src]][sym] = n_dst

        self._trans = new_tran
        self._fin = new_finals
        self._ini = new_starts
        self._states = new_states


    """
    Export the automaton to graphwiz format.
    """
    def to_graphiwiz(self, legend=None):
        """Convert the WFA to graphwiz format (for graphical visualization).

        Return: String (Graphwiz format)
        Keyword arguments:
        state_label -- label of each state (shown inside of the state)
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
                    for tr in tr_dest:
                        dot += self._print_transition(tr.src, tr.dest, tr.symbol, tr.weight)
                else:
                    dot += self._print_transition(dst.src, dst.dest, dst.symbol, dst.weight)

        dot += "}"
        return dot


    def _print_transition(self, src, dest, sym, weight):
        dot = str()
        dot += "\"" + str(src) + "\""
        dot += " -> "
        dot += "\"" + str(dest) + "\""
        dot += " [ label = \"" + str(sym) + " : " + str(weight)
        dot += "\" ];\n"
        return dot


    """
    Converts FFA to WFA (weighted finite automaton)
    """
    def to_wfa(self):
        trs = []
        for _, tr_dest in self._trans.items():
            for sym, dst in tr_dest.items():
                if isinstance(dst, set):
                    for tr in tr_dest:
                        trs.append(core_wfa.Transition(tr.src, tr.dest, \
                            tr.symbol, tr.weight))
                else:
                    trs.append(core_wfa.Transition(dst.src, dst.dest, \
                        dst.symbol, dst.weight))
        return core_wfa_export.CoreWFAExport(trs, self._fin, self._ini)
