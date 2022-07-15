#!/usr/bin/env python

""" Unit test for NGram class """

import csv
import glob
import math
import os
import random
import string
import time
import unittest

import numpy as np
import pytest

import melospy.basic_representations.jm_util
import melospy.pattern_retrieval.intspan
from melospy.input_output.melody_importer import *
from melospy.input_output.read_sv_project import *
from melospy.pattern_retrieval.ngram import *
from melospy.pattern_retrieval.ngram_bag import *
from melospy.pattern_retrieval.ngram_database import *
from melospy.pattern_retrieval.ngram_db_adapter import *
from melospy.pattern_retrieval.ngram_list import *
from melospy.pattern_retrieval.ngram_position import *
from melospy.pattern_retrieval.ngram_refrep import *
from melospy.pattern_retrieval.ngram_simulate import *

from melospy.tools.commandline_tools.dbinfo import DBInfo
from melospy.tools.commandline_tools.param_helper import SQLQuery

from tests.rootpath import *

seq_rep = ["abcc", "acbb", "bcaa", "acbb"]
seq_rep1 = ["abccabcc", "acbbacbb", "bcaabcaa", "acbbacbb"]
seq_rep2 = {'0':"abcc", '1':"acbb", '2':"bcaa", '3':"acbb"}
seq_rep3 = {'0':[1, 2, 3, 3], '1':[1, 3, 2, 2], '2':[2, 3, 1, 1], '3':[1, 3, 2, 2]}
seq_rep4 = {'0':[(1, 1), (2, 2), (3, 3), (3, 3)], '1':[(1, 1), (3, 3), (2, 2), (2, 2)], '2':[(2, 2), (3, 3), (1, 1), (1, 1)], '3':[(1, 1), (3, 3), (2, 2), (2, 2)]}
seq_rep5 = [[(1, 5), (2, 4), (3, 4), (3, 4)], [(1, 4), (3, 5), (2, 4), (2, 5)], [(2, 4), (3, 5), (1, 4), (1, 5)], [(1, 4), (3, 5), (2, 4), (2, 5)]]
seq_rep6 = [np.array([1, 2, 3, 3]), np.array([1, 3, 2, 2]), np.array([2, 3, 1, 1]), np.array([1, 3, 2, 2])]
seq_rep7 = ["abcabc", "bcabca", "cabcab", "abcabc"]

seq_rep8 = [[0, 1, 2, 2], [0, 2, 1, 1], [1, 2, 0, 0], [0, 2, 1, 1]]
global_sample = [-2  -1  -2  -5, 4  -3, 1  -6  -2  -7, 1  -3  -1, 1  -5  -3, 3, 1  -2, 2, 3, 1, 1  -2,\
-4  -1  -3, 2  -2, 2  -4, 1, 3  -2, 2, 0  -2, 4  -5, 5, 1  -2, 2, 4  -3  -2  -5  -2,\
1, 9  -2  -1, 4  -1, 1  -5, 2  -2, 3  -2  -7  -1  -3, 1, 2, 3  -2, 9, 7  -6, 1  -2,\
-3  -4, 8  -2  -4, 3  -5  -1, 2  -3, 2, 5  -7  -1, 1, 5  -2, 1  -2, 6  -2  -1, 2, 4,\
-1, 1, 2, 1  -5  -3 -12, 1, 2, 0, 2  -2, 7  -2, 2  -1, 1  -2  -4, 9, 4  -2, 2, 3,\
-4, 0 -10  -2  -4, 0  -5  -2, 1  -2, 2  -2  -3, 0, 4, 2  -3, 0  -3  -1, 3  -2, 0, 0,\
6, 1  -3  -4, 2  -2, 0, 2  -1  -2, 2, 7, 2, 0  -1  -2  -1  -5  -5  -2  -3, 0  -1, 3,\
0, 3  -2, 1, 1, 1, 2, 3  -4  -2  -2  -3  -2  -2  -3, 0  -1, 3  -1, 6  -4, 2  -6  -1,\
4  -3, 8, 1, 4, 4  -2  -1]


