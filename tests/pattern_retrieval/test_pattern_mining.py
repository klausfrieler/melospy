#!/usr/bin/env python

""" Unit test for NGram class """

import os
import unittest

import pytest

from melospy.pattern_retrieval.ngram_data_provider import *
from melospy.pattern_retrieval.pattern_mining import *
from melospy.pattern_retrieval.pattern_writer import *
from tests.rootpath import *


def mock_proc_hook( i, req):
    print("Procession request #{}, type: {}".format(i, req.type))

        
def createTestDataProviders():
    dbi = DBInfo("wjazzd.db", user="", pwd="", use=True)
    return NGramDataProvider(data_path(), "test-db", dbi, verbose=False)


def createTestSearches():
    search1 = {"transform":"cpc", "pattern":"[0, 2, '(', 3, '|', 4, ')']", "prefix":2, "suffix":3, "display":"stats", "label":"testsearch1", "search":None}
    search2 = {"transform":"interval", "pattern":"[-2, '*', -1]", "display":"list", "label":"testsearch2", "search":None}
    return [search1, search2]

def createTestPartitions():
    pp1 = {"pattern":"all", "transform":"cpc", "minN":5, "minOccur":2, "minSource":1, "display":"list", "label":"testpartition1", "items":"0"}
    pp2 = {"transform":"interval", "minN":3, "minOccur":2, "minSource":1, "display":"stats", "label":"testpartition2", "items":"0"}
    pp2["trillfilter"] = "1, 2"
    pp2["scalefilter"] = "u"
    pp2["arpeggiofilter"] = "d"
    pp2["pattern"] = "partition"
    return [pp1, pp2]

def createTestDatabase():
    pp1 = {"pattern":"database", "transform":"cpc", "display":"stats", "label":"testdatabase", "maxN":3}
    return [pp1]

class TestPatternMining( unittest.TestCase ):
    
    #@pytest.mark.skip(reason="Assertion mismatch")
    def testPatternSearch(self):
        
        ps = PatternSearch(transform="interval", pattern="[1,2,3]", display="list", label="testsearch")
        self.assertEqual(ps.transform, "interval")
        self.assertEqual(ps.pattern, "[1,2,3]")
        self.assertEqual(ps.display, ["list"])
        self.assertEqual(ps.label, "testsearch")
        self.assertEqual(ps.type, "search")
        search = {"transform":"tpc", "pattern":"[2,3,4]", "display":"stats", "label":"testsearch", "search": None}
        ps = PatternSearch.fromDict(search)
        self.assertEqual(ps.transform, "tpc")
        self.assertEqual(ps.pattern, "[2,3,4]")
        self.assertEqual(ps.display, ["stats"])
        self.assertEqual(ps.label, "testsearch")
        self.assertEqual(ps.type, "search")
        search = {"transform":"tpc", "pattern":"[2,3,4]", "display":"moin", "label":"testsearch", "search": None}
        self.assertRaises(ValueError, PatternSearch.fromDict, search)
        self.assertEqual(ps._eval_pattern("123"), [123])
        self.assertEqual(ps._eval_pattern("123<T"), "123<T")
        self.assertEqual(ps._eval_pattern("1,2,3"), [1, 2, 3])
        self.assertEqual(ps._eval_pattern([1, 2, 3]), [1, 2, 3])
        self.assertEqual(ps._eval_pattern("[1,2,3]"), [1, 2, 3])

    #@pytest.mark.skip(reason="Assertion mismatch")
    def testPatternPartition(self):
        #return
        pp = PatternPartition(transform="interval", minN=5, minOccur=3, minSource=2, display="list", label="testpartition")
        self.assertEqual(pp.transform, "interval")
        self.assertEqual(pp.minN, 5)
        self.assertEqual(pp.display, ["list"])
        self.assertEqual(pp.label, "testpartition")
        self.assertEqual(pp.minOccur, 3)
        self.assertEqual(pp.minSource, 2)
        self.assertEqual(pp.type, "partition")
        part = pp.__dict__
        #search = {"transform":"tpc", "pattern":"[2,3,4]", "prefix":2, "suffix":3, "display":"stats", "label":"testsearch"}
        part["trillfilter"] = "1, 2"
        part["scalefilter"] = "u"
        part["arpeggiofilter"] = "d"
        pp2 = PatternPartition.fromDict(part)
        self.assertEqual(pp2.filter_trills, True)
        self.assertEqual(pp2.trill_min, 1)
        self.assertEqual(pp2.trill_max, 2)
        self.assertEqual(pp2.filter_scales, True)
        self.assertEqual(pp2.filter_arpeggios, True)
        self.assertEqual(pp2.scale_directed, False)
        self.assertEqual(pp2.arp_directed, True)
        part["display"] = "moin"
        self.assertRaises(ValueError, PatternPartition.fromDict, part)

   # @pytest.mark.skip(reason="Signature mismatch")
    def testPatternMiner(self):
        self.ndp = createTestDataProviders()
        req = createTestPartitions()
        searches = createTestSearches()
        req.extend(searches)
        req.append(PatternSearch(transform="interval", pattern="[-2, '*', -1]", display="midi", label="testsearch", search=None))
        dbs = createTestDatabase()
        req.extend(dbs)
        pm = PatternMiner(req, self.ndp, verbose=False)
        pm.set_process_hooks([mock_proc_hook])
        results = pm.process(verbose=True)
        self.assertEqual(results[0].result[0].getStats(), ['MilesDavis_SoWhat_FINAL.sv', 221, 5, 30, 2, 1, 28, 0.38, 5.643, 2.741, 0.881, 5.765])
        

if __name__ == "__main__":
    unittest.main()
