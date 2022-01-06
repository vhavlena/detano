#!/usr/bin/env python3

"""!
\brief Class for exporting WFAs in a textual format

\details
    Class providing exporting a WFA into FA or DOT format. Taken and modified
    from <https://github.com/vhavlena/appreal>

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

import wfa.aux_functions as aux
import FAdo.fa
import wfa.wfa_exceptions as wfa_exceptions
import wfa.core_wfa as core_wfa

from typing import List, Optional, Set, TypeVar, Generic, Callable, Tuple, Union

PrintSymbolType = Union[core_wfa.SymbolType, List[core_wfa.SymbolType]]

# StateFloatMapType = dict[StateType, float]
# StateFloatMapOptType = Optional[dict[StateType, float]]
# TransFunctionType = dict[StateType, dict[SymbolType, Set[StateType]]]

## Precise of float numbers (for output)
PRECISE = 3
## Max number of symbols on transition (DOT format)
SYMBOLS = 25

class CoreWFAExport(core_wfa.CoreWFA[core_wfa.StateType, core_wfa.SymbolType]):
    """!
    Class for exporting WFAs to a text format
    """

    def __init__(self, transitions: List[core_wfa.Transition]=None, finals: core_wfa.StateFloatMapOptType=None, start: core_wfa.StateFloatMapType = dict(), alphabet: Optional[List[core_wfa.SymbolType]]=None):
        """!
        Constructor

        @param transitions: Transitions
        @param finals: Final states with weights
        @param start: Initial state
        @param alphabet: Alphabet
        """
        super(CoreWFAExport, self).__init__(transitions, finals, start, alphabet)


    def get_aggregated_transitions(self) -> dict[Tuple[core_wfa.StateType, core_wfa.StateType], Tuple[List[core_wfa.SymbolType], float]]:
        """!
        Get aggregated transitions (merging transitions which differs
        only on symbol into a transition labeled with the list of symbols).

        @return List of aggregated ransitions.
        """
        aggregate: dict[Tuple[core_wfa.StateType, core_wfa.StateType], Tuple[List[core_wfa.SymbolType], float] ] = dict()
        for transition in self._transitions:
            if (transition.src, transition.dest) not in aggregate:
                aggregate[(transition.src, transition.dest)] \
                    = [transition.symbol], transition.weight
            else:
                v1, v2 = aggregate[(transition.src, transition.dest)]
                v1.append(transition.symbol)
                v2 += float(transition.weight)
                aggregate[(transition.src, transition.dest)] = v1, v2
        return aggregate


    def to_dot(self, aggregate: bool=True, state_label: Optional[dict[core_wfa.StateType, str]]=None, legend: str=None) -> str:
        """!
        Convert the WFA to dot format (for graphical visualization). Use
        aggregation of transitions between same states.

        @param aggregate: Aggregate transitions between two states
        @param state_label: label of each state (shown inside of the state)
        @param legend: Optional legend to be part of the DOT automaton

        @return String (DOT, Graphwiz format)
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
                if state_label is None:
                    dot += "\"" + str(state) + "\"" + " [label=\"" \
                        + str(state) + ", " \
                        + str(round(weight, PRECISE)) + "\"]"
                else:
                    dot += "\"" + str(state) + "\"" + " [label=\"" \
                        + str(state) + ": " \
                        + "{0}, {1}".format(round(weight, PRECISE),state_label[state]) + "\"]"
                dot += ";\n"

        dot += "node [shape = circle];\n"
        if state_label is not None:
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
            src: core_wfa.StateType
            dest: core_wfa.StateType
            res: Tuple[List[core_wfa.SymbolType], float]
            for (src, dest), res in self.get_aggregated_transitions().items():
                dot += self._print_transition(src, dest, res[0], res[1])
        else:
            for tr in self.get_transitions():
                dot += self._print_transition(tr.src, tr.dest, tr.symbol, tr.weight)

        dot += "}"
        return dot


    def _print_transition(self, src: core_wfa.StateType, dest: core_wfa.StateType, sym: PrintSymbolType, weight: float) -> str:
        """!
        Print a single transition.

        @param src: Source state
        @param dest: Destination state
        @param sym: Symbol
        @param weight: Weight of the transition

        @return Transition in DOT format
        """
        dot = str()
        dot += "\"" + str(src) + "\""
        dot += " -> "
        dot += "\"" + str(dest) + "\""
        dot += " [ label = \"" + self._format_label(sym, weight)
        dot += "\" ];\n"
        return dot


    def to_fa_format(self, initial: bool=False, alphabet: bool=False) -> str:
        """!
        Converts automaton to FA format (WFA version).

        @param initial: Explicitly print the initial state
        @param alphabet: Whether show explicitly symbols from alphabet.

        @return String (WFA in the FA format)
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


    def _format_label(self, sym: PrintSymbolType, weight: float) -> str:
        """!
        Format label for DOT converting.

        @param sym: List of symbols
        @param weight: Weight of the transition.

        @return String (formatted label in the DOT format)
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
