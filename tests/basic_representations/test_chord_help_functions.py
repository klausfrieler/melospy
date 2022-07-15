#!/usr/bin/env python

""" Unit tests for chord help functions """

import unittest

import melospy.basic_representations.chord_help_functions as ch


class TestChordHelpFunctions( unittest.TestCase ):
    """ Unit tests for chord help functions """
    
    def testFindDictionaryValueInString(self):
        d = ['b5', '', 'sus', '#5', 'm']
        self.assertEqual(ch.findListItemInStringAfterSortingListInDescendingItemLengthOrder("Cm7b5", d), 'b5')
        self.assertEqual(ch.findListItemInStringAfterSortingListInDescendingItemLengthOrder("F##5", d), '#5')
        self.assertEqual(ch.findListItemInStringAfterSortingListInDescendingItemLengthOrder("Cm9", d), 'm')
        self.assertEqual(ch.findListItemInStringAfterSortingListInDescendingItemLengthOrder("G7", d), '')
        self.assertEqual(ch.findListItemInStringAfterSortingListInDescendingItemLengthOrder("G7sus", d), 'sus')
    
    def suite(self):
        return unittest.TestLoader().loadTestsFromTestCase(TestChordHelpFunctions)
    
if __name__ == "__main__":
    unittest.main()
