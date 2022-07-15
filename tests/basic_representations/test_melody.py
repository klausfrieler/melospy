#!/usr/bin/env python

""" Unit test for class RhythmEvent """

import unittest

import pytest

from melospy.basic_representations.melody import *
from melospy.basic_representations.metrical_note_event import *


class TestMelody( unittest.TestCase ):

    #@pytest.mark.skip(reason="Assertion mismatch")
    def testConstructor(self):
        """ Test assures constructor works properly"""

        #################################
        ##     NoteTrack     stuff     ##
        #################################

        C4 = 60
        C5 = C4 + 12
        e  = NoteEvent(C4,   0.0, 1)
        e1 = NoteEvent(C4+2, 0.1, 1)
        e2 = NoteEvent(C4+3, 0.2, 1)
        e3 = NoteEvent(C4+5, 0.3, 1)
        n  = NoteTrack()
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
        self.assertEqual(n.projection("pitch"), n.getPitches())

        self.assertEqual(n.intervals(), [2.0, 1.0, 2.0, -5.0])
        self.assertRaises(Exception, n.transpose, C5)
        n.transpose(5)
        self.assertEqual(n.getPitches(), [65, 67, 68, 70, 65])

        self.assertRaises(Exception, n.projection, 4)
        self.assertRaises(Exception, n.projection, "r")
        #print n.estimateKey()
        self.assertEqual(n.estimateKey(), Key("Bb", "maj"))
        n.clear()
        self.assertEqual(len(n), 0)

        #################################
        ##     MeterGrid stuff         ##
        #################################
        m = Melody()
        for i in range(16):
            duration = .25
            onset    = 1 + i*duration
            mc = MetricalContext(BeatInfo(2, .5), MeterInfo(4, 4))
            mp1 = MetricalPosition( i + 1, 1, 1, 0, mc)
            me = MetricalNoteEvent(onset, C4, mp1, duration)
            if i == 15:
                me.duration = 8*me.duration
            m.append(me)

        self.assertEqual(m.getTotalMetricalDuration(), 16)
        self.assertEqual(m.totalDuration(), 5.75)

        mel = Melody()

        #add a lot more of events
        bis = [BeatInfo(2, .5), BeatInfo(3, .5), BeatInfo(5, .5), BeatInfo(6, .5)]
        for i in range(16):
            duration = 1./8
            onset    = 1 + i*duration
            mc = mc.clone().setBeatInfo(bis[i % len(bis)].clone())
            mp1 = MetricalPosition( i + 1, 1, 2, 0, mc)
            me = MetricalNoteEvent(onset, C4, mp1, duration/2)
            mel.append(me)
        mod_anno = Rhythm().fromOnsets([1.1, 1.55, 2.1, 2.76])
        mod = ["gliss", "vib", "bend", "VIBRATIO"]
        for i, aa in enumerate(mod_anno):
            aa.setValue(mod[i % len(mod)])
        solo = mel.annotateModulation(mod_anno)
        self.assertEqual(solo[4].modulation.annotated, "vibrato")
        self.assertEqual(solo[14].modulation.annotated, "vibrato")
        self.assertEqual(solo[5].modulation.annotated, "")

        #test len, lcmTatum
        self.assertEqual(len(mel), 16)
        self.assertEqual(mel.leastCommonTatum(), 30)

        #test filterbar
        self.assertEqual(len(mel.getBarSequence(9, 12)), 4)
        self.assertEqual(mel.getBarSequence(9)[0] == mel[8], True)
        #print mel.filterbar(-100, 400).len()
        self.assertEqual(len(mel.getBarSequence(-1)), 0)
        self.assertEqual(len(mel.getBarSequence(-100, 100)), 16)
        self.assertRaises(Exception, mel.getBarSequence, 12, 9)


        mel.standardize()
        me = mel[0]
        self.assertEqual(me.getTatum(), 16)
        self.assertEqual(me.getBeatInfo().getTatums(), 30)
        self.assertEqual(me.getMetricalPosition().toString(), "4.30.1.1.16")
        self.assertEqual(me.getMeterInfo().toString(), "4/4|4|Equal")

        #projections
        self.assertEqual(mel.projection("onset"), mel.getOnsets())
        self.assertEqual(list(mel.export("norm_onsets")), mel.getNormalizedOnsets())
        self.assertEqual(mel.projection("duration"), mel.getDurations())
        self.assertEqual(mel.projection("meter"), mel.getMetricalPositions())
        self.assertEqual(mel.projection("durtatum"), mel.getDurationTatums())
        self.assertEqual(mel.projection("pitch"), mel.getPitches())
        self.assertEqual(mel.export("huroncontour", optParam="code"), mel.contour(type="huron", format= "code"))
        self.assertEqual(list(mel.export("gradient-contour")), [0.])
        self.assertEqual(m.export("total-metrical-duration"), 16)
        self.assertEqual(list(m.export("syncopations")), m.syncopations())
        self.assertEqual(m.export("syncopicity"), 0.0)
        #self.assertEqual(mel.export("metricalweights"),mel.getMetricalWeights())
        #self.assertEqual(len(mel.export("pitch")), 1)
        #self.assertEqual(len(mel.export("pitch")[0]), 16)
        #self.assertEqual(len(mel.export("pitch", "bars")), 16)
        #self.assertEqual(mel.export("pitch", "bars")[0][0], 60)
        #print (mel.export("pitch", "bars")[0][0])
        #print exp
        mel2 = mel.clone()
        firstOnset = mel2[0].onsetSec
        lastOnset = mel2[-1].onsetSec
        lastBar   = mel2.getLastBarNumber()
        firstBar  = mel2.getFirstBarNumber()
        mel2.shift(lastOnset - firstOnset + 1)
        mel2.shiftbar(lastBar -firstBar + 1)
        mel.concat(mel2)
        self.assertEqual(mel[-1].onsetSec, 5.75)
        self.assertEqual(mel.getLastBarNumber(), 32)
        for e in mel:
            values = {'max': 1.2, 'median': 2.3, 'stddev': .5, 'rel_peak_pos':.5, 'temp_centroid':.5}
            e.setLoudness(values)
        df = mel.to_dataframe(split_metrical_positions=True, ignore_loudness=False, ignore_f0mod=True, ignore_values=True, quote_signatures=True)
        #print df
        self.assertEqual(list(df["bar"]), mel.getEventBars())
        self.assertEqual(list(df["pitch"]), mel.getPitches())
        self.assertEqual(list(df["loud_max"]), mel.getLoudnessData(["max"])["max"])

if __name__ == "__main__":
    unittest.main()
