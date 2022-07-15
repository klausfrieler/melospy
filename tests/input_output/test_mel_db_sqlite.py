#!/usr/bin/env python

""" Class implementation of TestMelDBSqlite3Adapter"""

import unittest

import pytest

from melospy.basic_representations.solo import *
from melospy.input_output.esac_reader import *
from melospy.input_output.mel_db_adapter_factory import *
from melospy.input_output.mel_db_sqlite3_adapter import *
from melospy.input_output.mel_db_sqlite3_adapter2 import *
from melospy.input_output.read_sv_project import *
from melospy.rootpath import root_path
from melospy.tools.commandline_tools.dbinfo import *

from tests.rootpath import *

def getDB(DB):
    dbpath= add_data_path(DB)
    if DB[0:3] == "esac":
        version = "1"
    else:
        version = "2"
    dbinfo = DBInfo.fromDict({'path': dbpath, "use": True, "type":"sqlite3", "version":version})
    return MelDBAdapterFactory(dbinfo).create()

class TestMelDBSqlite3Adapter( unittest.TestCase ):


    @pytest.mark.skip(reason="Irrelevant")
    def testSpeed(self):
        #return
        with getDB("esac.db") as mdb:

            start = time.process_time()
            for i in range(1, 100):
                try:
                    esacSong = mdb.readSongs(i)
                except Exception as e:
                    print("Error for melid = ", i)
            print("Read 100 songs in {} s".format(round(time.process_time()-start, 3)))
            start = time.process_time()
            results = mdb.query("SELECT * FROM melody WHERE melid>=1 AND melid<=100")
            #results = mdb.query("SELECT * FROM esac_info WHERE melid>=1 AND melid<=100")
            #results = mdb.query("SELECT * FROM sections WHERE melid>=1 AND melid<=100")
            print("Performed 3 queries in {} s".format(round(time.process_time()-start, 3)))

    #@pytest.mark.skip(reason="DB-Path mismatch")
    def testReadEsac(self):
        #return
        with getDB("esac.db") as mdb:
            esacSong = mdb.readEsacSongs(2552)
            self.assertEqual(len(esacSong[2552]), 40)

    #@pytest.mark.skip(reason="DB-Path mismatch")
    def testReadSolo(self):
        #return
        with getDB("wjazzd.db") as mdb:
            song = mdb.readSolos(1)
            self.assertEqual(len(song[1]), 530)


    #@pytest.mark.skip(reason="DB-Path mismatch")
    def testReadSongs(self):
        #return
        with getDB("wjazzd.db") as mdb:
            song = mdb.readSongs(1)
            self.assertEqual(len(song[1]), 530)

        with getDB("esac.db") as mdb:
            song = mdb.readSongs(1)
            self.assertEqual(len(song[1]), 60)

    @pytest.mark.skip(reason="Too long")
    def testReadMelodies(self):
        #return
        start = time.process_time()
        with getDB("esac.db") as mdb:
            esacSongs = mdb.readMelodies()
            print(len(esacSongs ))
            self.assertEqual(len(esacSongs), 7352)

        print("Read Esac melodies in {}s".format(time.process_time()-start))

    @pytest.mark.skip(reason="Too long")
    def testReadEsacMetadata(self):
        #return
        start = time.process_time()
        with getDB("esac.db") as mdb:
            esacMeta = mdb.readEsacMetadata()
            self.assertEqual(len(esacMeta ), 7352)
        print("Read Esac metadata in {}s".format(time.process_time()-start))

    @pytest.mark.skip(reason="Too long")
    def testReadEsacSongs(self):
        #return
        start = time.process_time()
        print("Reading ESAC songs...")
        with getDB("esac.db") as mdb:
            esacSongs = mdb.readSongs()
            self.assertEqual(len(esacSongs), 7352)
        print("Read all Esac songs in {} s".format(time.process_time()-start))

    #@pytest.mark.skip(reason="DB-Path mismatch")
    def testReadSolos(self):
        #return
        timer = Timer()
        melids = [1, 2, 3]
        with getDB("omnibook.db") as mdb:
            solos = mdb.readSolos(melids)
            print("Read three solos in {} s".format(timer.end()))
            self.assertEqual(len(solos), 3)

    @pytest.mark.skip(reason="Too long")
    def testReadBeattracks(self):
        #return
        timer = Timer()
        melids = [1]
        with getDB("wjazzd.db") as mdb:
            bt = mdb.readBeatTracks()
            print("Read all beattracks in {} s".format(timer.end()))
            self.assertEqual(len(bt), 456)


    @pytest.mark.skip(reason="Too long")
    def testReadSections(self):
        #return
        #path_to_db = self.getDBpath("wjazzd.db")
        timer = Timer()
        melids = [17, 18, 114]
        with getDB("wjazzd.db") as mdb:
            sect = mdb.readSections(with_parse = False)
            print("Read all sections in {} s".format(timer.end()))
            self.assertEqual(len(sect), 456)

            timer.start()
            sect = mdb.readSections(sectType="PHRASE")
            print("Read phrase sections in {} s".format(timer.end()))
            self.assertEqual(len(sect), 456)

            timer.start()
            sect = mdb.readSections(melids)
            print("Read sections for three melodies in {} s".format(timer.end()))
            self.assertEqual(len(sect), 3)

            timer.start()
            sect = mdb.readSections(melids, sectType="PHRASE")
            print("Read phrase sections for three melodies in {} s".format(timer.end()))
            self.assertEqual(len(sect), 3)

    #@pytest.mark.skip(reason="OperationalError: no such table: sections")
    def testReadEsacSections(self):
        #return
        timer = Timer()
        melids = [17, 18, 114]
        with getDB("esac.db") as mdb:
            sect = mdb.readSections(with_parse=False)
            print("Read all sections in {} s".format(timer.end()))

            timer.start()
            sect = mdb.readSections(sectType="PHRASE", with_parse=False)
            print("Read phrase sections in {} s".format(timer.end()))
            timer.start()
            sect = mdb.readSections(melids, with_parse=False)
            print("Read sections for three melodies in {} s".format(timer.end()))
            self.assertEqual(len(sect), 3)
            timer.start()
            sect = mdb.readSections(melids, sectType="PHRASE", with_parse=False)
            print("Read phrase sections for three melodies in {} s".format(timer.end()))
            self.assertEqual(len(sect), 3)
            timer.start()
            sect = mdb.readSections(melids[0], sectType="PHRASE", with_parse=False)
            print("Read phrase sections for three melodies in {} s".format(timer.end()))
            sect = mdb.parseSection(sect[melids[0]], "PHRASE")
            self.assertEqual(len(sect), 7)

    @pytest.mark.skip(reason="Too long")
    def testReadSoloMetadata(self):
        #return

        start = time.process_time()
        with getDB("wjazzd.db") as mdb:
            solos = mdb.readSoloMetadata()
            self.assertEqual(len(solos), 456)
        print("Read all solo metadata in {}s".format(time.process_time()-start))

    @pytest.mark.skip(reason="Too long")
    def testReadDatabase(self):
        #return
        start = time.process_time()
        with getDB("wjazzd.db") as mdb:
            solos = mdb.readDatabase()
            self.assertEqual(len(solos), 456)
        print("Read wjazzd database in {}s".format(time.process_time()-start))

    @pytest.mark.skip(reason="Too long")
    def testConstructor(self):
        """ Initialize module """
        return
        esac_reader = EsacReader(add_data_path("K0001.esa"))
        song = esac_reader.solo
        ei = esac_reader.esacinfo
        song.setMetadata(ei)
        #print song
        with getDB("esac_test.db") as mdb:
            mdb.createDatabase()
            mdb.insertEsacSong(song, ei)
            esacSong = mdb.readEsacSongs(1)
            self.assertEqual(len(esacSong[1]), len(song ))

        s = SVReader(add_data_path("SonnyRollins_TenorMadness_FINAL.sv"))
        svp = SVReaderParams(flexq = FlexQParams())
        s.bundle(svp, normalize = False, diagnostic = False)
        solo1 = s.solo
        si = SoloInfo(performer = "Sonny Rollins", title="Tenor Madness")
        ti = TranscriptionInfo(fileNameSV = "SonnyRollins_TenorMadness_FINAL.sv")
        ri = RecordInfo(artist = "Sonny Rollins")
        ci = CompositionInfo(title = "Tenor Madness", composer = "Sonny Rollins")
        smd = SoloMetaData(soloInfo = si, transcriptionInfo = ti, recordInfo = ri, compositionInfo = ci)
        solo1.setMetadata(smd)

        s = SVReader(add_data_path("BobBerg_Angles_FINAL.sv"))
        s.bundle(svp, normalize = False, diagnostic = False)
        solo2 = s.solo
        si = SoloInfo(performer = "Bob Berg", title="Angles")
        ti = TranscriptionInfo(fileNameSV = "BobBerg_Angles_FINAL.sv")
        ri = RecordInfo(artist = "Bob Berg")
        ci = CompositionInfo(title = "Angles", composer = "Bob Berg")
        smd = SoloMetaData(soloInfo = si, transcriptionInfo = ti, recordInfo = ri, compositionInfo = ci)
        solo2.setMetadata(smd)

        with getDB("wjazzd_test.db") as mdb:
            mdb.createDatabase()
            mdb.insertSolo(solo1)
            mdb.insertSolo(solo2)
            solo = mdb.readSolos(1)
            #print len(solo[1]), len(solo1)
            self.assertEqual(len(solo[1]) == len(solo1), True)
            solo = mdb.readSolos(2)
            self.assertEqual(len(solo[2]) == len(solo2), True)
            soli = mdb.readDatabase()
            self.assertEqual(len(soli), 2)
            vals = mdb.getMelIDsByFilenameSV('%_FINAL.sv')
            self.assertEqual(vals, [1, 2] )

""" Function calls all unit tests """
if __name__ == '__main__':
    alltests = unittest.TestSuite([unittest.TestLoader().loadTestsFromTestCase(TestMelDBSqlite3Adapter)])
    unittest.main()
