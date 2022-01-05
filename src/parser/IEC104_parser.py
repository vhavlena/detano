#!/usr/bin/env python3

"""!
\brief Dividing list of messages into conversations.

\details
    Parsing IEC104 conversations from a list of messages (each message is a
    dictionary). Allowing to split according to communication pairs and time
    windows.

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

from typing import List, Dict, TypeVar, Generic, Optional, Callable, FrozenSet, Tuple

import parser.conversation_parser_base as par

from typing import List, NamedTuple
from collections import defaultdict
from enum import Enum


ComPairType = FrozenSet[Tuple[str,str]]
ConvSymbolType = Dict[str, str]
ConvStrType = List[ConvSymbolType]

class ConvType(Enum):
    """!
    Type of a conversation
    """
    ## File transfer
    FILETRANSFER = 0
    ## General interrogation
    GENERAL = 1
    ## General acknowledgement
    GENERAL_ACT = 2
    ## Spontaneous conversation
    SPONTANEOUS = 3
    ## Unknowt type
    UNKNOWN = 99


class IEC104Parser(par.ConvParserBase[Dict[str, str]]):
    """!
    Class for parsing IEC104 conversations
    """


    def __init__(self, inp: List[ConvSymbolType], pr: Optional[ComPairType]=None):
        """!
        Constructor taking a list of messages (each message is a dictionary)

        @param inp: Input list of messages
        @param pr: A communication pair
        """
        self.input = list(filter(IEC104Parser.is_inform_message, inp))
        self.compair = pr
        self.index = 0
        self.buffer: List[ConvSymbolType] = []
        self.conversations: List[ConvStrType] = []
        self.incomplete: List[ConvStrType] = []


    def parse_conversations(self) -> None:
        """!
        Parse and store all conversations
        """
        self.conversations = []
        self.incomplete = []
        conv = self.get_conversation()
        while conv is not None:
            if not self.is_conversation_complete(conv):
                self.incomplete.append(conv)
            self.conversations.append(conv)
            conv = self.get_conversation()


    @staticmethod
    def is_msg_match(compair: ComPairType, val: ConvSymbolType) -> bool:
        """!
        Does the message match communication pair restriction?

        @param compair: A communication pair (IP, port)
        @param val: A message

        @return Is the message sent by the compair?
        """
        if compair == frozenset([(val["srcIP"], val["srcPort"]), (val["dstIP"], val["dstPort"])]):
            return True
        return False



    def get_all_conversations(self, proj: Optional[Callable]=None) -> List[ConvStrType]:
        """!
        Get all conversations (possibly filter by communication pairs)

        @param proj: Projection on the messages

        @return All parsed conversations
        """
        ret = self.conversations

        if proj is not None:
            ret = list(map(lambda x: list(map(proj,x)), ret))
        return ret


    @staticmethod
    def is_spontaneous(row: ConvSymbolType) -> bool:
        """!
        Is the message spontaneous?

        @param row: Message
        @return True -- spontaneous message
        """
        return int(row["cot"]) == 3


    @staticmethod
    def is_inform_message(row: ConvSymbolType) -> bool:
        """!
        Is the message informal?

        @param row: Message
        @return True -- informal message
        """
        if row["fmt"] == str():
            return False
        if int(row["fmt"], 16) == 0:
            return True
        return False


    @staticmethod
    def get_initial_type(row: ConvSymbolType) -> ConvType:
        """!
        Get initial type of a conversation

        @param row: Message
        @return Type of the conversation initialized by the message row
        """
        if int(row["asduType"]) == 122:
            return ConvType.FILETRANSFER
        if int(row["cot"]) == 6:
            return ConvType.GENERAL_ACT
        if int(row["cot"]) == 3:
            return ConvType.SPONTANEOUS
        if int(row["cot"]) == 7:
            return ConvType.GENERAL
        return ConvType.UNKNOWN


    @staticmethod
    def in_middle_range(row: ConvSymbolType, tp: ConvType) -> bool:
        """!
        Is the message in the middle of a conversation

        @param row: Message
        @param tp: Type of the conversation

        @return True -- the message is in the middle of a conversation of that type
        """
        if tp == ConvType.FILETRANSFER and int(row["asduType"]) in range(123, 128):
            return True;
        if tp == ConvType.GENERAL and int(row["cot"]) not in [6,7]:
            return True
        if tp == ConvType.GENERAL_ACT and int(row["cot"]) not in [6]:
            return True
        return False


    @staticmethod
    def is_final(row: ConvSymbolType, tp: ConvType) -> bool:
        """!
        Is the message final

        @param row: Message
        @param tp: Type of the conversation

        @return True -- the message is final
        """
        if tp == ConvType.GENERAL and int(row["cot"]) in [10, 44, 45, 46, 47]:
            return True
        if tp == ConvType.GENERAL_ACT and int(row["cot"]) in [10, 44, 45, 46, 47]:
            return True
        if tp == ConvType.UNKNOWN and int(row["cot"]) in [10, 44, 45, 46, 47]:
            return True
        return False


    def get_symbol(self, buff_read: bool) -> ConvSymbolType:
        """!
        Get a next message from the buffer.

        @param buff_read: Buffer

        @return Next message in the buffer
        """
        if buff_read:
            return self.buffer.pop(0)
        if self.index >= len(self.input):
            raise IndexError("Index out of range")
        self.index += 1
        return self.input[self.index - 1]


    def return_symbol(self, val: ConvSymbolType, buff_read: bool) -> None:
        """!
        Return the message to the buffer.

        @param val: Value to be inserted
        @param buff_read: Is it read from the buffer
        """
        if buff_read:
            self.buffer.insert(0, val)
        else:
            self.index -= 1


    def is_conversation_complete(self, conv: ConvStrType) -> bool:
        """!
        Check if a given conversation is complete (according to the last packet).

        @param conv: Parsed conversation

        @return: True -- the message is complete
        """
        return (int(conv[-1]["asduType"]) in [123, 124, 70, 36]) or (int(conv[-1]["cot"]) in [3, 10, 44, 45, 46, 47])


    def get_conversation(self) -> Optional[ConvStrType]:
        """!
        Get a following conversation from a list of messages. It implements just a
        couple of cases (definitely not all of them)

        @return Parsed conversation
        """
        conv = list()
        buff = list()
        buff_read = len(self.buffer) > 0

        try:
            row = self.get_symbol(buff_read)
            if IEC104Parser.is_spontaneous(row):
                return [row]

            final = False
            tp = IEC104Parser.get_initial_type(row)
            if IEC104Parser.is_final(row, tp):
                return [row]

            conv.append(row)
            row = self.get_symbol(buff_read)


            while True:
                if IEC104Parser.is_spontaneous(row):
                    buff.append(row)
                    row = self.get_symbol(buff_read)
                    continue
                if IEC104Parser.in_middle_range(row, tp):
                    final = True
                if final and (not IEC104Parser.in_middle_range(row, tp)):
                    self.return_symbol(row, buff_read)
                    break
                conv.append(row)

                if IEC104Parser.is_final(row, tp):
                    break

                row = self.get_symbol(buff_read)

        except IndexError:
            pass

        if len(conv) == 0 and len(buff) == 0:
            return None
        self.buffer += buff
        return conv


    def split_communication_pairs(self) -> List["IEC104Parser"]:
        """!
        Split input according to the communication pairs.

        @return List of intances of IEC104Parser each for one communication pair
        """
        dct_spl = defaultdict(lambda: [])

        for item in self.input:
            id = frozenset([(item["srcIP"], item["srcPort"]), (item["dstIP"], item["dstPort"])])
            dct_spl[id].append(item)
        ret = []
        for k, v in dct_spl.items():
            ret.append(IEC104Parser(v, k))
        return ret


    def split_to_windows(self, dur: float) -> List["IEC104Parser"]:
        """!
        Split input according to time windows.

        @return List of intances of IEC104Parser each for one window
        """
        chunks = defaultdict(lambda: [])
        for item in self.input:
            chunks[int(float(item["Relative Time"])/dur)].append(item)

        if len(chunks) == 0:
            return []
        m = max(list(chunks.keys())) + 1
        ret = []
        for i in range(m):
            ret.append(IEC104Parser(chunks[i], self.compair))
        return ret


def get_messages(fd) -> List[ConvSymbolType]:
    """!
    Get all messages from a csv file.

    @param fd: File descriptor

    @return Messages from the csv file fd
    """
    reader = csv.DictReader(fd, delimiter=";")
    ret = []
    for item in reader:
        ret.append(item)
    return ret
