#!/usr/bin/env python

""" Unit test for class Song"""

import unittest

from melospy.basic_representations.simple_meta_data import *
from melospy.basic_representations.song import *


class TestSong( unittest.TestCase ):

    def testConstructor(self):
        # test with valid initialization
        ci = CompositionInfo("All the Things Your Are", "Johnny Mercer", [("A1", 8), ("A2", 8), ("B1", 8), ("A3", 8)])
        smd = SimpleMetaData(ci)
        s = Song(Melody(), smd)
        m = Melody()
        r = Rhythm()
        self.assertEqual(s.getMetadata(), smd)
        #self.assertEqual(str(s),"Supersong")
        # test with non-valid initialization
        self.assertRaises(Exception, s.__init__, r, "moin")
        self.assertRaises(Exception, s.__init__, m, 1)
        self.assertRaises(Exception, s.__init__, r, 1)

        C4 = 60
        C5 = C4 + 12
        mg = Melody()
        #4/4 signature, period = 4, equal beat proportions
        mi = MeterInfo(4, 4)
        #four sixteenth per Beat, .5 sec per beat = 120 bpm
        bi = BeatInfo(4, .5)
        mc = MetricalContext(bi, mi)
        mp = MetricalPosition(1, 2, 3, 0, mc)

        #add a lot more of events
        bis = [BeatInfo(2, .5), BeatInfo(3, .5), BeatInfo(5, .5), BeatInfo(6, .5)]
        for i in range(16):
            duration = 1./8
            onset    = 1 + i*duration
            mc = mc.clone().setBeatInfo(bis[i % len(bis)].clone())
            mp1 = MetricalPosition( i + 1, 1, 2, 0, mc)
            me = MetricalNoteEvent(onset, C4, mp1, duration/2, i)
            mg.append(me)
        s = Song(mg, smd)
        self.assertEqual(s.getMelodyEvents()[15], MetricalNoteEvent(3.-1./8, C4, MetricalPosition(16, 1, 2, 0, mc), 1./16, 16))

        #print s

    def testGetSetMetadata(self):
        """ test label set function """
        ci = CompositionInfo("All the Things Your Are", "Johnny Mercer", [("A1", 8), ("A2", 8), ("B1", 8), ("A3", 8)])
        smd = SimpleMetaData(ci)
        s = Song(Melody(), smd)

        self.assertEqual(s.getMetadata(), smd)

        ci = CompositionInfo("Autumn Leaves", "NN", [("A1", 8), ("A2", 8), ("B1", 8), ("A3", 8)])
        smd.setCompositionInfo(ci)
        s.setMetadata(smd)
        self.assertEqual(s.getMetadata().getCompositionInfo(), ci)
        self.assertRaises(Exception, s.setMetadata, s)
        self.assertRaises(Exception, s.setMetadata, 1)


    def testGetSetMelody(self):
        """ test interval structure set function """
        s = Song()
        m = Melody()
        r = Rhythm()
        # valid calls
        s.setMelody(m)
        self.assertRaises(Exception, s.setMelody, "r")
        self.assertRaises(Exception, s.setMelody, r)


if __name__ == "__main__":
    unittest.main()
