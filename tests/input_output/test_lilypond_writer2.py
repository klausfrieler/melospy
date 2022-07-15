#!/usr/bin/env python

""" Class implementation of LiylpondWriter"""
import os
import unittest
from fractions import Fraction

import pytest

from melospy.basic_representations.melody import *
from melospy.input_output.lilypond_writer2 import *
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

def prepareTestMelodyFile(filename, path):

    mi = MelodyImporter(tunes={"files":filename}, path=path)
    fetcher = mi.fetcher()
    mel = next(fetcher)
    return mel

def prepareTestDataEsac(esacid, collection=None):
    dbpath = add_data_path('esac.db')
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

class TestLilypondWriter2( unittest.TestCase ):

    #@pytest.mark.skip(reason="DB-Path mismatch")
    def testLilypondWriter2(self):
        #mel = self.prepareTestDataMiles(item=0)

        #mel = prepareTestData("Miles%", "So%", solopart="1", v1=False)
        #mel = prepareTestData("Michael%", "Peep%", solopart="%", v1=False)
        #mel = prepareTestData("Way%", "Or%", solopart="1", v1=False)
        #mel = prepareTestData("Don By%", "Body%", solopart="1", v1=False)
        #mel = prepareTestData("Art%", "Desa%", solopart="1", v1=False)
        #mel = prepareTestData("Can%", "This%", solopart="1", v1=False)
        #mel = prepareTestData("Chet%", "I F%", solopart="1", v1=False)
        #mel = prepareTestData("Joe%", "Sere%", solopart="1", v1=False)
        #mel = prepareTestData("Steve%", "Cross%", solopart="2", v1=False)
        #mel = prepareTestData("Sonny%", "Body%", solopart="1", v1=False)
        #mel = prepareTestData("Sonny%", "Body%", solopart="1", v1=False)
        #mel = prepareTestData("Steve%", "The %", solopart="1", v1=False)
        #mel = prepareTestData("Way%", "Foot%", solopart="1", v1=False)
        #mel = prepareTestData("Wyn%", "U.%", solopart="%", v1=False)
        #mel = prepareTestData("Cliff%", "I'll%", solopart="%", v1=False)
        #mel = prepareTestData("David%", "Pab%", solopart="%", v1=False)
        #mel = prepareTestData("Bob%", "No M%", solopart="1", v1=False)
        mel = prepareTestData(performer="Steve%", title="Pass%", solopart="1", v1=False)
        #print mel.getMetadata().getField("key")
        #print mel.simpleExport("meta.rhythmfeel")
        #mel = mel.slice(45, 55)
        #print mel.getBeatTrack()[0]
        #print mel
        #print mel.chords
        #mel = prepareTestData("David%", "Blues%", solopart="1", v1=False)
        #mel = prepareTestMelodyFile("input1.mid", "C:/Users/klaus/Projects/science/jazzomat/support/peter/")

        #mel = prepareTestMelodyFile("midi1children.mid", "C:/Users/klaus/Projects/science/jazzomat/support/20141217/")
        #mel = prepareTestDataEsac("A0020C")
        #mel = prepareTestDataEsac("A0015B")
        #print mel
        #mel = mel.slice(176, 178)
        #mel = mel.getBarSequence(14, 14)
        #mel = mel.getBarSequence(13, 14)
        lily = LilypondWriter2(mel, debug=False)

        #print Melody.__str__(mel)
        lily.write(add_data_path("testfile.ly"))
        #lily.write(os.path.join('LILYPOND',"MichaelBrecker_NothingPersonal_LILYPOND.ly"))

    def teardown_method(self, method):
        filenames = ["testfile.ly"]
        for filename in filenames:
            if os.path.exists(add_data_path(filename)):
                os.remove(add_data_path(filename))

""" Function calls all unit tests """
if __name__ == '__main__':
    alltests = unittest.TestSuite([unittest.TestLoader().loadTestsFromTestCase(TestLilypondWriter2)])
    unittest.main()
