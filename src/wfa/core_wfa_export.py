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

import wfa.aux_functions as aux
import FAdo.fa
import wfa.wfa_exceptions as wfa_exceptions
import wfa.core_wfa as core_wfa

#Precise of float numbers (for output)
PRECISE = 3
#Max number of symbols on transition (DOT format)
SYMBOLS = 25

class CoreWFAExport(core_wfa.CoreWFA):
    def __init__(self, transitions=None, finals=None, start=None, alphabet=None):
        super(CoreWFAExport, self).__init__(transitions, finals, start, alphabet)

    def get_aggregated_transitions(self):
        """Get aggregated transitions (merging transitions which differs
        only on symbol into a transition labeled with the list of symbols).

        Return: List(Transitions).
        """
        aggregate = dict()
        for transition in self._transitions:
            if (transition.src, transition.dest) not in aggregate:
                aggregate[(transition.src, transition.dest)] \
                    = [[transition.symbol], transition.weight]
            else:
                aggregate[(transition.src, transition.dest)][0]\
                    .append(transition.symbol)
                aggregate[(transition.src, transition.dest)][1] \
                    += float(transition.weight)
        return aggregate

    def to_dot(self, aggregate=True, state_label=None, legend=None):
        """Convert the WFA to dot format (for graphical visualization). Use
        aggregation of transitions between same states.

        Return: String (DOT format)
        Keyword arguments:
        state_label -- label of each state (shown inside of the state)
        """
        dot = str()
        dot += "digraph \" Automat \" {\n    rankdir=LR;\n"
        if legend is not None:
            dot += "{{ rank = LR\n Legend [shape=none, margin=0, label=\"{0}\"] }}\n".format(legend)
        dot += "node [shape = doublecircle];\n"
        if len(self._finals) > 0:
            for state, weight in self._finals.items():
                if weight == 0.0:
                    continue
                if state_label == None:
                    dot += "\"" + str(state) + "\"" + " [label=\"" \
                        + str(state) + ", " \
                        + str(round(weight, PRECISE)) + "\"]"
                else:
                    dot += "\"" + str(state) + "\"" + " [label=\"" \
                        + str(state) + ": " \
                        + "{0}, {1}".format(round(weight, PRECISE),state_label[state]) + "\"]"
                dot += ";\n"

        dot += "node [shape = circle];\n"
        if state_label != None:
            for state in self.get_states():
                if state not in self._finals:
                    dot += "\"" + str(state) + "\"" + " [label=\"" \
                        + str(state) + ", " \
                        + "{0}".format(state_label[state]) + "\"]"
                    dot += ";\n"
        else:
            for state in self.get_states():
                if state not in self._finals:
                    dot += "\"" + str(state) + "\"" + " [label=\"" \
                        + str(state) + "\"]"
                    dot += ";\n"


        for state, weight in self.get_starts().items():
            dot += "\"init{0}\" [label=\"{1}\",shape=plaintext];".format(state, weight)
            dot += "\"init{0}\" -> \"{1}\";\n".format(state, state)

        #dot += "node [shape = circle];\n"
        if aggregate:
            for (src, dest), res in self.get_aggregated_transitions().items():
                dot += self._print_transition(src, dest, res[0], res[1])
        else:
            for tr in self.get_transitions():
                dot += self._print_transition(tr.src, tr.dest, tr.symbol, tr.weight)

        dot += "}"
        return dot


    def _print_transition(self, src, dest, sym, weight):
        dot = str()
        dot += "\"" + str(src) + "\""
        dot += " -> "
        dot += "\"" + str(dest) + "\""
        dot += " [ label = \"" + self._format_label(sym, weight)
        dot += "\" ];\n"
        return dot


    def to_fa_format(self, initial=False, alphabet=False):
        """Converts automaton to FA format (WFA version).

        Return: String (WFA in the FA format)
        Keyword arguments:
        alphabet -- whether show explicitly symbols from alphabet.
        """
        if len(self._start) != 1:
            raise wfa_exceptions.WFAOperationException("Only WFA with a single initial state can be converted to FA format.")
        fa = str()
        if initial:
            fa += str(list(self._start.keys())[0]) + "\n"
        if alphabet:
            fa += ":"
            for sym in self.get_alphabet():
                fa += hex(sym) + " "
            fa += "\n"
        for transition in self._transitions:
            fa += "{0} {1} \"{2}\" {3}\n".format(transition.src, transition.dest,
                transition.symbol, transition.weight)
        for final, weight in self._finals.items():
            fa += "{0} {1}\n".format(final, weight)

        return fa


    def _format_label(self, sym, weight):
        """Format label for DOT converting.

        Return: String (formatted label)
        Keyword arguments:
        sym -- List of symbols
        weight -- Weight of the transition.
        """
        max_symbols = SYMBOLS

        if not isinstance(sym, list):
            return "{0} {1}".format(str(sym), round(weight, 2))
        sym_str = str()
        if set(sym) == set(self.get_alphabet()):
            return "^[] " + str(round(weight, PRECISE))
        for char in sorted(sym):
            if max_symbols > 0:
                if isinstance(char, int):
                    sym_str += aux.convert_to_pritable(chr(char), True)
                else:
                    sym_str += str(char)
                max_symbols = max_symbols - 1
            else:
                sym_str += "... {0}".format(len(sym))
                break
        return "[" + sym_str + "] " + str(round(weight, PRECISE))
