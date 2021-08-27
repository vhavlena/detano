#!/usr/bin/env python3

"""
Distribution-based anomaly detection.

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
import detection.anom_detect_base as anom
import wfa.core_wfa_export as core_wfa_export
import wfa.matrix_wfa as matrix_wfa
import algorithms.distance as dist

SPARSE = False

class AnomDistrComparison(anom.AnomDetectBase):

    def __init__(self, aut_map, learning_procedure):
        self.golden_map = aut_map
        self.learning_proc = learning_procedure


    """
    Select appropriate DPA according to a communication window and a
    communication pair.
    """
    def dpa_selection(self, window, compair):
        return self.golden_map[compair]


    """
    Detect if anomaly occurrs in the given window.
    """
    def detect(self, window, compair):
        auts = self.dpa_selection(window, compair)
        return [self.apply_detection(aut, window, compair) for aut in auts]


    """
    Remove identical automata from the golden map
    """
    def remove_identical(self):
        for k, v in self.golden_map.items():
            self.golden_map[k] = list(set(v))


    """
    Remove Euclid similar automata from the golden map (with the error bounded
    by max_error).
    """
    def remove_euclid_similar(self, max_error):
        self.remove_identical()
        for k, v in self.golden_map.items():
            self.golden_map[k] = self._remove_euclid_similar_it(max_error, v)


    """
    Remove Euclid similar automata from the given list of automata (with the error bounded
    by max_error).
    """
    def _remove_euclid_similar_it(self, max_error, lst):
        aut_dist = dict([ ((a,b), AnomDistrComparison.euclid_distance(a,b)) for a in lst for b in lst if a != b ])
        d = dist.Distance(aut_dist, lst)
        return d.compute_subset_error(max_error)


    """
    Compute Euclid distance between two automata
    """
    @staticmethod
    def euclid_distance(aut1, aut2):
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


    """
    Apply distribution-comparison-based anomaly detection.
    """
    def apply_detection(self, aut, window, compair):

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
