#!/usr/bin/python

"""!
\brief Class for working with a computation of language weights

\details
    Class providing support for a computation of weight of the language
    (specified by the WFA). Inmplements various methods and approaches for
    transition closure computation. Taken and modified from
    <https://github.com/vhavlena/appreal>

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

import numpy
import scipy.sparse
import scipy.sparse.linalg
import wfa.core_wfa as core_wfa
import warnings
from scipy.sparse import SparseEfficiencyWarning

from enum import Enum
from typing import List, Optional, Set, TypeVar, Generic, Callable

StateType = int
SymbolType = TypeVar("SymbolType")
StateFloatMapType = dict[StateType, float]
StateFloatMapOptType = Optional[dict[StateType, float]]
TransFunctionType = dict[StateType, dict[SymbolType, Set[StateType]]]


## Threshold for sparse matrices
THRESHOLD = 0.0

## Ignore a particular warning
warnings.simplefilter('ignore', SparseEfficiencyWarning)

class ClosureMode(Enum):
    """!
    Implemented methods for computing the closure.
    """

    ## Use matrix inversion
    inverse = 1
    ## Iterative matrix multiplication.
    iterations = 2
    ## Hotteling-Bodeqig algorithm
    hotelling_bodewig = 3

class MatrixWFAOperationException(Exception):
    """!
    Exception for invalid operations and errors during the closure computing.
    """

    def __init__(self, msg: str):
        """!
        Constructor

        @param msg: Error message
        """
        super(MatrixWFAOperationException, self).__init__()
        self.msg = msg


    def __str__(self) -> str:
        """!
        Convert to string

        @return Error message
        """
        return self.msg



class MatrixWFA(core_wfa.CoreWFA):
    """!
    Class for matrix operations with WFAs involving matrix operations.
    """


    def __init__(self, transitions: List[core_wfa.Transition]=None, finals: StateFloatMapOptType=None, start: StateFloatMapType = dict(), alphabet: Optional[List[SymbolType]]=None):
        """!
        Constructor

        @param transitions: Transitions
        @param finals: Final states with weights
        @param start: Initial state
        @param alphabet: Alphabet
        """
        super(MatrixWFA, self).__init__(transitions, finals, start, alphabet)


    def are_states_compatible(self) -> bool:
        """!
        Check whether the states of the WFA are compatible with matrix
        operations (states are labeled with consequtive numbers from 0 to n-1).

        @return Compatibility of states
        """
        states = super(MatrixWFA, self).get_states()

        for i in range(0, len(states)):
            found = False
            for state in states:
                if state == i:
                    found = True
                    break
            if not found:
                return False

        return True


    def get_transition_matrix(self, sparse: bool=False) -> numpy.matrix:
        """!
        Get a transition matrix corresponding to the WFA.

        @param sparse: Use sparse matrices

        @return Transition matrix (Numpy.matrix)
        """
        if not self.are_states_compatible():
            raise MatrixWFAOperationException("States must be renamed to the set {0,...,n}")

        if sparse:
            return self._get_transition_matrix_sparse()

        num_states = len(super(MatrixWFA, self).get_states())
        mtx = numpy.matrix(numpy.empty((num_states,num_states,)))
        mtx[:] = 0.0

        for transition in super(MatrixWFA, self).get_transitions():
            mtx[transition.src, transition.dest] \
                = mtx[transition.src, transition.dest] + transition.weight

        return mtx


    def _get_transition_matrix_sparse(self) -> numpy.matrix:
        """!
        Get CSR representation of the transition matrix.

        @return Sparse matrix representation (scipy.sparse.csr_matrix)
        """
        if not self.are_states_compatible():
            raise MatrixWFAOperationException("States must be renamed to the set {0,...,n}")

        num_states = len(super(MatrixWFA, self).get_states())
        tr_dict = super(MatrixWFA, self).get_dictionary_transitions()

        nonzeros = []
        columns = []
        row_num = [0]

        for state in range(num_states):
            row: dict[StateType, float] = {}
            for transition in tr_dict[state]:
                try:
                    row[transition.dest] += transition.weight
                except KeyError:
                    row[transition.dest] = transition.weight
            nonzero_elems = len(row)
            for key in range(num_states):
                val = row.get(key, None)
                if val is not None:
                    nonzeros.append(val)
                    columns.append(key)
            row_num.append(row_num[state] + nonzero_elems)


        mtx = scipy.sparse.csr_matrix((nonzeros, columns, row_num), shape=(num_states, num_states), dtype=numpy.float64)
        return mtx


    def get_final_vector(self, sparse: bool=False) -> numpy.matrix:
        """!
        Get a vector with final weights corresponding to the WFA.

        @param sparse: Use sparse matrices

        @return Final vector (Numpy.matrix)
        """
        if not self.are_states_compatible():
            raise MatrixWFAOperationException("States must be renamed to the set {0,...,n}")

        num_states = len(super(MatrixWFA, self).get_states())
        mtx = numpy.matrix(numpy.empty((num_states,)))
        mtx[:] = 0.0

        for state, weight in super(MatrixWFA, self).get_finals().items():
            mtx[0, state] = weight
        if sparse:
            return scipy.sparse.csr_matrix(mtx)
        else:
            return mtx


    def get_final_ones(self, sparse: bool=False) -> numpy.matrix:
        """!
        Get a vector with items 1.0 corresponding to final states (other states
        are set to 0).

        @param sparse: Use sparse matrices

        @return Numpy.matrix (final states are set to one).
        """
        if not self.are_states_compatible():
            raise MatrixWFAOperationException("States must be renamed to the set {0,...,n}")

        num_states = len(super(MatrixWFA, self).get_states())
        mtx = numpy.matrix(numpy.empty((num_states,)))
        mtx[:] = 0.0

        for state, weight in super(MatrixWFA, self).get_finals().items():
            if weight > 0.0:
                mtx[0, state] = 1.0
            else:
                mtx[0, state] = 0.0

        if sparse:
            return scipy.sparse.csr_matrix(mtx)
        else:
            return mtx


    def get_initial_vector(self, sparse: bool=False) -> numpy.matrix:
        """!
        Get a vector of initial weights.

        @param sparse: Use sparse matrices

        @return Vector of initial weights (Numpy.matrix).
        """
        if not self.are_states_compatible():
            raise MatrixWFAOperationException("States must be renamed to the set {0,...,n}")

        num_states = len(super(MatrixWFA, self).get_states())
        mtx = numpy.matrix(numpy.empty((num_states,)))
        mtx[:] = 0.0
        for state, weight in super(MatrixWFA, self).get_starts().items():
            mtx[0, state] = weight

        if sparse:
            return scipy.sparse.csr_matrix(mtx)
        else:
            return mtx


    @staticmethod
    def _get_sparse_inverse(mtx: numpy.matrix, num_states: int) -> numpy.matrix:
        """!
        Get inversion of the sparse matrix. The matrix inversion is computed
        using LU decomposition.

        @param mtx: Matrix
        @param num_states: Matrix dimension (number of states).

        @return Sparse matrix inversion (scipy.sparse.csr_matrix)
        """
        lu_obj = scipy.sparse.linalg.splu(mtx)
        nonzeros = []
        columns = []
        row_num = [0]
        count = 0

        i = 1
        for k in range(num_states):
            b = numpy.zeros((num_states,))
            b[k] = 1
            row_res = lu_obj.solve(b)
            count = 0

            #print i
            i += 1
            for i in range(num_states):
                if row_res[i] > THRESHOLD:
                    nonzeros.append(row_res[i])
                    columns.append(i)
                    count += 1
            row_num.append(row_num[k] + count)

        ret = scipy.sparse.csr_matrix((nonzeros, columns, row_num), shape=(num_states, num_states), dtype=numpy.float64)
        return ret.transpose()


    def compute_transition_closure(self, closure_mode: ClosureMode, sparse: bool=False, iterations: int=0, debug: bool=False) -> numpy.matrix:
        """!
        Compute transition closure by a specified method (assume that the
        conditions for given method are met).

        @param closure_mode: Method for computing the transition closure (ClosureMode).
        @param sparse: Use sparse matrices
        @param iterations: Maximum number of iteration (in the case of iterative methods).
        @param debug: Show debug info.

        @return Transition closure (Numpy.matrix)
        """
        if len(super(MatrixWFA, self).get_states()) == 0:
            return None

        num_states = len(super(MatrixWFA, self).get_states())
        transition_matrix = self.get_transition_matrix(sparse)
        result = None

        if sparse:
            identity = scipy.sparse.identity(num_states, dtype=numpy.float64)
        else:
            identity = numpy.matrix(numpy.identity(len(transition_matrix)))
        #identity = numpy.matrix(numpy.identity(len(transition_matrix)))
        #identity = scipy.sparse.identity(num_states, dtype=numpy.float64)
        #result = numpy.matrix(numpy.empty(len(transition_matrix)))


        #debug = True
        iterations = 100
        closure_mode = ClosureMode.inverse

        if debug:
            eig, _ = numpy.linalg.eig(transition_matrix)
            print("Eigenvalue: ", max(abs(eig)))

        debug = True

        if closure_mode == ClosureMode.inverse:
            if sparse:
                result = MatrixWFA._get_sparse_inverse(identity - transition_matrix, num_states)
            else:
                result = (identity - transition_matrix).getI()
        elif closure_mode == ClosureMode.iterations:
            all_mult = identity
            result = identity
            for i in range(iterations):
                if debug:
                    print("Iteration: {0}".format(i))
                all_mult = all_mult * transition_matrix
                if i == 0:
                    result = all_mult
                else:
                    result = result + all_mult

                print(len(result.nonzero()[0]))
        elif closure_mode == ClosureMode.hotelling_bodewig:
            vn = identity
            mtx = identity - transition_matrix
            for i in range(iterations):
                if debug:
                    print("Iteration: {0}".format(i))
                vn = vn*(2*identity - mtx*vn)
            result = vn

        return result

    #TODO: Merge the following two methods
    def compute_language_probability(self, closure_mode: ClosureMode, sparse: bool=False, iterations: int=0, debug: bool=False) -> float:
        """!
        Compute the total probability of the WFA's language.

        @param closure_mode: Method for computing the transition closure (ClosureMode).
        @param sparse: Use sparse matrices
        @param iterations: Maximum number of iteration (in the case of iterative methods).
        @param debug: Show debug info.

        @return Weight of the language (float)
        """
        if len(super(MatrixWFA, self).get_states()) == 0:
            return 0.0
        ini = self.get_initial_vector(sparse)
        fin = self.get_final_vector(sparse).transpose()
        closure = self.compute_transition_closure(closure_mode, sparse, iterations, debug)
        return ((ini*closure)*fin)[0,0]
