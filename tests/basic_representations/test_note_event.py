#!/usr/bin/env python

""" Unit test for class RhythmEvent """

import unittest

import pytest

from melospy.basic_representations.note_event import *


class TestNoteEvent( unittest.TestCase ):

    #@pytest.mark.skip(reason="Assertion mismatch")
    def testConstructor(self):
        """ Test assures that onsetSec and durationSec are set correctly if they are given as arguments to constructor """
        for pitch in self.getValidPitchValues():
            for onset in self.getValidOnsetSecValues():
                for duration in self.getValidDurationSecValues():
                    for loudness in self.getValidLoudnessValues():
                        r = NoteEvent(pitch, onset, duration, loudness)
                        self.assertEqual(r.getPitch(), pitch)
                        self.assertEqual(r.getOnsetSec(), onset)
                        self.assertEqual(r.getDurationSec(), duration)
                        self.assertEqual(r.getLoudness(), loudness)
                        del r
        n = NoteEvent(60, 0, 0)
        self.assertEqual(n.toString(), "t:0:00:00|d:0.0|p:60|vol:NA|mod:")
        self.assertEqual(str(n), "t:0:00:00|d:0.0|p:60|vol:NA|mod:")
        self.assertEqual(n.getLilypondName(), "c'")
        self.assertEqual(NoteEvent(61, 0, 0).getLilypondName(), "cis'")
        self.assertEqual(NoteEvent(61, 0, 0).getLilypondName(True), "des'")

    def testSetPitch(self):
        """ Test checks functionality of set pitch function for valid values and checks for exception throwing for non-valid pitch values """
        n = NoteEvent(60, 0, 0)
        self.assertEqual(n.transpose(5).getPitch(), 65)
        self.assertRaises(Exception, n.transpose, 68)

        # valid calls
        for pitch in self.getValidPitchValues():
            n.pitch = pitch
            self.assertEqual(pitch, n.pitch)

        # non-valid calls
        for pitch in self.getNonValidPitchValues():
            self.assertRaises(Exception, n.setPitch, pitch)

    def testSetLoudness(self):
        """ Test checks functionality of set loudness function for valid values and checks for exception throwing for non-valid pitch values """
        n = NoteEvent(60, 0, 0)
        # valid calls
        for loud in self.getValidLoudnessValues():
            n.loudness = loud
            self.assertEqual(loud, n.loudness)

        # non-valid calls
        for loud in self.getNonValidLoudnessValues():
            self.assertRaises(Exception, n.setLoudness, loud)

    def testGetLoudness(self):
        """ Test checks functionality of set loudness function for valid values and checks for exception throwing for non-valid pitch values """
        testLoud = self.getValidLoudnessValues()[2]
        n1 = NoteEvent(60, 0, 0)
        n2 = NoteEvent(60, 0, 0, testLoud)
        self.assertEqual(n1.getLoudnessField("max"), "NA")
        self.assertEqual(n1.getLoudnessField("max", "MOIN"), "MOIN")
        self.assertEqual(n2.getLoudnessField("max"), testLoud.max)
        self.assertEqual(n2.getLoudnessField("median"), "NA")
        self.assertEqual(n2.getLoudnessField("median", None), None)


    def getValidPitchValues(self):
        return (0, 10, 13, 32, 127)

    def getNonValidPitchValues(self):
        return (-1, 128, 'as')

    def getValidOnsetSecValues(self):
        return (0, 0.121, 1.33, 1000)

    def getValidLoudnessValues(self):
        return (None, Loudness(), Loudness.fromStruct([0.121]), Loudness.fromStruct({'median':1.33}))

    def getNonValidLoudnessValues(self):
        return (1, "LAUT", NoteEvent(60, 0, 0))

    def getNonValidOnsetSecValues(self):
        return ("b")

    def getValidDurationSecValues(self):
        return (0.121, 1.33, 1000)

    def getNonValidDurationSecValues(self):
        return (-.0001, -122, "a")

if __name__ == "__main__":
    unittest.main()
