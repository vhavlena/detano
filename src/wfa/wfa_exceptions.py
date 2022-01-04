#!/usr/bin/env python3

"""!
\brief Exception class for specifying errors when working with WFAs

\details
    Exception class for specifying errors when working with WFAs. Taken and
    modified from <https://github.com/vhavlena/appreal>

\author Vojtěch Havlena

\copyright
    Copyright (C) 2017  Vojtech Havlena, <xhavle03@stud.fit.vutbr.cz>\n
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

import enum

class WFAErrorType(enum.Enum):
    """!
    Error types for WFAs
    """

    ## General error
    general_error = 0
    ## Not directed acyclic graph
    not_DAG = 1

class WFAOperationException(Exception):
    """!
    Exception used when an error during parsing is occured.
    """


    def __init__(self, msg: str, err_type: WFAErrorType=WFAErrorType.general_error):
        """!
        Constructor

        @param msg: Error message
        @param err_type: Error Type
        """
        super(WFAOperationException, self).__init__()
        self.msg = msg
        self.err_type = err_type


    def __str__(self) -> str:
        """!
        Convert to string

        @return Error message
        """
        return self.msg
