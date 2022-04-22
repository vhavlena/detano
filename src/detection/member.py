#!/usr/bin/env python3

"""!
\brief
    Member-based anomaly detection.

\details
    Anomaly detection based on a single message reasoning. Given PAs
    representing a valid network traffic, we check if input messages in a window
    are in the language of a model.

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
import detection.anom_detect_base as anom
import wfa.core_wfa_export as core_wfa_export
import wfa.matrix_wfa as matrix_wfa
import wfa.core_wfa as core_wfa

from typing import Callable, List, no_type_check

class AnomMember(anom.AnomDetectBase):
    """!
    Anomaly detection based on a single message reasoning
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


    def dpa_selection(self, window: List, compair: anom.ComPairType) -> List[core_wfa.CoreWFA]:
        """!
        Select appropriate DPA according to a communication window and a
        communication pair.

        @param window: List of messages to be inspected
        @param compair: Pair of communicating devices

        @return Selected DPA
        """
        return self.golden_map[compair]


    def detect(self, window: List, compair: anom.ComPairType, accelerate: float = 0.0) -> List[float]:
        """!
        Detect if anomaly occurrs in the given window.

        @param window: List of messages to be inspected
        @param compair: Pair of communicating devices
        @param accelerate: Use acceleration with the given value (if a detection
            value is below accelerate, the detection analysis terminates without
            computing all detection values). 

        @return List of detection result for each model
        """
        auts = self.dpa_selection(window, compair)
        return [self.apply_detection(aut, window, compair) for aut in auts]


    def apply_detection(self, aut: core_wfa.CoreWFA, window: List, compair: anom.ComPairType):
        """!
        Apply member-based anomaly detection. Returns list of conversations that
        are not accepted by aut.

        @param aut: Golden automaton
        @param window: List of messages to be inspected
        @param compair: Pair of communicating devices

        @return List of not accepted messages
        """

        if aut is None:
            return window

        ret = []
        for conv in window:
            prob = aut.string_prob_deterministic(conv)
            if prob is None:
                ret.append(conv)

        return ret
