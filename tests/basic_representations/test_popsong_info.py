#!/usr/bin/env python

""" Unit test for class Section """

#from section import *
import unittest

from melospy.basic_representations.popsong_info import *


class TestPopSongInfo( unittest.TestCase ):

    def testConstructor(self):

        si = PopSongInfo("The Beatles", "Hey Jude", 120, "MEDIUM", "4/4", Key("F", "maj"), "122.csv")

        # test with valid initialization
        self.assertEqual(si.getArtist(), "The Beatles")
        self.assertEqual(si.getTitle(), "Hey Jude")
        self.assertEqual(si.avgtempo, 120)
        self.assertEqual(si.filename, "122.csv")
        self.assertEqual(si.getSignature(), Signature.fromString("4/4"))
        #print str(si.getKey())
        #print str(Key("B", "maj"))

        self.assertEqual(si.getKey().__eq__(Key("F", "maj")), True)
        self.assertEqual(si.getKey() != Key.fromString("B min"), True)

        # test with non-valid initialization
        self.assertRaises(ValueError, si.setSignature, "ABAShgs")
        self.assertRaises(TypeError, si.setSignature, 1)
        self.assertRaises(ValueError, si.setKey, "ABAShgs")
        self.assertRaises(TypeError, si.setKey, 1)
        #self.assertRaises(ValueError, si.setStyle, "ABC")
        #self.assertRaises(ValueError, si.setRhythmFeel, "ABC")
        #self.assertRaises(ValueError, si.setTempoClass, "ABC")
        #print si

if __name__ == "__main__":
    unittest.main()
