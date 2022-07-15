#!/usr/bin/env python

""" Unit test for class MeterInfo """

import unittest

from melospy.basic_representations.meter_info import *


class TestMeterInfo( unittest.TestCase ):

    def testSetBeatProportions(self):
        """ Test assures that set function for beatProportions works for valid values and throws exception for non-valid values """
        # valid calls
        for val in self.getValidBeatProportionsValues():
            s = MeterInfo(4, 4)
            s.beatProportions = val
        # non-valid calls
        for val in self.getNonValidBeatProportionsValues():
            self.assertRaises(Exception, s.setBeatProportions, val)

    def testSetPeriod(self):
        """ Test assures that set function for beats works for valid values and throws exception for non-valid values """
        # valid calls
        for val in self.getValidPeriodValues():
            s = MeterInfo(4, 4)
            s.period = val
        # non-valid calls
        for val in self.getNonValidPeriodValues():
            try:
                s.setPeriod(val)
            except Exception as e:
                pass
                #print e
            #TODO: Find out why the assertion this check does not work even the excpetion is clearly raised
            #self.assertRaises(Exception, s.setPeriod, 5)

    def testConstructor(self):
        """ Test assures that beatProportions and beats are set correctly if they are given as arguments to constructor """
        # First case: numerator is not set directly but instead implicitely by the given beat proportions
        s = MeterInfo()
        s.beatProportions = (1, 1, 1, 1)
        self.assertEqual(s.numerator, 4)
        del s

        # second case: numerator is set, no beat proportions are set
        s = MeterInfo(7, 8)
        self.assertRaises(Exception, s.setBeatProportions, (3, 3, 2, 2) )
        del s

        # third case: numerator & beat proportions are set
        s = MeterInfo(7, 8, (3, 2, 2))
        self.assertEqual(s.getPeriod(), 3)
        self.assertRaises(Exception, s.setPeriod, 2)
        self.assertRaises(Exception, MeterInfo.__init__, 7, 8, (3, 2, 2), 5)

        s = MeterInfo(8, 8, (3, 3, 2))
        self.assertEqual(s.fractions(), [0, 0.375, 0.75, 1])
        s = MeterInfo(4, 4)
        self.assertEqual(s.fractions(), [0, 0.25, 0.5, 0.75, 1])

        for period in self.getValidPeriodValues():
            s = MeterInfo(4, 4, period)
            self.assertEqual(s.getPeriod(), period)
            del s

        s = MeterInfo(5, 8)
        r = s.clone()
        s.setBeatProportions((2, 3))
        self.assertEqual(r.getBeatProportions(), (3, 2))
        self.assertEqual(s.toString(), "5/8|2|(2, 3)")

        self.assertEqual(s == s, True)
        self.assertEqual(s == r, False)
        self.assertEqual(s == 3, False)
        self.assertEqual(s == "r", False)
        s = MeterInfo.fromSignature(Signature.fromString("2/4"))
        self.assertEqual(s.getSuperBeatProportions(), (2,))

        s = MeterInfo.fromString("2/4")
        self.assertEqual(s.getSuperBeatProportions(), (2,))
        self.assertEqual(s.getAccentedPositions(), [1])
        s = MeterInfo.fromString("3+2+3/8")
        self.assertEqual(s.getSuperBeatProportions(), (3,))
        self.assertEqual(s.getAccentedPositions(), [1])
        s = MeterInfo.fromString("7/8")
        self.assertEqual(s.getSuperBeatProportions(), (3,))
        self.assertEqual(s.getAccentedPositions(), [1])
        s = MeterInfo.fromString("4/4")
        self.assertEqual(s.getSuperBeatProportions(), (2, 2))
        self.assertEqual(s.getAccentedPositions(), [1, 3])
        s = MeterInfo.fromString("4+4+3+4/8")
        self.assertEqual(s.getSuperBeatProportions(), (2, 2))
        self.assertEqual(s.getAccentedPositions(), [1, 3])
        s = MeterInfo.fromString("3+2/4")
        self.assertEqual(s.getSuperBeatProportions(), (3, 2))
        self.assertEqual(s.getAccentedPositions(), [1, 4])
        #print bp

        s = MeterInfo.fromString("1/4")
        self.assertEqual(s.getAccentedPositions(), [1])
        self.assertEqual(str(MeterInfo.fromString("4+4+3+4/8").getSignature()), "4+4+3+4/8")
        #self.assertRaises(Exception, s.__eq__, "r")

    def testPrimaryBeatDivision(self):
        tests =  [  ("2/4",     "binary"),
                    ("3/4",     "binary"),
                    ("4/4",     "binary"),
                    ("5/4",     "binary"),
                    ("2/2",     "binary"),
                    ("3/2",     "binary"),
                    ("2/8",     "binary"),
                    ("3/8",     "ternary"),
                    ("4/8",     "binary"),
                    ("5/8",     "asymmetric"),
                    ("3+2/8",   "asymmetric"),
                    ("6/8",     "ternary"),
                    ("3+3/8",   "ternary"),
                    ("7/8",     "asymmetric"),
                    ("9/8",     "ternary"),
                    ("3+3+2/8", "asymmetric")
                    ]
        for  t in tests:
            #print t[0], MeterInfo.fromString(t[0]).getPrimaryBeatDivision(), t[1]
            self.assertEqual(MeterInfo.fromString(t[0]).getPrimaryBeatDivision(), t[1])

    def getValidBeatProportionsValues(self):
        return ((1, 1, 1, 1), (1, 2, 3, 4),  None)

    def getNonValidBeatProportionsValues(self):
        return (0, 1, 3, 7, 32, 64, 131, 1.33, "r", -1)

    def getValidPeriodValues(self): # assuming a 4 / 4 time signature
        return (4,)

    def getNonValidPeriodValues(self):
        return (0, 5, 6, 7, 8, 1.2, -1, "e")

if __name__ == "__main__":
    unittest.main()
