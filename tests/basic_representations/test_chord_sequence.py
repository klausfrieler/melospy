#!/usr/bin/env python

""" Unit test for Chord Sequences classes """

import unittest

from melospy.basic_representations.chord_sequence import *


class TestChordSequence( unittest.TestCase ):
    """ Unit test for Chord Sequence classes """
    def getTestChords(self):
        return [Chord("C7"), Chord("Fmaj7"), Chord("E-6")]

    def getTestChordsSeqElements(self):
        c = self.getTestChords()
        return [ChordSequenceElement(c[0], 4, 1, 2),
                ChordSequenceElement(c[1], 4, 3, 8),
                ChordSequenceElement(c[2], 4, 3, 2)]

    def testSeqElement(self):
        """ Test constructor """
        c1 = Chord("C7")
        c2 = Chord("Fmaj7")
        c3 = Chord("E-6")
        c1e = ChordSequenceElement(c1, 4, 1, 2)
        c2e = ChordSequenceElement(c2, 4, 3, 8)
        c3e = ChordSequenceElement(c3, 4, 3, 2)
        c4e = ChordSequenceElement(c3, 4, 3, 6)
        c5e = ChordSequenceElement(Chord("F"), 4, 2, 1)
        #c4e = ChordSequenceElement(c3, 4, 1, 3.5)
        #print c1e.__repr__(), c1e
        #print c2e
        #print c3e
        #print c4e
        self.assertEqual(str(c1e), "|C7 ")
        self.assertEqual(str(c2e), "Fj7 |Fj7   |Fj7 ")
        self.assertEqual(str(c3e), "E-6 |")
        self.assertEqual(str(c4e), "E-6 |E-6   |")
        self.assertEqual(str(c5e), "F")
        self.assertEqual(c1e.rest_beats(), 4)
        self.assertEqual(c2e.rest_beats(), 2)
        self.assertEqual(c1e.length_in_bars(), .5)
        self.assertEqual(c1e.to_chord_vector(), [c1, c1])
        c1_split = c1e.split()
        self.assertEqual(c1_split, [c1e])
        c2_split = c2e.split()
        self.assertEqual(len(c2_split), 3)
        self.assertEqual(sum(len(_.to_chord_vector()) for _ in c2_split), c2e.length)
        self.assertRaises(ValueError, c1e.fuse, c1e)
        self.assertRaises(ValueError, c1e.fuse, c2e)
        self.assertEqual(str(c2e), str(c2_split[0].fuse(c2_split[1]).fuse(c2_split[2])))

    def testChordSequences(self):
        cse = self.getTestChordsSeqElements()
        cs = ChordSequence()
        for c in cse:
            cs.append(c)
        self.assertEqual(cs.length_in_bars(), 3.0)
        self.assertEqual(cs.length_in_beats(), 12.0)
        cs.append(ChordSequenceElement(Chord("F"), 4, 1, 3))
        self.assertEqual(cs.length_in_bars(), 3.75)
        self.assertRaises(ValueError, cs.append, ChordSequenceElement(Chord("F"), 4, 2, 3))
        self.assertEqual(str(cs), str(cs.normalize()))
        del cs
        cs = ChordSequence(cse)
        self.assertEqual(cs.length_in_bars(), 3.0)
        cs = ChordSequence(self.getTestChords())
        self.assertEqual(cs.length_in_bars(), 3.0)
        self.assertEqual(cs.to_chord_vector(), self.getTestChords())
        #print "\n".join([str(cse) for cse in cs])
        #print cs.normalize()
        strlist = ["C", "", "", "", "Fj7", "", "G", "", "", "", "", "", "Bb",]
        cs = ChordSequence.fromStringList(strlist, 4, fill_up=True)
        #print repr(cs)
        cs2 = ChordSequence.fromString(str(cs))
        self.assertEqual(str(cs), str(cs2))
        #print "-"*60
        strlist = ["C", "C/B", "C/Bb", "C/A", "Fj7", "", "G", "", "", "", "", "", "Bb"]
        cs = ChordSequence.fromStringList(strlist, 4, fill_up=True)
        self.assertEqual(cs.count_unique_chords(), 7)
        #print cs.simplify()
        #print cs
        #self.assertEqual(cs.unique_chords(), set([Chord("C"), Chord("C/Bb"), Chord("C/B"), Chord("C/A"), Chord("Bb"), Chord("Fj7"), Chord("G")]))
        cs2 = ChordSequence.fromString(str(cs))
        self.assertEqual(str(cs), str(cs2))
        strlist = ["NC", "NC", "NC", "NC"]
        cs = ChordSequence.fromStringList(strlist, 4, fill_up=True)
        self.assertEqual(str(cs.simplify()), "||NC   ||")
        strlist = ["C", "C", "C", "C"]
        cs = ChordSequence.fromStringList(strlist, 4, fill_up=True)
        self.assertEqual(str(cs.simplify()), "||C   ||")

        #print cs2
        #for _ in cs2:
        #    print repr(_)
        #    print "Chord: '{}'".format(str(_))
if __name__ == "__main__":
    unittest.main()
