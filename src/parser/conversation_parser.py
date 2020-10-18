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

from typing import List, NamedTuple


class ConvParser:

    """
    Takes a list of messages (each message is a dictionary)
    """
    def __init__(self, input):
        self.input = input


    """
    Get a following conversation from a list of messages. It implements just a
    couple of cases (definitely not all of them)
    """
    def get_conversation(self):
        if len(self.input) == 0:
            return None

        conv = list()
        buff = list()

        while True:
            if len(self.input) == 0:
                break
            row = self.input.pop(0)
            if not ConvParser.is_inform_message(row):
                continue

            ini = ConvParser.is_strict_initial_message(conv, row)
            if ini == 0 and len(conv) > 0:
                self.input.insert(0, row)
                break

            finality = ConvParser.is_final_message(conv, row)
            if finality == True:
                conv.append(row)
                break
            if finality is None:
                buff.append(row)
            if finality == False:
                ini = ConvParser.is_initial_message(conv, row)
                if ini != 0 and len(conv) > ini:
                    self.input.insert(0, row)
                    self.input = conv[-ini:] + self.input
                    conv = conv[0:-ini]
                    break
                else:
                    conv.append(row)

        if len(conv) == 0 and len(buff) == 0:
            return None

        self.input = buff + self.input
        return conv


    @staticmethod
    def is_initial_message(conv, row):
        if len(conv) == 0:
            return 0
        if int(row["asduType"]) == 120 and int(conv[-1]["asduType"]) == 122:
            return 1
        return 0


    @staticmethod
    def is_strict_initial_message(conv, row):
        if int(row["cot"]) == 6:
            return 0
        return -1


    @staticmethod
    def is_final_message(conv, new_row):
        if ConvParser.is_single_final_message(new_row):
            return True
        if ConvParser.is_block_final_message(conv + [new_row]):
            return True

        if ConvParser.is_spontaneous(new_row) and len(conv) == 0:
            return True
        if ConvParser.is_spontaneous(new_row):
            return None

        return False


    @staticmethod
    def is_spontaneous(row):
        return int(row["cot"]) == 3


    @staticmethod
    def is_block_final_message(buffer):
        if len(buffer) < 4:
            return False

        proj = list(map(lambda x: int(x["asduType"]) if x is not None else None, buffer))
        if proj[-4:] == [123, 124, 123, 124]:
            return True
        return False


    @staticmethod
    def is_single_final_message(row):
        if int(row["asduType"]) == 70:
            return True
        if int(row["cot"]) == 10:
            return True
        return False


    @staticmethod
    def is_inform_message(row):
        if row["fmt"] == str():
            return False
        if int(row["fmt"], 16) == 0:
            return True
        return False



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
