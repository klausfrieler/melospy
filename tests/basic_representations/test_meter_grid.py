#!/usr/bin/env python

""" Unit test for class MeterGrid"""
import os
import unittest

from melospy.basic_representations.meter_grid import *
from melospy.basic_representations.metrical_note_event import *
from melospy.input_output.melody_importer import *
from melospy.rootpath import root_path
from melospy.tools.commandline_tools.dbinfo import *


def prepareTestData(performer, title, titleaddon=None, solopart=None):
    dbpath =  os.path.join(root_path(), "analysis/data/FINAL/DB/wjazzd.db")

    dbinfo = DBInfo.fromDict({'path': dbpath, "use": True, "type":"sqlite3", "content-type":"SV", "version":2})
    query = MelodyImporter.queryFromSoloInfo(performer, title, titleaddon, solopart)
    mi = MelodyImporter(tunes=query, path=dbpath, dbinfo=dbinfo )
    mel = next(mi.fetcher())
    return mel

class TestMeterGrid( unittest.TestCase ):

    def prepareTestDataMiles(self, item=0):
        dbpath =  os.path.join(root_path(), "analysis/data/PREFINAL/DB/wjazzd.db")
        dbinfo = DBInfo.fromDict({'path': dbpath, "use": True, "type":"sqlite3"})
        #mi = MelodyImporter(tunes=tunes, path="", dbinfo=dbinfo)
        mi = MelodyImporter(tunes="test-db-"+str(item), path=dbpath, dbinfo=dbinfo )
        mel = next(mi.fetcher())
        return mel

    def prepareStrangeMeterGrid(self):
        mi = MeterInfo(4, 4)
        bi = BeatInfo()
        mc = MetricalContext(bi, mi)
        bis = [BeatInfo(2, .4), BeatInfo(3, .6), BeatInfo(5, .4), BeatInfo(6, .6)]
        mg = MeterGrid()
        for i in range(4):
            duration = .5
            onset    = 1 + i*duration
            bi = bis[i % len(bis)].clone()
            mc.setBeatInfo(bi)
            period = bi.getTatums()
            #print "-------------------------------------------"
            for j in range(period):
                dur = duration/period
                #print i/4 + 1, i % 4 + 1, j + 1, dur, onset + j*dur
                mp = MetricalPosition(i/4 + 1, i % 4 + 1, j + 1, 0, mc.clone())
                me = MetricalEvent(onset + j*dur, mp, dur)
                mg.append(me)
        return mg

    def testCompress(self):
        #print mg
        mg = self.prepareStrangeMeterGrid()
        mg_clone= mg.clone()
        mg.standardize()
        #print mg
        #print "Compressing......"
        mg.compress()
        for i in range(len(mg)):
            self.assertEqual(mg_clone[i], mg[i])

    def testDurationClassification(self):
        mi = MeterInfo(4, 4)
        bi = BeatInfo(4, .75)
        mc = MetricalContext(bi, mi)
        mg = MeterGrid()

        mp = MetricalPosition(1, 1, 1, 0, mc)
        me = MetricalEvent(0, mp, 4, None)
        mg.append(me)

        mp = MetricalPosition(1, 1, 2, 0, mc)
        me = MetricalEvent(0.125, mp, 2, None)
        mg.append(me)

        mp = MetricalPosition(1, 1, 4, 0, mc)
        me = MetricalEvent(.375, mp, 1, None)
        mg.append(me)

        mp = MetricalPosition(1, 2, 4, 0, mc)
        me = MetricalEvent(.875, mp, 1.0/2, None)
        mg.append(me)

        mp = MetricalPosition(1, 4, 4, 0, mc)
        me = MetricalEvent(1.875, mp, 1.0/4, None)
        mg.append(me)

        mp = MetricalPosition(3, 4, 4, 0, mc)
        me = MetricalEvent(3.875, mp, 1.0/8, None)
        mg.append(me)

        mp = MetricalPosition(10, 1, 4, 0, mc)
        me = MetricalEvent(7.875, mp, 1.0/16, None)

        mg.append(me)
        #print "ioi.abs"
        dc = mg.durationClassification(type="ioi", mode="abs")
        self.assertEqual(dc, [-2, -1, 0, 1, 2, 2])
        #print "ioi.rel"
        dc = mg.durationClassification(type="ioi", mode="rel")
        self.assertEqual(dc, [-2, -1, 0, 0, 1, 2])
        #print "dur.abs"
        dc = mg.durationClassification(type="dur", mode="abs")
        self.assertEqual(dc, [2, 2, 1, 0, -1, -2, -2])
        #print "dur.rel"
        dc = mg.durationClassification(type="dur", mode="rel")
        self.assertEqual(dc, [2, 1, 0, 0, -1, -2, -2])


    def testMetricalWeights(self):
        mi = MeterInfo(4, 4)
        bi = BeatInfo(4, .5)
        mc = MetricalContext(bi, mi)
        mg = MeterGrid()

        mp = MetricalPosition(1, 1, 1, 0, mc)
        me = MetricalEvent(0, mp, 4, None)
        mg.append(me)

        mp = MetricalPosition(1, 1, 3, 0, mc)
        me = MetricalEvent(0.25, mp, 2, None)
        mg.append(me)

        mp = MetricalPosition(1, 2, 1, 0, mc)
        me = MetricalEvent(.5, mp, 1, None)
        mg.append(me)

        mp = MetricalPosition(1, 2, 3, 0, mc)
        me = MetricalEvent(.75, mp, 1.0/2, None)
        mg.append(me)

        mp = MetricalPosition(1, 3, 1, 0, mc)
        me = MetricalEvent(1.0, mp, 1.0/4, None)
        mg.append(me)

        mp = MetricalPosition(1, 3, 3, 0, mc)
        me = MetricalEvent(1.25, mp, 1.0/8, None)
        mg.append(me)

        mp = MetricalPosition(1, 4, 1, 0, mc)
        me = MetricalEvent(1.5, mp, 1.0/16, None)
        mg.append(me)

        mp = MetricalPosition(1, 4, 3, 0, mc)
        me = MetricalEvent(1.75, mp, 1.0/16, None)
        mg.append(me)

        mp = MetricalPosition(1, 4, 4, 0, mc)
        me = MetricalEvent(1.875, mp, 1.0/16, None)
        mg.append(me)

        mw = mg.getMetricalWeights()
        self.assertEqual(mw, [2, 0, 1, 0, 2, 0, 1, 0, 0])

    def getTestGrid(self, beatString, division=4):
        mi = MeterInfo(4, 4)
        bi = BeatInfo(division, 1)
        mc = MetricalContext(bi, mi)
        mg = MeterGrid()
        r = Rhythm.fromString(beatString, 0.250/division, start=1.0)
        for ev in r:
            mp = MetricalPosition(1, 1, 1, 0, mc).fromDecimal(ev.onset, mc)
            me = MetricalEvent(ev.onset, mp, .25, None)
            mg.append(me)
        return mg

    def getTestGrid2(self, beatString, division=4):
        mg = MeterGrid.fromString(beatString, div=division)
        return mg

    def testSyncopations(self):
        mg = self.getTestGrid("1001100")
        self.assertEqual(mg.syncopations(), [0, 0, 0])
        self.assertEqual(mg.syncopicity(), 0)
        mg = self.getTestGrid("10010010")
        self.assertEqual(mg.syncopations(), [0, 1, 1])
        self.assertEqual(mg.syncopicity(), 2.0/3.0)
        mg = self.getTestGrid("1101100")
        self.assertEqual(mg.syncopations(), [0, 1, 0, 0])
        self.assertEqual(mg.syncopicity(), 1.0/4.0)
        mg = self.getTestGrid("110101001")
        self.assertEqual(mg.syncopations(), [0, 1, 1, 1, 0])
        self.assertEqual(mg.syncopicity(), 3.0/5.0)

    def testBeatChunks(self):
        mg2 = self.getTestGrid("1001101010101001")
        #print mg2
        bc = mg2.getBeatChunksRaw()
        self.assertEqual(len(bc), 4)
        self.assertEqual(sum(len(_) for _ in bc), len(mg2))
        #print "\n".join([",".join([str(e.getMetricalPosition()) for e in _]) for _ in bc])
        #cf = BeatChunkFilterDivision(2)
        #print type(cf)
        bc = mg2.getBeatChunksRaw(chunk_filter=BeatChunkFilterDivision(divisions=2))
        self.assertEqual(len(bc), 0)

        bc = mg2.getBeatChunksRaw(chunk_filter=BeatChunkFilterDivision(divisions=4))
        self.assertEqual(len(bc), 4)

        #print "\n".join([",".join([str(e.getMetricalPosition()) for e in _]) for _ in bc])
        bc = mg2.getBeatChunksRaw(chunk_filter=BeatChunkFilterPattern(pattern="first_last"))
        self.assertEqual(len(bc), 2)
        bcfp = BeatChunkFilterPattern(pattern="first_last")
        bcfd = BeatChunkFilterDivision(divisions=4)
        bcfc = BeatChunkFilterCombi([bcfp, bcfd])
        bc = mg2.getBeatChunksRaw(chunk_filter=bcfc)
        #print "\n".join([",".join([str(e.getMetricalPosition()) for e in _]) for _ in bc])
        self.assertEqual(len(bc), 2)
        bcfp = BeatChunkFilterPattern(pattern=[1, 0, 1, 0])
        bcfd = BeatChunkFilterDivision(divisions=4)
        bcfc = BeatChunkFilterCombi([bcfp, bcfd])
        bc = mg2.getBeatChunksRaw(chunk_filter=bcfc)
        self.assertEqual(len(bc), 2)
        #print "\n".join([",".join([str(e.getMetricalPosition()) for e in _]) for _ in bc])

        bcfp = BeatChunkFilterPattern(pattern=[1, 0, 1, 0], invert=True)
        bcfd = BeatChunkFilterDivision(divisions=23, invert=True)
        bcfc = BeatChunkFilterCombi([bcfp, bcfd])
        bc = mg2.getBeatChunksRaw(chunk_filter=bcfc)
        self.assertEqual(len(bc), 2)

        bcfp = BeatChunkFilterPattern(pattern=[1, 0, 1, 0], invert=True)
        bcfd = BeatChunkFilterDivision(divisions=23, invert=True)
        bcfc = BeatChunkFilterCombi([bcfp, bcfd], invert=True)
        bc = mg2.getBeatChunksRaw(chunk_filter=bcfc)
        self.assertEqual(len(bc), 2)

    def testSwingRatio(self):
        #mg = MeterGrid.createIsoMeter(8, div=2, tempo=60, start=1.2)
        #sr = mg.getSwingRatios(average = False)
        #self.assertEqual(len(sr), 4)
        #self.assertEqual(sum(sr)/len(sr), 1.0)
        mg2 = self.getTestGrid2("1001111010101011", 2)
        # print "MG", mg2, len(mg2)
        #sr = mg2.getSwingRatios(average=True)
        #self.assertEqual(sr, 1.0)
        cands = mg2.getSwingCandidates(only_full=True)
        self.assertEqual(cands, [2, 3, 8, 9])
        cands = mg2.getSwingCandidates(only_full=False)
        self.assertEqual(cands, [1, 2, 3, 8, 9])

    def testConstructor(self):
        """ Test assures constructor works properly"""
        #4/4 signature, period = 4, equal beat proportions
        mi = MeterInfo(4, 4)
        #four sixteenth per Beat, .5 sec per beat = 120 bpm
        bi = BeatInfo(4, .5)
        mc = MetricalContext(bi, mi)
        mp = MetricalPosition(1, 2, 3, 0, mc)
        me = MetricalEvent(0, mp, 1.0/3, None)
        C4 = 60

        mg = MeterGrid()
        mg.append(me)
        mg1 = MeterGrid(mg)
        self.assertEqual(mg.toString(), mg1.toString())
        #test toString() method
        self.assertEqual(mg.toString(), me.toString())
        self.assertEqual(mg.getEventBeatDurations(), [0.5])
        #see if we are only allowed to add the right objects
        self.assertRaises(Exception, mg.append, mi)
        #mg.append(e1).append(e2).append(e3)

        #see if we can add objetcs of derived classes
        mne = MetricalNoteEvent(0.5, C4, MetricalPosition(1, 3, 3, 0, mc), 1.0/2, None)
        mg.append(mne)
        self.assertEqual(len(mg), 2)

        #next event should be later in time
        self.assertRaises(Exception, mg.append, me)

        #next event should be later in time, also metrically
        mne = MetricalNoteEvent(0.5, C4, MetricalPosition(1, 2, 3, 0, mc), 1.0/2, None)
        self.assertRaises(Exception, mg.append, me)

        #consistency checks
        #first: inconsistent BeatInfo
        me = MetricalEvent(0.7, MetricalPosition(1, 3, 4, 0, MetricalContext(BeatInfo(4, .7), mi)), 1.0/3, None)
        self.assertRaises(Exception, mg.append, me)
        #second: inconsistent MeterInfo
        me = MetricalEvent(0.7, MetricalPosition(1, 3, 4, 0, MetricalContext(bi, MeterInfo(3, 4))), 1.0/3, None)
        self.assertRaises(Exception, mg.append, me)

        #test deep copying
        t = mg.clone()
        mg.shift(1.5)

        #should not have changed start time
        self.assertEqual(mg.startTime(), 1.5)

        #test some various methods
        self.assertEqual(mg.getDurationTatums(), [3, 4])
        self.assertEqual(mg.projection("durtatum"), [3, 4])
        self.assertRaises(Exception, mg.projection, 5)
        self.assertRaises(Exception, mg.projection, "r")
        self.assertEqual(mg.getMetricalIOIsDecimal(), [0.25])
        #print mg.getMetricalPositionsDecimal()

        #test transation of bar numbers
        mg.shiftbar(300)
        self.assertEqual(mg[0].getMetricalPosition().getBar(), 301)
        self.assertRaises(Exception, mg.shiftbar, "r")

        #get rid of it!
        mg.clear()
        self.assertEqual(len(mg), 0)
        self.assertEqual(mg.isEmpty(), True)

        #add a lot more of events
        bis = [BeatInfo(2, .4), BeatInfo(3, .6), BeatInfo(5, .4), BeatInfo(6, .6)]
        for i in range(16):
            duration = 1./8
            onset    = 1 + i*duration
            mc = mc.clone().setBeatInfo(bis[i % len(bis)].clone())
            mp1 = MetricalPosition( i + 1, 1, 2, 0, mc)
            me = MetricalEvent(onset, mp1, duration/2)
            mg.append(me)
        #print mg
        #bc = mg.getBeatChunks(div_filter=None, grid_pattern="complete")
        #print "\n".join([",".join([str(e.getMetricalPosition()) for e in _]) for _ in bc])
        #self.assertEqual(sum(len(_) for _ in bc), len(mg))


        #print "\n".join([",".join([str(e.getMetricalPosition()) for e in _]) for _ in bc])
        #print mg.division_complexity()
        self.assertEqual(mg.binary_rhythm(as_string=False, flat=False), [[0, 1], [0, 1, 0], [0, 1, 0, 0, 0], [0, 1, 0, 0, 0, 0], [0, 1], [0, 1, 0], [0, 1, 0, 0, 0], [0, 1, 0, 0, 0, 0], [0, 1], [0, 1, 0], [0, 1, 0, 0, 0], [0, 1, 0, 0, 0, 0], [0, 1], [0, 1, 0], [0, 1, 0, 0, 0], [0, 1, 0, 0, 0, 0]])
        self.assertEqual(mg.binary_rhythm(as_string=False, flat=True), [0, 1, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0])
        self.assertEqual(mg.binary_rhythm(as_string=True, flat=False), ['01', '010', '01000', '010000', '01', '010', '01000', '010000', '01', '010', '01000', '010000', '01', '010', '01000', '010000'])
        self.assertEqual(mg.binary_rhythm(as_string=True, flat=True, sep="."), "01.010.01000.010000.01.010.01000.010000.01.010.01000.010000.01.010.01000.010000")
        self.assertEqual(mg.binary_rhythm(as_string=True, flat=True, sep="|"), "01|010|01000|010000|01|010|01000|010000|01|010|01000|010000|01|010|01000|010000")
        self.assertEqual(mg.division_complexity(), 1.0)
        self.assertEqual(mg.compression_complexity(), 1.0)
        self.assertEqual(mg.metric_complexity(), 1.0)
        #test len, leastCommonTatum
        self.assertEqual(len(mg), 16)
        self.assertEqual(mg.leastCommonTatum(), 30)

        #test meantop
        mean, std = mg.getMeanTempo()
        #sr = mg.getSwingRatios()
        #print sr
        #sr = mg.getSwingRatios(average = True)
        #print sr
        #print "Mean: {}, sd: {}".format(mean, std)
        self.assertEqual(mean, .5)
        self.assertEqual(std,  0.10327955589886441)

        #test filterbar01.010.01000.010000.01.010.01000.010000.01.010.01000.010000.01.010.01000.010000
        self.assertEqual(len(mg.getBarSequence(9, 12)), 4)
        self.assertEqual(mg.getBarSequence(9)[0] == mg[8], True)
        #print len(mg.filterbar(-100, 400))
        self.assertEqual(len(mg.getBarSequence(-1)), 0)
        self.assertEqual(len(mg.getBarSequence(-100, 100)), 16)
        self.assertRaises(Exception, mg.getBarSequence, 12, 9)

        mg.standardize()
        me = mg[0]
        self.assertEqual(me.getTatum(), 16)
        self.assertEqual(me.getBeatInfo().getTatums(), 30)
        self.assertEqual(me.getMetricalPosition().toString(), "4.30.1.1.16")
        self.assertEqual(me.getMeterInfo().toString(), "4/4|4|Equal")
        self.assertEqual(mg.getBarNumbers(), list(range(1, 17)))
        self.assertEqual(mg.getFirstBarNumber(), 1)
        self.assertEqual(mg.getLastBarNumber(), 16)
        self.assertEqual(str(mg.getSignatures()[0]), "4/4")

        self.assertEqual(mg.getEventBars(), [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16])
        self.assertEqual(mg.getEventBeats(), [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1])
        self.assertEqual(mg.getEventTatums(), [16, 11, 7, 6, 16, 11, 7, 6, 16, 11, 7, 6, 16, 11, 7, 6])
        self.assertEqual(mg.getEventDivisions(), [30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30])
        self.assertEqual(mg.getEventPeriods(), [4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4])
        mps = mg.splitMetricalPositions()
        self.assertEqual(mps["bar"], [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16])
        self.assertEqual(mps["beat"], [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1])
        self.assertEqual(mps["tatum"], [16, 11, 7, 6, 16, 11, 7, 6, 16, 11, 7, 6, 16, 11, 7, 6])
        self.assertEqual(mps["division"], [30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30])
        self.assertEqual(mps["period"], [4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4])
        df = mg.to_dataframe(split_metrical_positions=True, ignore_values=True)
        self.assertEqual(list(df["bar"]), [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16])
        self.assertEqual(list(df["beat"]), [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1])
        self.assertEqual(list(df["tatum"]), [16, 11, 7, 6, 16, 11, 7, 6, 16, 11, 7, 6, 16, 11, 7, 6])
        self.assertEqual(list(df["division"]), [30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30])
        self.assertEqual(list(df["period"]), [4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4])
        self.assertEqual(list(df["beat_duration"]), [0.4, 0.6, 0.4, 0.6, 0.4, 0.6, 0.4, 0.6, 0.4, 0.6, 0.4, 0.6, 0.4, 0.6, 0.4, 0.6])
        #print "\n".join([str(ev[0]) + ": " + str(ev[1]) for ev in mg.getMeterInfosForBars()])
        #print mg.getCumulativeBarLengths()
        #print mg.getQuarterIOIsDecimal()
        #print mg.getMetricalPositionsDecimal()
        #print mg.getMetricalIOIsDecimal()
        self.assertEqual( ";".join([str(v) for v in mg.getBeatPositionsFractional()]), "1/2;13/3;41/5;73/6;33/2;61/3;121/5;169/6;65/2;109/3;201/5;265/6;97/2;157/3;281/5;361/6")
        #print mg.syncopations()

        #mg.compress()
        mg = MeterGrid.createIsoMeter(8, div=2, tempo=60, start=1.2)
        bbd = mg.getBarBeatDict("mp", False)
        self.assertEqual(mg.getBarBeatDict("index", False)[1][1], [0, 1])
        self.assertEqual(bbd[1][1][0][1], mg[0].mp)
        self.assertEqual(mg.division_complexity(), 0.0)
        self.assertEqual(mg.compression_complexity(), 0.0)
        self.assertEqual(mg.metric_complexity(), 0.0)
        self.assertEqual(len(mg), 8)
        self.assertEqual(mg[0].onset, 1.2)
        self.assertEqual(mg[1].onset, 1.7)
        self.assertEqual(str(mg[5].getMetricalPosition()), "4.2.1.3.2")
        #self.assertEqual(sum(len(_) for _ in mg.getBeatChunks(div_filter=2)), 8)
        mg = MeterGrid.createIsoMeter(12, signature="3/2", div=5, tempo=60, start=1.2)
        qIOI = mg.getQuarterIOIsFractional()
        #print qIOI
        #print mg.getQuarterPositionsFractional()
if __name__ == "__main__":
    unittest.main()
