#!/usr/bin/env python

""" Unit test for class SoloMetaData"""

import unittest

from melospy.basic_representations.solo_meta_data import *


class TestSoloMetaData( unittest.TestCase ):

    def testConstructor(self):
        si = SoloInfo(1, "John Coltrane", "Giant Steps", "Alternate Take",  1, "ts", 240.3, "Up", "Hardbop", "Swing", "2/2", False, Key("B", "maj"))
        ri = RecordInfo("John Coltrane", "Giant Steps", "Impulse", "I2012", 1, "Impulse:John Coltrane;bs: Reggie Workman;dr: Elvin Jones;p: Paul Flanagan", "02.04.1959", "09.1958")
        ti = TranscriptionInfo("www.saxsolo.de", "SCAN", "Mr. X", "Klaus Frieler", "02.04.2013", "PREFINAL", "JohnColtrane_GiantSteps.wav", "JohnColtrane_GiantSteps_Solo.wav", "JohnColtrane_GiantSteps_FINAL.sv", 126, 267)
        ci = CompositionInfo("All the Things Your Are", "Johnny Mercer", [("A1", 8), ("A2", 8), ("B1", 8), ("A3", 8)])

        smd = SoloMetaData(si, ri, ti, ci)
        smd_c = smd.clone()
        smd_c.setField("title", "Nonsense")
        self.assertEqual(smd.getField("title"), "Giant Steps")
        self.assertEqual(smd_c.getField("title"), "Nonsense")
        self.assertEqual(smd.getSoloInfo(), si)
        self.assertEqual(smd.getRecordInfo(), ri)
        self.assertEqual(smd.getTranscriptionInfo(), ti)
        self.assertEqual(smd.getCompositionInfo(), ci)
        si = smd.getSubInfo("SoloInfo")
        self.assertEqual(smd.getSubInfo("SoloInfo"), si)
        self.assertEqual(smd.getSubInfo("RecordInfo"), ri)
        self.assertEqual(smd.getSubInfo("TranscriptionInfo"), ti)
        self.assertEqual(smd.getSubInfo("CompositionInfo"), ci)
        self.assertEqual(smd.getField("filenamesv"), "JohnColtrane_GiantSteps_FINAL.sv")
        self.assertEqual(smd.setField("filenamesv", "DUMMY").getField("filenamesv"), "DUMMY")
        self.assertRaises(TypeError, smd.__init__, ri, si, ti, ci)
        self.assertRaises(TypeError, smd.__init__, 0, si, ti, ci)
        self.assertRaises(TypeError, smd.__init__, ri, 0, ti, ci)
        self.assertRaises(TypeError, smd.__init__, ri, si, 0, ci)
        self.assertRaises(TypeError, smd.__init__, ri, si, ti, 0)
        smd = SoloMetaData(None, None, None, ci)
        self.assertEqual(smd.getSoloInfo(), None)
        self.assertEqual(smd.getCompositionInfo(), ci)
        #print smd
if __name__ == "__main__":
    unittest.main()
