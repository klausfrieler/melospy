#!/usr/bin/env python

""" Unit test for class SloppyDate """

#from section import *
import unittest

from melospy.basic_representations.sloppy_date import *


class TestSloppyDate( unittest.TestCase ):

    def testConstructor(self):
        s = SloppyDate(2013, 2, 1)
        self.assertEqual(str(s), "01.02.2013")
        self.assertEqual(s.getYear(), 2013)
        self.assertEqual(s.getMonth(), 2)
        self.assertEqual(s.getDay(), 1)

        s = SloppyDate(2013, 2)
        self.assertEqual(str(s), "Feb 2013")
        self.assertEqual(s.getYear(), 2013)
        self.assertEqual(s.getMonth(), 2)
        self.assertEqual(s.getDay(), None)

        s = SloppyDate(2013)
        self.assertEqual(str(s), "2013")
        self.assertEqual(s.getYear(), 2013)
        self.assertEqual(s.getMonth(), None)
        self.assertEqual(s.getDay(), None)

        s = SloppyDate.fromString("01.02.2013")
        self.assertEqual(str(s), "01.02.2013")
        self.assertEqual(s.getYear(), 2013)
        self.assertEqual(s.getMonth(), 2)
        self.assertEqual(s.getDay(), 1)

        s = SloppyDate.fromString("02.2013")
        self.assertEqual(str(s), "Feb 2013")
        self.assertEqual(s.getYear(), 2013)
        self.assertEqual(s.getMonth(), 2)
        self.assertEqual(s.getDay(), None)

        s = SloppyDate.fromString("2013")
        self.assertEqual(str(s), "2013")
        self.assertEqual(s.getYear(), 2013)
        self.assertEqual(s.getMonth(), None)
        self.assertEqual(s.getDay(), None)


        self.assertRaises(Exception, SloppyDate.fromString, "018.234.20135")
        self.assertRaises(Exception, SloppyDate.fromString, "01-23-2013")
        self.assertRaises(Exception, SloppyDate.fromString, "01.23.2013")

        #s = SloppyDate.fromString("")
        #print len(str(s))
        self.assertRaises(Exception, SloppyDate.__init__, None, 1, -1)
        self.assertRaises(Exception, SloppyDate.__init__, None, 1, None)
        self.assertRaises(Exception, SloppyDate.__init__, None, None, 1)
        self.assertRaises(Exception, SloppyDate.__init__, 2013, 1, -1)
        self.assertRaises(Exception, SloppyDate.__init__, 2013, None, 1)
        self.assertRaises(Exception, SloppyDate.__init__, "r", 2, 1)
        self.assertRaises(Exception, SloppyDate.__init__, 1789, 2, 1)
if __name__ == "__main__":
    unittest.main()