def metricalFilter(event):
    mp = None
    try:
        mp = event.getMetricalPosition()
    except Exception:
        return False
    mw = mp.getMetricalWeight()
    #print("MP", mp, " mw, ", mw)
    if mw == 2:
        return False
    return True

def make_large_rep(count=100, elements=100, type="plain", symset=None, random_set=True):
    ret = []
    if symset == None:
        sample = global_sample
    else:
        sample = symset
    for i in range(count):
        #ret.append(''.join(random.choice(['a', 'b','c','d']) for _ in range(elements)))
        try:
            ret.append("".join([random.choice(sample) for _ in range(elements)]))
        except:
            ret.append([random.choice(sample) for _ in range(elements)])
    if type == "plain":
        return ret
    nr = NGramRefRepository(valtype = "int")
    nr.extend(ret)
    return nr

def make_melody_rep(transform="interval", valtype="int", count=10,
                    random=False, dbname="wjazzd.db"):
    dbi = DBInfo(dbtype="sqlite3", use=True, path=add_data_path(dbname))
    query = SQLQuery(data_type="sv", display={"transcription_info": "filename_sv"})
    random_bit = "ORDER BY RANDOM()" if random else ""
    query.add_sql_condition('SELECT DISTINCT(melid) FROM melody {} LIMIT {}'.format(random_bit, count))

    mi = MelodyImporter(query(), "", dbi)
    fetcher = mi.fetcher()
    mel_rep = NGramRefRepository(valtype=valtype)
    tmp = []
    for mel in fetcher:
        if valtype == "int":
            tmp.append([int(v) for v in mel.export(transform)])
        elif valtype == "float":
            tmp.append([float(v) for v in mel.export(transform)])
        else:
            tmp.append("".join([str(v) for v in mel.export(transform)]))
    mel_rep.extend(tmp, mi.tunes)
    return mel_rep


def writeMelodyDatabase(filename, transform, maxN = 30, count = 0, valtype="string"):
    nr, soli = make_melody_rep(transform=transform, valtype=valtype, count=count)
    ndb = NGramDatabase(nr, maxN)
    ndb.prune()
    with NGramDBAdapter(filename, ndb) as ndba:
        print("Writing database with ", transform, " and ", filename)
        ndba.createDatabase()
        ndba.writeDatabase()
    return nr

def readMelodyRepFromDB(filename, transform, count = 0, valtype="string"):
    stringify = True if valtype == "string" else False
    with NGramDBAdapter(filename) as ndba:
        try:
            rep = ndba.readRepository(stringify = stringify)
        except Exception as e:
            ndba.close()
            print("Error: ", e.args[0])
            print("DB '", filename, "' not found, creating...")
            rep = writeMelodyDatabase(filename, transform, count, valtype)
    return rep

class TestNGramPositionClass( unittest.TestCase ):
    """ Unit test for pattern class """

    def testConstructor(self):
        """ Test functionality """
        # print "\nTest NGramPosition"
        # print "-"*16
        p = NGramPosition(1, 1, 3)
        self.assertEqual(p.getSeqId(), 1)
        self.assertEqual(p.getStartId(), 1)
        self.assertEqual(p.getN(), 3)
        self.assertEqual(p.getEndId(), 3)
        self.assertEqual(p.getTag(), "")
        self.assertEqual(p.setTag("moin").getTag(), "moin")
        self.assertEqual(p.hasOverlap(NGramPosition(1, 1, 2)), True)
        self.assertEqual(p.hasOverlap(NGramPosition(1, 2, 13)), True)
        self.assertEqual(p.hasOverlap(NGramPosition(1, 3, 17)), True)
        self.assertEqual(p.hasOverlap(NGramPosition(2, 3, 17)), False)
        self.assertEqual(p.hasOverlap(NGramPosition(1, 4, 17)), False)
        self.assertEqual(p.contains(NGramPosition(1, 1, 2)), True)
        self.assertEqual(p.contains(NGramPosition(1, 2, 2)), True)
        self.assertEqual(p.contains(NGramPosition(1, 2, 4)), False)
        self.assertEqual(p.contains(NGramPosition(2, 2, 3)), False)
        self.assertEqual(p.overlap(NGramPosition(2, 2, 3)), 0)
        self.assertEqual(p.overlap(NGramPosition(1, 2, 3)), 2)
        self.assertEqual(p.overlap(NGramPosition(1, 1, 3)), 3)
        self.assertEqual(p.overlap(NGramPosition(1, 4, 5)), 0)
        self.assertEqual(p.toIntSpan(), IntSpan("1-3"))

