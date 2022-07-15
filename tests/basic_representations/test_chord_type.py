#!/usr/bin/env python

""" Unit test for ChordType class """

import unittest

from melospy.basic_representations.chord_type import *


class TestChordType( unittest.TestCase ):

    def testSetTriadTypeValidValues(self):
        """ test triad type set function """
        c = ChordType()
        # valid calls
        for val in self.getValidTriadTypeValues():
            c.triadType = val
        # non-valid calls
        for val in self.getNonValidTriadTypeValues():
            self.assertRaises(Exception, c.setTriadType, val)

    def testSeventh(self):
        """ Test seventh set function """
        c = ChordType()
        # valid calls
        validValues = self.getValidSeventhValues()
        for val in validValues:
            c.seventh = val

    def testNinth(self):
        """ Test ninth set function """
        c = ChordType()
        # valid calls
        validValues = self.getValidNinthValues()
        for val in validValues:
            c.ninth = val

    def testEleventh(self):
        """ Test eleventh set function """
        c = ChordType()
        # valid calls
        validValues = self.getValidEleventhValues()
        for val in validValues:
            c.eleventh = val

    def testThirteenth(self):
        """ Test thirteenth set function """
        c = ChordType()
        # valid calls
        validValues = self.getValidThirteenthValues()
        for val in validValues:
            c.thirteenth = val

    def testGetLilypondLabel(self):
        c = ChordType("79#11#13b")
        self.assertEqual(c.getLilypondLabel(), "13-.9+11+")
        c = ChordType("7alt")
        self.assertEqual(c.getLilypondLabel(), "13-.9+11+")
        c = ChordType("m7b5")
        self.assertEqual(c.getLilypondLabel(), "min5-7")
        c = ChordType("j79")
        self.assertEqual(c.getLilypondLabel(), "maj9")
        c = ChordType("79")
        self.assertEqual(c.getLilypondLabel(), "9")
        self.assertEqual(c.getLilypondLabel(), "9")

    def testGetChordTypeLabel(self):
        """ Test getChordTypeLabel() function """
        #does not work anymore because of polysemantics and subsequent standardization of labels
        #c = ChordType()
        #for (triadTypeKey, triadTypeLabel) in c.triadTypeLabel.items():
        #    for (seventhKey, seventhLabel) in c.seventhLabel.items():
        #        for (ninthKey, ninthLabel) in c.ninthLabel.items():
        #            for (eleventhKey, eleventhLabel) in c.eleventhLabel.items():
        #                for (thirteenthKey, thirteenthLabel) in c.thirteenthLabel.items():
        #                    c.triadType = triadTypeKey
        #                    c.seventh = seventhKey
        #                    c.ninth = ninthKey
        #                    c.eleventh =eleventhKey
        #                    c.thirteenth = thirteenthKey
        #                    for triadLabel in triadTypeLabel:
        #                        chordLabel = triadLabel + seventhLabel + ninthLabel + eleventhLabel + thirteenthLabel
        #                        if c.seventh == 0 and c.triadType == "dim":
        #                            chordLabel = "m7b5" + ninthLabel + eleventhLabel + thirteenthLabel
        #                        msg = chordLabel + ":" + c.getChordTypeLabel() + " seventh  :" + str(seventhKey)
        #                        self.assertEqual(c.getChordTypeLabel(), chordLabel, msg)

    def testDimChord(self):
        """ Test special behavior for diminished chords """
        c = ChordType("dim")
        self.assertEqual(c.triadType, "dim")
        #self.assertEqual(c.seventh,-1)

    def testSetChordTypeByLabelInConstructor(self):
        """ Test if chord label is set properly when given as parameter in constructor of the class """
        #does not work anymore because of polysemantics and subsequent standardization of labels
        c = ChordType()

        #for (triadTypeKey, triadTypeLabel) in c.triadTypeLabel.items():
        #    for (seventhKey, seventhLabel) in c.seventhLabel.items():
        #        for (ninthKey, ninthLabel) in c.ninthLabel.items():
        #            for (eleventhKey, eleventhLabel) in c.eleventhLabel.items():
        #                for (thirteenthKey, thirteenthLabel) in c.thirteenthLabel.items():
        #                    chordLabel = triadTypeLabel[0] + seventhLabel + ninthLabel + eleventhLabel + thirteenthLabel;
        #                    c2 = ChordType(chordLabel)
                            #KF disabled test because it doesn't work any more due to the implied tension (e.g, a ninth implies a seventh)
                            #self.assertEqual(chordLabel, c2.getChordTypeLabel())
        #                    del c2

    def getValidTriadTypeValues(self):
        """ Return valid values for triad type """
        return ("aug", "maj", "dim", "min", "sus", "DIM", "AUG", "MIN", "MAJ", "SUS", "m", "-", "+")

    def getNonValidTriadTypeValues(self):
        """ Return non-valid values for triad type """
        return ("diim", "dm", "1", "MA", "12a", "ss")

    def getValidSeventhValues(self):
        """ Return value seventh values """
        return ("N/A", -1, 0, 1)

    def getValidNinthValues(self):
        """ Return value ninth values """
        return ("N/A", -1, 0, 1)

    def getValidEleventhValues(self):
        """ Return value eleventh values """
        return ("N/A", 0, 1)

    def getValidThirteenthValues(self):
        """ Return value thirteenth values """
        return ("N/A", -1, 0)


if __name__ == "__main__":
    unittest.main()
