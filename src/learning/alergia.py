#!/usr/bin/env python3

"""!
\brief Alergia algorithm

\details
    Alergia algorithm for learning deterministic probabilistic automata for
    the context of network communication.

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

import sys
import math
import learning.fpt as fpt
import learning.dffa as dffa
import learning.ffa as ffa

from typing import Set, Optional

def choose_blue_state(freq_aut: dffa.DFFA, blue_set: Set[ffa.StateType], t0: int) -> Optional[ffa.StateType]:
    """!
    Chose a blue state from a set of blue states.

    @param freq_aut: Frequency automaton
    @param blue_set: Set of blue states
    @param t0: The minimum number of strings for merging a state

    @return Chosen blue state
    """
    for bl in sorted(blue_set):
        if freq_aut.state_freq(bl) >= t0:
            return bl
    return None


def choose_red_state(freq_aut: dffa.DFFA, red_set: Set[ffa.StateType], blue: ffa.StateType, alpha: float) -> Optional[ffa.StateType]:
    """!
    Chose a red state from a set of red states.

    @param freq_aut: Frequency automaton
    @param red_set: Set of red states
    @param blue: Blue state
    @param alpha: Merging parameter

    @return Chosen red state
    """
    for red in sorted(red_set):
        if freq_aut.alergia_compatible(red, blue, alpha):
            return red
    return None


def alergia(freq_aut: dffa.DFFA, alpha: float, t0: int) -> dffa.DFFA:
    """!
    PA learning using the Alergia algorithm.

    @param freq_aut: A frequency automaton constructed from the input sample
    @param alpha: Merging parameter
    @param t0: The minimum number of strings for merging a state

    @return Compact frequency automaton (no normalization applied)
    """
    freq_aut.get_states()
    red_set = set([freq_aut.get_root()])
    blue_set = freq_aut.successors(freq_aut.get_root())

    blue = choose_blue_state(freq_aut, blue_set, t0)
    while blue is not None:
        red = choose_red_state(freq_aut, red_set, blue, alpha)

        if red is not None:
            freq_aut.stochastic_merge(red, blue)
            freq_aut.trim()
        else:
            red_set.add(blue)

        blue_set = freq_aut.successors_set(red_set) - red_set
        blue = choose_blue_state(freq_aut, blue_set, t0)


    return freq_aut
