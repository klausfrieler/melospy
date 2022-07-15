#!/usr/bin/env python

""" Unit test for class AnnotatedBeatTrack"""
import unittest

from melospy.basic_representations.annotated_beat_track import *
from melospy.basic_representations.note_track import *


class TestAnnotatedBeatTrack( unittest.TestCase ):

    def testConstructor(self):
        """ Test assures constructor works properly"""
        mi = MeterInfo(4, 4)
        #four sixteenth per Beat, .5 sec per beat = 120 bpm
        bi = BeatInfo(4, .5)
        mc = MetricalContext(bi, mi)
        bass_pitch = 36
        form = FormName("A1")
        chord = Chord("C+j711#")
        abe   = AnnotatedBeatEvent(0, MetricalPosition(1, 1, 1, 0, mc), form, chord, bass_pitch)
        abe1  = AnnotatedBeatEvent(0.5, MetricalPosition(1, 2, 1, 0, mc), "", "", bass_pitch+2)
        abe2  = AnnotatedBeatEvent(1, MetricalPosition(1, 3, 1, 0, mc), "", "D7", bass_pitch+3)
        abe3  = AnnotatedBeatEvent(1.5, MetricalPosition(1, 4, 1, 0, mc), "", "", bass_pitch+4)

        abt = AnnotatedBeatTrack()
        abt.append(abe)
        self.assertEqual(abt.toString(), "t:0:00:00|d:0.5|val:'C+j7911#'|pos:4.4.1.1.1|C+j7911#|36|A1|")
        abt.append(abe1).append(abe2).append(abe3)
        self.assertEqual(abt.getChordList(as_string=True), ['C+j7911#', '', 'D7', ''])
        self.assertEqual(abt.getFormList(as_string=True), ['A1', '', '', ''])
        self.assertEqual(abt.getSignatureList(as_string=True), ['4/4', '4/4', '4/4', '4/4'])
        self.assertEqual(abt.getSignatureList(as_string=True, simplify=True), ['4/4', '', '', ''])

        self.assertEqual(abt.bass_pitches, [36, 38, 39, 40])
        self.assertEqual(abt.get_chord_changes_by_form(), "A1: ||C+j7911# D7 ||")
        self.assertEqual(abt._get_form_start(), 0)
        self.assertEqual(AnnotatedBeatTrack()._get_form_start(), None)
        #print abt.getChords()
        #print abt.getForm()
        self.assertDictEqual(abt.getBarBeatDict(), {1: {1: [0], 3: [1]}})
        self.assertEqual(str(abt.toMeterGrid()[0].value), "C+j7911#")

        walkingbass = [36, 38, 37, 40]
        ne = NoteTrack()
        for i in range(len(abt)):
            ne.append(NoteEvent(walkingbass[i], abt[i].onset, abt[i].duration))
        #print abt.addBassData(ne)
        self.assertEqual(abt.addBassData(ne).getBassPitches(), walkingbass)
        self.assertEqual(abt.addBassData(walkingbass).getBassPitches(), walkingbass)
        self.assertEqual(abt.addBassData([]).getBassPitches(), walkingbass)
        abt2 = abt.clone()
        mi = MeterInfo(5, 4)
        mc = MetricalContext(bi, mi)
        abt2.append(AnnotatedBeatEvent(2.0, MetricalPosition(2, 1, 1, 0, mc), "", "", bass_pitch+6))
        abt2.append(AnnotatedBeatEvent(2.5, MetricalPosition(2, 2, 1, 0, mc), "", "", bass_pitch+8))
        abt2.calcSignatureChanges()
        self.assertEqual(abt2.getSignatureChanges(), ['4/4', '', '', '', '5/4', ''])
        self.assertEqual(abt2.setChorusIDs().getChorusIDs(), [1, 1, 1, 1, 1, 1])
        mps = abt2.splitMetricalPositions()
        self.assertEqual(mps["period"], [4, 4, 4, 4, 5, 5])
        df = abt2.to_dataframe(include_tatums=True)
        self.assertEqual(list(df["bass"]), abt2.bass_pitches)
        self.assertEqual(list(df["tatum"]), [1]*len(abt2))
        new_abt = abt2.cut_overhead(first_bar=2)
        self.assertEqual(len(new_abt), 2)
        self.assertEqual(new_abt[0].getFormString(), "A1")
        self.assertEqual(str(new_abt[0].chord), "D7")
        new_abt = abt2.cut_overhead(first_bar=1, last_bar=1)
        self.assertEqual(len(new_abt), 4)
        self.assertEqual(new_abt[0].getFormString(), "A1")
        self.assertEqual(str(new_abt[0].chord), "C+j7911#")
        self.assertEqual(new_abt.findBeat(new_abt[0].getBar(), new_abt[0].getBeat()), new_abt[0])

    def testFillUp(self):
        mi = MeterInfo(4, 4)
        #four sixteenth per Beat, .5 sec per beat = 120 bpm
        bi = BeatInfo(4, .5)
        mc = MetricalContext(bi, mi)
        bass_pitch = 60
        abe   = AnnotatedBeatEvent(0, MetricalPosition(1, 1, 1, 0, mc), "", "D7", bass_pitch)
        #abe1  = AnnotatedBeatEvent(1, MetricalPosition(1,3,1,0, mc), "", "", bass_pitch+2)
        abe2  = AnnotatedBeatEvent(2, MetricalPosition(2, 1, 1, 0, mc), "", "D7", bass_pitch+3)
        abe3  = AnnotatedBeatEvent(3, MetricalPosition(2, 3, 1, 0, mc), "", "", bass_pitch+4)

        abt = AnnotatedBeatTrack()
        abt.append(abe)
        #abt.append(abe1)
        abt.append(abe2)
        abt.append(abe3)
        abt.fill_up()
        #print abt
        self.assertEqual(len(abt), 8)
        self.assertEqual(abt.findNextFullBar(2, forward = True), 4)
        self.assertEqual(abt.findNextFullBar(2, forward = False), 0)
        self.assertEqual(abt.findNextFullBar(0, forward = False), 0)
        self.assertEqual(abt.findNextFullBar(0, forward = True), 4)

if __name__ == "__main__":
    unittest.main()