class TestNGramClass( unittest.TestCase ):
    """ Unit test for pattern class """

    def testConstructor(self):
        """ Test functionality """

        # print "\nTest NGram"
        # print "-"*16
        n       = NGram(3, seq_rep3)
        n2      = NGram(4, seq_rep3)
        pos     = NGramPosition('1', 1, 3)
        pos2    = NGramPosition('3', 1, 3)
        #pos     = NGramPosition(1, 1, 3)
        #pos2    = NGramPosition(3, 1, 3)
        n.add(pos)
        self.assertEqual(n.getValue(), [3, 2, 2])
        n.add(pos2)
        #print n
        self.assertEqual(n.fits(NGramPosition('3', 1, 3)), True)
        self.assertEqual(n.fits(NGramPosition('2', 1, 3)), False)
        self.assertEqual(n.fits(NGramPosition('3', 1, 2)), False)
        #print n.getValue()
        self.assertEqual(n.getSeqIds(), ['1', '3'])
        self.assertEqual(n.getStartIds(), [1, 1])

        n3 = NGram(1, seq_rep3)
        n3.add(NGramPosition('1', 1, 1))
        self.assertEqual(n3.isSubNGram(n), False)
        n3.add(NGramPosition('3', 1, 1))
        self.assertEqual(n3.isSubNGram(n), True)

        n.add(pos2)
        self.assertEqual(n.getSeqIds(), ['1', '3'])
        self.assertEqual(n.getStartIds(), [1, 1])

        self.assertEqual(n.getN(), 3)
        self.assertEqual(n.__eq__(n2), False)
        self.assertEqual(n.singleSource(), False)
        self.assertEqual(n.sourceCount(), 2)
        self.assertEqual(n.filterBySeqId('3').getValue(), [3, 2, 2])
        self.assertEqual(n.filterBySeqId('2').getValue(), None)
        self.assertEqual(n.hasOverlap(n.filterBySeqId('2')), False)
        self.assertEqual(n.hasOverlap(n.filterBySeqId('1')), True)
        test_n = NGram(2, seq_rep3)
        test_n.add(NGramPosition('3', 1, 2))
        self.assertEqual(n.commonPositions(test_n)[0], NGramPosition('3', 1, 3))
        self.assertEqual(test_n.commonPositions(n)[0], NGramPosition('3', 1, 2))
        #n.exportText("test_ngram.txt")
        #n.exportStats("test_ngram.txt")

class TestNGramBagClass( unittest.TestCase ):
    """ Unit test for NGramList class """
    def testConstructor(self):
        """ Test functionality """

        nb = NGramBag(seq_rep1)
        n = NGram(1, seq_rep)
        n.add(NGramPosition(0, 0, 1))
        n.add(NGramPosition(1, 0, 1))
        n.add(NGramPosition(2, 2, 1))
        n.add(NGramPosition(3, 0, 1))
        nb.add(n)
        self.assertEqual(nb[0][0], NGramPosition(0, 0, 1))
        n = NGram(1, seq_rep1)

        n.add(NGramPosition(0, 1, 1))
        n.add(NGramPosition(0, 5, 1))
        n.add(NGramPosition(1, 2, 1))
        n.add(NGramPosition(1, 3, 1))
        n.add(NGramPosition(1, 6, 1))
        n.add(NGramPosition(1, 7, 1))
        n.add(NGramPosition(2, 0, 1))
        n.add(NGramPosition(2, 4, 1))
        n.add(NGramPosition(3, 2, 1))
        n.add(NGramPosition(3, 3, 1))
        n.add(NGramPosition(3, 6, 1))
        n.add(NGramPosition(3, 7, 1))
        nb.add(n)
        self.assertEqual(nb[1][0], NGramPosition(0, 1, 1))
        self.assertEqual(len(nb), 2)
        self.assertEqual(len(nb[0]), 4)
        self.assertEqual(len(nb[1]), 12)
        #nl.exportText("test_ngramlist.txt")
        self.assertEqual(nb.find("a")[0], NGramPosition(0, 0, 1))

