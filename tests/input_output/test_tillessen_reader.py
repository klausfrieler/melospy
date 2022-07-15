#!/usr/bin/env python

""" Class implementation of TestTillessenReader"""

import unittest
#import rootpath
import os
import csv

from melospy.input_output.tillessen_reader import *
from melospy.basic_representations.jm_util import chomp, Timer

class TestTillessenReader( unittest.TestCase ):

    def init_reader(self, db=1):
        if db == 1:
            till_path = "e:/projects/science/tillessen/data/songs_mit_ref.xls"
        else:
            till_path = "e:/projects/science/tillessen/data/songs_ohne_ref.xls"
            
        self.till_reader = TillessenReader(till_path)

    def testTillessenChordSequence(self):
        #return
        gt_chords1 = [Chord("Bb-"), Chord("C+"), Chord("F#o"), Chord("D-")]
        gt_chords2 = [Chord("C"), Chord("F#"), Chord("D-"), Chord("Bb-")]
        cs = {1: gt_chords1, 2:gt_chords2}       
        tcs = TillessenChordSequence()
        self.assertEqual(str(tcs), "")
        tcs = TillessenChordSequence(cs)
        self.assertEqual(str(tcs), "Bb-C+F#oD-|CF#D-Bb-")
        self.assertEqual(len(tcs), 2)

        self.init_reader()
        song = self.till_reader.read_song(17)
        vc = song.verse_chords
        self.assertEqual(vc.num_chords(), 35)
        dbv = vc.get_downbeat_sequence().flatten()
        self.assertEqual("".join([str(c) for c in dbv]), "CGE-FCGE-FCGE-FFFFGCGE-FCGE-FCGE-FGGE-FFFGGFGCC")
        cc = song.chorus_chords
        self.assertEqual(cc.num_chords(), 9)
        dbc = cc.get_downbeat_sequence().flatten()
        self.assertEqual("".join([str(c) for c in dbc]), "CCCCCCCCCCCCFFFC")

        dbv = vc.get_downbeat_sequence(downbeats="1").flatten()
        self.assertEqual("".join([str(c) for c in dbv]), "CE-CE-CE-FFCE-CE-CE-GE-FGFC")

        dbc = cc.get_downbeat_sequence(downbeats="1").flatten()
        self.assertEqual("".join([str(c) for c in dbc]), "CCCCCCFF")

        dbn = vc.get_downbeat_sequence().flatten()
        self.assertEqual("".join([str(c) for c in vc.flatten()]), 
                         "CGE-FCGE-FCGE-FFFGCGE-FCGE-FCGE-FGE-FFGFGC")
        self.assertEqual("".join([str(c) for c in dbn]), 
                         "CCGGE-E-FFCCGGE-E-FFCCGGE-E-FFFFFFFFGGCCGGE-E-FFCCGGE-E-FFCCGGE-E-FFGGGGE-E-FFFFFFGGGGFFGGCCCC")
        dbn = cc.normalize().flatten()
        self.assertEqual("".join([str(c) for c in dbn]), "CCCCCCCCCCCCCCCCCCCCCCCCFFFFFFCC")

    def testChordEditDistance(self):     
        return
        sed = SimilarityEditDistance(ins_del_cost = 1, sub_cost=chord_sub_cost_with_minor_parallels)
        #sed = SimilarityEditDistance()
        cs1 = [Chord("C"), Chord("G"), Chord("F"), Chord("Bb")]
        cs2  = [Chord("D"), Chord("Em"), Chord("Dm"), Chord("Bb")]
        sim = sed.process(cs1, cs2)
        self.assertEqual(sim, .75)
        cs1 = [Chord("C"), Chord("G"), Chord("F"), Chord("Bb")]
        cs2  = [Chord("C"), Chord("G"), Chord("F"), Chord("Bb")]
        sim = sed.process(cs1, cs2)
        self.assertEqual(sim, 1.)
        cs1 = [Chord("C"), Chord("G"), Chord("F"), Chord("Bb")]
        cs2  = [Chord("Am"), Chord("Em"), Chord("Dm"), Chord("Gm")]
        sim = sed.process(cs1, cs2)
        self.assertEqual(sim, 1.)
        cs1 = [Chord("C"), Chord("Em"), Chord("F"), Chord("Bb")]
        cs2  = [Chord("Am"), Chord("G"), Chord("Dm"), Chord("Gm")]
        sim = sed.process(cs1, cs2)
        self.assertEqual(sim, 1.)

        sed = SimilarityEditDistance(ins_del_cost = 1, sub_cost=chord_sub_cost)
        #sed = SimilarityEditDistance()
        cs1 = [Chord("C"), Chord("G"), Chord("F"), Chord("Bb")]
        cs2  = [Chord("D"), Chord("Em"), Chord("Dm"), Chord("Bb")]
        sim = sed.process(cs1, cs2)
        self.assertEqual(sim, .25)
        cs1 = [Chord("C"), Chord("G"), Chord("F"), Chord("Bb")]
        cs2  = [Chord("C"), Chord("G"), Chord("F"), Chord("Bb")]
        sim = sed.process(cs1, cs2)
        self.assertEqual(sim, 1.)
        cs1 = [Chord("C"), Chord("G"), Chord("F"), Chord("Bb")]
        cs2  = [Chord("Am"), Chord("Em"), Chord("Dm"), Chord("Gm")]
        sim = sed.process(cs1, cs2)
        self.assertEqual(sim, 0)
        cs1 = [Chord("C"), Chord("Em"), Chord("F"), Chord("Bb")]
        cs2  = [Chord("Am"), Chord("G"), Chord("Dm"), Chord("Gm")]
        sim = sed.process(cs1, cs2)
        self.assertEqual(sim, 0.)

        
    def testTillessenChordSequenceSimilarity(self):
        return
        self.init_reader()                
        max_id = 50
        sum_above = 0
        tot_count = 0
        for i in range(max_id-1):
            s1 = self.till_reader.read_song(i)
            for j in range(i+1, max_id):
                tot_count += 1
                s2 = self.till_reader.read_song(j)
                #print s1
                #print s2
                #print "Testing:",i, j
                cs1= s1.chorus_chords
                cs2 = s2.chorus_chords
                sim = cs1.similarity(cs2)
                sim2 = cs1.similarity(cs2, minor_parallels=False)
                if sim != sim2:
                    print(u"sim1({}:{}, {}:{}) = {} ".format(s1.performer, s1.title, s2.performer, s2.title, sim))
                    print(u"sim2({}:{}, {}:{}) = {} ".format(s1.performer, s1.title, s2.performer, s2.title, sim2))
                    print("CS1 {}◘".format(cs1))
                    print("CS2 {}".format(cs2))
                    sum_above += 1
        print("Tested {} song pairs with {} over .85".format(tot_count, sum_above))
        
    def _print_sim(self, sim, thresh=0):
        for k in sim:
            if sim[k] >= thresh:
                print("{}: {}".format(k, sim[k]))

    def testTillessenSongSimilarity(self):
        return
        def testSim(max_id, sim_type, printing=False, minor_parallels=True):
            for i in range(max_id-1):
                s1 = self.till_reader.read_song(i)
                #print "Testing ", s1
                for j in range(i+1, max_id):
                    s2 = self.till_reader.read_song(j)
                    sims = s1.similarity(s2, sim_type, minor_parallels=minor_parallels)
                    if printing:
                        self._print_sim(sims) 
                        print("-"*60)
                    #print sims
                    #if sims["sim_tot"] >=.85:
                    #    self._print_sim(sims) 
                    #    print "-"*60
            return sims
        max_id = 100
        self.init_reader(db=1)
        t = Timer()
        t.start()
        sims1 = testSim(max_id, sim_type="edit_distance")
        t.tick("Edit distance of {} pairs".format(max_id*(max_id-1)*.5))
        t.start()
        sims2  = testSim(max_id, sim_type="match")
        t.tick("Match of {} pairs".format(max_id*(max_id-1)*.5))
        #self.assertDictEqual(sims1, sims2)

        t.start()
        sims1 = testSim(max_id, sim_type="edit_distance", minor_parallels=False)
        t.tick("Edit distance of {} pairs".format(max_id*(max_id-1)*.5))
        t.start()
        sims2  = testSim(max_id, sim_type="match", minor_parallels=False)
        t.tick("Match of {} pairs".format(max_id*(max_id-1)*.5))
        #self.assertDictEqual(sims1, sims2)
        
    def testTillessenSongEq(self):
        return
        self.init_reader()
        song1 = self.till_reader.read_song(238)
        song2 = self.till_reader.read_song(246)
        self.assertEqual(song1 == song2, True)

    def testTillessenReader(self):
        #return
        self.init_reader()
        row1 = self.till_reader.read_row(10)
        #print row1
        #for i in range(0, 2800):
        #    song = self.till_reader.read_song(i)
        #    s = song.__str__()
            #print s, type(s)
            #print u"{}".format(song)
        song = self.till_reader.read_song(17)
        #print song
        #print song.verse_chords
        #print song.chorus_chords
        #self.till_reader.read_all_songs()
        #fsv = mt_reader.guess_filename_sv_base(63)
        #return
    def testParseBar(self):
        #return
        self.init_reader()
        ch1, ch2 = self.till_reader._parse_bar("b7m1ab5d2m01b52mb7m")
        gt_chords1 = [Chord("Bb-"), Chord("C+"), Chord("F#o"), Chord("D-")]
        gt_chords2 = [Chord("C"), Chord("F#"), Chord("D-"), Chord("Bb-")]
        self.assertEqual(ch1, gt_chords1)
        self.assertEqual(ch2, gt_chords2)
    
    def testParseChordSequence(self):
        #return
        self.init_reader()
        cs = ["b7m1ab5d2m01b52mb7m", "15", "103b"]
        cs1, cs2, w = self.till_reader._parse_chord_sequence(cs)
        #print "CS1", cs1
        #print "CS2", cs2
        self.assertDictEqual(cs1, {1: [Chord('Bb-'), Chord('C+'), Chord('F#o'), Chord('D-')], 2: [Chord('C'), Chord('G')], 3: [Chord('C')]})
        #self.assertDictEqual(cs1, {1: ['b7m', '1a', 'b5d', '2m'], 2: ['1', '5'], 3: ['1']})
        #self.assertDictEqual(cs2, {1: ['1', 'b5', '2m', 'b7m'], 2: ['1', '5'], 3: ['3']})
        self.assertDictEqual(w, {"more_than_4": 0, "uneven_number": 0})

        cs1 = "1|4|1|4|1|4|2m|5".split("|")
        cs2 = "1|1|4|5|1|1|4|5".split("|")
        cs1, dummy, w = self.till_reader._parse_chord_sequence(cs1)
        cs2, dummy, w = self.till_reader._parse_chord_sequence(cs2)
        tcs1 = TillessenChordSequence(cs1)
        tcs2 = TillessenChordSequence(cs2)
        self.assertEqual(tcs1.similarity(tcs2, sim_type="match", minor_parallels=False), (.375, ''))

    def testParseChord(self):
        #return
        self.init_reader()
        ch1, ch2 = self.till_reader._parse_bar("b7m1ab5d2m01b52mb7m")
        gt_chords = [Chord("Bb-"), Chord("C+"), Chord("F#o"), Chord("D-")]
        for i in range(len(ch1)):
            self.assertEqual(ch1[i], gt_chords[i])


""" Function calls all unit tests """
if __name__ == '__main__':
    alltests = unittest.TestSuite([unittest.TestLoader().loadTestsFromTestCase(TestTillessenReader)])
    unittest.main()
