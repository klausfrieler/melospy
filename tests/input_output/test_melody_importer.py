#!/usr/bin/env python

""" Class implementation of TestMelodyImporter"""

import unittest

import pytest

from melospy.basic_representations.melody import *
from melospy.input_output.melody_importer import *
from melospy.rootpath import root_path
from melospy.tools.commandline_tools.dbinfo import *

from tests.rootpath import *

def getFullPath(filename):
    return add_data_path(filename).replace("\\", "/")

def getDB(DB):
    dbpath = add_data_path(DB)
    if DB[0:3] == "esac": 
        version = "1"
    else:
        version = "2"
    dbinfo = DBInfo.fromDict({'path': dbpath, "use": True, "type":"sqlite3", "version":version})
    return MelDBAdapterFactory(dbinfo).create()

class TestMelodyImporter( unittest.TestCase ):

    #@pytest.mark.skip(reason="Path mismatch")
    def testDBInfo(self):
        """ Initialize module """
        dbpath = getFullPath("wjazzd.db")
        dbinfo = DBInfo(dbpath)
        self.assertEqual(dbinfo.type, "sqlite3")
        self.assertEqual(dbinfo.path, dbpath)
        self.assertEqual(dbinfo.use, False)
        self.assertEqual(dbinfo.pwd, "")
        self.assertEqual(dbinfo.user, "")

   # @pytest.mark.skip(reason="Path mismatch")
    def testMelodyImporterFileModeSV(self):        
        #return
        mi = MelodyImporter(tunes="test-files", path=data_path())
        self.assertEqual(mi.sep, "/")
        self.assertEqual(mi.path, add_path_sep(data_path(), "/"))
        self.assertEqual(mi.melids, None)
        self.assertEqual(mi.dbinfo, None)
        first = next(mi.fetcher()).getMetadata().getTranscriptionInfo().filenamesv
        self.assertEqual(first, add_data_path("MilesDavis_SoWhat_FINAL.sv").replace("\\", "/"))

    #@pytest.mark.skip(reason="Path mismatch")
    def testMelodyImporterFileModeCSV(self):
        #return
        mi = MelodyImporter(tunes={"files":"test_mcsv1.csv"}, path=data_path())
        fetcher = mi.fetcher()
        mel = next(fetcher)
        self.assertEqual(len(mel), 233)
        #mel = next(fetcher)
        #mel = next(fetcher)


    #@pytest.mark.skip(reason="Path mismatch")
    def testMelodyImporterFileModeKRN(self):
        #return
        mi = MelodyImporter(tunes={"files":"*.krn"}, path=data_path())
        fetcher = mi.fetcher()
        mel = next(fetcher)
        #print len(mel)
        self.assertEqual(len(mel), 229)
        mel = next(fetcher)
        self.assertEqual(len(mel), 355)
        #print len(mel)
        mel = next(fetcher)
        self.assertEqual(len(mel), 644)
        #print len(mel)

    #@pytest.mark.skip(reason="Path mismatch")
    def testMelodyImporterFileModeMIDI(self):
        #return
        #path = "c:/Users/klaus/Projects/science/jazzomat/melopy/analysis/data/PREFINAL/MIDI/test"
        mi = MelodyImporter(tunes= {"files": "*.mid"}, path=data_path())
        self.assertEqual(mi.sep, "/")
        self.assertEqual(mi.path, add_path_sep(data_path(), "/"))
        self.assertEqual(mi.melids, None)
        self.assertEqual(mi.dbinfo, None)
        mel = next(mi.fetcher())
        self.assertEqual(len(mel), 30)
        self.assertEqual(type(mel), Solo)

    #@pytest.mark.skip(reason="DB-Path mismatch")
    def testMelodyImporterDBModeWjazzd(self):
        #return
        #query = MelodyImporter.queryFromSoloInfo("John Coltrane", "Impressions", "1961", "2")
        #print query
        #dbpath = getFullPath("analysis/data/FINAL/RELEASE2.0/DB/")
        dbi = DBInfo("wjazzd.db", user ="klaus", pwd="moin", use=True)
        mimp = MelodyImporterParams(use_cache = False)

        mi = MelodyImporter(tunes = "all", path=data_path(), params={"melody_importer": mimp}, dbinfo=dbi )
        query = MelodyImporter.queryFromSoloInfo("Art%", "An%")
        self.assertEqual(mi.sep, "/")
        self.assertEqual(mi.path, add_path_sep(data_path(), "/"))
        #self.assertEqual(mi.melids, [142])
        self.assertEqual(mi.dbinfo, dbi)
        first = next(mi.fetcher())
        #print "\n".join([str(f) for f in first.getF0Modulations()])
        self.assertEqual(first.getMetadata().getTranscriptionInfo().filenamesv, "ArtPepper_Anthropology_FINAL.sv")
        del mi
        query = MelodyImporter.queryFromSoloInfo("Miles%", "So%")
        mi = MelodyImporter(tunes=query, path=data_path(), params={"melody_importer": mimp}, dbinfo=dbi )
        #self.assertEqual(mi.melids, [142])
        first = next(mi.fetcher()).getMetadata().getTranscriptionInfo().filenamesv
        self.assertEqual(first, "MilesDavis_SoWhat_FINAL.sv")
        #print query

    #@pytest.mark.skip(reason="DB-Path mismatch")
    def testMelodyImporterDBModeOmnibook(self):
        #return
        #query = MelodyImporter.queryFromSoloInfo("John Coltrane", "Impressions", "1961", "2")
        #print query

        #dbpath = getFullPath("analysis/data/FINAL/RELEASE2.0/DB/")
        mimp = MelodyImporterParams(use_cache = False)
        dbi = DBInfo("omnibook.db", user ="klaus", pwd="moin", use=True)
        mi = MelodyImporter(tunes = "all", path=data_path(),  params={"melody_importer": mimp}, dbinfo=dbi )
        query = MelodyImporter.queryFromSoloInfo("Char%", "Ah%")
        self.assertEqual(mi.sep, "/")
        self.assertEqual(mi.path, add_path_sep(data_path(), "/"))
        first = next(mi.fetcher())
        #print first.getMetadata().getCompositionInfo().harmonytemplate
        self.assertEqual(first.getMetadata().getField("harmonytemplate"), "I Got Rhythm")
        #self.assertEqual(mi.melids, [142])

    @pytest.mark.skip(reason="Too heavy data")
    def testMelodyImporterDBModePop(self):
        #query = MelodyImporter.queryFromSoloInfo("John Coltrane", "Impressions", "1961", "2")
        #print query
        mimp = MelodyImporterParams(use_cache = False)
        dbi = DBInfo("popdaniel_00-03.db", user ="klaus", pwd="moin", use=True)
        #query = MelodyImporter.queryFromPopSongInfo("%", "%")
        #mi = MelodyImporter(tunes=query, path=dbpath, dbinfo=dbi )
        #pi = next(mi.fetcher()).getMetadata().getPopSongInfo()
        mi = MelodyImporter(tunes = "test-pop", params={"melody_importer": mimp}, path=data_path(), dbinfo=dbi )
        self.assertEqual(mi.sep, "/")
        self.assertEqual(mi.path, add_path_sep(data_path(), "/"))
        self.assertEqual(mi.melids, [10])
        self.assertEqual(mi.dbinfo, dbi)
        first = next(mi.fetcher())
        fname = first.getMetadata().getPopSongInfo().filename
        self.assertEqual(fname, "010.csv")
        del mi
        query = MelodyImporter.queryFromPopSongInfo("Beat%", "%")
        mi = MelodyImporter(tunes=query, path=data_path(),  params={"melody_importer": mimp}, dbinfo=dbi )
        self.assertEqual(len(mi.melids), 92)
        first = next(mi.fetcher()).getMetadata().getPopSongInfo().filename
        self.assertEqual(first, "001.csv")

    @pytest.mark.skip(reason="Too long")
    def testMelodyImporterSample(self):
        #return
        dbi = DBInfo("wjazzd.db", user ="klaus", pwd="moin", use=True)
        mimp = MelodyImporterParams(use_cache = True, samples = 10, seed = 1234)
        mi = MelodyImporter(tunes = "all", path=data_path(), dbinfo=dbi, params={"melody_importer": mimp})
        self.assertEqual(mi.sep, "/")
        self.assertEqual(mi.path, add_path_sep(data_path(), "/"))
        #self.assertEqual(mi.melids, [142])
        self.assertEqual(mi.dbinfo, dbi)
        count = 0
        fetcher = mi.fetcher(verbose=False)
        while True and count<1000:
            try:
                mel = next(fetcher)
                #print mel.getMetadata().getTranscriptionInfo().filenamesv
            except:
                break
                pass
            count += 1

        self.assertEqual(count, 10)

""" Function calls all unit tests """
if __name__ == '__main__':
    alltests = unittest.TestSuite([unittest.TestLoader().loadTestsFromTestCase(TestMelodyImporter)])
    unittest.main()