class TestNGramListClass( unittest.TestCase ):
    """ Unit test for NGramList class """
    def testConstructor(self):
        """ Test functionality """

        nl = NGramList(1, seq_rep1)
        n = NGram(1, seq_rep)
        n.add(NGramPosition(0, 0, 1))
        n.add(NGramPosition(1, 0, 1))
        n.add(NGramPosition(2, 2, 1))
        n.add(NGramPosition(3, 0, 1))
        nl.add(n)
        self.assertEqual(nl[0][0], NGramPosition(0, 0, 1))
        n = NGram(1, seq_rep1)

        n.add(NGramPosition(0, 1, 1))
        n.add(NGramPosition(0, 5, 1))
        n.add(NGramPosition(1, 2, 1))
        n.add(NGramPosition(1, 3, 1))
        n.add(NGramPosition(1, 6, 1))
        n.add(NGramPosition(1, 7, 1))
        n.add(NGramPosition(2, 0, 1))
        n.add(NGramPosition(2, 4, 1))
        n.add(NGramPosition(3, 2, 1))
        n.add(NGramPosition(3, 3, 1))
        n.add(NGramPosition(3, 6, 1))
        n.add(NGramPosition(3, 7, 1))
        nl.add(n)
        self.assertEqual(nl[1][0], NGramPosition(0, 1, 1))
        self.assertRaises(RuntimeError, nl.addNGramPosition, NGramPosition(0, 0, 3))
        self.assertEqual(nl.getN(), 1)
        self.assertEqual(len(nl), 2)
        self.assertEqual(len(nl[0]), 4)
        self.assertEqual(len(nl[1]), 12)
        #nl.exportText("test_ngramlist.txt")
        self.assertEqual(nl.find("a")[0], NGramPosition(0, 0, 1))
        #print nl.sample(10)

class TestNGramPartitionClass( unittest.TestCase ):
    """ Unit test for NGramPartition class """
    #@pytest.mark.skip(reason="Assertion mismatch")
    def testConstructor(self):
        """ Test functionality """

        print("\nTest NGramPartition")
        print("-"*16)

        n = NGram(3, seq_rep)
        np = NGramPartition(seq_rep)
        tags = "abcdefghijklmnopqrstuvwxyz"
        for i in range(3, -1, -1):
            for j in range(3, -1, -1):
                if i + j + 1 > 4:
                    continue
                np.add(NGramPosition(0, i, j+1, tag = tags[i]*(4-i-j), freq=i+j+5), sort = False)
        self.assertEqual(len(np), 10)
        np.add(NGramPosition(1, 0, 1))
        self.assertEqual(len(np), 10)
        np.sort()
        ret = np.full_export(melodyRep = None)
        #print ret
        #print np
        self.assertEqual(np[0], NGramPosition(0, 0, 4, freq = 8))
        self.assertEqual(np.getSeqId(), 0)
        self.assertEqual(np.findByValue(NGramPosition(0, 0, 4, freq = 8))[0], NGramPosition(0, 0, 4, freq = 4))
        self.assertEqual(np.findByTag("a")[0], NGramPosition(0, 0, 4, freq = 8))
        self.assertEqual(np.innerFreq("a"), 1)
        self.assertEqual(np.innerFreq(NGramPosition(0, 0, 4, freq = 8)), 1)
        self.assertEqual(np.lengthSum(), 20)
        self.assertEqual(np.coverage(), 1.0)
        self.assertEqual(np.overCoverage(), 4.0)

        self.assertEqual(len(np.filterTrills(min_period = 1)), 9)


