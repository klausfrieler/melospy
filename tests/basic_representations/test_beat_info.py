#!/usr/bin/env python

""" Unit test for class BeatInfo """

import unittest

from melospy.basic_representations.beat_info import *


class TestBeatInfo( unittest.TestCase ):

#           self.__tatums = None
#        self.__beatDurationSec = None
#        self.__tatumProportion = None


    def testSetTatums(self):
        """ Test assures that set function for tatums works for valid values and throws exception for non-valid values """
        s = BeatInfo()
        # valid calls
        for val in self.getValidTatumsValues():
            s.tatums = val
        # non-valid calls
        for val in self.getNonValidTatumsValues():
            self.assertRaises(Exception, s.setTatums, val)

        #test rescaling
        s = BeatInfo(2, 0.5, (1, 1.5))
        self.assertEqual(s.hasEqualProportions(), False)
        self.assertRaises(Exception, s.rescale, 2)

        s = BeatInfo(2)
        self.assertEqual(s.hasEqualProportions(), True)
        s.rescale(2)
        self.assertEqual(s.getTatums(), 4)

        s = BeatInfo(2, .5, (1, 1.75))
        s.rescale(2, True)
        self.assertEqual(s.getTatums(), 4)

        s = BeatInfo(4, .5, (1, 1.75, 1, 1.5))
        s.rescale(2, True, upscale = False)
        self.assertEqual(s.getTatums(), 2)

    def testSetBeatDurationSec(self):
        """ Test assures that set function for beatDurationSec works for valid values and throws exception for non-valid values """
        s = BeatInfo()
        # valid calls
        for val in self.getValidBeatDurationSecValues():
            s.beatDurationSec = val
        # non-valid calls
        for val in self.getNonValidBeatDurationSecValues():
            self.assertRaises(Exception, s.setBeatDurationSec, val)

    def testSetTatumProportion(self):
        """ Test assures that set function for tatumProportion works for valid values and throws exception for non-valid values """
        s = BeatInfo()
        # valid calls
        for val in self.getValidTatumProportionValues():
            s = BeatInfo(len(val))
            s.tatumProportion = val
            del s
        # non-valid calls
        #BeatInfo(2, .5).setTatumProportions, (1,1, 1)
        self.assertRaises(Exception, BeatInfo(2, .5).setTatumProportions, (1, 1, 1))

        s = BeatInfo()
        for val in self.getNonValidTatumProportionValues():
            self.assertRaises(Exception, s.setTatumProportions, val)

    def testConstructor(self):
        """ Test assures that onsetSec and durationSec are set correctly if they are given as arguments to constructor """
        s = BeatInfo(1, .5, (1,))
        self.assertEqual(s.getTatums(), 1)
        self.assertEqual(s.getBeatDurationSec(), .5)
        self.assertEqual(s.getTatumProportions(), (1,))

        s = BeatInfo(2, .25, (1, 1.5))
        self.assertEqual(s.getTatums(), 2)
        self.assertEqual(s.getBeatDurationSec(), .25)
        self.assertEqual(s.getTatumProportions(), (1, 1.5))
        self.assertEqual(s.toString(), "2|0.25|(1, 1.5)")

        d = BeatInfo(4, .25, (1, 2, 3, 4))
        self.assertEqual(d.fractions(), [0, 0.1, 0.3, 0.6, 1])

        d = BeatInfo(4, .5)
        self.assertEqual(d.fractions(), [0, 0.25, 0.5, 0.75, 1])

        self.assertEqual(d == d, True)
        self.assertEqual(d == s, False)
        self.assertEqual(d == "s", False)
        self.assertEqual(d == None, False)
        self.assertEqual(d == 3, False)
        #self.assertRaises(Exception, s.__eq__, "e")

        #self.assertRaises(Exception, BeatInfo.__init__, s, 2.1, 0.5)
        self.assertRaises(Exception, BeatInfo.__init__, s, 2, -0.5)
        self.assertRaises(Exception, BeatInfo.__init__, s, 2, 0.5, (1, 1, 1))
        self.assertRaises(Exception, BeatInfo.__init__, s, 2, 0.5, -1)
        self.assertRaises(Exception, BeatInfo.__init__, s, "r", 0.5)
        self.assertRaises(Exception, BeatInfo.__init__, s, 2, "r")
        self.assertRaises(Exception, BeatInfo.__init__, s, 2, 0.5, "r")

        r = s.clone()
        s.setBeatDurationSec(1)
        self.assertEqual(r.getBeatDurationSec(), 0.5)

    def getValidTatumsValues(self):
        return (1, 2, 3)

    def getNonValidTatumsValues(self):
        return (0, "r", -1)

    def getValidBeatDurationSecValues(self):
        return (2, 4.11, 8.1, 16.1221)

    def getNonValidBeatDurationSecValues(self):
        return (-1, 'e')

    def getValidTatumProportionValues(self):
        return ((1,), (1, 1.5, 1), (1.3, 1))

    def getNonValidTatumProportionValues(self):
        return ( "r", -1)

if __name__ == "__main__":
    unittest.main()
