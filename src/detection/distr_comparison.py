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

## Use sparse matrices to comput the Euclid distance
SPARSE = False

class AnomDistrComparison(anom.AnomDetectBase):
    """!
    Anomaly detection based on comparing distributions
    """


    def __init__(self, aut_map, learning_procedure):
        """!
        Constructor

        @param aut_map: Mapping of communication pairs to automata representing normal behavior
        @param learning_procedure: procedure used to obtain a PA from a list of messages
        """
        ## Mapping of communication pairs to automata representing normal behavior
        self.golden_map = aut_map
        ## Procedure used to obtain a PA from a list of messages
        self.learning_proc = learning_procedure



    def dpa_selection(self, window, compair):
        """!
        Select appropriate DPA according to a communication window and a
        communication pair.

        @param window: List of messages corresponding to a single window
        @param compair: Pair of communicating devices

        @return Selected DPA
        """
        return self.golden_map[compair]


    def detect(self, window, compair):
        """!
        Detect if anomaly occurrs in the given window.

        @param window: List of messages corresponding to a single window to be checked
        @param compair: Pair of communicating devices

        @return List of floats representing distance between golden automata and a window
        """
        auts = self.dpa_selection(window, compair)
        return [self.apply_detection(aut, window, compair) for aut in auts]


    def remove_identical(self):
        """!
        Remove identical automata from the golden map
        """
        for k, v in self.golden_map.items():
            self.golden_map[k] = list(set(v))


    def remove_euclid_similar(self, max_error):
        """!
        Remove Euclid similar automata from the golden map (with the error bounded
        by max_error).

        @param max_error: Maximum error bound
        """
        self.remove_identical()
        for k, v in self.golden_map.items():
            self.golden_map[k] = self._remove_euclid_similar_it(max_error, v)


    def _remove_euclid_similar_it(self, max_error, lst):
        """!
        Remove Euclid similar automata from the given list of automata (with the error bounded
        by max_error).

        @param max_error: Maximum error bound
        @param lst: List of automata to be pruned

        @return List with removed similar automata
        """
        aut_dist = dict([ ((a,b), AnomDistrComparison.euclid_distance(a,b)) for a in lst for b in lst if a != b ])
        d = dist.Distance(aut_dist, lst)
        return d.compute_subset_error(max_error)


    @staticmethod
    def euclid_distance(aut1, aut2):
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


    def apply_detection(self, aut, window, compair):
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

        test_fa = self.learning_proc(window)
        d = None
        try:
            d = AnomDistrComparison.euclid_distance(aut, test_fa)
        except ValueError:
            SPARSE = True
            d = AnomDistrComparison.euclid_distance(test_fa, aut)
            SPARSE = False
        return d

""" @} """