class TestNGramRefRepositoryClass( unittest.TestCase ):
    """ Unit test for NGramRefRepository class """

    #@pytest.mark.skip(reason="Assertion mismatch")
    def testConstructor(self):
        """ Test functionality """

        print("\nTest NGramRefRepository")
        print("-"*16)

        nr = NGramRefRepository(valtype="string")
        nr.extend(seq_rep)
        self.assertEqual(nr.codebook, {0: 'a', 1: 'b', 2: 'c'})
        self.assertEqual(nr.getRep(), seq_rep)
        self.assertEqual(nr.getType(), ['str'])
        self.assertRaises(Exception, nr.setKeys, seq_rep)
        keys = ["k1", "k2", "k3", "k4"]
        nr.setKeys(keys)
        self.assertEqual(set(nr.getDict().keys()), set(keys))
        self.assertEqual(set(nr.getDict().values()), set(seq_rep))
        self.assertEqual(nr.getDict(), {'k1': 'abcc', 'k3': 'bcaa', 'k2': 'acbb', 'k4': 'acbb'})
        nr.add("abcd", "k5")
        self.assertEqual(set(nr.getDict().keys()), {"k1", "k2", "k3", "k4", "k5"})
        tmp = seq_rep
        tmp.append("abcd")
        self.assertEqual(set(nr.getDict().values()), set(tmp))
        self.assertEqual(nr.getCodebook(), {0: 'a', 1: 'b', 2: 'c', 3: 'd'})
        #print nr
        self.assertEqual(len(nr), 5)
        #nr.exportText("ngramrefrep.txt")
        self.assertEqual(nr.getIdFromKey("k1"), 0)
        self.assertEqual(nr.getKeyFromId(0), "k1")
        self.assertEqual(nr.getCodedSequence(0), [0, 1, 2, 2])
        self.assertEqual(nr.total_count(), 20)
        self.assertEqual(nr.total_count(4), 5)
        nr = NGramRefRepository(valtype="tuple")
        nr.extend(seq_rep5)
        self.assertEqual(nr.getType(), ['tuple', 'int', 'int'])
        self.assertEqual(len(nr.sample(10)), 10)
        tmp = []
        for vec in seq_rep5:
            tmp.extend(vec)
        self.assertEqual(nr.sample(0), tmp)

