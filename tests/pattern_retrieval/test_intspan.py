#!/usr/bin/env python

""" Unit test for IntSpan class"""

import unittest

from melospy.pattern_retrieval.intspan import IntSpan


class TestIntSpanClass( unittest.TestCase ):
    """ Unit test for pattern class """
    
    def testConstructorAndMethods(self):
        """ Test functionality """
        ispan = IntSpan("0-2")
        self.assertEqual(ispan.symmetric_difference("5-10").as_start_duration_patches(), [(0, 3), (5, 6)])
        self.assertEqual(str(ispan.add("3")), "0-3")
        self.assertEqual(str(ispan.add("3-7")), "0-7")
        self.assertEqual(str(ispan.remove("7")), "0-6")
        self.assertEqual(str(ispan.discard("6")), "0-5")
        self.assertEqual(str(ispan.update("6-8")), "0-8")
        self.assertEqual(str(ispan.intersection("0-2")), "0-2")
        self.assertEqual(str(ispan.union("9-10")), "0-10")
        self.assertEqual(str(ispan.difference("9-10")), "0-8")
        self.assertEqual(str(ispan.symmetric_difference("5-10")), "0-4,9-10")
        self.assertEqual(ispan.issubset("0-10"), True)
        self.assertEqual(ispan.issuperset("0-1"), True)
        self.assertEqual(ispan[0:2], [0, 1])
        self.assertEqual([i for i in ispan], [ispan[i] for i in range(len(ispan))])
        self.assertEqual(IntSpan("0-9").coverage("0-1"), 1)
        self.assertEqual(IntSpan("0-1").coverage("0-9"), .2)
        self.assertEqual(IntSpan("0-1").coverage("2-9"), 0)
        self.assertEqual(str(ispan.clear()), "")
        self.assertEqual(str(IntSpan.from_start_length(0, 5)), "0-4") 
        self.assertEqual(str(IntSpan.from_start_length(5, -2)), "3-4") 
        self.assertEqual(str(IntSpan.from_start_end(5, 7)), "5-7") 
        self.assertEqual(str(IntSpan.from_start_end(7, 5)), "5-7") 
        self.assertEqual(len(IntSpan.from_start_end(7, 5)), 3) 
if __name__ == "__main__":
    unittest.main()
