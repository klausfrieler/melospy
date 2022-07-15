#!/usr/bin/env python

""" Unit test for class MetricalEvent """

import unittest

import pytest

from melospy.basic_representations.metrical_note_event import *


class TestMetricalNoteEvent( unittest.TestCase ):

    #@pytest.mark.skip(reason="Assertion mismatch")
    def testConstructorAndMembers(self):
        """ Test assures that constructor works correctly"""
        #Four quarter signature, period = 4, equal beat proportions
        mi = MeterInfo(4, 4)
        #four sixteenth per Beat, .5 sec per beat = 120 bpm
        bi = BeatInfo(4, .5)
        mc = MetricalContext(bi, mi)
        mp = MetricalPosition(1, 2, 3, 0, mc)
        C4 = 60
        mne = MetricalNoteEvent(0, C4, mp, 1.0/3, None)
        self.assertRaises(Exception, MetricalNoteEvent.__init__, "r", C4, mp, 1, None, None)
        self.assertRaises(Exception, MetricalNoteEvent.__init__, 0, "invalid", mp, 1, None, None)
        self.assertRaises(Exception, MetricalNoteEvent.__init__, 0, C4, mi, 1., None, None)
        self.assertRaises(Exception, MetricalNoteEvent.__init__, 0, C4, mp, -1., None, None)
        self.assertRaises(Exception, MetricalNoteEvent.__init__, 0, C4, mp, 1., 2.3, None)
        self.assertRaises(Exception, MetricalNoteEvent.__init__, 0, C4, mp, 1., None, 3.0)
        self.assertEqual(mne.getPitch(), C4)
        self.assertEqual(mne.setPitch(C4+12).getPitch(), C4+12)
        self.assertEqual(mne.setOnsetSec(10).getOnsetSec(), 10)
        self.assertEqual(mne.setDurationSec(10).getDurationSec(), 10)
        self.assertEqual(mne.getMetricalContext(), mc)
        self.assertEqual(mne.setDurationSec(.25).getDurationTatum(), 2)
        self.assertEqual(mne.getTempoBPM(), 120.0)
        self.assertEqual(mne.toString(), "t:0:00:10|d:0.25|pos:4.4.1.2.3|dtat:2.0|p:72|vol:NA|mod:")

        ne = NoteEvent(60, 0, 0.5)
        me = MetricalEvent(0.5, mp, 1.0/4, None)
        mne = MetricalNoteEvent.fuse(ne, me, 1)

        self.assertEqual(mne.toString(), "t:0:00:00|d:0.5|pos:4.4.1.2.3|dtat:2.0|p:60|vol:NA|mod:")

        mne = MetricalNoteEvent.fuse(ne, me, 2)
        self.assertEqual(mne.toString(), "t:0:00:00.500000|d:0.25|pos:4.4.1.2.3|dtat:2.0|p:60|vol:NA|mod:")

        mne = MetricalNoteEvent.fuse(ne, me, 3)
        self.assertEqual(mne.toString(), "t:0:00:00|d:0.5|pos:4.4.1.2.3|dtat:2.0|p:60|vol:NA|mod:")
        self.assertEqual(mne.estimateMetricalDurationDecimal(), .25)
        self.assertEqual(float(mne.estimateBeatDurationFractional()), 1)
        self.assertEqual(mne.estimateQuarterDuration(), 1)
        mne.duration = mne.duration/2
        self.assertEqual(mne.estimateMetricalDurationDecimal(), .125)
        self.assertEqual(float(mne.estimateBeatDurationFractional()), .5)
        self.assertEqual(mne.estimateQuarterDuration(), Fraction(1, 2))
        mne.duration = mne.duration/2
        self.assertEqual(mne.estimateMetricalDurationDecimal(), .0625)
        self.assertEqual(float(mne.estimateBeatDurationFractional()), .25)
        self.assertEqual(mne.estimateQuarterDuration(), Fraction(1, 4))

        #print mne.getMeterInfo()
        mi = MeterInfo(6, 8)
        #four sixteenth per Beat, .5 sec per beat = 120 bpm
        bi = BeatInfo(4, .5)
        mc = MetricalContext(bi, mi)
        mp = MetricalPosition(1, 1, 3, 0, mc)

        mne.setMetricalPosition(mp)
        mne.duration = .5
        #print mne.getBeatFactor()
        #print mne.getMeterInfo().getBeatFactor()
        #print mne.duration/.5
        #print mne.estimateQuarterDuration()

if __name__ == "__main__":
    unittest.main()
