#!/usr/bin/env python

""" Unit test for class Accents """

import os
import unittest

import pytest

from melospy.basic_representations.accents import *
from melospy.basic_representations.rhythm import *
from melospy.input_output.melody_importer import *
from melospy.input_output.tony_csv_reader import *
from melospy.tools.commandline_tools.dbinfo import *

from tests.rootpath import *

class TestAccents( unittest.TestCase ):

    def prepareTestDataMiles(self, item=0):
        dbinfo = DBInfo.fromDict({'path': add_data_path("wjazzd.db"), "use": True, "type":"sqlite3"})
        #mi = MelodyImporter(tunes=tunes, path="", dbinfo=dbinfo)
        mi = MelodyImporter(tunes="test-db-"+str(item), path="", dbinfo=dbinfo )
        mel = next(mi.fetcher())
        return mel

    def prepareTestDataEsac(self):
        dbinfo = DBInfo.fromDict({'path': add_data_path("esac.db"), "use": True, "type":"sqlite3"})
        #mi = MelodyImporter(tunes=tunes, path="", dbinfo=dbinfo)
        mi = MelodyImporter(tunes = "test-esac", path="", dbinfo=dbinfo )
        mel = next(mi.fetcher())
        return mel

    def prepareStrangeMeterGrid(self, syncopated=False, division=2):
        mc = MetricalContext(BeatInfo(tatums=division), MeterInfo(4, 4))
        mis = [MeterInfo(2, 4), MeterInfo(3, 4), MeterInfo(5, 4), MeterInfo(6, 8), MeterInfo(7, 8), MeterInfo(7, 4), MeterInfo(11, 8)]
        mg = MeterGrid()
        duration = .5
        bar_onset = 1
        for i in range(len(mis)):
            mi = mis[i % len(mis)].clone()
            mc.setMeterInfo(mi)
            period = mi.period
            bar = i+1
            for j in range(period):
                beat = j + 1
                if not syncopated:
                    tatum = 1
                else:
                    tatum = 2
                onset = bar_onset + j *duration
                mp = MetricalPosition(bar, beat, tatum, 0, mc.clone())
                me = MetricalEvent(onset, mp, duration)
                mg.append(me)
            bar_onset = bar_onset + duration*period
        return mg


    def createIsoRhythm(self, N=10, dt=.25, start=0):
        return Rhythm.isochronous(N, 0, 0.250)

    def createTestRhythm(self):
        onsets = [0, 1., 1.5, 2, 3.5, 3.75, 4.0]
        return Rhythm.fromOnsets(onsets)

    def createTestNoteTrack(self):
        onsets = [0, 1., 1.5, 2, 3.5, 3.75, 4.0]
        pitch = [60, 62, 58, 59, 63, 65, 72]
        nt = NoteTrack()
        for p, o in zip(pitch, onsets):
            ne = NoteEvent(p, o, .25)
            nt.append(ne)
        return nt

    def createTestPitchExtremaNoteTrack(self):
        onsets = [0, 1., 1.5, 2, 3.5, 3.75, 4.0]
        pitch = [60, 63, 60, 62, 63, 62, 60]
        nt = NoteTrack()
        for p, o in zip(pitch, onsets):
            ne = NoteEvent(p, o, .25)
            nt.append(ne)
        return nt

    def testAccentBase(self):
        """ Testing basic functionality"""

        a = AccentsBase(baseAccent=3)
        self.assertEqual(a.baseAccent, 3)
        params = {"baseAccent":3, "noAccent": 0, "dummy": None}
        a.setParams(params)
        self.assertDictEqual(a.__dict__, {'noAccent': 0, 'baseAccent': 3})

    def testAccentFactory(self):
        """ Testing basic functionality"""
        af = AccentFactory()
        self.assertRaises(ValueError, af.create, "standard-gauss")

        a = af.create("const")
        self.assertEqual(isinstance(a, ConstantAccent), True)
        weights=[0 for _ in range(10)]
        a = af.create("external", weights=weights)
        self.assertEqual(a.weights, weights)
        self.assertEqual(isinstance(a, ExternalAccents), True)

        a = af.create("periodic")
        self.assertEqual(isinstance(a, PeriodicAccents), True)
        self.assertEqual(a.period, 2)
        self.assertEqual(a.phase, 0)
        self.assertEqual(a.weight, 1)
        params_periodic = {"period": 3, "phase": 1, "weight": 2}
        a.setParams(params_periodic)
        self.assertEqual(a.period, 3)
        self.assertEqual(a.phase, 1)
        self.assertEqual(a.weight, 2)

        a = af.create("gauss_standard", a_min=2, a_maj=5, sigma=.5)
        self.assertEqual(isinstance(a, GaussificationStandardAccents), True)
        self.assertEqual(a.a_min, 2)
        self.assertEqual(a.a_maj, 5)
        self.assertEqual(a.sigma, .5)


        #rules = ["flat", "fixed", "gauss-standard"]
        #print a.calculate(rules)


    def testConstantAccents(self):
        r = self.createIsoRhythm()
        af = AccentFactory()
        a = af.create("const")
        self.assertEqual(a.calculate(r), [1 for e in r])
        pass

    def testExternalAccents(self):
        r = self.createIsoRhythm()
        af = AccentFactory()
        w = [1.5 for e in r]
        a = af.create("external", weights=w)
        self.assertEqual(a.calculate(r), w)

    def testPeriodicAccents(self):
        r = self.createIsoRhythm()
        af = AccentFactory()
        a = af.create("periodic", period=3, phase=1, weight=2)
        self.assertEqual(a.calculate(r), [0, 2, 0, 0, 2, 0, 0, 2, 0, 0 ])

    def testThresholdAccents(self):
        af = AccentFactory()
        a = af.create("threshold", threshold=.5, position="onsite")
        r = [0, .25, .75, 1, 0]
        self.assertEqual(a.calculate(r), [0, 0, 1, 1, 0])
        a.setPosition("after")
        self.assertEqual(a.calculate(r), [0, 0, 0, 1, 1])
        a.setPosition("before")
        self.assertEqual(a.calculate(r), [0, 1, 1, 0, 0])
        a.addPosition("after")
        self.assertEqual(a.calculate(r), [0, 1, 1, 1, 1])

        a.setPosition(["after", "onsite"])
        self.assertEqual(a.calculate(r), [0, 0, 1, 1, 1])

        a.setPosition(["after", "onsite"]*2)
        self.assertEqual(a.calculate(r), [0, 0, 1, 1, 1])

        a.setPosition(["onsite"])
        r = [0, -.25, -.75, -1, 0]
        self.assertEqual(a.calculate(r), [0, 0, 1, 1, 0])

        a.abs_mode = False
        r = [0, -.25, -.75, -1, 0]
        self.assertEqual(a.calculate(r), [0, 0, 0, 0, 0])

        r = [0, -.25, .75, -1, 0]
        self.assertEqual(a.calculate(r), [0, 0, 1, 0, 0])

        a.threshold= -.5
        r = [0, -.25, -.75, -1, 0]
        self.assertEqual(a.calculate(r), [0, 0, 1, 1, 0])

        a.threshold= -.5
        r = [0, -.25, -.49, -1, 0]
        self.assertEqual(a.calculate(r), [0, 0, 0, 1., 0])

    def testJumpAccents(self):
        m = self.createTestNoteTrack()
        #print m.intervals()
        #print m.pitches
        af = AccentFactory()
        a = af.create("jumpbef3")
        self.assertEqual(a.calculate(m), [0, 1, 0, 1, 0, 1, 0])
        a = af.create("jumpbef4")
        self.assertEqual(a.calculate(m), [0, 1, 0, 1, 0, 1, 0])
        a = af.create("jumpbef5")
        self.assertEqual(a.calculate(m), [0, 0, 0, 0, 0, 1, 0])
        a = af.create("jumpbef", threshold=7)
        self.assertEqual(a.calculate(m), [0, 0, 0, 0, 0, 1, 0])
        a = af.create("jumpbef", threshold=8)
        self.assertEqual(a.calculate(m), [0, 0, 0, 0, 0, 0, 0])

        a = af.create("jumpaft3")
        self.assertEqual(a.calculate(m), [0, 0, 1, 0, 1, 0, 1])
        a = af.create("jumpaft4")
        self.assertEqual(a.calculate(m), [0, 0, 1, 0, 1, 0, 1])
        a = af.create("jumpaft5")
        self.assertEqual(a.calculate(m), [0, 0, 0, 0, 0, 0, 1])
        a = af.create("jumpaft", threshold=7)
        self.assertEqual(a.calculate(m), [0, 0, 0, 0, 0, 0, 1])
        a = af.create("jumpaft", threshold=8)
        self.assertEqual(a.calculate(m), [0, 0, 0, 0, 0, 0, 0])
        #print m, acc

        a = af.create("jumpbea3")
        self.assertEqual(a.calculate(m), [0, 1, 1, 1, 1, 1, 1])
        a = af.create("jumpbea4")
        self.assertEqual(a.calculate(m), [0, 1, 1, 1, 1, 1, 1])
        a = af.create("jumpbea5")
        self.assertEqual(a.calculate(m), [0, 0, 0, 0, 0, 1, 1])
        a = af.create("jumpbea", threshold=7)
        self.assertEqual(a.calculate(m), [0, 0, 0, 0, 0, 1, 1])
        a = af.create("jumpbea", threshold=8)
        self.assertEqual(a.calculate(m), [0, 0, 0, 0, 0, 0, 0])

        a = af.create("jumploc", threshold=2, direction_change=False)
        self.assertEqual(a.calculate(m), [0., 0., 1., 0., 1., 0., 0.])

        a = af.create("jumploc", threshold=2, direction_change=True)
        self.assertEqual(a.calculate(m), [0., 0., 1., 0., 0., 0., 0.])

        a = af.create("jumploc", threshold=2, direction_change=True)
        self.assertEqual(a.calculate(m.slice(0, 2)), [0., 0., 0.])

    def testPitchExtremaAccents(self):
        m = self.createTestNoteTrack()
        #print m.intervals()
        #print m.pitches
        af = AccentFactory()
        a = af.create("pextrem")
        self.assertEqual(a.calculate(m), [0., 1.0, 1.0, 0., 0., 0., 0.])
        self.assertEqual(a.calculate(m.slice(0, 1)), [0.0, 0.0])
        #mel = self.prepareTestDataMiles(item=1)
        #p = mel.pitches
        #acc = a.calculate(mel)
        #print "\n".join([str(m) + ":" + str(a) for m,a in zip(p, acc)])

        m1 = self.createTestPitchExtremaNoteTrack()
        #print m1.intervals()
        #print m1.pitches
        a = af.create("pextrmf")
        self.assertEqual(a.calculate(m1), [0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0])
        self.assertEqual(a.calculate(m1.slice(0, 2)), [0.0, 0.0, 0.0])

        a = af.create("pextrst")
        self.assertEqual(a.calculate(m1), [0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0])
        self.assertEqual(a.calculate(m1.slice(0, 3)), [0.0, 0.0, 0.0, 0.0])
        m1.clear()
        self.assertEqual(a.calculate(m1), [])


    def testThomassenAccents(self):
        m = self.createTestNoteTrack()
        m1 = self.createTestPitchExtremaNoteTrack()
        #print m.intervals()
        #TODO: Do a real accents with validated data
        af = AccentFactory()
        a = af.create("thom")
        self.assertEqual(a.calculate(m), [0.355, 0.29, 0.0, 0.33, 0.2211, 0.2211, 0.5561])
        self.assertEqual(a.calculate(m1), [0.355, 0.29, 0.0, 0.33, 0.67, 0.0, 0.0])
        a = af.create("thom", threshold=.5)
        self.assertEqual(a.calculate(m1), [0., 0., 0.0, 0.0, 1., 0.0, 0.0])

    def testDurationAccents(self):
        af = AccentFactory()
        #mel = self.prepareTestDataMiles()
        #mel = mel.slice(0,25)
        #a = af.create("long-ioi", threshold=1.41, offset=0.04, classes=None, window_size=5)
        #a1 = a.calculate(mel)
        #a = af.create("long-ioi", threshold=2, offset=0.04, classes=None, window_size=5)
        #a2 = a.calculate(mel)
        #print np.sum(np.abs(np.array(a1)-np.array(a2)))
        m = self.createTestNoteTrack()
        af = AccentFactory()
        a = af.create("longpr")
        self.assertEqual(a.calculate(m), [0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0])
        a = af.create("long2pr")
        self.assertEqual(a.calculate(m), [0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0])
        a = af.create("longmod")
        self.assertEqual(a.calculate(m), [1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0])
        a = af.create("long2mod")
        self.assertEqual(a.calculate(m), [0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0])
        #print a.calculate(m)
        a = af.create("long-ioi", threshold=2, offset=0, classes="abs", window_size=-1)
        self.assertEqual(a.calculate(m), [1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0])

        #a = af.create("long-ioi", threshold=2, offset=0, classes="abs", window_size=3)
        #self.assertEqual(a.calculate(m), [0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0])
        #print a.calculate(m)
        #mel = self.prepareTestDataEsac()

    def testStructureAccents(self):
        #m = self.createTestNoteTrack()
        af = AccentFactory()
        a = af.create("phrasbeg")
        mel = self.prepareTestDataMiles()
        phrases = mel.getSection(sect_type="PHRASE")
        begins = a.calculate(mel)
        a = af.create("phrasend")
        ends = a.calculate(mel)
        a = af.create("phrasbor")
        borders = a.calculate(mel)
        a = af.create("phrase")
        params = {"positions":["first", "end"], "baseAccent":2.}
        a.setParams(params)
        borders_gen = a.calculate(mel)
        for s in phrases:
            self.assertEqual(begins[s.startID], 1.0)
            self.assertEqual(ends[s.endID], 1.0)
            self.assertEqual(borders[s.startID], 1.0)
            self.assertEqual(borders[s.endID], 1.0)
            self.assertEqual(borders_gen[s.startID], 2.0)
            self.assertEqual(borders_gen[s.endID], 2.0)
        a = af.create("bars")
        params = {"positions":["first"]}
        a.setParams(params)
        bars_beg = a.calculate(mel)
        bars = mel.getSection(sect_type="BAR")
        for b in bars:
            self.assertEqual(bars_beg[b.startID], 1.0)
        a = af.create("chords")
        params = {"positions":["first"]}
        a.setParams(params)
        chords_beg = a.calculate(mel)
        chords = mel.getSection(sect_type="CHORD")
        for b in chords:
            self.assertEqual(chords_beg[b.startID], 1.0)

    def testMetricalAccents(self):
        mg = self.prepareStrangeMeterGrid()
        af = AccentFactory()
        a = af.create("beat1")
        self.assertEqual(a.calculate(mg), [1.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0])
        a = af.create("beat13")
        self.assertEqual(a.calculate(mg), [1.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 1.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 1.0, 0.0, 1.0, 0.0, 1.0, 0.0])
        a = af.create("beatall")
        self.assertEqual(a.calculate(mg), [1.0]*26)

    def testSyncopationAccents(self):
        mg = self.prepareStrangeMeterGrid(syncopated=True, division=2)
        af = AccentFactory()
        a = af.create("sync1")
        self.assertEqual(a.calculate(mg), [0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0])
        a = af.create("sync13")
        self.assertEqual(a.calculate(mg), [0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 1.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 1.0, 0.0, 1.0, 0.0, 1.0, 0.0, 0.0])
        a = af.create("sync1234")
        tmp = [1.0]*25
        tmp.append(0)
        self.assertEqual(a.calculate(mg), tmp)

        a = af.create("syncall")
        self.assertEqual(a.calculate(mg), [1.0]*26)
        mg = self.prepareStrangeMeterGrid(syncopated=True, division=4)
        a = af.create("syncall")
        self.assertEqual(a.calculate(mg), [1.0]*26)
        #mpos =  mel.getMetricalPositions()
        #acc = a.calculate(mel)
        #print "\n".join([str(m) + ":" + str(a) for m,a in zip(mpos, acc)])
        #print a.calculate(mel)

    def testSwingMarkers(self):
        mel = self.prepareTestDataMiles(item=1)
        af = AccentFactory()
        a = af.create("swing-markers")
        a = a.calculate(mel)
        #a = af.create("swing-markers", max_div=3, only_full=True)
        #a = a.calculate(mel)

    def testHarmonyAccents(self):
        mel = self.prepareTestDataMiles(item=1)
        #cpt = mel.getChordalPitchTypes()
        af = AccentFactory()
        a = af.create("triad")
        #print "\n".join([str(m) + ":" + str(a) for m,a in zip(cpt, acc)])
        self.assertEqual(a.calculate(mel)[0:26], [0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0])
        a = af.create("inchord")
        self.assertEqual(a.calculate(mel)[0:26], [0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0])
        a = af.create("outchord")
        self.assertEqual(a.calculate(mel)[0:26], [1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 1.0])

    def testMonsterAccents(self):
        mel = self.prepareTestDataMiles(item=1)
        af = AccentFactory()
        a = af.create("monster")
        #print a.calculate(mel)
        accents = ["jumpaft3", "pextrem", "beat13"]
        weights = [1, 1, 1]
        ac = AccentCombinator(accents=accents, weights=weights, method="sum" )
        combi_v = ac.calculate(mel)
        a1 = af.create("jumpaft3")
        a2 = af.create("pextrem")
        a3 = af.create("beat13")
        a1_val = a1.calculate(mel)
        a2_val = a2.calculate(mel)
        a3_val = a3.calculate(mel)
        a_tot = [p+q for p, q in zip(a1_val, a2_val)]
        a_tot = [p+q for p, q in zip(a_tot, a3_val)]
        self.assertEqual(combi_v, a_tot)

        ac.method="max"
        combi_v = ac.calculate(mel)
        a1 = af.create("jumpaft3")
        a2 = af.create("pextrem")
        a3 = af.create("beat13")
        a1_val = a1.calculate(mel)
        a2_val = a2.calculate(mel)
        a3_val = a3.calculate(mel)
        a_tot = [max(p, q) for p, q in zip(a1_val, a2_val)]
        a_tot = [max(p, q) for p, q in zip(a_tot, a3_val)]
        self.assertEqual(combi_v, a_tot)

    def testGaussStandardAccents(self):
        r = self.createTestRhythm()
        af = AccentFactory()
        a = af.create("gauss_standard", a_min=2., a_maj=3., sigma=0.04)

        a.setBaseAccent(1.0)
        #print a.rhythm
        self.assertEqual(a.calculate(r), [2, 1, 1, 3, 1, 1, 2])
        # valid calls
        #test_file = os.path.join(root_path(), "input_output\\test\\bb_normal_nd.csv")
        #tcsvr = TonyCSVReader(test_file)
        #print a.calculate(tcsvr.melody)
        #a.setRhythm(tcsvr.melody)
        #test_accents = [2, 1, 2, 1, 2, 1, 1, 1, 1, 1, 3, 2, 1, 1, 1, 3, 3, 2, 1, 1, 1, 1, 3, 3, 1, 2, 1, 3, 1, 1, 1, 1, 3, 3, 1, 1, 1, 1, 3, 3, 2, 1, 1, 1, 3, 3, 2, 1, 1, 1, 1, 3, 3, 2, 1, 1, 3, 1, 1, 2, 1, 3, 3, 1, 1, 1, 1, 3, 3, 3, 1, 1, 1, 3, 3, 3, 2, 1, 2, 1, 1, 3, 3, 1, 1, 1, 2]
        #self.assertEqual(a.calculate("gauss-standard", params=params_gauss), test_accents)


    def testAccentAggregator(self):

        ag = AccentAggregator()
        r = self.createIsoRhythm()

        ag.createAndAdd("gauss-standard", a_min=2, a_maj=3, sigma=0.04)
        ag.createAndAdd("const", baseAccent=0)
        ag.createAndAdd("external", weights=[5. for e in r])
        ag.createAndAdd("periodic", period=3, phase=1, weight=1)
        #print ag
        sum_result = [7.0, 7.0, 6.0, 6.0, 7.0, 6.0, 6.0, 7.0, 6.0, 7.0]
        sum_norm_result = [v/7.0 for v in sum_result]
        sum_norm_result2 = [v/8.0 for v in sum_result]
        self.assertEqual(ag.calculate(r), sum_result)
        self.assertEqual(ag.calculate(r, method="max"), [5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0])
        self.assertEqual(ag.calculate(r, method="sum-norm"), sum_norm_result)
        self.assertEqual(ag.calculate(r, method="sum-norm2"), sum_norm_result2)

if __name__ == "__main__":
    #unittest.main()
    ta = TestAccents()    
    ta.testPitchExtremaAccents()
    pass