class TestNGramDatabaseClass( unittest.TestCase ):
    """ Unit test for NGramDatabase class """

    #@pytest.mark.skip(reason="DB-Path mismatch")
    def testGenreSearch(self):

        transform = ["interval", "int"]

        mel_rep = make_melody_rep(transform=transform[0], valtype=transform[1],
                                  count=10, random=False, dbname="wjazzd.db")
        #print mel_rep[0]
        #print "makeMelodyRep:", end-start
        #mel_rep = readMelodyRepFromDB("ngram_cdpc.db", "cdpc", valtype="string")
        ndb = NGramDatabase(mel_rep, maxN=30, transform=transform[0], build=False)
        pattern = [2, '+?(.){1,2}', 2, '+?']
        #pattern = [-2, +1]
        start = time.process_time()
        #print "Start search..."
        ngrambag = ndb.genreSearch(pattern)
        #print "...completed in {} s".format(time.process_time()-start)
        self.assertEqual(len(ngrambag), 59)

    @pytest.mark.skip(reason="Too messy")
    def testConstructor(self):
        """ Test functionality """
        return
        print("\nTest NGramDatabase")
        print("-"*16)
        count = 37
        elements = 20
        #elements = ["a", "b", "c", "d"]
        #large_rep = make_large_rep(type="rep", count=count, elements=elements, symset="abcd", random_set=False)
        large_rep = make_large_rep(type="rep",  count=count, elements=elements,
                                   symset = list(range(elements)), random_set=False)
        #print large_rep
        ndb = NGramDatabase(large_rep, maxN=30)
        ndb.simulate_seq_markov(10, 2)
        #sample = [n.getValue() for n in ndb[0]]
        #print len(sample)
        #print ndb
        #values = ["a", "b", "c", "d", "aa", "bb", "cc", "dd", "aaa", "aba", "aca", "ada"]
        elements = ["a", "b", "c", "d"]
        bigrams = [[v1 + v2 for v1 in elements] for v2 in elements]
        values = []
        for bi in bigrams:
            values.extend(bi)
        #values = ["aa", "bb", "cc", "dd", "ab", "ac", "ad", "bc", "bd", "cd"]
        s1 = 0
        s2 = 0
        for v in values:
            #print "=" * 60
            #print "Value: {}".format(v)
            pv = ndb.getProbability(v)
            s1 += pv
            #print "Prob: {}".format(pv)
            apv = ndb.getAPrioriProbability(v)
            s2 += apv
            #print "A priori prob: {}".format(apv)
            excess_prob = math.log(pv/apv) if pv >0.0 else 0
            #print "Excess prob: ", excess_prob, ndb.getExcessProbability(v, use_log=False)
        #print "Sums = ",s1, s2
        minOccur = 2
        minSource = 2
        outfile = "simul_coverage.csv"
        with open(outfile, 'w') as csvfile:
            csvwriter = csv.writer(csvfile, delimiter=';', lineterminator="\n", quotechar='"', quoting=csv.QUOTE_MINIMAL)
            header = ["performer", "title", "note_count", "min_N", "pattern_count", "coverage", "avg_N", "avg_overlap"]
            csvwriter.writerow(header)
        for minN in range(3, 9):
            #minN = 4
            coverage = []
            patterns = []
            avg_N = []
            avg_overlaps = []
            #print "Running pattern analysis for minN: {} with minOccur:{} und minSource:{}".format(minN, minOccur, minSource)
            for i in range(len(large_rep)):
                ngrams = ndb.getMaximalNGramPartition(i, normalize = True, minN = minN, minOccur = minOccur, minSource = minSource)
                #print "-"*15
                if len(ngrams)==0:
                    coverage.append(0)
                    patterns.append(0)
                    avg_N.append(0)
                    avg_overlaps.append(0)
                    continue
                ispan = IntSpan(list(range(0, len(large_rep[i]))))
                patterns.append(len(ngrams))
                coverage.append(ngrams.toIntSpan().coverage(ispan))
                avg_N.append(ngrams.averageN())
                avg_overlaps.append(ngrams.averageOverlap())
            with open(outfile, "a") as csvfile:
                csvwriter = csv.writer(csvfile, delimiter=';', lineterminator="\n", quotechar='"', quoting=csv.QUOTE_MINIMAL)
                for i in range(len(coverage)):
                    row = ["simul", i, elements, minN, patterns[i], coverage[i], avg_N[i], avg_overlaps[i]]
                    csvwriter.writerow(row)
            #print "Avg Coverage: ", sum(coverage)/len(coverage)
        #print "\n".join([str(_) for _ in ndb.findPrefixes([0])])

        #print "\nFindSuff:"
        #print "\n".join([str(_) for _ in ndb.findSuffixes([0])])

        #self.assertEqual(ndb.find("a")[0], NGramPosition(0,0,1))
        #ndb.printStatistics()
        #large_rep = makeLargeRep(100, 50, type="ngramref")
        #print large_rep
        #ndb = NGramDatabase(large_rep, maxN = 30)
        #ndb.find("abccdaa")
        #ndb.printStatistics()
        #seqid = 0

        #start= time.process_time()
        transform = ["interval", "int"]
        mel_rep = make_melody_rep(transform=transform[0],
                                        valtype=transform[1], count = 1,
                                        random = False)

        #end= time.process_time()
        #print "makeMelodyRep:", end-start
        #mel_rep = readMelodyRepFromDB("ngram_cdpc.db", "cdpc", valtype="string")
        ndb = NGramDatabase(mel_rep, maxN = 30)


        #gem = [-2, -1]
        #gem = [-2, +1]
        gems = [[-2, +1], [-2, -1], [+2, -1], [+2, +1]]
        for gem in gems:
            infixes = ndb.findEnvelope(gem, 0, 0)
            #infixes.extend(ndb.findSuffixes(gem))
            if infixes:
    #            print "{} infixes for {}".format(len(infixes), gem)
                print("Infixes for ", gem)
                print("\n".join([str(_.getValue())+ "|" + str(len(_)) for _ in infixes]))
            else:
                print("No infixes found for", gem)

        fourgrams = ndb[4]
        fourgrams.filterTrills()
        maxPat = fourgrams.getMaxWeightNGram(minSource = 5, threshold = 5)
        print(maxPat)
        #maxPats = sorted(fourgrams, key = lambda p: (-p.getWeight()))
        print("\n".join([str(v) for v in maxPat]))
        #maxPat[7].exportSnippetList("int_5grams_snippet_min7_th7.txt",
        #      refRep = mel_rep, melodyRep = soli, lengthOffset = 1)
        #seqid = mel_rep.getIdFromKey("JohnColtrane_GiantSteps-1")
        #ngrams = ndb.getMaximalNGramPartition(0, normalize = True, minN = 5, minOccur = 3)
        minN = 4
        minOccur = 2
        minSource = 1
        print("Running {} pattern analysis for minN: {} with minOccur:{} und minSource:{}".format(transform[0], minN, minOccur, minSource))
        for i in range(len(mel_rep)):
            ngrams = ndb.getMaximalNGramPartition(i, normalize = True, minN = minN, minOccur = minOccur, minSource = minSource)
            key = mel_rep.getKeyFromId(i)
            print("-"*15)
            print("Before: ", len(ngrams))
            if len(ngrams):
                ngrams.filterTrills()
            print("After:", len(ngrams))

            if len(ngrams) == 0:
                print("Tune: ", key)
                print("No Notes: ", len(mel_rep[i]))
                print("No Pat: ", 0)
                print("Coverage: ", 0)
                print("Avg. N: ", 0)
                print("Avg. Overlap: ", 0)
                print("Over Coverage: ", 0)
                continue
            ispan = IntSpan(list(range(0, len(mel_rep[i]))))
            print("Tune: ", key)
            #print("No Notes: ", len(soli[i]))
            print("No Pat: ", len(ngrams))
            print("Coverage: ", ngrams.toIntSpan().coverage(ispan))
            print("Avg. N: ", ngrams.averageN())
            print("Avg. Overlap: ", ngrams.averageOverlap())
            print("Over Coverage: ", ngrams.overCoverage())
            ngrams.exportText("{}_cdpc_pat_N{}_min{}.txt".format(key, minN, minOccur), soli[i], indexOffset = 0)

        #ngrams.exportCSV("JohnColtrane_GiantSteps-1_PREFINAL_cdpc_pat_min5.csv", soli[seqid], indexOffset = 0, lengthOffset = 0)
        #ngrams.exportText("JohnColtrane_GiantSteps-1_PREFINAL_cdpc_pat_min5.txt", soli[seqid], indexOffset = 0)

        for seqid in range(len(mel_rep)):
            key = mel_rep.getKeyFromId(seqid)
            print("Writing: ", key)
            try:
                ngrams = ndb.getMaximalNGramPartition(seqid, normalize = False, minN = 8)
                #ngrams.exportText(key+"_ngrams.txt", soli[seqid], indexOffset = 0)
                for i, n in enumerate(ngrams):
                    n.setTagsAsSeqKey()
                    append = True
                    if n.getFreq()>0:
                        n.exportText("all_long_ngrams_int.txt", append = append, melody_rep = soli, indexOffset = 0, separateRecords = True)
            except Exception as e:
                print("Error: {}".format(e.args))
                pass
        #ngrams.exportCSV("JohnColtrane_SoWhat_FINAL_Internal_Pattern.csv", soli[seqid], indexOffset = 0, lengthOffset = 1)
        #ngrams.exportText("JohnColtrane_SoWhat_FINAL_Internal_Pattern.txt", soli[seqid], indexOffset = 0)

