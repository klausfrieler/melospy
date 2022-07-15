#!/usr/bin/env python

""" Unit test for class AnnotatedBeatEvent """

import unittest

import pytest

from melospy.basic_representations.annotated_beat_event import *


class TestAnnotatedBeatEvent( unittest.TestCase ):

    #@pytest.mark.skip(reason="Assertion mismatch")
    def testConstructorAndMembers(self):
        """ Test assures that constructor works correctly"""
        #Four quarter signature, period = 4, equal beat proportions
        mi = MeterInfo(4, 4)
        #four sixteenth per Beat, .5 sec per beat = 120 bpm
        bi = BeatInfo(4, .5)
        mc = MetricalContext(bi, mi)
        mp = MetricalPosition(1, 1, 1, 0, mc)
        bass_pitch = 36
        form = FormName("*A1")
        chord = Chord("C+j711#")
        abe  = AnnotatedBeatEvent(0, mp, form, chord, bass_pitch)
        self.assertEqual(abe.getFormString(), "*A1")
        self.assertEqual(str(abe), "t:0:00:00|d:0.5|val:'C+j7911#'|pos:4.4.1.1.1|C+j7911#|36|A1|")
        self.assertEqual(str(abe.toMetricalEvent()), "t:0:00:00|d:0.5|val:'C+j7911#'|pos:4.4.1.1.1|dtat:4.0")
        abe  = AnnotatedBeatEvent(0)
        self.assertEqual(str(abe), "t:0:00:00|d:0.0|pos:NA||||")
        self.assertEqual(abe.toMetricalEvent(), None)

if __name__ == "__main__":
    unittest.main()
