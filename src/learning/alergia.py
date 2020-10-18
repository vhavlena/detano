#!/usr/bin/env python3

"""
Alergia algorithm for learning deterministic probabilistic automata.

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

import sys
import math
import learning.fpt as fpt
import learning.dffa as dffa

def choose_blue_state(freq_aut, blue_set, t0):
    for bl in sorted(blue_set):
        if freq_aut.state_freq(bl) >= t0:
            return bl
    return None


def choose_red_state(freq_aut, red_set, blue, alpha):
    for red in sorted(red_set):
        if freq_aut.alergia_compatible(red, blue, alpha):
            return red
    return None


"""
PA learning using the Alergia algorithm.

Keyword arguments:
  freq_aut: a frequency automaton constructed from the input sample
  alpha: merging parameter
  t0: a minimum number of strings for merging a state 
"""
def alergia(freq_aut, alpha, t0):
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
