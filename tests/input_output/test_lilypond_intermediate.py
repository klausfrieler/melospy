#!/usr/bin/env python

""" Tests for Lilypond Intermediate classes"""
import os
import unittest
from fractions import Fraction

import pytest

from melospy.input_output.lilypond_intermediate import *
from melospy.input_output.melody_importer import *
from melospy.rootpath import root_path
from melospy.tools.commandline_tools.dbinfo import *
from tests.rootpath import *

def prepareTestData(performer, title, titleaddon=None, solopart=None, v1=True):
    dbpath = add_data_path('wjazzd.db')    
    dbinfo = DBInfo.fromDict({'path': dbpath, "use": True, "type":"sqlite3"})
    query = MelodyImporter.queryFromSoloInfo(performer, title, titleaddon, solopart)
    mi = MelodyImporter(tunes=query, path=dbpath, dbinfo=dbinfo )
    mel = next(mi.fetcher())
    return mel

def prepareTestDataEsac( esacid, collection=None):
    dbpath = add_data_path('esasc.db') 
    dbinfo = DBInfo.fromDict({'path': dbpath, "use": True, "type":"sqlite3", "content_type":"esac"})
    query = MelodyImporter.queryFromEsacInfo(esacid, collection)
    mi = MelodyImporter(tunes=query, path=dbpath, dbinfo=dbinfo )
    mel = next(mi.fetcher())
    return mel

def constructDummyMelody():
    C4 = 60

    #4/4 signature, period = 4, equal beat proportions
    mi = MeterInfo(4, 4)
    #four sixteenth per Beat, .5 sec per beat = 120 bpm
    bi = BeatInfo(4, .5)
    mc = MetricalContext(bi, mi)
    mel = Melody()

    #add a lot more of events
    bis = [BeatInfo(2, .5), BeatInfo(3, .5), BeatInfo(5, .5), BeatInfo(6, .5)]
    for i in range(16):
        duration = 1./8
        onset    = 1 + i*duration
        bi = BeatInfo(i+1, .5)
        #mc = mc.clone().setBeatInfo(bis[i % len(bis)].clone())
        mc = mc.clone().setBeatInfo(bi)
        mp1 = MetricalPosition( i + 1, 1, 1, 0, mc)
        me = MetricalNoteEvent(onset, C4, mp1, duration/2)
        mel.append(me)
    return mel

def constructDummyMelody2():
    C4 = 60
    mg = MeterGrid.createIsoMeter(8, div=2, tempo=120, start=0)
    mel = Melody()
    for i, m in enumerate(mg):
        mne = MetricalNoteEvent(m.onset, C4 + i, m.getMetricalPosition(), m.duration)
        mel.append(mne)
    return mel


