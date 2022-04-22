#!/usr/bin/env python3

"""!
\brief Distribution-based anomaly detection.

\details
    This file contains support for anomaly detection based on comparing
    distributions, which works as follows. In the first step, we learn a PA from
    an input traffic window. Consequently, we compare the difference between a
    model PA and the PA representing input window.

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
}
"""

import math
import detection.anom_detect_base as anom
import wfa.core_wfa_export as core_wfa_export
import wfa.matrix_wfa as matrix_wfa
import algorithms.distance as dist
import wfa.core_wfa as core_wfa

from typing import Callable, List, no_type_check

## Use sparse matrices to comput the Euclid distance
SPARSE = False

class AnomDistrComparison(anom.AnomDetectBase):
    """!
    Anomaly detection based on comparing distributions
    """


    def __init__(self, aut_map: dict[anom.ComPairType, List[core_wfa.CoreWFA]], learning_procedure: Callable):
        """!
        Constructor

        @param aut_map: Mapping of communication pairs to automata representing normal behavior
        @param learning_procedure: procedure used to obtain a PA from a list of messages
        """
        ## Mapping of communication pairs to automata representing normal behavior
        self.golden_map = aut_map
        ## Procedure used to obtain a PA from a list of messages
        self.learning_proc = learning_procedure
        self.test_fa = None



    def dpa_selection(self, window: List, compair: anom.ComPairType) -> List[core_wfa.CoreWFA]:
        """!
        Select appropriate DPA according to a communication window and a
        communication pair.

        @param window: List of messages corresponding to a single window
        @param compair: Pair of communicating devices

        @return Selected DPA
        """
        return self.golden_map[compair]


    def detect(self, window: List, compair: anom.ComPairType, accelerate: float = 0.0) -> List[float]:
        """!
        Detect if anomaly occurrs in the given window.

        @param window: List of messages corresponding to a single window to be checked
        @param compair: Pair of communicating devices
        @param accelerate: Use acceleration with the given value (if a detection
            value is below accelerate, the detection analysis terminates without
            computing all detection values). 

        @return List of floats representing distance between golden automata and a window
        """
        auts = self.dpa_selection(window, compair)
        ret = []
        self.test_fa = self.learning_proc(window)

        for aut in auts:
            val = self.apply_detection(aut, window, compair)
            ret.append(val)

            if val <= accelerate:
                return ret

        return ret


    def remove_identical(self) -> None:
        """!
        Remove identical automata from the golden map
        """
        for k, v in self.golden_map.items():
            self.golden_map[k] = list(set(v))


    def remove_euclid_similar(self, max_error: float) -> None:
        """!
        Remove Euclid similar automata from the golden map (with the error bounded
        by max_error).

        @param max_error: Maximum error bound
        """
        self.remove_identical()
        for k, v in self.golden_map.items():
            self.golden_map[k] = list(self._remove_euclid_similar_it(max_error, v))


    def _remove_euclid_similar_it(self, max_error: float, lst: List[core_wfa.CoreWFA]) -> List[core_wfa.CoreWFA]:
        """!
        Remove Euclid similar automata from the given list of automata (with the error bounded
        by max_error).

        @param max_error: Maximum error bound
        @param lst: List of automata to be pruned

        @return List with removed similar automata
        """
        aut_dist = dict()

        for i in range(len(lst)):
            for j in range(i+1, len(lst)):
                a = lst[i]
                b = lst[j]
                aut_dist[(a, b)] = AnomDistrComparison.euclid_distance(a,b)
                aut_dist[(b, a)] = aut_dist[(a, b)]

        d = dist.Distance(aut_dist, lst)
        return d.compute_subset_error(max_error)


    @staticmethod
    @no_type_check
    def euclid_distance(aut1: core_wfa.CoreWFA, aut2: core_wfa.CoreWFA) -> float:
        """!
        Compute Euclid distance between two automata

        @param aut1: First PA
        @param aut2: Second PA

        @return Euclid distance of aut1 and aut2
        """
        if ((len(aut1.get_transitions()) > 0 and len(aut2.get_transitions()) == 0)) or \
            ((len(aut1.get_transitions()) == 0 and len(aut2.get_transitions()) > 0)):
            return 1.0

        pr1 = aut1.product(aut1).get_trim_automaton()
        pr2 = aut1.product(aut2).get_trim_automaton()
        pr3 = aut2.product(aut2).get_trim_automaton()

        pr1.rename_states()
        pr2.rename_states()
        pr3.rename_states()

        pr1.__class__ = matrix_wfa.MatrixWFA
        pr2.__class__ = matrix_wfa.MatrixWFA
        pr3.__class__ = matrix_wfa.MatrixWFA

        try:
            res1 = pr1.compute_language_probability(matrix_wfa.ClosureMode.inverse, SPARSE)
            res2 = pr2.compute_language_probability(matrix_wfa.ClosureMode.inverse, SPARSE)
            res3 = pr3.compute_language_probability(matrix_wfa.ClosureMode.inverse, SPARSE)
        except ValueError:
            res1 = pr1.compute_language_probability(matrix_wfa.ClosureMode.iterations, SPARSE, 20)
            res2 = pr2.compute_language_probability(matrix_wfa.ClosureMode.iterations, SPARSE, 20)
            res3 = pr3.compute_language_probability(matrix_wfa.ClosureMode.iterations, SPARSE, 20)

        return min(1.0, math.sqrt(max(0.0, res1 - 2*res2 + res3)))


    def apply_detection(self, aut: core_wfa.CoreWFA, window: List, compair: anom.ComPairType) -> float:
        """!
        Apply distribution-comparison-based anomaly detection.

        @param aut: Golden automaton
        @param window: List of messages to be inspected
        @param compair: Pair of communicating devices

        @return Number representing similarity of aut and window
        """

        if aut is None and len(window) == 0:
            return 0.0
        if aut is None and len(window) > 0:
            return 1.0
        if len(window) == 0 and len(aut.get_transitions()) > 1:
            return 1.0

        d = None
        try:
            d = AnomDistrComparison.euclid_distance(aut, self.test_fa)
        except ValueError:
            SPARSE = True
            d = AnomDistrComparison.euclid_distance(self.test_fa, aut)
            SPARSE = False
        return d

""" @} """
