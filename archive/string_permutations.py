# -*- coding: utf-8 -*-
"""
Created on Tue Nov  3 23:16:02 2015

@author: David
"""

import unittest

#def extra_ordered_substrings(alphabet):
#    '''Return every ordered substring of alphabet, recursing down all subbranches even if they have already been explored.'''
#    yield alphabet
#    if len(alphabet) > 1:
#        for a in extra_ordered_substrings(alphabet[:-1]): yield a
#        for a in extra_ordered_substrings(alphabet[1:]): yield a
#        if len(alphabet) > 2:
#            for skip in range(1, len(alphabet)-1):
#                short = alphabet[:skip]+alphabet[skip+1:]
#                for a in extra_ordered_substrings(short): yield a
#
#def ordered_substrings(alphabet):
#    '''Use a set to eliminate repetitions from the extra_ordered_substrings.'''
#    answer = set(extra_ordered_substrings(alphabet))
#    for a in answer:
#        yield a

#def ordered_substrings(alphabet):
#    if alphabet != '':
#        yield alphabet
#        for skip in range(1, len(alphabet)-1):
#            left = alphabet[:skip]
#            right = alphabet[skip+1:]
#            for l in ordered_substrings(left):
#                for r in ordered_substrings(right):
#                    yield l+r

def ordered_substrings_of_length(x, master, d=1):
    #print('%sordered_substrings_of_length called with %d and "%s" (depth = %d)'%('_'*d*3, x, master, d))
    if len(master) == x:
        # max boundary condition
        yield master
    elif len(master) > x:
        if x == 1:
            # min boundary condition
            for a in master:
                yield a
        else:
            # solutions including the first character
            for a in ordered_substrings_of_length(x-1, master[1:], d+1):
                #print('%scombining "%s" and "%s"'%('_'*d*3, master[0], a))
                yield master[0]+a
            # solutions NOT including the first character
            for a in ordered_substrings_of_length(x, master[1:], d+1):
                #print('%swithout "%s" returning "%s"'%('_'*d*3, master[0], a))
                yield a

class TestOSOL(unittest.TestCase):
    def test_a(self):
        answer = [a for a in ordered_substrings_of_length(1, 'z')]
        self.assertEqual(answer, ['z'])
    def test_ab(self):
        answer = [a for a in ordered_substrings_of_length(1, 'yz')]
        self.assertItemsEqual(['y', 'z'], answer)
    def test_ab2(self):
        answer = [a for a in ordered_substrings_of_length(2, 'yz')]
        self.assertItemsEqual(['yz'], answer)
    def test_abc(self):
        answer = [a for a in ordered_substrings_of_length(1, 'xyz')]
        self.assertItemsEqual(['x', 'y', 'z'], answer)
    def test_abc2(self):
        answer = [a for a in ordered_substrings_of_length(2, 'xyz')]
        self.assertItemsEqual(['xy', 'yz', 'xz'], answer)


def ordered_substrings(master):
    for l in range(len(master)):
        for a in ordered_substrings_of_length(l+1, master):
            yield a


class CheckAllIn(unittest.TestCase):
    def all_in(self, actual, expected):
        self.assertEqual(len(actual), len(expected))
        #for a in actual:
        #    print(a)
        for e in expected:
            self.assertTrue(e in actual)

class TestSubstrings(CheckAllIn):
    def test_a(self):
        answer = [x for x in ordered_substrings('a')]
        self.assertEqual(answer, ['a'])
    def test_ab(self):
        answer = [x for x in ordered_substrings('ab')]
        self.all_in(answer, ['a', 'b', 'ab'])
    def test_abc(self):
        answer = [x for x in ordered_substrings('abc')]
        #for a in answer:
        #    print(a)
        self.all_in(answer, ['a', 'b', 'c', 'ab', 'ac', 'bc', 'abc'])
    def test_abcd(self):
        answer = [x for x in ordered_substrings('abcd')]
        #for a in answer:
        #    print(a)
        self.all_in(answer, ['a', 'b', 'c', 'd', 'ab', 'ac', 'ad', 'bc', 'bd', 'cd', 'abc', 'bcd', 'acd', 'abd', 'abcd'])


def string_permutations(alphabet):
    '''abc => abc, acb, bac, bca, cab, cba'''
    if len(alphabet) <= 1:
        yield alphabet
    elif len(alphabet) == 2:
        yield alphabet[1]+alphabet[0]
        yield alphabet
    else:
        working = alphabet + alphabet
        for i in range(len(alphabet)):
            first = alphabet[i]
            rest = working[i+1:i+len(alphabet)]
            for x in string_permutations(rest):
                yield first+x


class TestStringPermutations(CheckAllIn):
    def test_a(self):
        answer = [x for x in string_permutations('a')]
        self.assertEqual(answer, ['a'])
    def test_ab(self):
        answer = [x for x in string_permutations('ab')]
        self.all_in(answer, ['ab', 'ba'])
    def test_abc(self):
        answer = [x for x in string_permutations('abc')]
        #for a in answer:
        #    print(a)
        self.all_in(answer, ['abc', 'acb', 'bac', 'bca', 'cab', 'cba'])
    def test_abcd(self):
        answer = [x for x in string_permutations('abcd')]
        self.all_in(answer, ['abcd', 'abdc', 'acbd', 'acdb', 'adcb', 'adbc', 'bacd', 'badc', 'bcad', 'bcda', 'bdac', 'bdca', 'cabd', 'cadb', 'cbad', 'cbda', 'cdab', 'cdba', 'dabc', 'dacb', 'dbac', 'dbca', 'dcab', 'dcba'])


def permutated_substrings(alphabet):
    for a in ordered_substrings(alphabet):
        for b in string_permutations(a):
            yield b


class TestSubStringPermutations(CheckAllIn):
    def test_a(self):
        answer = [x for x in permutated_substrings('a')]
        self.assertEqual(answer, ['a'])
    def test_ab(self):
        answer = [x for x in permutated_substrings('ab')]
        self.all_in(answer, ['a', 'b', 'ab', 'ba'])
    def test_abc(self):
        answer = [x for x in permutated_substrings('abc')]
        #for a in answer:
        #    print(a)
        self.all_in(answer, ['abc', 'acb', 'bac', 'bca', 'cab', 'cba', 'ab', 'ba', 'ac', 'ca', 'ba', 'cb','a', 'b', 'c'])


