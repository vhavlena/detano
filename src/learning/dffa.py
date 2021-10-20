#!/usr/bin/env python3

"""!
\brief Class for deterministic frequency automata.

\details Class providing operations for deterministic frequency automata.

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

import math
from collections import defaultdict
import learning.ffa as ffa

class DFFA(ffa.FFA):
    """!
    Deterministic frequency automaton class
    """

    def __init__(self, states, trans, ini, fin):
        """!
        Constructor

        @param states: States of the DFFA
        @param trans: Transitions of the DFFA
        @param ini: Initial states
        @param fin: Final states
        """
        super(DFFA, self).__init__(states, trans, ini, fin)
        inits = self._get_inits()
        if len(inits) != 1:
            raise Exception("Not deterministic")
        self._root = inits[0][0]


    def __init__(self, states, trans, ini, fin, root):
        """!
        Constructor

        @param states: States of the DFFA
        @param trans: Transitions of the DFFA
        @param ini: Initial states
        @param fin: Final states
        @param root: The root state
        """
        super(DFFA, self).__init__(states, trans, ini, fin)
        self._root = root


    def get_root(self):
        """!
        Get the root (initial) state

        @return Root (initial) state
        """
        return self._root


    def _find_pred(self, state):
        """!
        Get the predecessor of a given state

        @return Transition leading to the state state
        """
        for src, sym_dct in self._trans.items():
            for sym, tr in sym_dct.items():
                if tr.dest == state:
                    return tr
        return None


    def stochastic_merge(self, red, blue):
        """!
        Merging two states red and blue (followed by folding frequencies from the
        merged subtree).

        @param red: Red state
        @param blue: Blue state
        """
        tr_pred = self._find_pred(blue)
        if tr_pred is None:
            raise Exception("State {0} has no predecessors".format(blue))

        self._trans[tr_pred.src][tr_pred.symbol] = ffa.FFATrans(tr_pred.src, \
            red, tr_pred.weight, tr_pred.symbol, tr_pred.label)
        self.stochastic_fold(red, blue)



    def stochastic_fold(self, red, blue):
        """!
        Fold frequencies from subtree given by blue root into the automaton
        rooted at the red state.

        @param red: Red state
        @param blue: Blue state
        """
        self._fin[red] += self._fin[blue]
        for sym, tr in self._trans[blue].items():
            tr_dest = None
            try:
                tr_dest = self._trans[red][sym]
                tr_dest.weight += tr.weight
            except KeyError:
                self._trans[red][sym] = ffa.FFATrans(red, tr.dest, tr.weight, tr.symbol, tr.label)
                continue
            self.stochastic_fold(tr_dest.dest, tr.dest)


    @staticmethod
    def alergia_test(f1, n1, f2, n2, alpha):
        """!
        Alergia test for checking whether to merge two states

        @param f1: Frequency of the first state
        @param n1: Number of incomming strings of the first state
        @param f2: Frequency of the second state
        @param n2: Number of incomming strings of the second state
        @param alpha: Merging parameter

        @return Compatibility of two states/transitions (represented by freqencies)
        """
        gamma = abs(float(f1)/n1 - float(f2)/n2)
        return gamma < (math.sqrt(1.0/n1) + math.sqrt(1.0/n2)) * math.sqrt(0.5 * math.log10(2.0/alpha))


    def state_freq(self, state):
        """!
        Compute frequency of a state (number of strings accepted at the state
        or leaving the state).

        @param state: Given state

        @return Frequency of a state
        """
        sum = 0
        sum += self._fin[state]
        for _, tr_dst in self._trans[state].items():
            if isinstance(tr_dst, set):
                for tr in tr_dst:
                    sum += tr.weight
            else:
                sum += tr_dst.weight
        return sum


    def alergia_compatible(self, qa, qb, alpha):
        """!
        Determine whether two states are compatible for merging (wrt the parameter
        alpha).

        @param qa: The first state
        @param qb: The second state
        @param alpha: Merging parameter

        @return Are two states compatible for merging
        """
        cnt_qa = self.state_freq(qa)
        cnt_qb = self.state_freq(qb)
        if not DFFA.alergia_test(self._fin[qa], cnt_qa, self._fin[qb], cnt_qb, alpha):
            return False

        alph = set(self._trans[qa].keys()) | set(self._trans[qb].keys())
        for sym in alph:
            tr1 = self._trans[qa].get(sym, None)
            tr2 = self._trans[qb].get(sym, None)
            w1 = 0 if tr1 is None else tr1.weight
            w2 = 0 if tr2 is None else tr2.weight

            if not DFFA.alergia_test(w1, cnt_qa, w2, cnt_qb, alpha):
                return False
        return True


    def normalize(self):
        """!
        Normalize frequency automaton to obtain a probabilistic automaton
        (probabilities are in the range [0,1] with the sum-consistency condition).

        @return Normalized automaton
        """
        aut = self.to_wfa()
        for tr in aut.get_transitions():
            w = self.state_freq(tr.src)
            tr.weight = float(tr.weight) / w
        fin_new = defaultdict(lambda: 0)
        for f in aut.get_finals().keys():
            w = self.state_freq(f)
            if aut.get_finals()[f] != 0:
                fin_new[f] = aut.get_finals()[f] / float(w)

        aut.set_finals(fin_new)
        iniState = list(aut.get_starts())[0]
        aut.get_starts()[iniState] = 1.0
        return aut
