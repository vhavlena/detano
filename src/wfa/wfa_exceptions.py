#!/usr/bin/env python3

"""
Tool for approximate reductions of finite automata used in network traffic
monitoring. Taken and modified from https://github.com/vhavlena/appreal

Copyright (C) 2017  Vojtech Havlena, <xhavle03@stud.fit.vutbr.cz>

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

import enum

class WFAErrorType(enum.Enum):
    general_error = 0
    not_DAG = 1

class WFAOperationException(Exception):
    """Exception used when an error during parsing is occured.
    """
    def __init__(self, msg, err_type=WFAErrorType.general_error):
        super(WFAOperationException, self).__init__()
        self.msg = msg
        self.err_type = err_type

    def __str__(self):
        return self.msg
