#!/usr/bin/env python

""" Unit test for PatternWriter class """

import os
import unittest

import pytest

import test_pattern_mining as tpm
from melospy.pattern_retrieval.ngram_data_provider import *
from melospy.pattern_retrieval.pattern_mining import *
from melospy.pattern_retrieval.pattern_writer import *
from tests.rootpath import *


class TestPatternWriter( unittest.TestCase ):

    def init(self):
        self.ndp = tpm.createTestDataProviders()
        self.outdir = data_path()
        req = tpm.createTestPartitions()
        searches = tpm.createTestSearches()
        req.extend(searches)
        r = PatternSearch(transform="interval", pattern="[-2, '*', -1]", display="MIDI", label="testsearch")
        req.append(r)
        dbs = tpm.createTestDatabase()
        req.extend(dbs)
        self._prepare_requests(req)

    def _get_request_type(self, pattern):
        """Check if request is database, search or partition
            Args:
                pattern (string):
                    parameter that defines request type
            Returns:
                string:
                    "database", "partition" or "search"
        """
        pt = pattern.lower()
        pr_type = ""
        if pt == "*" or pt == "partition" or pt =="max" or pt == "all":
            pr_type = "partition"
        elif pt == "database":
            pr_type = "database"
        else:
            pr_type = "search"
        return pr_type

    def _prepare_requests(self, requests):
        """Prepares interal list of pattern requests
            Args:
                requests (var, mandatory):
                    either a list of dictionaries containing
                    parameters defining requests
                    or a list of objects inheriting from PatternRequest
        """
        self.requests   = []
        self.build_db = False
        need_build = False
        for r in requests:
            if isinstance(r, PatternRequest):
                # be trustful that all elements in the list are PatternRequests
                tmp = r
                pr_type = self._get_request_type(r.type)
            else:
                pr_type = self._get_request_type(r["pattern"])

                try:
                    if pr_type == "partition":
                        tmp = PatternPartition.fromDict(r)
                    elif pr_type == "database":
                        tmp = PatternDatabase.fromDict(r)
                    else:
                        tmp = PatternSearch.fromDict(r)
                except:
                    raise RuntimeError("Invalid request: {}".format(r))
            #print "added request of type", pr_type
            self.requests.append(tmp)
            self.build_db = self.build_db or pr_type != "search"

        if len(self.requests) == 0:
            raise ValueError("No requests found.")

    #@pytest.mark.skip(reason="Signature mismatch")
    def testConstructor(self):
        self.init()
        ngw = PatternWriter("testngram", self.outdir, self.ndp.mel_rep)
        ofs = [ngw._make_outfilename(r, "stats") for r in self.requests]
        self.assertEqual(os.path.basename(ofs[0]), "testpartition1_cpc_5_2_1_stats.csv")
        ofs = [ngw._make_outfilename(r, "list") for r in self.requests]
        self.assertEqual(os.path.basename(ofs[0]), "testpartition1_cpc_5_2_1.csv")
        header = [";".join(ngw._get_header(r, "stats")) for r in self.requests]
        self.assertEqual(header[0], "value;N;freq;prob100;noSources")
        header = [";".join(ngw._get_header(r, "list")) for r in self.requests]
        self.assertEqual(header[0], "id;start;N;onset;dur;metricalposition;value;freq;prob100")

    #@pytest.mark.skip(reason="Signature mismatch")
    def testPatternMiner(self):
        self.init()
        pm = PatternMiner(self.requests, self.ndp, verbose=False)
        pm.set_process_hooks([tpm.mock_proc_hook])
        results = pm.process(verbose=True)
       
        ngw = PatternWriter("testngram", self.outdir, self.ndp.mel_rep)
        ngw.sep=";"
        for r in results:
            print("-"*60)
            print("Executing ", r.type, r.display)
            if r.type == "partition":
                ngw.write_pattern_partition(r)
                #print "Partition"
                pass
            elif r.type == "search":
                ngw.write_search_result(r)
                #if r.display == "MIDI":
                #    ngw.write_search_result(r)
                #else:
                #    ngw.print_search_result(r)
                pass
            elif r.type == "database":
                #ngw.print_database(r)
                ngw.write_database(r)
                #print "Partition"
                pass
    def teardown_method(self, method):
        files = [
            "testdatabase_cpc_1_3_1_1_stats_db.csv",
            "testpartition1_cpc_5_2_1.csv",
            "testsearch.mid",
            "testsearch1_stats.csv",
            "testsearch2.csv",
            "testpartition2_interval_3_2_1_sf_tf_af_stats.csv",
            
            ]
        for filename in files:
            if os.path.exists(add_data_path(filename)):
                os.remove(add_data_path(filename))
            
if __name__ == "__main__":
    unittest.main()
