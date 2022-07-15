#!/usr/bin/env python

""" Unit test for class MetricalEvent """

import unittest

from melospy.basic_representations.metrical_event import *


class TestMetricalEvent( unittest.TestCase ):

    def testConstructorAndMembers(self):
        """ Test assures that constructor works correctly"""
        #Four quarter signature, period = 4, equal beat proportions
        mi = MeterInfo(4, 4)
        #four sixteenth per Beat, 1 sec per beat = 60 bpm
        bi = BeatInfo(4, .5)
        mc = MetricalContext(bi, mi)
        mp = MetricalPosition(1, 2, 3, 0, mc)

        me = MetricalEvent(0, mp, 1.0/2, None)
        self.assertRaises(Exception, MetricalEvent.__init__, "r", mp, 1, None, None)
        self.assertRaises(Exception, MetricalEvent.__init__, 0, mi, 1., None, None)
        self.assertRaises(Exception, MetricalEvent.__init__, 0, mp, -1., None, None)
        self.assertRaises(Exception, MetricalEvent.__init__, 0, mp, 1., 2.3, None)
        self.assertRaises(Exception, MetricalEvent.__init__, 0, mp, 1., None, 3.0)

        self.assertEqual(me.getOnsetSec(), 0)
        self.assertEqual(me.getDurationSec(), 1.0/2)
        self.assertEqual(me.getMetricalContext(), mc)
        self.assertEqual(me.getDurationTatum(), 4)
        self.assertEqual(me.getBeatDuration(), .5)
        self.assertEqual(me.getSignature(), mi.getSignature())
        self.assertEqual(me.getTempoBPM(), 120.0)
        self.assertEqual(me.toString(), "t:0:00:00|d:0.5|pos:4.4.1.2.3|dtat:4.0")
        self.assertEqual(me.getBar(), 1)
        self.assertEqual(me.getBeat(), 2)
        self.assertEqual(me.getTatum(), 3)
        self.assertEqual(me.getSubtatum(), 0)
        self.assertEqual(me.getMeterInfo()== mi, True)
        self.assertEqual(me.getBeatInfo() == bi, True)
        self.assertEqual(me.rescale(16).getTatum(), 9)

    def testRichComparison(self):
        """ Test assures that constructor works correctly"""
        #Four quarter signature, period = 4, equal beat proportions
        mi = MeterInfo(4, 4)
        #four sixteenth per Beat, 1 sec per beat = 60 bpm
        bi = BeatInfo(4, .5)
        mc = MetricalContext(bi, mi)

        mp1 = MetricalPosition(1, 2, 3, 0, mc)
        me1 = MetricalEvent(0, mp1, 1.0/2, None)

        mp2 = MetricalPosition(1, 2, 2, 0, mc)
        me2 = MetricalEvent(0.5, mp2, 1.0/2, None)
        self.assertEqual(me1<=me2, True)
        self.assertEqual(me1.getMetricalPosition() < me2.getMetricalPosition(), False)
if __name__ == "__main__":
    unittest.main()
