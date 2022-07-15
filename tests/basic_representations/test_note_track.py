#!/usr/bin/env python

""" Unit test for class RhythmEvent """

import unittest

import pytest

from melospy.basic_representations.metrical_note_event import *
from melospy.basic_representations.note_track import *


class TestNoteTrack( unittest.TestCase ):

    #@pytest.mark.skip(reason="Assertion mismatch")
    def testConstructor(self):
        """ Test assures constructor works properly"""
        C4 = 60
        C5 = C4 + 12
        e  = NoteEvent(C4,   0.0, 1)
        e1 = NoteEvent(C4+2, 0.1, 1)
        e2 = NoteEvent(C4+3, 0.2, 1)
        e3 = NoteEvent(C4+5, 0.3, 1)
        n = NoteTrack()
        n.append(e)
        self.assertEqual(n.toString(), "t:0:00:00|d:1.0|p:60|vol:NA|mod:")
        n.append(e1).append(e2).append(e3)

        #4/4 signature, period = 4, equal beat proportions
        mi = MeterInfo(4, 4)
        #four sixteenth per Beat, .5 sec per beat = 120 bpm
        bi = BeatInfo(4, .5)
        mc = MetricalContext(bi, mi)
        mp = MetricalPosition(1, 2, 3, 0, mc)
        mne = MetricalNoteEvent(0.5, C4, mp, 1.0/2, None)
        n.append(mne)

        t = n.clone()
        n.shift(1.5)
        self.assertEqual(n.startTime(), 1.5)

        self.assertEqual(n.getPitches(), [60, 62, 63, 65, 60])
        self.assertEqual(n.projection(3), n.getPitches())
        self.assertEqual(n.projection(3), n.pitches)
        self.assertEqual(n.getPitches(), n.pitches)
        self.assertEqual(n.projection("pitch"), n.getPitches())

        self.assertEqual(n.intervals(), [2.0, 1.0, 2.0, -5.0])

        self.assertEqual(n.parsons(), [1., 1., 1.0, -1.0])

        self.assertEqual(n.intervalClassification(numeric=False), ["+S", "+S", "+S", "-L"])
        self.assertEqual(n.intervalClassification(), [1, 1, 1, -3])

        self.assertRaises(Exception, n.transpose, C5)
        n.transpose(5)
        self.assertEqual(n.getPitches(), [65, 67, 68, 70, 65])

        self.assertEqual(n.contour(type="huron"), "convex")
        self.assertEqual(n.contour(type="abesser"), "convex")

        self.assertRaises(Exception, n.projection, 4)
        self.assertRaises(Exception, n.projection, "r")
        ld = n.getLoudnessData(fields=["max", "median"])
        self.assertEqual(any(ld["max"]), False)
        self.assertEqual(any(ld["median"]), False)
        for e in n:
            values = {'max': 1.2, 'median': 2.3, 'stddev': .5, 'rel_peak_pos':.5, 'temp_centroid':.5}
            e.setLoudness(values)
        #print "\n".join([_.__str__(short=False) for _ in n.getLoudnessData()])
        ld = n.getLoudnessData(fields=["max", "median"])
        self.assertEqual(ld["max"], [1.2, 1.2, 1.2, 1.2, 1.2])
        self.assertRaises(Exception, n.getLoudnessData, fields=["MAX"])

        df = n.to_dataframe(ignore_loudness=False, ignore_values=True)
        self.assertEqual(list(df["loud_max"]), [1.2, 1.2, 1.2, 1.2, 1.2])
        self.assertEqual(list(df["pitch"]), [65, 67, 68, 70, 65])
        n.clear()
        self.assertEqual(len(n), 0)
if __name__ == "__main__":
    unittest.main()
