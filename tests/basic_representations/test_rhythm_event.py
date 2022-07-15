#!/usr/bin/env python

""" Unit test for class RhythmEvent """

import unittest

from melospy.basic_representations.rhythm_event import *


class TestRhythmEvent( unittest.TestCase ):


    def testSetOnsetSec(self):
        """ Test assures that set function for onsetSec works for valid values and throws exception for non-valid values """
        r = RhythmEvent(0)
        # valid calls
        for val in self.getValidOnsetSecValues():
            r.onsetSec = val
        # non-valid calls
        for val in self.getNonValidOnsetSecValues():
            self.assertRaises(Exception, r.setOnsetSec, val)

    def testSetDurationSec(self):
        """ Test assures that set function for durationSec works for valid values and throws exception for non-valid values """
        r = RhythmEvent(0)
        # valid calls
        for val in self.getValidDurationSecValues():
            r.onsetSec = val
        # non-valid calls
        for val in self.getNonValidDurationSecValues():
            self.assertRaises(Exception, r.setDurationSec, val)

    def testConstructor(self):
        """ Test assures that onsetSec and durationSec are set correctly if they are given as arguments to constructor """
        for onset in self.getValidOnsetSecValues():
            for duration in self.getValidDurationSecValues():
                r = RhythmEvent(onset, duration)
                self.assertEqual(r.getOnsetSec(), onset)
                self.assertEqual(r.getDurationSec(), duration)
                del r

        r = RhythmEvent(0, 1)
        self.assertEqual(r.toString(), "t:0:00:00|d:1.0")
        r = RhythmEvent(0, 1, value = "New Event")
        self.assertEqual(r.toString(), "t:0:00:00|d:1.0|val:'New Event'")
        r = RhythmEvent(0, 1, value = 3)
        self.assertEqual(r.toString(), "t:0:00:00|d:1.0|val:'3'")
        r = RhythmEvent(0, 1, value = (1, 2, 3))
        self.assertEqual(r.toString(), "t:0:00:00|d:1.0|val:'(1, 2, 3)'")
        self.assertEqual(r.getOffset(), 1.0)
        self.assertEqual(r.inSpan(.5), True)
        self.assertEqual(r.inSpan(-.5), False)
        self.assertEqual(r.inSpan(1.5), False)
        self.assertEqual(r.inSpan(0.0), True)
        self.assertEqual(r.inSpan(1.0), True)

    def testRichComparison(self):
        r1 = RhythmEvent(0, 0)
        r2 = RhythmEvent(1, 0)
        self.assertEqual(r1 == r2, False)
        self.assertEqual(r1 != r2, True)
        self.assertEqual(r1 <= r2, True)
        self.assertEqual(r1 >= r2, False)
        self.assertEqual(r1 < r2, True)
        self.assertEqual(r1 > r2, False)

        self.assertEqual(r1 == r1, True)
        self.assertEqual(r1 <= r1, True)
        self.assertEqual(r1 >= r1, True)

    def getValidOnsetSecValues(self):
        return (0, 0.121, 1.33, 1000)

    def getNonValidOnsetSecValues(self):
        return ("b")

    def getValidDurationSecValues(self):
        return (0.121, 1.33, 1000)

    def getNonValidDurationSecValues(self):
        return (-.0001, -122, "a")

if __name__ == "__main__":
    unittest.main()
