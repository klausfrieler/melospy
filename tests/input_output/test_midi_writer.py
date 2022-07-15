#!/usr/bin/env python

""" Class implementation of test MIDI writer"""

import unittest

import pytest

from melospy.basic_representations.melody import *
from melospy.input_output.melody_importer import *
from melospy.input_output.midi_writer import *
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

def prepareTestDataEsac( esacid, collection=None):
    #dbpath =  os.path.join(root_path(), "analysis/data/PREFINAL/DB/esac.db")
    dbpath =  "c:/Users/klaus/Projects/science/jazzomat/development/melospy-db/melospy_db/data/pool/db/esac.db"
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

class TestMIDIWriter( unittest.TestCase ):

    def getKey(self, mel):
        try:
            key = mel.getMetadata().getField("key")
        except:
            key = None
            if not isinstance(key, Key):
                try:
                    key = Key.fromString(key)
                except:
                    key = None
        return key

    #@pytest.mark.skip(reason="DB-Path mismatch")
    def testMIDIWriter(self):
        """ Initialize module """
        params = MIDIWriterParams(quantize = False, quantize_duration = False)
        #print "params", params
        #mel = prepareTestData("Benny%", "I got%", solopart="1")
        mel = prepareTestData("Wayne%", "Foot%", solopart="1")
        key = self.getKey(mel)
        #print "Found key", key
        #outfile = os.path.join('MIDI',"test_midi.mid")
        outfile = add_data_path("test_midi.mid")
        midi_writer = MIDIWriter(params, verbose=True)
        midi_writer.writeMIDIFile(mel, outfile, key=key)

""" Function calls all unit tests """
if __name__ == '__main__':
    alltests = unittest.TestSuite([unittest.TestLoader().loadTestsFromTestCase(TestMIDIWriter)])
    unittest.main()
