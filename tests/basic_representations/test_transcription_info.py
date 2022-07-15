#!/usr/bin/env python

""" Unit test for class TranscriptionInfo"""

import unittest

from melospy.basic_representations.transcription_info import *


class TestTranscriptionInfo( unittest.TestCase ):

    def testConstructor(self):

        ti = TranscriptionInfo("www.saxsolo.de", "SCAN", "Mr. X", "Klaus Frieler", "02.04.2013", "FINAL", "JohnColtrane_GiantSteps.wav", "JohnColtrane_GiantSteps_Solo.wav", "JohnColtrane_GiantSteps_FINAL.sv", 126, 267)
        #print ti
        # test with valid initialization
        self.assertEqual(ti.getSource(), "www.saxsolo.de")
        self.assertEqual(ti.getTranscriber(), "Mr. X")
        for st in SOURCE_TYPES:
              self.assertEqual(ti.setSourceType(st).getSourceType(), st)
        self.assertEqual(ti.getCoder(), "Klaus Frieler")
        self.assertEqual(ti.getDateOfCoding(), SloppyDate.fromString("02.04.2013"))
        for ts in TRANSCRIPTION_STATUS:
              self.assertEqual(ti.setStatus(ts).getStatus(), ts)
        self.assertEqual(ti.getFileNameSV(), "JohnColtrane_GiantSteps_FINAL.sv")
        self.assertEqual(ti.getFileNameTrack(), "JohnColtrane_GiantSteps.wav")
        self.assertEqual(ti.getFileNameSolo(), "JohnColtrane_GiantSteps_Solo.wav")
        self.assertEqual(ti.getSoloStartSec(), 126)
        self.assertEqual(ti.getSoloEndSec(), 267)

        self.assertRaises(ValueError, ti.setStatus, "ASJHGd")
        #self.assertRaises(ValueError, ti.setSourceType, "ASJHGd")
        #ti = RecordInfo("John Coltrane")
        # test with non-valid initialization
        #self.assertRaises(Exception, ti.__init__, 1)
        #self.assertRaises(Exception, ti.__init__, "www.saxsolo.de", 2.)
        #self.assertRaises(Exception, ti.__init__, "www.saxsolo.de", "SCAN")
        #self.assertRaises(Exception, ti.__init__, "www.saxsolo.de", "SCAN", "Mr. X", 4)
        #self.assertRaises(Exception, ti.__init__, "www.saxsolo.de", "SCAN", "Mr. X", 5.)
        #self.assertRaises(Exception, ti.__init__, "www.saxsolo.de", "SCAN", "Mr. X", "Klaus Frieler", 6.)
        #self.assertRaises(Exception, ti.__init__, "www.saxsolo.de", "SCAN", "Mr. X", "Klaus Frieler", "003.23.2012")
        #self.assertRaises(Exception, ti.__init__, "www.saxsolo.de", "SCAN", "Mr. X", "Klaus Frieler", "02.04.2013", 7.)
        #self.assertRaises(Exception, ti.__init__, "www.saxsolo.de", "SCAN", "Mr. X", "Klaus Frieler", "02.04.2013", "TBC", 8.)
        #self.assertRaises(Exception, ti.__init__, "www.saxsolo.de", "SCAN", "Mr. X", "Klaus Frieler", "02.04.2013", "TBC", "JohnColtrane_GiantSteps.wav", 9.)
        #self.assertRaises(Exception, ti.__init__, "www.saxsolo.de", "SCAN", "Mr. X", "Klaus Frieler", "02.04.2013", "TBC", "JohnColtrane_GiantSteps.wav", "JohnColtrane_GiantSteps_solo.wav", "10")
        #self.assertRaises(Exception, ti.__init__, "www.saxsolo.de", "SCAN", "Mr. X", "Klaus Frieler", "02.04.2013", "TBC", "JohnColtrane_GiantSteps.wav", "JohnColtrane_GiantSteps_solo.wav", 126, "r")

if __name__ == "__main__":
    unittest.main()
