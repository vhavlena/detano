#!/usr/bin/env python3

"""!
\brief Core class for working with WFAs

\details
    Class providing basic support for working with WFA. Implements various
    usefull algorithms, such as, product, trim, ... Taken and modified from
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

import copy
import bidict
import math
import wfa.wfa_exceptions as wfa_exceptions

from collections import deque

class Transition(object):
    """!
    Class for the represention of a WFA transition.
    """

    def __init__(self, src, dest, sym, weight):
        """!
        Constructor

        @param src: Source state
        @param dest: Destination state
        @param sym: Symbol
        @param weight: Weight of the transition
        """
        self.src = src
        self.dest = dest
        self.symbol = sym
        self.weight = weight
        self.count = 0


    def __str__(self):
        """!
        String representation

        @return String representation of the transition
        """
        return "({0}, {1}, {2}, {3})".format(self.src, self.dest, self.symbol, self.weight)


    def __repr__(self):
        """!
        String representation

        @return String representation of the transition
        """
        return self.__str__()


    def __eq__(self, other):
        """!
        Equality of two transitions

        @param other: Other transition

        @return True -- both transitions are equal
        """
        return (self.src == other.src) and (self.dest == other.dest) and (self.symbol == other.symbol) and (self.weight == other.weight)


    def __ne__(self, other):
        """!
        Inequality of two transitions

        @param other: Other transition

        @return True -- both transitions are NOT equal
        """
        return not self.__eq__(other)


    def __hash__(self):
        """!
        Hash method

        @return Hash
        """
        return hash((self.src, self.dest, self.symbol, self.weight))


class CoreWFA(object):
    """!
    Basic class for representation of WFA
    """

    def __init__(self, transitions=None, finals=None, start=None, alphabet=None):
        """!
        Constructor

        @param transitions: Transitions
        @param finals: Final states with weights
        @param start: Initial state
        @param alphabet: Alphabet
        """
        self._transitions = transitions
        if self._transitions == None:
            self._transitions = []
        self._finals = finals
        if self._finals == None:
            self._finals = dict()
        self._start = start
        if self._start is None:
            self._start = {0: 1.0}
        self._states_dict = None
        self._alphabet = alphabet
        if alphabet is None:
            self._alphabet = self.get_alphabet()
        self._states = self._get_states()


    def __eq__(self, other):
        """!
        Equality of two WFAs

        @param other: Other WFA

        @return True -- both WFAs are equal
        """
        return (self._transitions == other._transitions) and \
            (self._finals == other._finals) and \
            (self._start == other._start) and \
            (self._alphabet == other._alphabet)


    def __hash__(self):
        """!
        Hash method

        @return Hash
        """
        return hash((tuple(self._transitions), tuple(self._finals), tuple(self._start), tuple(self._alphabet)))


    def get_transitions(self):
        """!
        Get all transitions of the WFA.

        @return List of all transitions
        """
        return self._transitions


    def set_all_finals(self):
        """!
        Set all states to be final (all having the accepting weight 1.0)
        """
        for st in self.get_states():
            self._finals[st] = 1.0


    def get_finals(self):
        """!
        Get all final states of the WFA.

        @return Final states with accepting weights -- Dictionary: Final state -> float (weight)
        """
        return self._finals


    def set_finals(self, finals):
        """!
        Set final states of the WFA.

        @param finals: Dictionary of final states and their weight of accepting.
        """
        self._finals = finals


    def get_starts(self):
        """!
        Get the start state (only one start state is allowed).

        @return Start state.
        """
        return self._start


    def set_starts(self, start):
        """!
        Set the initial state.

        @param start: New initial state
        """
        self._start = start


    def get_alphabet(self):
        """!
        Get alphabet used by the WFA. If the alphabet is not explicitly
        given (in constructor), the alphabet is computed from the transitions.

        @return List of symbols.
        """
        alph = []
        if self._alphabet != None:
            return self._alphabet
        for transition in self._transitions:
            if transition.symbol not in alph:
                alph.append(transition.symbol)
        return alph


    def rename_alphabet(self, dct):
        """!
        Rename alphabet of the automaton (in place).

        @param dct: Mapping of the new symbols
        """
        self._alphabet = None
        tran = list()

        self._transitions = list(map (lambda x: Transition(x.src, x.dest, \
            dct.inverse[x.symbol], x.weight), self._transitions))


    def _get_states(self):
        """!
        Get all states of the WFA (the list of states is computed from the
        transitions).

        @return List of states.
        """
        states = set([])
        for start, _ in self._start.items():
            if start not in states:
                states.add(start)
        for final, _ in self._finals.items():
            if final not in states:
                states.add(final)
        for transition in self._transitions:
            if transition.src not in states:
                states.add(transition.src)
            if transition.dest not in states:
                states.add(transition.dest)

        self._states = list(states)
        return list(states)


    def get_states(self):
        """!
        Get all states of the WFA (the list of states is computed from the
        transitions).

        @return List of states.
        """
        return self._states


    def get_rename_dict(self):
        """!
        Get the dictionary containing original state labels and renamed state
        labels. The dictionary is created after method rename_states is invoked.

        @return Dictionary: State (original) -> State (renamed).
        """
        return self._states_dict


    def get_single_dictionary_transitions(self):
        """!
        Get the transitions (ommiting transitions that differ only on the
        symbol) in the form of dictinary (for each state there is a list of
        transitions leading from this state).

        @return Dictionary assigning State -> List(Transitions)
        """
        tr_dict = dict()
        destinations = dict()

        states = self.get_states()
        for st in states:
            tr_dict[st] = []
            destinations[st] = set([])

        for transition in self._transitions:
            if transition.dest not in destinations[transition.src]:
                tr_dict[transition.src].append(transition)
                destinations[transition.src].add(transition.dest)
        return tr_dict


    def get_dictionary_transitions(self):
        """!
        Get transitions in the form of dictionary (for each state there is a
        list of transitions leading from this state).

        @return Dictionary assigning State -> List(Transitions)
        """
        tr_dict = dict()

        states = self.get_states()
        for st in states:
            tr_dict[st] = []

        for transition in self._transitions:
            tr_dict[transition.src].append(transition)
        return tr_dict


    def get_state_symbol_dict(self):
        """!
        Get transitions in the form of dictionary (for each state there is a
        dictionary assigning to symbols a set of transitions)

        @return Dictionary assigning State -> (Dictionary: Symbol -> Set of transitions)
        """
        tr_dict = dict()

        states = self.get_states()
        for st in states:
            tr_dict[st] = dict()

        for transition in self._transitions:
            try:
                tr_dict[transition.src][transition.symbol].add(transition)
            except KeyError:
                tr_dict[transition.src][transition.symbol] = set([transition])
        return tr_dict


    def get_rev_transitions_aut(self):
        """!
        Get automaton with reversed directions of transitios.

        @return WFA with reversed transitions.
        """
        rev_transitions = []
        for transition in self.get_transitions():
            rev_transitions.append(Transition(transition.dest, transition.src, \
                transition.symbol, transition.weight))

        return CoreWFA(rev_transitions, copy.copy(self._finals), copy.copy(self._start), copy.copy(self.get_alphabet()))


    def rename_states(self):
        """!
        Rename states of the WFA. Assign to the states numbers from 0 to n-1 (n
        is the number of states). The start state has number 0. The renamed and
        original states are stored in the states_dict dictionary.
        """
        self._states_dict = dict()
        new_transitions = []
        new_finals = dict()
        new_starts = dict()
        count = 0

        for st, weight in self._start.items():
            self._states_dict[st] = count
            new_starts[count] = weight
            count += 1

        for state in self.get_states():
            if state not in self._states_dict:
                self._states_dict[state] = count
                count += 1

        for (state, prob) in self._finals.items():
            dest = self._states_dict[state]
            new_finals[dest] = prob

        for transition in self._transitions:
            new_transitions.append(Transition( \
                self._states_dict[transition.src], \
                self._states_dict[transition.dest], \
                transition.symbol, transition.weight))

        self._transitions = new_transitions
        self._finals = new_finals
        self._start = new_starts
        self._states = self._get_states()


    def product(self, aut):
        """!
        Perform the product of two WFAs.

        @param aut: Second automaton for the product.

        @return WFA representing the product of WFAs
        """
        #queue = deque([])
        queue = []
        ret_finals = dict()
        ret_start = dict()
        ret_transitions = []

        self_finals = set(self._finals.keys())
        aut_finals = set(aut.get_finals().keys())

        for st1, weight1 in self._start.items():
            for st2, weight2 in aut.get_starts().items():
                queue.append((st1, st2))
                ret_start[(st1, st2)] = weight1 * weight2

        finished = set([])
        tr_dict1 = self.get_dictionary_transitions()
        tr_dict2 = aut.get_dictionary_transitions()

        while len(queue) > 0:
            act = queue.pop(0)
            finished.add(act)

            if (act[0] in self_finals) \
                and (act[1] in aut_finals):
                ret_finals[act] = self._finals[act[0]] \
                    * aut.get_finals()[act[1]]

            for tr1 in tr_dict1[act[0]]:
                for tr2 in tr_dict2[act[1]]:
                    if tr2.symbol != tr1.symbol:
                        continue

                    dest_state = (tr1.dest, tr2.dest)
                    ret_transitions.append(Transition(act, dest_state, \
                        tr1.symbol, tr1.weight * tr2.weight))

                    if (dest_state not in finished): #and (dest_state not in queue):
                        queue.append(dest_state)

        alphabet = set(self.get_alphabet()) & set(aut.get_alphabet())
        return CoreWFA(ret_transitions, ret_finals, ret_start, alphabet)


    def breadth_first_search(self, state, visited, tr_dict):
        """!
        BFS in the automaton graph.

        @param state: The start state of the BFS.
        @param visited: The list of visited states (out parameter).
        @param tr_dict: Transition dictionary.

        @return Out parameter visited (the list of visited states).
        """
        queue = deque([state])
        if tr_dict is None:
            tr_dict = self.get_single_dictionary_transitions()
        while queue:
            head = queue.popleft()
            visited.add(head)
            for transition in tr_dict[head]:
                if (transition.dest not in visited) \
                    and (transition.dest not in queue):
                    queue.append(transition.dest)


    def get_coaccessible_states(self, tr_dict=None):
        """!
        Get coaccessible states of the WFA.

        @param tr_dict: Transition dictionary.

        @return The list of coaccessible states.
        """
        visited = set([])
        reverse_aut = self.get_rev_transitions_aut()
        if tr_dict is None:
            tr_dict = reverse_aut.get_single_dictionary_transitions()
        for state, _ in reverse_aut.get_finals().items():
            reverse_aut.breadth_first_search(state, visited, tr_dict)
        return visited


    def get_accessible_states(self, tr_dict=None):
        """!
        Get accessible states of the WFA.

        @param tr_dict: Transition dictionary.

        @return The list of accessible states.
        """
        visited = set([])
        if tr_dict is None:
            tr_dict = self.get_single_dictionary_transitions()
        for state, _ in self.get_starts().items():
            self.breadth_first_search(state, visited, tr_dict)
        return visited


    def get_automata_restriction(self, states):
        """!
        Get WFA restriction to only states in states.

        @param states: The list of states of the new WFA.

        @return WFA (restriction to states in the list states)
        """
        rest_transitions = []
        rest_finals = dict()
        rest_initials = dict()
        alphabet = self.get_alphabet()
        for transition in self._transitions:
            if (transition.src in states) and (transition.dest in states):
                rest_transitions.append(Transition(transition.src, transition.dest,\
                    transition.symbol, transition.weight))

        for state, weight in self._finals.items():
            if state in states:
                rest_finals[state] = weight

        #Since some NFA formalisms do not allow an NFA without an initial state,
        #if the list states do not contain any initial state, we add new initial
        #state (but only if the original NFA contains at least one intial state).
        for state, weight in self._start.items():
            if state in states:
                rest_initials[state] = weight
        if len(rest_initials) == 0 and len(self._start) > 0:
            single_ini = list(self._start.keys())[0]
            rest_initials[single_ini] = self._start[single_ini]

        return CoreWFA(rest_transitions, rest_finals,\
            rest_initials, alphabet)


    def get_trim_automaton(self):
        """!
        Get trimed WFA.

        @return Trimmed WFA.
        """
        sts = self.get_coaccessible_states() & self.get_accessible_states()
        return self.get_automata_restriction(sts)


    def get_predecessors(self, state):
        """!
        Operation that finds predessors of the state state.

        @param state: The state whose predessors are found.

        @return List of predecessors
        """
        ret = set([])
        transitions = self.get_transitions()
        for tr in transitions:
            if tr.dest == state:
                ret.add(tr.src)
        return ret


    def get_predecessors_transitions(self):
        """!
        Get predecessors of all states of the WFA.

        @return Dict: State -> Set(State)
        """
        predecessors = {}
        for state in self.get_states():
            predecessors[state] = []

        for transition in self.get_transitions():
            predecessors[transition.dest].append(transition)

        return predecessors


    def is_deterministic(self):
        """!
        Is the WFA deterministic

        @return True deterministic, otherwise False
        """
        if len(self._start) > 1:
            return False
        tr_dict = self.get_state_symbol_dict()
        for st, sym_dict in tr_dict.items():
            for symbol, trs in sym_dict.items():
                if len(trs) > 1:
                    return False
        return True


    def string_prob_deterministic(self, word):
        """!
        Compute the probability of the word word.

        @param word: Word

        @return Probability of word
        """
        prob = 0.0
        tr_dict = self.get_state_symbol_dict()
        act = list(self._start.keys())[0]
        prob = math.log(self._start[act])
        try:
            for sym in word:
                n_tr = list(tr_dict[act][sym])[0]
                prob += math.log(n_tr.weight)
                act = n_tr.dest
            prob += math.log(self._finals[act])
        except ValueError:
            return None
        except KeyError:
            return None
        return prob


    def map_symbols(self, fnc):
        """!
        Apply the function fnc on the symbols of all transitions

        @param fnc: Function applied on symbols
        """
        for tr in self.get_transitions():
            tr.symbol = fnc(tr.symbol)
