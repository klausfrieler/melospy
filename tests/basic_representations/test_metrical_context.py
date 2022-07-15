#!/usr/bin/env python

""" Unit test for class BeatInfo """

import unittest

from melospy.basic_representations.metrical_context import *


class TestMetricalContext( unittest.TestCase ):

    def testGetPeriodAndDivision(self):
        """ Test assures that period and division can be easily retrieved"""
        mi = MeterInfo(7, 8, (3, 2, 2))
        bi = BeatInfo(2, 0.5)
        mc = MetricalContext(bi, mi)
        self.assertEqual(mc.getPeriod(), 3)
        self.assertEqual(mc.getDivision(), 2)

    def testConstruction(self):
        """ Test assures that construction and setting members works fine"""
        mi = MeterInfo(8, 8, (3, 3, 2))
        bi = BeatInfo(2, 0.5)
        mc = MetricalContext(bi, mi)
        self.assertRaises(Exception, MetricalContext, mi, bi )
        self.assertRaises(Exception, mc.setBeatInfo, mi )
        #self.assertRaises(Exception, mc.setMeterInfo, bi )
        mc2 = mc.clone()
        mc.setBeatInfo(BeatInfo(3, .75))
        self.assertEqual(mc2.toString(), "2|0.5|None--3+3+2/8|3|(3, 3, 2)")
        self.assertEqual(mc2.estimateBarLengthSeconds(), 2.)
        self.assertEqual(str(mc2.getSignature()), "3+3+2/8")
        mc3 = MetricalContext(BeatInfo(2, 0.5), MeterInfo(4, 4))
        self.assertEqual(mc3.estimateBarLengthSeconds(), 2.)
        self.assertEqual(mc3.getBeatDuration(), .5)

    def testRescaling(self):
        mi = MeterInfo()
        bi = BeatInfo(2, 0.5)
        mc = MetricalContext(bi, mi).rescale(3)
        self.assertEqual(mc.getDivision(), 6)
        mc.setBeatInfo(BeatInfo(2, 0.5, (1, 1.5)))
        self.assertRaises(Exception, mc.rescale, 2)

if __name__ == "__main__":
    unittest.main()
