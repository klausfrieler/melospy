#!/usr/bin/env python

""" Unit test for class Signature """

import unittest

from melospy.basic_representations.signature import *


class TestSignature( unittest.TestCase ):

    def testSetNumerator(self):
        """ Test assures that set function for meterNumerator works for valid values and throws exception for non-valid values """
        s = Signature.fromString("4/4")
        # valid calls
        for val in self.getValidMeterNumeratorValues():
            s.numerator = val
        # non-valid calls
        for val in self.getNonValidMeterNumeratorValues():
            self.assertRaises(Exception, s.setNumerator, val)

    def testSetMeterDenominator(self):
        """ Test assures that set function for meterDenominator works for valid values and throws exception for non-valid values """
        s = Signature.fromString("4/4")

        # valid calls
        for val in self.getValidMeterDenominatorValues():
            s.denominator = val
        # non-valid calls
        for val in self.getNonValidMeterDenominatorValues():
            self.assertRaises(Exception, s.setDenominator, val)

    def testSetPartition(self):
        """ Test assures that set function for meterDenominator works for valid values and throws exception for non-valid values """
        s = Signature.fromString("7/4")
        self.assertRaises(Exception, s.setPartition, [3, 3, 2])
        self.assertRaises(Exception, s.setPartition, [17])

    def testBeatProportions(self):
        """ Test assures that set function
            for meterDenominator works for valid values and throws
            exception for non-valid values
        """
        s = Signature.fromString("4/4")
        period, bp = s.getMeterInfo()
        self.assertEqual(period, 4)
        self.assertEqual(bp, None)

        s = Signature.fromString("4/8")
        period, bp = s.getMeterInfo()
        self.assertEqual(period, 2)
        self.assertEqual(bp, None)

        s = Signature.fromString("5/8")
        period, bp = s.getMeterInfo()
        self.assertEqual(period, 2)
        self.assertEqual(bp, (3, 2))

    def testPrimaryBeatDivision(self):
        tests   = ["2/4",    "3/4",    "4/4",    "5/4",    "2/2",    "3/2",
                   "2/8",    "3/8",    "4/8",    "5/8",    "3+2/8",      "6/8",
                   "3+3/8",   "7/8",    "9/8",     "3+3+2/8"]
        results = ["binary", "binary", "binary", "binary", "binary", "binary",
                   "binary", "ternary", "binary", "binary", "asymmetric", "ternary",
                   "ternary", "binary", "ternary", "asymmetric"]
        beat_factors = [1., 1., 1., 1., 2., 2.,
                        1, 1.5, 1, 1, None, 1.5,
                        1.5, 1, 1.5, None]
        beat_factors_fraction = [Fraction(1), Fraction(1),
                                 Fraction(1), Fraction(1), Fraction(2), Fraction(2),
                                 Fraction(1), Fraction(3, 2),
                                 Fraction(1), Fraction(1), None, Fraction(3, 2),
                                 Fraction(3, 2), Fraction(1), Fraction(3, 2), None]
        quarter_lengths = [2., 3., 4., 5., 4., 6.,
                        1, 1.5, 2, 2.5, 2.5, 3,
                        3, 3.5, 4.5, 4]
        for i, t in enumerate(tests):
            self.assertEqual(Signature.fromString(t).getPrimaryBeatDivision(), results[i])
            if results[i] != "asymmetric":
                self.assertEqual(Signature.fromString(t).getBeatFactor(True), beat_factors[i])
            if results[i] != "asymmetric":
                self.assertEqual(Signature.fromString(t).getBeatFactor(True, as_fraction=True), beat_factors_fraction[i])
            self.assertEqual(Signature.fromString(t).getQuarterLength(True), quarter_lengths[i])
            self.assertEqual(Signature.fromString(t).getQuarterLength(as_fraction=True), Fraction(quarter_lengths[i]))
          #print "t:{}, div:{}".format(t,Signature.fromString(t).getPrimaryBeatDivision())

    def testConstructor(self):
        """ Test assures that onsetSec and durationSec are set correctly if they are given as arguments to constructor """
        for meterNumerator in self.getValidMeterNumeratorValues():
            for meterDenominator in self.getValidMeterDenominatorValues():
                s = Signature(meterNumerator, meterDenominator)
                self.assertEqual(s.getNumerator(), meterNumerator)
                self.assertEqual(s.getDenominator(), meterDenominator)
                del s
        s = Signature.fromString("7/8")
        self.assertEqual(s.toString(), "7/8")
        s1 = s.clone()
        self.assertEqual(s1.toString(), "7/8")
        s = Signature.fromString("3+2+2/8")
        self.assertEqual(s.toString(), "3+2+2/8")
        self.assertEqual(s.getNumerator(), 7)
        self.assertEqual(s.getDenominator(), 8)


    def getValidMeterNumeratorValues(self):
        return (1, 2, 4, 9)

    def getNonValidMeterNumeratorValues(self):
        return ( 1.33, "r", -1)

    def getValidMeterDenominatorValues(self):
        return (2, 4, 8, 16, 64, 256)

    def getNonValidMeterDenominatorValues(self):
        return (0, 1, 3, 7, 131, 1.33, "r", -1)

if __name__ == "__main__":
    unittest.main()
