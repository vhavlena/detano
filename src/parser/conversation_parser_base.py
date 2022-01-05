#!/usr/bin/env python3

"""!
\brief Dividing list of messages into conversations -- base class.

\details
    Base class providing interface for conversation parsers (from the input
    list of messages).

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

from typing import List, Dict, TypeVar, Generic, Optional, Callable, Type


ItemType = TypeVar("ItemType")
ConvBaseType = List[ItemType]


class ConvParserBase(ABC, Generic[ItemType]):
    """!
    Base class for parsing conversations
    """


    @abstractmethod
    def parse_conversations(self):
        """!
        Parse and store all conversations
        """
        pass


    @abstractmethod
    def get_all_conversations(self, proj: Optional[Callable]=None) -> List[ConvBaseType]:
        """!
        Get all conversations (possibly projected by abstraction)

        @param proj: Projection applied on data

        @return List of all conversations
        """
        pass


    @abstractmethod
    def get_conversation(self) -> Optional[ConvBaseType]:
        """!
        Get a following conversation from a list of messages. It implements just a
        couple of cases (definitely not all of them)

        @return Next conversation
        """
        pass


    @abstractmethod
    def split_communication_pairs(self) -> List["ConvParserBase"]:
        """!
        Split input according to the communication pairs.

        @return List of ConvParserBase (or derived)
        """
        pass


    @abstractmethod
    def split_to_windows(self, dur: float) -> List["ConvParserBase"]:
        """!
        Split input according to time windows

        @param dur: Time duration
        @return List of ConvParserBase (or derived)
        """
        pass
