#!/usr/bin/env python3

"""
Class for deterministic frequency automata.

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

import math
from collections import defaultdict
import learning.ffa as ffa

class DFFA(ffa.FFA):

    def __init__(self, states, trans, ini, fin):
        super(DFFA, self).__init__(states, trans, ini, fin)
        inits = self._get_inits()
        if len(inits) != 1:
            raise Exception("Not deterministic")
        self._root = inits[0][0]


    def __init__(self, states, trans, ini, fin, root):
        super(DFFA, self).__init__(states, trans, ini, fin)
        self._root = root


    def get_root(self):
        return self._root


    def _find_pred(self, state):
        for src, sym_dct in self._trans.items():
            for sym, tr in sym_dct.items():
                if tr.dest == state:
                    return tr
        return None


    """
    Merging two states (followed by folding frequencies from the
    merged subtree).
    """
    def stochastic_merge(self, red, blue):
        tr_pred = self._find_pred(blue)
        if tr_pred is None:
            raise Exception("State {0} has no predecessors".format(blue))

        self._trans[tr_pred.src][tr_pred.symbol] = ffa.FFATrans(tr_pred.src, \
            red, tr_pred.weight, tr_pred.symbol)
        self.stochastic_fold(red, blue)


    """
    Fold frequencies from subtree given by blue root into the automaton
    rooted at the red state.
    """
    def stochastic_fold(self, red, blue):
        self._fin[red] += self._fin[blue]
        for sym, tr in self._trans[blue].items():
            tr_dest = None
            try:
                tr_dest = self._trans[red][sym]
                tr_dest.weight += tr.weight
            except KeyError:
                self._trans[red][sym] = ffa.FFATrans(red, tr.dest, tr.weight, tr.symbol)
                continue
            self.stochastic_fold(tr_dest.dest, tr.dest)


    @staticmethod
    def alergia_test(f1, n1, f2, n2, alpha):
        gamma = abs(float(f1)/n1 - float(f2)/n2)
        return gamma < (math.sqrt(1.0/n1) + math.sqrt(1.0/n2)) * math.sqrt(0.5 * math.log10(2.0/alpha))



    """
    Compute frequency of a state (number of strings accepted at the state
    or leaving the state).
    """
    def state_freq(self, state):
        sum = 0
        sum += self._fin[state]
        for _, tr in self._trans[state].items():
            sum += tr.weight
        return sum


    """
    Determine whether two states are compatible for merging (wrt the parameter
    alpha).
    """
    def alergia_compatible(self, qa, qb, alpha):
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


    """
    Normalize frequency automaton to obtain a probabilistic automaton
    (probabilities are in the range [0,1] with the sum-consistency condition).
    """
    def normalize(self):
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
