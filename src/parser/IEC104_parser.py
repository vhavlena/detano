#!/usr/bin/env python3

"""
Dividing list of messages into conversations.

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

import sys
import csv
import time
import bidict

import parser.conversation_parser_base as par

from typing import List, NamedTuple
from collections import defaultdict
from enum import Enum


class ConvType(Enum):
    FILETRANSFER = 0
    GENERAL = 1
    GENERAL_ACT = 2
    SPONTANEOUS = 3
    UNKNOWN = 99


class IEC104Parser(par.ConvParserBase):

    """
    Takes a list of messages (each message is a dictionary)
    """
    def __init__(self, inp, pr=None):
        self.input = list(filter(IEC104Parser.is_inform_message, inp))
        self.compair = pr
        self.index = 0
        self.buffer = []
        self.conversations = []
        self.incomplete = []


    """
    Parse and store all conversations
    """
    def parse_conversations(self):
        self.conversations = []
        self.incomplete = []
        conv = self.get_conversation()
        while conv is not None:
            if not self.is_conversation_complete(conv):
                self.incomplete.append(conv)
            self.conversations.append(conv)
            conv = self.get_conversation()


    """
    Does the item match communication pair restriction?
    """
    @staticmethod
    def is_msg_match(compair, val):
        if compair == frozenset([(val["srcIP"], val["srcPort"]), (val["dstIP"], val["dstPort"])]):
            return True
        return False


    """
    Get all conversations (possibly filter by communication pairs)
    """
    def get_all_conversations(self, proj=None):
        ret = self.conversations

        if proj is not None:
            ret = list(map(lambda x: list(map(proj,x)), ret))
        return ret


    """
    Is message spontaneous?
    """
    @staticmethod
    def is_spontaneous(row):
        return int(row["cot"]) == 3


    """
    Is a message informal?
    """
    @staticmethod
    def is_inform_message(row):
        if row["fmt"] == str():
            return False
        if int(row["fmt"], 16) == 0:
            return True
        return False


    """
    Get initial type of a conversation
    """
    @staticmethod
    def get_initial_type(row):
        if int(row["asduType"]) == 122:
            return ConvType.FILETRANSFER
        if int(row["cot"]) == 6:
            return ConvType.GENERAL_ACT
        if int(row["cot"]) == 3:
            return ConvType.SPONTANEOUS
        if int(row["cot"]) == 7:
            return ConvType.GENERAL
        return ConvType.UNKNOWN


    """
    Is message in the middle of a conversation
    """
    @staticmethod
    def in_middle_range(row, tp):
        if tp == ConvType.FILETRANSFER and int(row["asduType"]) in range(123, 128):
            return True;
        if tp == ConvType.GENERAL and int(row["cot"]) not in [6,7]:
            return True
        if tp == ConvType.GENERAL_ACT and int(row["cot"]) not in [6]:
            return True
        return False


    """
    Get a next symbol
    """
    def get_symbol(self, buff_read):
        if buff_read:
            return self.buffer.pop(0)
        if self.index >= len(self.input):
            raise IndexError("Index out of range")
        self.index += 1
        return self.input[self.index - 1]


    """
    Return a symbol to input buffer
    """
    def return_symbol(self, val, buff_read):
        if buff_read:
            self.buffer.insert(0, val)
        else:
            self.index -= 1


    """
    Check if a given conversation is complete (according to the last packet)
    """
    def is_conversation_complete(self, conv):
        return (int(conv[-1]["asduType"]) in [123, 124, 70, 36]) or (int(conv[-1]["cot"]) in [3, 10, 44, 45, 46, 47])

    """
    Get a following conversation from a list of messages. It implements just a
    couple of cases (definitely not all of them)
    """
    def get_conversation(self):
        conv = list()
        buff = list()
        buff_read = len(self.buffer) > 0

        try:
            row = self.get_symbol(buff_read)
            if IEC104Parser.is_spontaneous(row):
                return [row]

            final = False
            tp = IEC104Parser.get_initial_type(row)
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
                row = self.get_symbol(buff_read)

        except IndexError:
            pass

        if len(conv) == 0 and len(buff) == 0:
            return None
        self.buffer += buff
        return conv


    """
    Split input according to the communication pairs.
    """
    def split_communication_pairs(self):
        dct_spl = defaultdict(lambda: [])

        for item in self.input:
            id = frozenset([(item["srcIP"], item["srcPort"]), (item["dstIP"], item["dstPort"])])
            dct_spl[id].append(item)
        ret = []
        for k, v in dct_spl.items():
            ret.append(IEC104Parser(v, k))
        return ret


    """
    Split input according to time windows
    """
    def split_to_windows(self, dur):
        chunks = defaultdict(lambda: [])
        for item in self.input:
            chunks[int(float(item["Relative Time"])/dur)].append(item)

        if len(chunks) == 0:
            return []
        m = max(list(chunks.keys()))
        ret = []
        for i in range(m):
            ret.append(IEC104Parser(chunks[i], self.compair))
        return ret


def filter_to_conversations(reader, rows_filter):
    lines = list()
    conversation = list()
    for row in reader:
        item = tuple([row[k] for k in rows_filter])
        if not all(item):
            lines.append(conversation)
            conversation = list()
        else:
            conversation.append(item)
    return lines


"""
Get all messages from a csv file
"""
def get_messages(fd):
    reader = csv.DictReader(fd, delimiter=";")
    ret = []
    for item in reader:
        ret.append(item)
    return ret


def values_bidict(vals):
    dct = bidict.bidict()
    cnt = 0

    for row in vals:
        for item in row:
            if item not in dct:
                dct[item] = cnt
                cnt += 1
    return dct


def rename_values(vals, dct):
    ren_vals = list()
    for row in vals:
        ren_vals.append(map(lambda x: dct[x], row))
    return ren_vals
