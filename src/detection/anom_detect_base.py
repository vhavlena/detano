#!/usr/bin/env python3

"""!
\brief Anomaly detection base class.

\details
    Base class giving an interface for methods used for concrete analyses.

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

from abc import ABC, abstractmethod
from typing import FrozenSet, Tuple, List

import wfa.core_wfa as core_wfa

ComPairType = FrozenSet[Tuple[str,str]]

class AnomDetectBase(ABC):
    """!
    Base class providing an interface for concrete detections
    """

    @abstractmethod
    def dpa_selection(self, window: List, compair: ComPairType):
        """!
        Abstract DPA selection

        @param window: List of messages corresponding to a single window
        @param compair: Pair of communicating devices

        @return Selected DPA
        """
        pass


    @abstractmethod
    def apply_detection(self, aut: core_wfa.CoreWFA, window: List, compair: ComPairType):
        """!
        Abstract apply detection on a given window

        @param aut: Golden PA (representing a normal behavior)
        @param window: List of messages corresponding to a single window to be checked
        @param compair: Pair of communicating devices

        @return abstact detection values
        """
        pass


    def detect(self, window: List, compair: ComPairType, accelerate: float = 0.0):
        """!
        Abstract anomaly detection

        @param window: List of messages corresponding to a single window to be checked
        @param compair: Pair of communicating devices
        @param accelerate: Use acceleration with the given value (if a detection
            value is below accelerate, the detection analysis terminates without
            computing all detection values). 

        @return abstact detection values
        """
        aut = self.dpa_selection(window, compair)
        return self.apply_detection(aut, window, compair)


""" @} """