class TestLilypondIntermediateEvent( unittest.TestCase ):

    #@pytest.mark.skip(reason="Assertion mismatch")
    def testSplitting(self):
        lily_stream = LilypondIntermediateStream()
        mbar = LilypondIntermediateBar(1, "4/4")
        mb = LilypondIntermediateBeat(qbeat=3, bar=1, division=4, bar_container = mbar)
        qpos=Fraction(1, 2)
        qioi=Fraction(5, 4)
        qdur=Fraction(5, 4)
        me = LilypondIntermediateEvent(60, qpos=qpos, qioi=qioi, qdur=qdur, beat_container = mb, backref=0)
        mb.append(me)
        mbar.append(mb)
        lily_stream.append(mbar)
        me.get_split_durations()
        splits = me.split()
        #print splits
        #print mbar
        #mbar.expand_overhang2()
        #print mbar
        #print lily_stream
        lily_stream.expand_overhang()
        #print lily_stream

    #@pytest.mark.skip(reason="AssertionError: 'pitch:60|pos:None.None.0|qioi:1|qdur=1|vdur:None|bref:0||f0:' != 'pitch:60|qpos:0|qioi:1|qdur=1|vdur:None,0|bref:0'")
    def testConstructor(self):
        qpos=Fraction(0, 1)
        qioi=Fraction(1, 1)
        qdur=Fraction(1, 1)
        mbar = LilypondIntermediateBar(1, "4/4")
        mb = LilypondIntermediateBeat(qbeat=3, bar=1, division=4, bar_container = mbar)

        me = LilypondIntermediateEvent(60, qpos=qpos, qioi=qioi, qdur=qdur, beat_container = mb, backref=0)
        self.assertEqual(str(me), "pitch:60|pos:1.3.0|qioi:1|qdur=1|vdur:None|bref:0||f0:")
        me.set_virtual_duration(tuplet_factor=1)
        self.assertEqual(str(me), "pitch:60|pos:1.3.0|qioi:1|qdur=1|vdur:1|bref:0||f0:")

        qpos=Fraction(1, 2)
        qioi=Fraction(19, 6)
        qdur=Fraction(3, 2)
        me = LilypondIntermediateEvent(60, qpos=qpos, qioi=qioi, qdur=qdur, beat_container = mb,  backref=0)
        self.assertEqual(str(me), "pitch:60|pos:1.3.1/2|qioi:19/6|qdur=3/2|vdur:None|bref:0||f0:")
        me.set_virtual_duration(tuplet_factor=1)
        
        self.assertEqual(str(me), "pitch:60|pos:1.3.1/2|qioi:19/6|qdur=3/2|vdur:3/2|bref:0||f0:")

        qpos=Fraction(1, 2)
        qioi=Fraction(13, 6)
        qdur=Fraction(3, 2)
        me = LilypondIntermediateEvent(60, qpos=qpos, qioi=qioi, qdur=qdur, beat_container = mb, backref=0)
      
        self.assertEqual(str(me), "pitch:60|pos:1.3.1/2|qioi:13/6|qdur=3/2|vdur:None|bref:0||f0:")
        me.set_virtual_duration(tuplet_factor=1)
        self.assertEqual(str(me), "pitch:60|pos:1.3.1/2|qioi:13/6|qdur=3/2|vdur:3/2|bref:0||f0:")

        qpos=Fraction(1, 2)
        qioi=Fraction(1, 2)
        qdur=Fraction(1, 4)
        me = LilypondIntermediateEvent(60, qpos=qpos, qioi=qioi, qdur=qdur, beat_container = mb,  backref=0)
        self.assertEqual(str(me), "pitch:60|pos:1.3.1/2|qioi:1/2|qdur=1/4|vdur:None|bref:0||f0:")
        me.set_virtual_duration(tuplet_factor=1)

        self.assertEqual(str(me), "pitch:60|pos:1.3.1/2|qioi:1/2|qdur=1/4|vdur:1/4|bref:0||f0:")

        qpos=Fraction(1, 2)
        qioi=Fraction(3, 2)
        qdur=Fraction(1, 4)
        me = LilypondIntermediateEvent(60, qpos=qpos, qioi=qioi, qdur=qdur, beat_container = mb,  backref=0)
        self.assertEqual(str(me), "pitch:60|pos:1.3.1/2|qioi:3/2|qdur=1/4|vdur:None|bref:0||f0:")
        me.set_virtual_duration(tuplet_factor=1)
        self.assertEqual(str(me), "pitch:60|pos:1.3.1/2|qioi:3/2|qdur=1/4|vdur:1/4|bref:0||f0:")

        qpos=Fraction(1, 2)
        qioi=Fraction(2, 1)
        qdur=Fraction(1, 4)
        me = LilypondIntermediateEvent(60, qpos=qpos, qioi=qioi, qdur=qdur, beat_container = mb,  backref=0)
        self.assertEqual(str(me), "pitch:60|pos:1.3.1/2|qioi:2|qdur=1/4|vdur:None|bref:0||f0:")
        me.set_virtual_duration(tuplet_factor=1)
        self.assertEqual(str(me), "pitch:60|pos:1.3.1/2|qioi:2|qdur=1/4|vdur:1/4|bref:0||f0:")

    #@pytest.mark.skip(reason="Assertion mismatch")
    def testHelper(self):
        qpos=Fraction(1, 2)
        qioi=Fraction(2, 1)
        qdur=Fraction(5, 4)
        mbar = LilypondIntermediateBar(1, "4/4")
        mb = LilypondIntermediateBeat(qbeat=1, bar=1, division=4, bar_container = mbar)

        me = LilypondIntermediateEvent(60, qpos=qpos, qioi=qioi, qdur=qdur, beat_container = mb, backref=0)
        ev1, ev2 = tuple(me.split(Fraction(1, 2)))

        self.assertEqual(str(ev1["event"]), "pitch:60|pos:1.1.1/2|qioi:1/2|qdur=1/2|vdur:None|bref:0|~|f0:")
        self.assertEqual(str(ev2["event"]), "pitch:60|pos:None.None.0|qioi:3/2|qdur=3/4|vdur:None|bref:0||f0:")
        self.assertEqual(me.is_multi_beat(), False)
        qpos=Fraction(0, 1)
        qioi=Fraction(3, 1)
        qdur=Fraction(3, 1)
        me = LilypondIntermediateEvent(60, qpos=qpos, qioi=qioi, qdur=qdur, beat_container = mb, backref=0)
        self.assertEqual(me.is_multi_beat(virtual=False), True)
        self.assertEqual(me.has_atomic_duration(virtual=False), True)
        qpos=Fraction(0, 1)
        qioi=Fraction(5, 8)
        qdur=Fraction(5, 8)
        me = LilypondIntermediateEvent(60, qpos=qpos, qioi=qioi, qdur=qdur, backref=0)
        self.assertEqual(me.is_multi_beat(virtual=False), False)
        self.assertEqual(me.has_atomic_duration(virtual=False), False)
        qpos=Fraction(1, 2)
        qioi=Fraction(1, 1)
        qdur=Fraction(1, 1)
        me = LilypondIntermediateEvent(60, qpos=qpos, qioi=qioi, qdur=qdur, beat_container = mb, backref=0)
        self.assertEqual(me.is_multi_beat(virtual=False), True)


