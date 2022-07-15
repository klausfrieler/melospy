#!/usr/bin/env python

""" Unit test for class Section """

import unittest

from melospy.basic_representations.chord import *
from melospy.basic_representations.key import *
from melospy.basic_representations.scale import *
from melospy.basic_representations.section import *


class TestSection( unittest.TestCase ):

    def testConstructor(self):
        n = NoteName("Ab")
        k = Key("Ab", 'maj')
        c = Chord("Caug13b")
        # test with valid initialization
        s = Section("KEY", k, 1, 2)
        self.assertEqual(s.getType(), "KEY")
        s = Section("FORM", FormName("A1"), 1, 2)
        self.assertEqual(s.getType(), "FORM")
        s = Section("PHRASE", 1, 1, 2)
        self.assertEqual(s.getType(), "PHRASE")
        s = Section("CHORUS", 1, 1, 2)
        self.assertEqual(s.getType(), "CHORUS")
        s = Section("chord", c, 1, 20)
        self.assertEqual(s.getType(), "CHORD")

        self.assertEqual(str(s.getValue()), "C+7913b")
        self.assertEqual(len(s), 20)

        r = s.clone()
        self.assertEqual(len(s), len(r))
        self.assertEqual(str(s), str(r))

        s = Section("PHRASE", 1, 1, 1)


        # test with non-valid initialization
        self.assertRaises(Exception, s.__init__, "INVALID", 1, 2)
        self.assertRaises(Exception, s.__init__, None, 1, 2)
        self.assertRaises(Exception, s.__init__, "KEY", 2, 1)
        self.assertRaises(Exception, s.__init__, "KEY", None, 1)
        self.assertRaises(Exception, s.__init__, "KEY", 1, None)
        self.assertRaises(Exception, s.__init__, "KEY", 1.0, 2.0)

    def testMethods(self):
        k = Key("Ab", 'maj')
        c = Chord("Caug13b")

        # test with valid initialization
        s = Section("KEY", k, 1, 2)
        self.assertRaises(Exception, s.type, 1, 1.0, 2.0)
        self.assertRaises(Exception, s.startID, 1.0, 1.0, 2.0)
        self.assertRaises(Exception, s.endID, 1.0, 1.0, 2.0)
        self.assertRaises(Exception, s.value, 1.0, 1.0, 2.0)

        s = Section("KEY", k, 1, 10)
        self.assertRaises(Exception, s.clone().snip, 0, 7)
        self.assertRaises(Exception, s.clone().snip, 1, 17)
        self.assertEqual(s.clone().snip(3, 7).getEndID(), 7)
        self.assertEqual(s.clone().snip(3, 7).getStartID(), 3)
        self.assertEqual(s.clone().snip(3, 7).type, "KEY")
        self.assertEqual(s.clone().snip(3, 7).value, k)
        self.assertEqual(s.clone().shiftIDs(5).startID, 6)
        self.assertEqual(s.clone().shiftIDs(-1).startID, 0)
        self.assertEqual(s.clone().shiftIDs(5).endID, 15)
        self.assertEqual(s.clone().shiftIDs(-1).endID, 9)
        self.assertRaises(Exception, s.clone().shiftIDs, -5)

if __name__ == "__main__":
    unittest.main()
