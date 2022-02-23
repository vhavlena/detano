#!/usr/bin/env python3

"""!
\brief Class for removing similar automata in a set

\details
    Implementation of a greedy approach for removing items from a given set that
    causes a smallest error (the minimum distance from a removed item to a
    remaining item).

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

from typing import TypeVar, Generic, List, Tuple, Set

T = TypeVar("T")
DistType = dict[Tuple[T, T], float]
SortedDictType = List[Tuple[Tuple[T,T], float]]

class Distance(Generic[T]):
    """!
    Class removing items from a set causing the minimum error
    """


    def __init__(self, dists: DistType, pts: List[T]):
        """!
        Constructor

        @param dists: Distances between items
        @param pts: Items in the set
        """
        self.dist = dists
        self.points = set(pts)


    def _get_error_bound(self, removed: Set[T], sorted_dist: SortedDictType) -> float:
        """!
        Compute the error bound with the set of removed automata.

        @param removed: Removed items from the set
        @param sorted_dist: Distances between pairs of items sorted from the smallest one

        @return: Error bound caused by removing items from removed
        """
        error = None
        for r in removed:
            for k, v in sorted_dist:
                if (k[0] == r and k[1] not in removed) or (k[1] == r and k[0] not in removed):
                    if error is None:
                        error = 0.0
                    error = max(v, error)
                    break
        return error if error is not None else 1.0


    def compute_subset_error(self, max_error: float) -> Set[T]:
        """!
        Get subset of items that meets the max_error bound.

        @param max_error: Maximum allowed error

        @return: Subset of items causing error less that max_error
        """
        error = 0.0
        removed: Set[T] = set()
        sorted_dist = sorted(self.dist.items(), key=lambda x: x[1])

        for k, v in sorted_dist:
            if (k[0] in removed) and (k[1] in removed):
                continue
            a = k[0] if k[0] not in removed else k[1]
            if self._get_error_bound(removed | set([a]), sorted_dist) > max_error:
                break
            removed.add(a)
            error += v
        return self.points - removed
