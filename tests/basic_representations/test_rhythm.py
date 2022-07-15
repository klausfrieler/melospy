#!/usr/bin/env python

""" Unit test for class RhythmEvent """

import random
import unittest

from melospy.basic_representations.metrical_note_event import *
from melospy.basic_representations.rhythm import *


class TestRhythm ( unittest.TestCase ):

    def testConstructor(self):
        """ Test assures that onsetSec and durationSec are set correctly if they are given as arguments to constructor """

        e  = RhythmEvent(0,   1)
        e1 = RhythmEvent(0.1, 1)
        e2 = RhythmEvent(0.2, 1)
        e3 = RhythmEvent(0.3, 1)
        r = Rhythm()
        r.append(e)
        self.assertEqual(r.toString(), "t:0:00:00|d:1.0")
        r.append(e1).append(e2).append(e3)
        #r.writeCSV("rhythm_test.csv")
        df = r.to_dataframe(ignore_values =False)
        #print df
        t = Rhythm(r[-1])
        self.assertEqual(t.toString(), e3.toString())
        #Four quarter signature, period = 4, equal beat proportions
        mi = MeterInfo(4, 4)
        #four sixteenth per Beat, .5 sec per beat = 120 bpm
        bi = BeatInfo(4, .5)
        mc = MetricalContext(bi, mi)
        mp = MetricalPosition(1, 2, 3, 0, mc)
        C4 = 60
        mne = MetricalNoteEvent(0.5, C4, mp, 1.0/2, None)
        r.append(mne)
        self.assertEqual(r.last(), mne)

        mne = MetricalNoteEvent(0.5, C4, mp, 1.0/2, None)
        self.assertRaises(Exception, r.append, mne)

        self.assertEqual(r.totalDuration(), 1.0)
        self.assertEqual(r.hasOverlap(), True)
        self.assertEqual(r.getOnsets(), [0.0, .1, .2, .3, 0.5] )
        self.assertEqual(r.projection(1), [0.0, .1, .2, .3, 0.5] )
        self.assertEqual(r.projection("onset"), [0.0, .1, .2, .3, 0.5] )
        self.assertEqual(r.values, [None, None, None, None, None])
        #print Rhythm().getOffsets()
        self.assertRaises(Exception, Rhythm().getOffsets )
        s = r.clone().durationToIOI()
        self.assertEqual(s.getOffsets(), [0.1, 0.2, 0.3, 0.5, 0.5] )
        self.assertEqual(s.getOOIs(), [0, 0, 0, 0] )
        self.assertEqual(s.getNormalizedOnsets(), [0.0, 0.2, 0.4, 0.6, 1.0] )
        s.normalize(minVal = 0., maxVal =.5)
        self.assertEqual(s.getOnsets(), [0, 0.2, 0.4, 0.6, 1.0] )
        self.assertRaises(Exception, r.projection, 4)
        self.assertRaises(Exception, r.projection, "r")

        self.assertEqual(r.getDurations(), [1, 1, 1, 1, .5] )
        self.assertEqual(r.projection(2), r.getDurations() )
        self.assertEqual(r.projection("duration"), r.getDurations() )


        self.assertRaises(Exception, r.shift, "r")
        t = r.clone()
        r.shift(1.5)
        self.assertEqual(r.startTime(), 1.5)

        r.warp(2)
        self.assertEqual(r.totalDuration(), 2.0)
        self.assertEqual(r.startTime(), 1.5)
        self.assertEqual(r.getIOIs(), [.2, .2, .2, .4] )
        self.assertEqual(r.getDurationRatios(), [1.0, 1.0, 1.0, 0.5])
        self.assertEqual(r.getDurationRatios(classify=True), [0, 0, 0, -1])
        self.assertEqual(r.getIOIRatios(), [1.0, 1.0, 2.0])
        self.assertEqual(r.getIOIRatios(classify=True), [0, 0, 1])
        #print r
        #start, end = r.getIDsFromRegion(1.5, 1.568)
        #print start, end
        #test IDs from region
        start, end = r.getIDsFromRegion(2, 3)
        self.assertEqual(start, 3)
        self.assertEqual(end, 4)
        start, end = r.getIDsFromRegion(-2, -1)
        self.assertEqual(start, None)
        self.assertEqual(end, None)

        start, end = r.getIDsFromRegion(5, 10)
        self.assertEqual(start, None)
        self.assertEqual(end, None)
        onset, dur = r.getRegionFromIDs(3, 4)
        self.assertEqual(onset, 2.1)
        self.assertEqual(dur, 1.4)

        self.assertEqual(r.findEvent(0.75), None)
        self.assertEqual(r.findEvent(1.75), 1)
        self.assertEqual(r.findEvent(2.75), 4)
        #self.assertRaises(Exception, r.getIDsFromRegion, "t", 3)
        #self.assertRaises(Exception, r.getIDsFromRegion, 3, "t")
        #self.assertRaises(Exception, r.getIDsFromRegion, 4, 3)

        r.insert(RhythmEvent(1.0, 2))
        self.assertEqual(r[0].onsetSec, 1.0)
        r.insert(RhythmEvent(2.0, 2))
        self.assertEqual(r[4].onsetSec, 2.0)
        r.insert(RhythmEvent(3.0, 2))
        self.assertEqual(r[7].onsetSec, 3.0)
        self.assertRaises(Exception, r.insert, RhythmEvent(3.0, 2))

        self.assertEqual(r.without([0]), r.without(0))
        tmp = r.without(0)
        self.assertEqual(tmp[0].onsetSec, 1.5)
        tmp = r.without(list(range(len(r))))
        self.assertEqual(len(tmp), 0)
        tmp = tmp.without(list(range(len(r))))
        self.assertEqual(len(tmp), 0)


        self.assertEqual(r.slice(-1, 3)[0].onsetSec, 1.0)
        self.assertEqual(r.slice(1, 3)[0].onsetSec, 1.5)
        self.assertEqual(r.slice(1, 4)[2].onsetSec, 1.9)

        self.assertEqual(r.sliceByTime(0, 3)[0].onsetSec, 1.0)
        self.assertEqual(r.sliceByTime(1.2, 3)[0].onsetSec, 1.5)
        self.assertEqual(r.sliceByTime(1., 3.)[-1].onsetSec, 3.0)

        #test clear
        r.clear()
        r.insert(RhythmEvent(1.0, 2))
        self.assertEqual(len(r), 1)
        r.clear()

        self.assertRaises(Exception, r.getIDsFromRegion, 0, 3)
        self.assertEqual(len(r), 0)
        self.assertEqual(r.last(), None)
        r = Rhythm.isochronous(10, 0, .2)
        self.assertEqual(r.first(), RhythmEvent(0, .2, 1))
        self.assertEqual(r.last(), RhythmEvent(1.8, .2, 17))
        q = Rhythm.fromOnsets(r.onsets)
        self.assertEqual(q.first(), RhythmEvent(0.0, 0.0, None))
        self.assertEqual(q.last(),  RhythmEvent(1.8, 0.0, None))

        q = Rhythm.fromString("10010010", timebase=.25, start=1.0)
        self.assertEqual(q.first(), RhythmEvent(1.0, 0.0, None))
        self.assertEqual(q.last(),  RhythmEvent(2.5, 0.0, None))
        q2 = Rhythm.fromString("x--x--x-", timebase=.25, start=1.0)
        self.assertEqual(q,  q2)
        q2 = Rhythm.fromString("XooXooxo", timebase=.25, start=1.0)
        self.assertEqual(q,  q2)

        q = Rhythm.fromString("10010010", repeat=100, timebase=.25, start=1.0)
        self.assertEqual(len(q), 300)

        self.assertEqual(q.first(),  RhythmEvent(1, 0.0, None))
        self.assertEqual(q.last(),  RhythmEvent(200.5, 0.0, None))

        #q1 = Rhythm.fromString("XooXooxo", repeat=1000, timebase=.25, start=0.0, jitter=0.)
        #q2 = Rhythm.fromString("XooXooxo", repeat=1000, timebase=.25, start=0.0, jitter=.01)
        #diff = sum(abs(e1-e2) for e1, e2 in zip(q1.onsets, q2.onsets))
        #print [(e1-e2) for e1, e2 in zip(q1.onsets, q2.onsets)]
        #print diff

    def testEventDensity(self):
        t = 0
        r = Rhythm()
        for i in range(100):
            dur = random.random()
            t = t + dur
            r.append(RhythmEvent(t, dur))

        densities = r.eventDensity(4., .5)
        #print densities

    def testOperations(self):
        t = 0
        r1 = Rhythm()
        r2 = Rhythm()
        N = 3
        gap = 1
        for i in range(N):
            dur = random.random()
            t = t + dur
            r2.append(RhythmEvent(t, dur))
        self.assertRaises(ValueError, r1.concat, r2, gap=0)
        r1.concat(r2, gap = gap)
        self.assertEqual(r1, r2)
        r1 = r2.clone()
        endTime = r1.endTime()

        r1.concat(r2, gap = gap)
        self.assertEqual(len(r1), 2*N)
        self.assertEqual(r1[N].getOnset(), endTime + gap)

if __name__ == "__main__":
    unittest.main()
