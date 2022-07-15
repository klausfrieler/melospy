#!/usr/bin/env python

""" Unit test for class CompositionInfo"""

import unittest

from melospy.basic_representations.composition_info import *


class TestCompositionInfo( unittest.TestCase ):

    def testConstructor(self):

        ci = CompositionInfo("All the Things You Are", "Johnny Mercer", [("A1", 8), ("A2", 8), ("B1", 8), ("A3", 8)], "Functional", "Great American Songbook", "All the Things You Are")
        #print ci
        # test with valid initialization
        self.assertEqual(ci.getTitle(), "All the Things You Are")
        self.assertEqual(ci.getComposer(), "Johnny Mercer")
        self.assertEqual(str(ci.getForm()), FormDefinition([("A1", 8), ("A2", 8), ("B1", 8), ("A3", 8)]).getShortForm(withLengths=True))
        self.assertEqual(ci.getTonalityType(), "FUNCTIONAL")
        self.assertEqual(ci.getGenre(), "GREAT AMERICAN SONGBOOK")
        self.assertEqual(ci.getHarmonyTemplate(), "All the Things You Are")
        cic =  ci.clone()
        cic.composer = "Donald Duck"
        self.assertEqual(ci.getComposer(), "Johnny Mercer")
        self.assertEqual(cic.getComposer(), "Donald Duck")

        #ci = CompositInfo("John Coltrane")
        # test with non-valid initialization
        #self.assertRaises(Exception, ci.__init__, 1)
        #self.assertRaises(Exception, ci.__init__, "www.saxsolo.de", 2.)
        self.assertRaises(Exception, ci.__init__, "www.saxsolo.de", "SCAN", 3. )
        self.assertRaises(Exception, ci.__init__, "www.saxsolo.de", "SCAN", [1, 2, 3] )
        self.assertRaises(Exception, ci.__init__, "www.saxsolo.de", "SCAN", [("AA1", 8), ("A2", 8), ("B1", 8), ("A3", 8)] )
        self.assertRaises(ValueError, ci.__init__, "www.saxsolo.de", "SCAN", [("A1", 8.3), ("A2", 8), ("B1", 8), ("A3", 8)] )
        self.assertRaises(ValueError, ci.__init__, "www.saxsolo.de", "SCAN", [("Z1", 8), ("A2", 8), ("B1", 8), ("A3", 8)] )
        self.assertRaises(ValueError, ci.__init__, "www.saxsolo.de", "SCAN", [("A1", 8), ("A3", 8), ("B1", 8), ("A3", 8)] )
        self.assertRaises(ValueError, ci.__init__, "www.saxsolo.de", "SCAN", [("A1", 8), ("A''2", 8), ("B1", 8), ("A3", 8)] )
        self.assertRaises(ValueError, ci.__init__, "www.saxsolo.de", "SCAN", [("A1", 8), ("A2", 8), ("C1", 8), ("A3", 8)] )
        self.assertRaises(ValueError, ci.__init__, "www.saxsolo.de", "SCAN", [("A", 8), ("A2", 8), ("B1", 8), ("A3", 8)] )
        self.assertRaises(ValueError, ci.__init__, "www.saxsolo.de", "SCAN", [("AC1", 8), ("A2", 8), ("B1", 8), ("A3", 8)] )
        self.assertRaises(ValueError, ci.setTonalityType, "BLUE")
        self.assertRaises(ValueError, ci.setTonalityType, "BLUE")
        self.assertRaises(ValueError, ci.setGenre, "ABC")

if __name__ == "__main__":
    unittest.main()
