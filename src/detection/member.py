#!/usr/bin/env python3

"""
Member-based anomaly detection.

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


class AnomMember(anom.AnomDetectBase):

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
        aut = self.dpa_selection(window, compair)
        return self.apply_detection(aut, window, compair)


    """
    Apply member-based anomaly detection. Returns list of conversations that
    are not accepted by aut.
    """
    def apply_detection(self, aut, window, compair):

        if aut is None:
            return window

        ret = []
        for conv in window:
            prob = aut.string_prob_deterministic(conv)
            if prob is None:
                ret.append(conv)

        return ret