class TestLilypondIntermediateBeat( unittest.TestCase ):
    def testConstructor(self):
        mbar = LilypondIntermediateBar(1, "4/4")
        mb = LilypondIntermediateBeat(qbeat=1, bar=1, division=1)
        qpos=Fraction(1, 2)
        qioi=Fraction(1, 4)
        qdur=Fraction(1, 4)
        me = LilypondIntermediateEvent(60, qpos=qpos, qioi=qioi, qdur=qdur, backref=0)
        mb.append(me)

        qpos=Fraction(3, 4)
        qioi=Fraction(30, 2)
        qdur=Fraction(30, 2)
        me = LilypondIntermediateEvent(60, qpos=qpos, qioi=qioi, qdur=qdur, backref=0)
        mb.append(me)
        mbar.append(mb)
        #print mb
        #splits = mb.split()
        #print splits[0]
        #print splits[1]
        qpos=Fraction(0, 1)
        qioi=Fraction(1, 2)
        qdur=Fraction(1, 2)
        me = LilypondIntermediateEvent(60, qpos=qpos, qioi=qioi, qdur=qdur, backref=0)
        mb.insert_simple_event(me)
        #print mb.events[1]
        #print mb.events[0].get_succeeding_event()
        #print mb.events[0].get_preceding_event()
        self.assertEqual(mb.events[0].get_succeeding_event(), mb.events[1])
        self.assertEqual(mb.events[0].get_preceding_event(), None)
        self.assertEqual(mb.events[-1].get_succeeding_event(), None)
        self.assertEqual(mb.events[-1].get_preceding_event(), mb.events[-2])
        self.assertEqual(mb.monotony_check(), True)

class TestLilypondIntermediateBar( unittest.TestCase ):
    def testConstructor(self):
        mbar = LilypondIntermediateBar(1, "4/4")

        mb = LilypondIntermediateBeat(qbeat=1, bar=1, division=4)

        qpos=Fraction(1, 2)
        qioi=Fraction(1, 4)
        qdur=Fraction(1, 4)
        me = LilypondIntermediateEvent(60, qpos=qpos, qioi=qioi, qdur=qdur, backref=0)
        mb.append(me)

        qpos=Fraction(3, 4)
        qioi=Fraction(17, 4)
        qdur=Fraction(17, 4)
        me = LilypondIntermediateEvent(60, qpos=qpos, qioi=qioi, qdur=qdur, backref=1)
        mb.append(me)
        mbar.append(mb)

        mb = LilypondIntermediateBeat(qbeat=2, bar=1, division=4)

        qpos=Fraction(1, 2)
        qioi=Fraction(1, 4)
        qdur=Fraction(1, 4)
        me = LilypondIntermediateEvent(60, qpos=qpos, qioi=qioi, qdur=qdur, backref=2)
        mb.append(me)

        qpos=Fraction(3, 4)
        qioi=Fraction(17, 4)
        qdur=Fraction(17, 4)
        me = LilypondIntermediateEvent(60, qpos=qpos, qioi=qioi, qdur=qdur, backref=3)
        mb.append(me)
        mbar.append(mb)

        #print mbar[-1].get_preceding_beat()
        #print mbar[-1]
        self.assertEqual(mbar[0].get_succeeding_beat(), mbar[1])
        self.assertEqual(mbar[0].get_preceding_beat(), None)
        self.assertEqual(mbar[-1].get_succeeding_beat(), None)
        self.assertEqual(mbar[-1].get_preceding_beat(), mbar[-2])
        self.assertEqual(mbar.first_ref(), 0)
        self.assertEqual(mbar.last_ref(), 3)

        #print "="*60
        #print mbar
        #rest = mbar.expand_overhang()
        #print "="*60
        #print mbar
        #rest = mbar.expand_overhang()
        #print "="*60
        #print mbar
        #print "Rest = ", rest

