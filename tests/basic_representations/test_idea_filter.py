#!/usr/bin/env python

""" Unit test for IdeaFilter class """

import unittest

import pytest

from melospy.basic_representations.idea_filter import *
from melospy.basic_representations.solo import *


class TestIdeaFilter( unittest.TestCase ):

    def getTestSolo(self):
        s = Solo()
        # test with valid initialization
        si = SoloInfo(1, "John Coltrane", "Giant Steps", "Alternate Take",  1, "ts", 240.3, "Up", "Hardbop", "Swing", "2/2", False, Key("B", "maj"))
        ri = RecordInfo("John Coltrane", "Giant Steps", "Impulse", "I2012", 1, "Impulse:John Coltrane;bs: Reggie Workman;dr: Elvin Jones;p: Paul Flanagan", "02.04.1959", "09.1958")
        ti = TranscriptionInfo("www.saxsolo.de", "SCAN", "Mr. X", "Klaus Frieler", "02.04.2013", "PREFINAL", "JohnColtrane_GiantSteps.wav", "JohnColtrane_GiantSteps_Solo.wav", "JohnColtrane_GiantSteps_FINAL.sv", 126, 267)
        ci = CompositionInfo("All the Things Your Are", "Johnny Mercer", [("A1", 8), ("A2", 8), ("B1", 8), ("A3", 8)])

        smd = SoloMetaData(si, ri, ti, ci)
        beattrack = Rhythm.isochronous(4, 0, 1)
        mg = Melody()
        #4/4 signature, period = 4, equal beat proportions
        mi = MeterInfo(4, 4)
        #four sixteenth per Beat, .5 sec per beat = 120 bpm
        bi = BeatInfo(4, .5)
        mc = MetricalContext(bi, mi)
        mp = MetricalPosition(1, 2, 3, 0, mc)
        C4 = 60
        C5 = C4 + 12

        #add a lot more of events
        bis = [BeatInfo(2, .5), BeatInfo(3, .5), BeatInfo(5, .5), BeatInfo(6, .5)]
        for i in range(16):
            duration = 1./8
            onset    = 1 + i*duration
            mc  = mc.clone().setBeatInfo(bis[i % len(bis)].clone())
            mp1 = MetricalPosition( i + 1, 1, 2, 0, mc)
            me  = MetricalNoteEvent(onset, C4 + (i %4), mp1, duration/2, i)
            mg.append(me)

        ksl = SectionList("KEY")
        ksl.append(Section("KEY", Key("Ab"), 0,   3))
        ksl.append(Section("KEY", Key("Db"), 4,   7))
        ksl.append(Section("KEY", Key("Db"), 8,  11))
        ksl.append(Section("KEY", Key("Eb"), 12, 15))

        fsl = SectionList("FORM")
        fsl.append(Section("FORM", FormName("A1"), 0,  3))
        fsl.append(Section("FORM", FormName("A2"), 4,  7))
        fsl.append(Section("FORM", FormName("A1"), 8, 15))

        csl = SectionList("CHORD")
        csl.append(Section("CHORD", Chord("Dm7"), 0,  3))
        csl.append(Section("CHORD", Chord("Eb7"), 4,  7))
        csl.append(Section("CHORD", Chord("Dm7"), 8,  11))
        csl.append(Section("CHORD", Chord("Eb7"), 12, 15))

        chsl = SectionList("CHORUS")
        chsl.append(Section("CHORUS", 1, 0, 7))
        chsl.append(Section("CHORUS", 2, 8, 15))

        psl = SectionList("PHRASE")
        psl.append(Section("PHRASE", 1, 0, 3))
        psl.append(Section("PHRASE", 2, 4, 7))
        psl.append(Section("PHRASE", 3, 8, 9))
        psl.append(Section("PHRASE", 4, 10, 12))
        psl.append(Section("PHRASE", 5, 13, 13))
        psl.append(Section("PHRASE", 6, 14, 15))

        isl = SectionList("IDEA")
        isl.append(Section("IDEA", Idea("lick_blues"), 0,  3))
        isl.append(Section("IDEA", Idea("#*lick_blues"), 4, 7))
        isl.append(Section("IDEA", Idea("void->line_w_asdl"), 8, 11))
        isl.append(Section("IDEA", Idea("~theme:t1"), 12, 15))

        #s = Solo(mg, smd, None, psl, fsl, chsl, csl, ksl)
        s = Solo(mg, smd, beattrack, psl, fsl, chsl, csl, None, ideas=isl)
        return s

    def testConstructor(self):
        """ test constructor """
        s = self.getTestSolo()
        IF = IFAFilter(s)
        self.assertEqual(IF.filter(event_based=False, filter_type="id"), ['lick_blues', '#*lick_blues', 'void->line_w_asdl', '~theme:t1'])
        self.assertEqual(IF.filter(event_based=False, filter_type="full-type"), ['lick-blues', 'lick-blues', 'line-wavy-slide', 'theme'])
        self.assertEqual(IF.filter(event_based=False, filter_type="main-type"), ['lick', 'lick', 'line', 'theme'])
        self.assertEqual(IF.filter(event_based=False, filter_type="backref"), [0, 1, 0, 0])
        self.assertEqual(IF.filter(event_based=False, filter_type="glue"), [False, False, False, True])
        self.assertEqual(IF.filter(event_based=False, filter_type="main-direction"), ['NA', 'NA', 'descending', 'NA'])
        self.assertEqual(IF.filter(event_based=False, filter_type="main-direction-reduced"), ['NA', 'NA', 'descending', 'NA'])
        self.assertEqual(IF.filter(event_based=False, filter_type="main-direction-reduced", include_voids=True), ['NA', 'NA', 'NA', 'descending', 'NA'])

        self.assertEqual(IF.filter(event_based=False, filter_type="main-direction-reduced"), ['NA', 'NA', 'descending', 'NA'])
        self.assertEqual(IF.getIdeaDurations(type="IOI", units="sec", include_voids=True),  [0.5, 0.4375, 0.125, 0.5, 0.375])
        self.assertEqual(IF.getIdeaDurations(type="IOI", units="sec", include_voids=False), [0.5, 0.4375, 0.5, 0.375])
        self.assertEqual(IF.getIdeaDurations(type="IOI", units="bars", include_voids=False),  [4.0, 2.916666666666666, 4.0, 2.916666666666668])
        self.assertEqual(IF.getIdeaDurations(type="IOI", units="bars", include_voids=True),   [4.0, 2.916666666666666, 1.083333333333334, 4.0, 2.916666666666668])
        self.assertEqual(IF.getIdeaDurations(type="notes", units="sec", include_voids=True),  [4, 4, 0, 4, 4])
        self.assertEqual(IF.getIdeaDurations(type="notes", units="sec", include_voids=False), [4, 4, 4, 4])
        self.assertEqual(IF.getIdeaDurations(type="duration", units="sec", include_voids=True),  [0.4375, 0.4375, 0.0625, 0.4375, 0.4375])
        self.assertEqual(IF.getIdeaDurations(type="duration", units="sec", include_voids=False), [0.4375, 0.4375, 0.4375, 0.4375])
        #print IF.getPhrasesFromIFA()
        #print IF.filter(event_based=False, filter_type="main-direction")
        #print IF.getIdeaGaps()

if __name__ == "__main__":
    unittest.main()
