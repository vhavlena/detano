#!/usr/bin/env python3

"""!
\brief Parsing files with already divided conversations

\details
    Parsing IEC104 conversations from a file. Allowing to split according to
    communication pairs and time windows.

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

import sys
import csv
import time
import bidict
import re

from typing import List, Dict, TypeVar, Generic, Optional, Callable, FrozenSet, Tuple

import parser.conversation_parser_base as par

from typing import List, NamedTuple
from collections import defaultdict
from enum import Enum


ComPairType = FrozenSet[Tuple[str,str]]
RowType = Dict[str, str]
ConvSymbolType = Tuple[str, str]
ConvStrType = List[ConvSymbolType]


class IEC104ConvParser(par.ConvParserBase[Tuple[str,str]]):
    """!
    Class for parsing IEC104 conversations from already divided messages
    """

    def __init__(self, inp: List[RowType], pr: Optional[ComPairType]=None):
        """!
        Constructor taking a list of messages (each message is a dictionary)

        @param inp: Input list of messages
        @param pr: A communication pair
        """
        self.input = inp
        self.compair = pr
        self.index = 0
        self.conversations: List[ConvStrType] = []


    def parse_conversations(self) -> None:
        """!
        Parse and store all conversations
        """
        self.index = 0
        self.conversations = []
        conv = self.get_conversation()
        while conv is not None:
            self.conversations.append(conv)
            conv = self.get_conversation()


    def get_all_conversations(self, proj: Optional[Callable]=None) -> List[ConvStrType]:
        """!
        Get all conversations (possibly filter by communication pairs)

        @param proj: Projection on the messages

        @return All parsed conversations
        """
        return self.conversations


    def get_line(self) -> RowType:
        """!
        Get a next line

        @return Next line of the buffer
        """
        if self.index >= len(self.input):
            raise IndexError("Index out of range")
        self.index += 1
        return self.input[self.index - 1]


    def parse_data(self, data: str) -> ConvStrType:
        """!
        Parse data

        @param data: Input to be parsed

        @return List of parsed values
        """
        ret = []
        lst = data.split(",")
        for it in lst:
            m = re.match(r"\<([0-9]+)\.(([0-9]+|n))\>", it)
            if m is not None:
                ret.append((m.group(1), m.group(2)))
        return ret


    def get_conversation(self) -> Optional[ConvStrType]:
        """!
        Get a following conversation from already divided messages.

        @return Parsed conversation
        """
        conv = list()
        try:
            ln = self.get_line()
            while ln["Data"] is None or len(ln["Data"]) == 0:
                ln = self.get_line()
        except IndexError:
            return None
        conv = self.parse_data(ln["Data"])
        return conv


    def split_communication_pairs(self) -> List["IEC104ConvParser"]:
        """!
        Split input according to the communication pairs.

        @return List of intances of IEC104ConvParser each for one communication pair
        """
        dct_spl = defaultdict(lambda: [])

        actId = None
        for item in self.input:
            if item["Timestamp"] == "Key":
                val = item["Relative Time"].strip().split("-")
                if len(val) != 2:
                    if len(val) == 4:
                        actId = frozenset([(val[0], val[2]), (val[1], val[3])])
                    else:
                        raise Exception("Bad format of communication pair")
                else:
                    source = val[0].split(":")
                    dest = val[1].split(":")
                    actId = frozenset([(source[1], source[0]), (dest[0], dest[1])])
            else:
                dct_spl[actId].append(item)
        ret = []
        for k, v in dct_spl.items():
            ret.append(IEC104ConvParser(v, k))
        return ret


    def split_to_windows(self, dur: float) -> List["IEC104ConvParser"]:
        """!
        Split input according to time windows.

        @return List of intances of IEC104ConvParser each for one window
        """
        chunks = defaultdict(lambda: [])
        for item in self.input:
            chunks[int(float(item["Relative Time"])/dur)].append(item)

        if len(chunks) == 0:
            return []
        m = max(list(chunks.keys())) + 1
        ret = []
        for i in range(m):
            ret.append(IEC104ConvParser(chunks[i], self.compair))
        return ret