class TestNGramDBAdapterClass( unittest.TestCase ):
    """ Unit test for NGramDBAdapter class """

    @pytest.mark.skip(reason="Class not in used")
    def testConstructor(self):
        return
        print("\nTest NGramDBAdapter")
        print("-"*16)
        start = time.process_time()

        ndb = None
        with NGramDBAdapter("ngram_int2.db") as ndba:
            ndb = ndba.readDatabase(rebuild = False)

        print("Read DB in {} s".format(time.process_time()-start))
        #ndb1.printStatistics()
        inf1 = ndb.findEnvelope([4, 4], 1, 1)
        if inf1:
            print("\n".join(["Value: {}, Freq: {}".format(_.getValue(), _.getFreq()) for _ in sorted(inf1, key=lambda x: -x.freq)]))

            for ngram in inf1:
                ngram.exportText("1235.txt", append=True)

        inf1 = ndb.findEnvelope([-4, -4], 1, 1)
        if inf1:
            print("\n".join(["Value: {}, Freq: {}".format(_.getValue(), _.getFreq()) for _ in sorted(inf1, key=lambda x: -x.freq)]))

            for ngram in inf1:
                ngram.exportText("1235.txt", append=True)

        dbi = DBInfo(dbtype = "sqlite3", path = add_data_path("wjazz.db"))
        tunes = [{'query': {'conditions':{'SQL': 'SELECT DISTINCT(melid) FROM melody LIMIT 37'}, 'display':{'transcription_info': 'filename_sv'}, 'type': 'sv'}}]
        #dbi = DBInfo(dbtype = "sqlite3", path = "c:/Users/klaus/Projects/science/jazzomat/software/melopy/analysis/data/PREFINAL/DB/esac.db")
        #tunes = [{'query': {'conditions':{'SQL': 'SELECT DISTINCT(melid) FROM esac_info WHERE collection = "ERKNER"'}, 'display':{'esac_info': 'esacid'}, 'type': 'esac'}}]
        mi = MelodyImporter(tunes, "", dbi)
        fetcher = mi.fetcher()
        mel_rep = NGramRefRepository()
        tmp = []
        for mel in fetcher:
            tmp.append([int(v) for v in mel.export("interval")])
        mel_rep.extend(tmp, mi.tunes)
        print("Read rep in {} s".format(round(time.process_time()-start, 3)))
        start = time.process_time()

        ndb = NGramDatabase(mel_rep, maxN = 30, transform = "interval")
        ndb.prune()
        #print "PRUNED!"

        print("Preparation done in {} s".format(round(time.process_time()-start, 3)))

        start = time.process_time()
        with NGramDBAdapter("ngram_int2.db", ndb) as ndba:
            ndba.createDatabase(withIndex = False)
            ndba.writeDatabase()
            ndba.createIndices()

        print("Wrote DB in {} s".format(round(time.process_time()-start, 3)))
        start = time.process_time()


        inf1 = ndb.findEnvelope([2, 1], 1, 1)
        inf2 = ndb1.findEnvelope([2, 1], 1, 1)
        print("\n".join(["Value: {}, Freq: {}".format(_.getValue(), _.getFreq()) for _ in sorted(inf2, key=lambda x: -x.freq)]))
        print(len(inf2), len(inf1))
        ispan2 = IntSpan.from_start_length(ngram_pos.startid, ngram_pos.N)
        overlap = len(ispan1.intersection(ispan2))



class TestSimulate( unittest.TestCase ):
    """ Unit test for NgramSimulate class """
    #@pytest.mark.skip(reason="DB-Path mismatch")
    def testConstructor(self):
        print("\nTest NGramSimulate")
        print("-"*16)
        transform = "interval"
        valtype ="int"
        maxN = 3
        mel_rep = make_melody_rep(transform=transform, valtype=valtype, count=5, random=False)
        print(mel_rep.getKeys())
        ndb = NGramDatabase(mel_rep, maxN=maxN, transform=transform)
        sim_db = SimulateNGramDB(verbose=True)
        sdb = sim_db.simulate(ndb, maxN, transform)
        sdb = sim_db.simulate(ndb, maxN, transform)

if __name__ == "__main__":
    unittest.main()
