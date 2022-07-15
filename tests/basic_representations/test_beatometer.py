#!/usr/bin/env python

""" Unit test for class Beatometer"""
import os
import unittest

import pytest

from melospy.basic_representations.beatometer import *
from melospy.basic_representations.beatometer_param import *
from melospy.input_output.melody_importer import *
from melospy.input_output.tony_csv_reader import *
from tests.rootpath import *

class TestBeatometer( unittest.TestCase ):

    def prepareTestDataMiles(self):
        dbpath =  add_data_path("wjazzd.db")
        dbinfo = DBInfo.fromDict({'path': dbpath, "use": True})
        #mi = MelodyImporter(tunes=tunes, path="", dbinfo=dbinfo)
        mi = MelodyImporter(tunes = "test-db", path=dbpath, dbinfo=dbinfo )
        mel = next(mi.fetcher())
        return mel

    def prepareTestDataEsac(self):
        dbpath =  add_data_path()("esac.db")
        dbinfo = DBInfo.fromDict({'path': dbpath, "use": True})
        #mi = MelodyImporter(tunes=tunes, path="", dbinfo=dbinfo)
        mi = MelodyImporter(tunes = "test-esac", path=dbpath, dbinfo=dbinfo )
        mel = next(mi.fetcher())
        return mel

    def prepareTestDataTony(self, which=1):
        if which==1:
            test_file = add_data_path("bb_normal_nd.csv")
        elif which==2:
            test_file = add_data_path("mm_normal_nd.csv")
        else:
            test_file = add_data_path(which)
        tcsvr = TonyCSVReader(test_file, method="dummy")
        return tcsvr.melody

    def prepareTestRhythmWithShorties(self, jitter=0.0):
        onsets = [0, 0.5, 1.0, 1.5, 2.0, 2.49, 2.5]
        r = Rhythm.fromOnsets(onsets)
        return r

    def prepareTestRhythm(self, timebase=.5, repeat=1, jitter=0.0):
        return Rhythm.fromString("11111111", timebase=timebase, repeat=repeat, jitter=jitter)

    def prepareTestRhythmClave(self, timebase=.25, repeat=1, jitter=0.0):
        return Rhythm.fromString("10010010", timebase=timebase, repeat=repeat, jitter=jitter)

    def prepareTestRhythmDotted(self, timebase=.25, repeat=1, jitter=0.0):
        return Rhythm.fromString("1001", timebase=timebase, repeat=repeat, jitter=jitter)

    def prepareTestRhythm532(self, timebase=.25, repeat=1, jitter=0.0):
        return Rhythm.fromString("10010", timebase=timebase, repeat=repeat, jitter=jitter)

    def prepareTestRhythm523(self, timebase=.25, repeat=1, jitter=0.0):
        return Rhythm.fromString("10100", timebase=timebase, repeat=repeat, jitter=jitter)

    def prepareTestRhythmHappyBirthday(self, variant=0, timebase=.15, repeat=1, jitter=0.0):
        variants = ["1001|1000.1000.1000|10000000.1001|1000.1000.1000|10000000.1001|1000.1000.1001|1000.1000.1001|1000.1000.1000|1000.0000",
                    "1010|1000.1000.1000|10000000.1010|1000.1000.1000|10000000.1010|1000.1000.1010|1000.1000.1010|1000.1000.1000|1000.0000",
                    "1000|1000.1000.1000|10000000.1000|1000.1000.1000|10000000.1000|1000.1000.1000|1000.1000.1000|1000.1000.1000|1000.0000"
                    ]
        return Rhythm.fromString(variants[variant], timebase=timebase, repeat=repeat, jitter=jitter)

    def prepareTestRhythmSwing(self, timebase=.5, repeat=1, jitter=0.0):
        return Rhythm.fromString("100.101.100.101", timebase=timebase/3, repeat=repeat, jitter=jitter)

    def prepareTestRhythmTempoChange(self, timebase1=.5, timebase2=.67, repeat=1, jitter=0.0):
        r1 = Rhythm.fromString("11111111", timebase=timebase1, repeat=repeat, jitter=jitter)
        r2 = Rhythm.fromString("11111111", timebase=timebase2, repeat=repeat, jitter=jitter)
        return r1.concat(r2, timebase1)

    def prepareTestRhythmMeterChange(self, timebase=.5, period1=4, period2 = 2, repeat=1, jitter=0.0):
        p1 = ("1"+"0"*(period1-1))*4
        p2 = ("1"+"0"*(period2-1))*4
        #print p1+p2
        return Rhythm.fromString(p1+p2, timebase=timebase, repeat=repeat, jitter=jitter)

    def prepareTestRhythmSwing2(self, jitter=0.0):
        e  = RhythmEvent(0,   0, Signature(4, 4) )
        e1 = RhythmEvent(0.3, 0)
        e2 = RhythmEvent(0.5, 0)
        e3 = RhythmEvent(0.8, 0)
        e4 = RhythmEvent(1.0, 0)
        e5 = RhythmEvent(1.3, 0)
        e6 = RhythmEvent(1.5, 0)
        r = Rhythm()
        r.append(e).append(e1).append(e2).append(e3).append(e4).append(e5).append(e6)
        return r

    def testConstructor(self):
        r = self.prepareTestRhythmWithShorties()
        bm = Beatometer(r)
        mg = bm.annotate()
        self.assertEqual(len(mg), len(r))
        del bm, mg
        #bm = Beatometer()
        #mg = bm.annotate()
        #self.assertEqual(mg, None)
        #bm.setRhythm(r)
        #mg = bm.getMeterGrid()
        #test_mg = MeterGrid.createIsoMeter(len(r))
        #self.assertEqual(mg, test_mg)
        #self.assertEqual(len(r)-len(bm.removeShorties(r, threshold=.1)),1)
        #bm.calculate()

    def testTimeRangeForRhythm(self, rhythm = None, gbp = None, t0=.10, t1=.90, dt=.025, jitter=0, repeat=8):

        if rhythm == None:
            return
        if gbp == None:
            setDefaultSigma(.03)
            gbp = GaussBeatParameters()
            gbp.setValue("spontaneous_tempo", .5)
            gbp.setValue("subjective_presence", 3.0)
            gbp.setValue("domain", "uniform")
            gbp.setValue("deltaT", 0.005)
        #print "Testing: {}, with: ({}, {}, {})".format(rhythm, t0, t1, dt)
        tb = t0
        while tb<t1:
            if rhythm =="iso":
                r = self.prepareTestRhythm(jitter=jitter, timebase=tb, repeat=repeat)
            elif rhythm == "dotted":
                r = self.prepareTestRhythmDotted(jitter=jitter, timebase=tb, repeat=repeat)
            elif rhythm == "clave":
                r = self.prepareTestRhythmClave(jitter=jitter, timebase=tb, repeat=repeat)
            elif rhythm == "532":
                r = self.prepareTestRhythm532(jitter=jitter, timebase=tb, repeat=repeat)
            elif rhythm == "523":
                r = self.prepareTestRhythm523(jitter=jitter, timebase=tb, repeat=repeat)
            elif rhythm == "swing":
                r = self.prepareTestRhythmSwing(jitter=jitter, timebase=tb, repeat=repeat)
            elif rhythm == "happy1":
                r = self.prepareTestRhythmHappyBirthday(variant=0, jitter=jitter, timebase=tb, repeat=repeat)
            elif rhythm == "happy2":
                r = self.prepareTestRhythmHappyBirthday(variant=1, jitter=jitter, timebase=tb, repeat=repeat)
            elif rhythm == "happy3":
                r = self.prepareTestRhythmHappyBirthday(variant=2, jitter=jitter, timebase=tb, repeat=repeat)
            #filename = "auto_corr_"+str(int(tb*1000))+ ".csv"
            #bm.writeAutoCorrelation(filename)
            bm = GaussBeat(r, gbp, debug=BeatometerDebugParams())
            cands = bm.calculate()
            #print "tb: {}".format(tb)
            #for c in cands:
                #print "Tb:{}, Tempo:{}, rel. tmpo:{}, bp:{}, period: {}, mp:{}".format(tb, round(beat_dur, 3), round(beat_dur/tb, 3), round(beat_phase, 3), period, round(meter_phase, 3))
            #    print "...Rel. T:{} {}".format(round(c.beat_dur/tb,3), c)
            tb += dt

    @pytest.mark.skip(reason="Too long")
    def testGaussBeatIso(self):
        self.testTimeRangeForRhythm(rhythm="iso")

    @pytest.mark.skip(reason="Too long")
    def testGaussBeatDotted(self):
        self.testTimeRangeForRhythm(rhythm="dotted")

    @pytest.mark.skip(reason="Too long")
    def testGaussBeatClave(self):
        self.testTimeRangeForRhythm(rhythm="clave")

    @pytest.mark.skip(reason="Too long")
    def testGaussBeat5(self):
        print("-"*40)
        print("3+2")
        self.testTimeRangeForRhythm(rhythm="532")
        print("-"*40)
        print("2+3")
        self.testTimeRangeForRhythm(rhythm="523")

    @pytest.mark.skip(reason="Too long")
    def testGaussBeat(self):
        setDefaultSigma(.03)
        gbp = GaussBeatParameters()
        #wr = {"method":"gauss-standard", "params":{"a_min":2, "a_maj":3, "sigma":def_sigma.sigma}}
        #params = {"sigma":def_sigma.sigma, "beta":2.0, "deltaT":.01, "subjective-presence":2.0, "weight-rules":wr, "min-ioi":2*def_sigma.sigma, "domain":"jazz"}
        gbp.setValue("spontaneous_tempo", .5)
        gbp.setValue("subjective_presence", 5.0)
        gbp.setValue("domain", "folk")
        gbp.setValue("deltaT", 0.01)

        #r = self.prepareTestRhythm(jitter=.01, repeat=4)
        #r = self.prepareTestRhythmSwing(jitter=.04, repeat=16)
        #r = self.prepareTestRhythmHappyBirthday(jitter=0.04, variant=0, repeat=1, timebase=.15)
        r = self.prepareTestDataTony(2).withoutShorties(threshold=.1)
        #r = self.prepareTestDataMiles().withoutShorties(threshold=.1)
        #r = self.prepareTestRhythm532(jitter=.00, repeat=16, timebase=.8)
        #r = self.prepareTestRhythmTempoChange()
        #r = self.prepareTestRhythm(timebase=.25, jitter=.0, repeat=4)
        #r = self.prepareTestRhythmTempoChange(timebase1=.5, timebase2=.75)

        #r = self.prepareTestDataEsac()
        bm = GaussBeat(r, gbp)
        #bm.writeTimeLine("mm_normal_tl.csv")
        #print r
        #print "\n".join(["("+str(e[0]) + ", " + str(e[1])+")" for e in zip(r.events, bm.getWeights())])
        cands = bm.calculate()
        #print bm.getWeights()
        #print "Cands: ",cands
        return

    def testBeatometer(self):
        setDefaultSigma(.03)
        #wr = {"method":"gauss-standard", "params":{"a_min":2, "a_maj":3, "sigma":def_sigma.sigma}}
        #params = {"sigma":def_sigma.sigma, "deltaT":.01, "subjective-presence":2.0, "weight-rules":wr, "min-ioi":2*def_sigma.sigma, "domain":"jazz", "window-size":6.0, "hop-size":1.0, "glue-sigma":.1, "glue-threshold":1.8, "single_meter":False}
        bmp = BeatometerParameters()
        bmp.setValue("spontaneous_tempo", .5)
        bmp.setValue("window_size", 3.)
        bmp.setValue("subjective_presence", 3.0)
        bmp.setValue("domain", "folk")
        bmp.setValue("deltaT", 0.01)
        bmp.setValue("min_tempo", 1.)
        bmp.setValue("single_meter", True)
        bmp.setValue("propagate", False)
        #bmp.setValue("glue_sigma", .001)
        #bmp.setValue("glue_threshold", 1.5)
        r = self.prepareTestRhythm(jitter=.0, repeat=4)
        #r = self.prepareTestRhythmSwing(jitter=.00, repeat=16)
        #r = self.prepareTestRhythmHappyBirthday(jitter=0.00, variant=0, repeat=1, timebase=.15)
        #r = self.prepareTestDataTony(2)
        #r = self.prepareTestDataMiles()
        #r = self.prepareTestDataEsac()
        #r = self.prepareTestRhythm5(jitter=.00, repeat=16)
        #r = self.prepareTestRhythmTempoChange(timebase1=.67, timebase2=.5)
        #r = self.prepareTestRhythmMeterChange(timebase=.16, period1=3, period2=4, repeat=2)
        #r = self.prepareTestRhythm532(jitter=.00, repeat=16, timebase=.5)
        #print "before construction"
        bm = Beatometer(r, bmp)
        bt = bm.calculate(method="gaussification")
        #print bt
        #bt = TimeSeries(bt)
        #ts = TimeSeries(r)
        #print bt.times
        #print ts.times
        #print mean(diff(bt.times)), sd(diff(bt.times))
        #bt.magneticMove(ts, max_dist=.10)
        #print mean(diff(bt.times)), sd(diff(bt.times))
        #print "="*60
        #mg = bm.annotate(method="gaussification")
        #mel = r.clone().annotateMeter(mg)
        #print mel
        #print r
        #r = self.prepareTestRhythmSwing(jitter=.02, repeat=16)
        #bm = Beatometer(r, params, debug=False)
        #bm.calculate(method="gaussification")
        #bm = Beatometer(mel, params, debug=False)
        #bm.calculate(method="gaussification")

        #print round(mel.getMeanTempo(bpm=False)[0],1)
        #bm = Beatometer(mel, params)
        #bm.calculate(method="gaussification")
if __name__ == "__main__":
    unittest.main()
