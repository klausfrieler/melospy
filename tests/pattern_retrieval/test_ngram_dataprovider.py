#!/usr/bin/env python

""" Unit test for NGram class """

import os
import unittest

import pytest

from melospy.pattern_retrieval.ngram_data_provider import *

from tests.rootpath import *

class TestNGramDataProvider( unittest.TestCase ):
    """ Unit test for NGramDataProvider class """
    def setTestParameter(self):
        self.wdir = data_path()
        self.tunes = "test-db"
        self.dbi = DBInfo("wjazzd.db", user="", pwd="", use=True)
        self.maxN = 30
        self.transform = "interval"

    #@pytest.mark.skip(reason="DB-Path mismatch")
    def testBasics(self):
        print("\nTest NGramDatabaseProvider")
        print("-"*16)
        self.setTestParameter()

        ndp = NGramDataProvider(self.wdir, self.tunes, self.dbi, verbose=False)

        ndp.read_melodies()
        self.assertEqual(len(ndp.mel_rep[0]), 221)

        nrr = ndp.get_transform_rep(self.transform)
        self.assertEqual(nrr.getValtype(), "int")
        self.assertEqual(len(nrr.getSequenceByKey(ndp.keys[0])), 220)

        ndb = ndp.get_database(self.transform, False, self.maxN)
        #ndb.printStatistics()
        self.assertEqual(len(ndb.refrep), 1)
        ndp.clear_cache()
        self.assertEqual(len(ndp.ngram_dbs), 0)

        ndb = ndp.get_database(self.transform, True, self.maxN)
        #ndb.printStatistics()
        self.assertEqual(len(ndb.refrep), 1)

        ndp.clear_cache()
        self.assertEqual(len(ndp.ngram_dbs), 0)

        ndb = ndp.simulate_database(self.transform, self.maxN, 3)
        #ndb.printStatistics()
        rep = ndb.getRep()
        self.assertEqual(rep.total_count(), 220)
        #print len["SIMUL_0"])
if __name__ == "__main__":
    unittest.main()
