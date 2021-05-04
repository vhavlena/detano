#!/usr/bin/env python3

"""
Dividing list of messages into conversations -- base class.

Copyright (C) 2021  Vojtech Havlena, <ihavlena@fit.vutbr.cz>

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

class ConvParserBase(ABC):

    """
    Parse and store all conversations
    """
    @abstractmethod
    def parse_conversations(self):
        pass


    """
    Get all conversations (possibly projected by abstraction)
    """
    @abstractmethod
    def get_all_conversations(self, proj=None):
        pass


    """
    Get a following conversation from a list of messages. It implements just a
    couple of cases (definitely not all of them)
    """
    @abstractmethod
    def get_conversation(self):
        pass


    """
    Split input according to the communication pairs.
    @return List of ConvParserBase (or derived)
    """
    @abstractmethod
    def split_communication_pairs(self):
        pass


    """
    Split input according to time windows
    @param dur Time duration
    @return List of ConvParserBase (or derived)
    """
    @abstractmethod
    def split_to_windows(self, dur):
        pass