class TestLilypondIntermediateStream( unittest.TestCase ):
    def testParse(self):
        #mel = constructDummyMelody()
        #mel = prepareTestData("David M%", "Blues For%", solopart="1", v1=False)
        #mel = prepareTestData("Wayne%", "Foot%", solopart="1", v1=False)
        #mel = prepareTestData("Miles%", "So%", solopart="1", v1=False)
        #mel = prepareTestData("David Lie%", "Softly%", solopart="1", v1=False)
        #mel = prepareTestData("Bob%", "No Moe%", solopart="1", v1=False)
        #mel = prepareTestData("Don By%", "Out%", solopart="1", v1=False)
        #mel = prepareTestData("Cliff%", "I'll%", solopart="1", v1=False)
        #mel = prepareTestData("Art%", "Anth%", solopart="1", v1=False)
        #mel = prepareTestData("Art%", "Stard%", solopart="2", v1=False)
        #mel = prepareTestData("Joe%", "Body%", solopart="2", v1=False)
        #mel = prepareTestData("Mich%", "Nev%", solopart="%", v1=False)
        #mel = prepareTestData("Dext%", "Soc%", solopart="1", v1=False)
        #mel = prepareTestData("Michael%", "Nothin%", solopart="1", v1=False)
        #mel = prepareTestData("Cliff%", "I'll%", solopart="%", v1=False)
        #mel = prepareTestData("Rex%", "%", solopart="%", v1=False)
        #mel = prepareTestData("Chet%", "I F%", solopart="1", v1=False)
        #mel = prepareTestData("Zoot%", "Dan%", solopart="1", v1=False)
        #mel = prepareTestData("Steve%", "Cross%", solopart="2", v1=False)
        #mel = prepareTestData("Art%", "Anthr%", solopart="1", v1=False)

        #mel = prepareTestData("Sonny%", "Body%", solopart="1", v1=False)
        #mel = prepareTestData("John%", "Nature%", solopart="1", v1=False)
        #mel = prepareTestData("Way%", "Down%", solopart="%", v1=False)
        mel = prepareTestData("David%", "Blues%", solopart="1", v1=False)
        mel = mel.slice(305, 327)
        #print mel
        #mel = prepareTestDataEsac("A0001")
        #mel = mel.slice(192, 205)
        #events= mel.getEventNumbersForBarSequence(13)
        #print events
        ##rint mel[0].bar
        #mel = mel.getBarSequence(13)
        #mel = mel.slice(571, 573)
        #mel = mel.slice(33, 36)
        #print Melody.__str__(mel)
        #print len(mel)
        #mel = mel.beattrack
        lis = LilypondIntermediateStream(mel, debug=False)
        #ev = lis.flatten()
        #print "NUM EVENTS", len(ev)
        self.assertEqual(lis.backref_check(), 0)
        self.assertEqual(lis.duration_check(True), True)
        self.assertEqual(lis.tie_check(), True)
        self.assertEqual(lis.pitch_check(), 0)
        self.assertEqual(lis.monotony_check(), True)
        #self.assertEqual(lis.check_all(), True)
        #self.assertEqual(lis[0].get_succeeding_bar(), lis[1])
        #self.assertEqual(lis[0].get_preceding_bar(), None)
        #self.assertEqual(lis[-1].get_succeeding_bar(), None)
        #self.assertEqual(lis[-1].get_preceding_bar(), lis[-2])
        #print lis[1]
        #print lis
        #lis.post_process()
        #lis.insert_rests()
        #print lis
        #print str(lis)
        #print lis.render()
        #print s
        #print "\n".join([str(_) for _ in ret])

""" Function calls all unit tests """
if __name__ == '__main__':
    alltests = unittest.TestSuite([unittest.TestLoader().loadTestsFromTestCase(TestLilypondIntermediateStream)])
    unittest.main()
