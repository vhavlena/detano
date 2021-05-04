#!/usr/bin/env python3

"""
Anomaly detection base.

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

from abc import ABC, abstractmethod

class AnomDetectBase(ABC):

    """
    Abstract DPA selection
    """
    @abstractmethod
    def dpa_selection(self, window, compair):
        pass


    """
    Abstract DPA selection
    """
    @abstractmethod
    def apply_detection(self, aut, window, compair):
        pass


    """
    Anomaly detection
    """
    def detect(self, window, compair):
        aut = self.dpa_selection(window, compair)
        return self.apply_detection(aut, window, compair)
