#!/usr/bin/env python

""" Check MelodyCutter"""

import unittest

from melospy.basic_representations.melody_cutter import *


class TestMelodyCutter( unittest.TestCase ):
    """ test """
    def prepareTestDataMiles(self, item=0):
        dbpath =  os.path.join(root_path(), "analysis/data/MIDLEVEL/DB/wjazzd_ifa.db")
        dbinfo = DBInfo.fromDict({'path': dbpath, "use": True, "type":"sqlite3"})
        #mi = MelodyImporter(tunes=tunes, path="", dbinfo=dbinfo)
        mi = MelodyImporter(tunes="test-db-"+str(item), path=dbpath, dbinfo=dbinfo )
        mel = next(mi.fetcher())
        return mel

    def getTestSections(self, sect_type):
        sl = None
        if sect_type == "KEY":
            sl = SectionList("KEY")
            sl.append(Section("KEY", Key("Ab"), 0,   3))
            sl.append(Section("KEY", Key("Db"), 4,   7))
            sl.append(Section("KEY", Key("Db"), 8,  11))
            sl.append(Section("KEY", Key("Eb"), 12, 15))
        elif sect_type=="FORM":
            sl = SectionList("FORM")
            sl.append(Section("FORM", FormName("A1"), 0,  3))
            sl.append(Section("FORM", FormName("A2"), 4,  7))
            sl.append(Section("FORM", FormName("A1"), 8, 15))
        elif sect_type=="CHORD":
            sl = SectionList("CHORD")
            sl.append(Section("CHORD", Chord("Dm7"), 0,  3))
            sl.append(Section("CHORD", Chord("Eb7"), 4,  7))
            sl.append(Section("CHORD", Chord("Dm7"), 8,  11))
            sl.append(Section("CHORD", Chord("Eb7"), 12, 15))
        elif sect_type=="CHORUS":
            sl = SectionList("CHORUS")
            sl.append(Section("CHORUS", 1, 0, 7))
            sl.append(Section("CHORUS", 2, 8, 15))
        elif sect_type=="PHRASE":
            sl = SectionList("PHRASE")
            sl.append(Section("PHRASE", 1, 0, 3))
            sl.append(Section("PHRASE", 2, 4, 7))
            sl.append(Section("PHRASE", 3, 8, 9))
            sl.append(Section("PHRASE", 4, 10, 12))
            sl.append(Section("PHRASE", 5, 13, 13))
            sl.append(Section("PHRASE", 6, 14, 15))
        elif sect_type=="IDEA":
            sl = SectionList("IDEA")
            sl.append(Section("IDEA", Idea("lick_blues"), 0,  5))
            sl.append(Section("IDEA", Idea("#*lick_blues"), 6, 9))
            sl.append(Section("IDEA", Idea("line_w_asdl"), 10, 12))
            sl.append(Section("IDEA", Idea("~theme:t1"), 13, 15))
        else:
            raise ValueError("Invalid section type:{}".format(sect_type))
        return sl
    def getTestSoloMetadata(self):
        si = SoloInfo(1, "John Coltrane", "Giant Steps", "Alternate Take",  1, "ts", 240.3, "Up", "Hardbop", "Swing", "2/2", False, Key("B", "maj"))

        ri = RecordInfo("John Coltrane", "Giant Steps", "Impulse", "I2012", 1, "Impulse:John Coltrane;bs: Reggie Workman;dr: Elvin Jones;p: Paul Flanagan", "02.04.1959", "09.1958")
        ti = TranscriptionInfo("www.saxsolo.de", "SCAN", "Mr. X", "Klaus Frieler", "02.04.2013", "PREFINAL", "JohnColtrane_GiantSteps.wav", "JohnColtrane_GiantSteps_Solo.wav", "JohnColtrane_GiantSteps_FINAL.sv", 126, 267)
        ci = CompositionInfo("All the Things Your Are", "Johnny Mercer", [("A1", 8), ("A2", 8), ("B1", 8), ("A3", 8)])

        smd = SoloMetaData(si, ri, ti, ci)
        return smd

    def getTestSolo(self):
        mg = Melody()
        #4/4 signature, period = 4, equal beat proportions
        mi = MeterInfo(4, 4)
        #four sixteenth per Beat, .5 sec per beat = 120 bpm
        bi = BeatInfo(4, .5)
        mc = MetricalContext(bi, mi)
        mp = MetricalPosition(1, 2, 3, 0, mc)

        #add a lot more of events
        bis = [BeatInfo(2, .5), BeatInfo(3, .5), BeatInfo(5, .5), BeatInfo(6, .5)]
        for i in range(16):
            duration = 1./8
            onset    = 1 + i*duration
            mc  = mc.clone().setBeatInfo(bis[i % len(bis)].clone())
            mp1 = MetricalPosition( i + 1, 1, 2, 0, mc)
            me  = MetricalNoteEvent(onset, 60 + (i %4), mp1, duration/2, i)
            mg.append(me)

        beattrack = Rhythm.isochronous(4, 0, 1)
        ksl = self.getTestSections("KEY")
        fsl = self.getTestSections("FORM")
        csl = self.getTestSections("CHORD")
        chsl = self.getTestSections("CHORUS")
        psl = self.getTestSections("PHRASE")
        isl = self.getTestSections("IDEA")

        smd = self.getTestSoloMetadata()
        s = Solo(mg, smd, beattrack, psl, fsl, chsl, csl, ksl, ideas=isl)
        return s

    def testParseDirective(self):
        """ Check construction and helper"""
        mc = MelodyCutter()

        self.assertRaises(ValueError, mc.parse_directive, "moin")
        self.assertRaises(ValueError, mc.parse_directive, {"moin": "moin"})
        self.assertRaises(ValueError, mc.parse_directive, {"moin": "moin", "hallo": "hallo"})
        self.assertRaises(ValueError, mc.parse_directive, "bars: moin hallo: hallo")
        self.assertRaises(ValueError, mc.parse_directive, "bars: 2-1")
        self.assertRaises(ValueError, mc.parse_directive, "chunk: 1 2 3")
        self.assertRaises(ValueError, mc.parse_directive, "chunk: 1 2 3")
        self.assertRaises(ValueError, mc.parse_directive, "chords: moin")
        self.assertRaises(ValueError, mc.parse_directive, "form: moin")
        self.assertRaises(ValueError, mc.parse_directive, "chunk")
        self.assertRaises(ValueError, mc.parse_directive, "chunk: 1 ")
        self.assertRaises(ValueError, mc.parse_directive, "chunk: bars 1")

        seg_types = ['phrases', 'bars', 'chorus', 'form', 'chords', 'ideas']
        for seg in seg_types:
            self.assertEqual(mc.parse_directive(seg)[0], seg)

        self.assertEqual(mc.parse_directive("form: A1"), ("form", ["A1"]))
        self.assertEqual(mc.parse_directive("bars: 1 4 5"), ("bars", ["1", "4", "5"]))
        self.assertEqual(mc.parse_directive("bars: 1-2 5"), ("bars", ["1", "2", "5"]))
        self.assertEqual(mc.parse_directive("bars: 1-2 5-6 123-124"), ("bars", ["1", "2", "5", "6", "123", "124"]))
        self.assertEqual(mc.parse_directive("chords: G7 D7 F7#9"), ("chords", ["G7", "D7", "F7#9"]))
        self.assertEqual(mc.parse_directive("chords: set"), ("chords", ["set"]))
        self.assertEqual(mc.parse_directive("chorus: 1 4      5"), ("chorus", ["1", "4", "5"]))
        self.assertEqual(mc.parse_directive("phrases: 1 4 5"), ("phrases", ["1", "4", "5"]))

        self.assertEqual(mc.parse_directive("chunk: 1 4 "), ("chunk", ["1", "4"]))
        self.assertEqual(mc.parse_directive("bars: chunks 1 4 "), ("bars", ["chunks", "1", "4"]))
        self.assertEqual(mc.parse_directive("ideas: wavy   slide  line_w_asdl"), ("ideas", ["wavy", "slide", "line_w_asdl"]))
        #print mc.parse_directive("")

    def testCutting(self):
        solo = self.getTestSolo()
        self.assertEqual(len(solo), 16)
        segmentations = [{"ideas": "wavy   tick  line_w_asdl"}]
        segmentations = ["ideas"]
        segmentations = [{"ideas": "line_w_asdl"}]
        #segmentations = [{"phrases": "1 2 4 "}]
        mc = MelodyCutter(melody=solo, segmentations=segmentations, verbose=True)
        mc.cut()
if __name__ == "__main__":
    unittest.main()
