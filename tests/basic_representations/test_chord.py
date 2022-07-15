#!/usr/bin/env python

""" Unit test for Chord class """

import unittest

import pytest

from melospy.basic_representations.chord import *
from melospy.basic_representations.note_name import *


class TestChord( unittest.TestCase ):
    """ Unit test for Chord class """

    def testConstructorAndSetAndGetChordLabel(self):
        """ Test constructor & set and get function for chord label """
        c = Chord("F79b9#")
        #print c.getChordLabel()
        #print c.getLilypondTemplate()
        c = Chord("Dbmaj711#")
        self.assertEqual(c.getLilypondTemplate(), "des{}:maj11+.9")
        c = Chord("Db711#13b")
        self.assertEqual(c.getLilypondTemplate(), "des{}:13-.911+")
        c = Chord("Db-")
        self.assertEqual(c.getLilypondTemplate(), "des{}:min")
        c = Chord("Fb")
        self.assertEqual(c.getLilypondTemplate(), "fes{}")
        c = Chord("NC")
        self.assertEqual(c.getLilypondTemplate(), "r{}")
        c=Chord("NC")
        self.assertEqual(c.getChordLabel(), "NC")
        c = Chord("Cj7/E")
        self.assertEqual(c.getChordLabel(), "Cj7/E")
        c = Chord("Cmin11")
        self.assertEqual(c.getChordLabel(), "C-7911")
        c = Chord("Caug13b")
        self.assertEqual(c.getChordLabel(), "C+7913b")
        c = Chord("Cm7b5")
        self.assertEqual(c.getChordLabel(), "Cm7b5")
        c = Chord("C7b5")
        self.assertEqual(c.getChordLabel(), "C7alt")
        c = Chord("Cdim7")
        self.assertEqual(c.getChordLabel(), "Co7")
        c = Chord("Cmaj7")
        self.assertEqual(c.getChordLabel(), "Cj7")
        c = Chord("C")
        self.assertEqual(c.getChordTypeLabel(reduced=True), "maj")
        c = Chord("C7alt")
        self.assertEqual(c.getChordLabel(), "C7alt")

    def testSetAndGetRootNote(self):
        """ Test set and get function for chord root note in class Chord() """
        # 1) pass note name object to set function
        n = NoteName("C#")
        c = Chord()
        c.rootnote = n
        self.assertEqual(c.rootnote, n)
        del c
        del n

        # 2) pass note name as string to set function
        c = Chord
        c.rootnote = "C#"
        self.assertEqual(c.rootnote, "C#")

    def testSetAndGetBassNote(self):
        """ Test set and get function for chord bass note in class Chord() """
        # 1) pass note name object to set function
        n = NoteName("Eb")
        c = Chord()
        c.bassnote = n
        self.assertEqual(c.bassnote, n)
        del c
        del n

        # 2) pass note name as string to set function
        c = Chord
        c.bassnote = "F"
        self.assertEqual(c.bassnote, "F")

    def testGetPitchClassSet(self):
        self.assertEqual(Chord("NC").getPitchClassSet(),  None)
        self.assertEqual(Chord("C").getPitchClassSet(),  [0, 4, 7])
        self.assertEqual(Chord("Cm").getPitchClassSet(), [0,  3,  7])
        self.assertEqual(Chord("Cmin").getPitchClassSet(), [0,  3,  7])
        self.assertEqual(Chord("C-").getPitchClassSet(), [0,  3,  7])
        self.assertEqual(Chord("C+").getPitchClassSet(), [0,  4,  8])
        self.assertEqual(Chord("Caug").getPitchClassSet(), [0,  4,  8])
        self.assertEqual(Chord("Cdim").getPitchClassSet(), [0,  3,  6])
        self.assertEqual(Chord("Co").getPitchClassSet(), [0,  3,  6])
        self.assertEqual(Chord("Csus").getPitchClassSet(), [0,  5,  7])
        self.assertEqual(Chord("C6").getPitchClassSet(), [0,  4,  7, 9])
        self.assertEqual(Chord("C69").getPitchClassSet(), [0, 2, 4,  7, 9])

        self.assertEqual(Chord("C7").getPitchClassSet(), [0, 4, 7, 10])
        self.assertEqual(Chord("Cj7").getPitchClassSet(),  [0, 4, 7, 11])
        self.assertEqual(Chord("Cmaj7").getPitchClassSet(),  [0, 4, 7, 11])
        self.assertEqual(Chord("Cm7").getPitchClassSet(), [0, 3, 7, 10])
        self.assertEqual(Chord("C-7").getPitchClassSet(), [0, 3, 7, 10])
        self.assertEqual(Chord("Cmin7").getPitchClassSet(), [0, 3, 7, 10])
        self.assertEqual(Chord("Cmj7").getPitchClassSet(), [0, 3, 7, 11])
        self.assertEqual(Chord("C-j7").getPitchClassSet(), [0, 3, 7, 11])
        self.assertEqual(Chord("Cminj7").getPitchClassSet(), [0, 3, 7, 11])
        self.assertEqual(Chord("Cdim7").getPitchClassSet(), [0, 3, 6, 9])
        self.assertEqual(Chord("Co7").getPitchClassSet(), [0, 3, 6, 9])
        self.assertEqual(Chord("C-7b5").getPitchClassSet(), [0, 3, 6, 10])
        self.assertEqual(Chord("Cmin7b5").getPitchClassSet(), [0, 3, 6, 10])
        self.assertEqual(Chord("Cm7b5").getPitchClassSet(), [0, 3, 6, 10])
        self.assertEqual(Chord("C+7").getPitchClassSet(), [0, 4, 8, 10])
        self.assertEqual(Chord("Caug7").getPitchClassSet(), [0, 4, 8, 10])
        self.assertEqual(Chord("C+j7").getPitchClassSet(), [0, 4, 8, 11])
        self.assertEqual(Chord("Csus7").getPitchClassSet(), [0,  5,  7, 10])
        self.assertEqual(Chord("C7alt").getPitchClassSet(), [0, 1, 3, 4, 6, 7, 8, 10])
        self.assertEqual(Chord("C79b9#").getPitchClassSet(), [0, 1, 3, 4,  7, 10])


        self.assertEqual(Chord("C9").getPitchClassSet(), [0, 2, 4, 7, 10])
        self.assertEqual(Chord("Cj79").getPitchClassSet(), [0, 2, 4, 7, 11])
        self.assertEqual(Chord("C+9").getPitchClassSet(), [0, 2, 4, 8, 10])
        self.assertEqual(Chord("C79#").getPitchClassSet(), [0,  3, 4, 7, 10])

        self.assertEqual(Chord("Cm9").getPitchClassSet(), [0, 2, 3, 7, 10])
        self.assertEqual(Chord("C-9").getPitchClassSet(), [0, 2, 3, 7, 10])
        self.assertEqual(Chord("Cmin9").getPitchClassSet(), [0, 2, 3, 7, 10])

        self.assertEqual(Chord("Csus79b").getPitchClassSet(), [0,  1, 5,  7, 10])
        self.assertEqual(Chord("Csus79").getPitchClassSet(), [0,  2, 5,  7, 10])
        self.assertEqual(Chord("Csus9").getPitchClassSet(), [0,  2, 5,  7, 10])
        self.assertEqual(Chord("Csus13").getPitchClassSet(), [0,  2,  5,  7,  9, 10])

        self.assertEqual(Chord("Cm11").getPitchClassSet(), [0, 2, 3, 5, 7, 10])
        self.assertEqual(Chord("Cmin11").getPitchClassSet(), [0, 2, 3, 5, 7, 10])
        self.assertEqual(Chord("C-11").getPitchClassSet(), [0, 2, 3, 5, 7, 10])

        self.assertEqual(Chord("C11").getPitchClassSet(), [0, 2, 4, 5, 7, 10])
        self.assertEqual(Chord("C9b11").getPitchClassSet(), [0, 1, 4, 5, 7, 10])
        self.assertEqual(Chord("C11").getPitchClassSet(), [0, 2, 4, 5, 7, 10])

        self.assertEqual(Chord("C13").getPitchClassSet(), [0, 2, 4,  7, 9, 10])
        self.assertEqual(Chord("Caug13b").getPitchClassSet(), [0, 2, 4,  8,  10])
        self.assertEqual(Chord("C+13b").getPitchClassSet(), [0, 2, 4,  8,  10])
        self.assertEqual(Chord("C79b11#13b").getPitchClassSet(), [0, 1, 4,  6, 7, 8, 10])

        self.assertEqual(Chord("C/F").getPitchClassSet(), [0,  4,  7])
        self.assertEqual(Chord("C/F").getPitchClassSet(includeBass=True), [0,  4,  5, 7])
        self.assertEqual(Chord("AbDIM").getPitchClassSet(includeBass=True), [0,  3,  6])
        self.assertEqual(Chord("F7").getPitchClassSet(rootRelative = False), [0, 3, 5, 9])
        self.assertEqual(Chord("F7/Eb").getPitchClassSet(includeBass=True, rootRelative = False), [0, 3, 5, 9])
        self.assertEqual(Chord("F7/D").getPitchClassSet(includeBass=True, rootRelative = False), [0, 2, 3, 5, 9])
        self.assertEqual(Chord("C7alt").getPitchClassSet(withTensions = False), [0, 4, 7, 10])
        self.assertEqual(Chord("Coj6").getPitchClassSet(withTensions = False), [0, 3, 6, 9])
        #self.assertEqual(Chord("C79b11#13b").__len__(), 7)
        #print Chord("D-").getMostLikelyScale()
        self.assertEqual(Chord("C").onTheFlatSide(), False)
        self.assertEqual(Chord("C-").onTheFlatSide(), True)
        self.assertEqual(Chord("C7").onTheFlatSide(), True)
        self.assertEqual(Chord("C7alt").onTheFlatSide(), True)
        self.assertEqual(Chord("Dm7b5").onTheFlatSide(), True)
        self.assertEqual(Chord("Em7b5").onTheFlatSide(), True)
        self.assertEqual(Chord("Fmaj711#").onTheFlatSide(), False)
        self.assertEqual(Chord("Do7").onTheFlatSide(), True)
        self.assertEqual(Chord("G#-7").onTheFlatSide(), False)
        self.assertEqual(Chord("Ab-7").onTheFlatSide(), True)
        self.assertEqual(Chord("Eb7").onTheFlatSide(), True)
        self.assertEqual(Chord("Db7").onTheFlatSide(), True)
        self.assertEqual(Chord("C#7").onTheFlatSide(), False)

    def testGetDiatonicPitchClass(self):
        c1 = Chord("C")
        c2 = Chord("C-7")
        pitches = list(range(0, 11))
        mapping_ext1 = ['1', '-', '2', 'B', '3', '4', 'T', '5', '%', '6', '7', 'L']
        mapping1     = ['1', '2', '2', 'B', '3', '4', 'T', '5', '6', '6', '7', 'L']
        mapping_ext2 = ['1', '-', '2', '3', '>', '4', 'T', '5', '%', '6', '7', 'L']
        mapping2     = ['1', '2', '2', '3', '>', '4', 'T', '5', '6', '6', '7', 'L']

        for p in pitches:
            self.assertEqual(c1.getDiatonicPitchClass(p+60), mapping1[p])
            self.assertEqual(c1.getDiatonicPitchClass(p+60, extended=True), mapping_ext1[p])
            self.assertEqual(c2.getDiatonicPitchClass(p+60), mapping2[p])
            self.assertEqual(c2.getDiatonicPitchClass(p+60, extended=True), mapping_ext2[p])

        self.assertEqual(Chord("NC").getDiatonicPitchClass(60, extended=True), "X")


    def testChordConstructorWithoutBassNote(self):
        """ Test constructor without bass note """
        rootNoteNames = []
        rootNoteNames = self.appendAllValidNoteNames(rootNoteNames)
        for rootNoteName in rootNoteNames:
            for triadType in self.getValidTriadTypeValues():
                chordName = rootNoteName + triadType
                #c = Chord(chordName)
                #del c


    def testChordConstructorWithBassNote(self):
        """
        Test constructor with simple major chord that includes
        slash-notation for bass note
        """
        rootNoteNames = []
        rootNoteNames = self.appendAllValidNoteNames(rootNoteNames)
        bassNoteNames = []
        NamesrootNotes = self.appendAllValidNoteNames(bassNoteNames)
        for rootNoteName in rootNoteNames:
            for bassNoteName in bassNoteNames:
                chordName = rootNoteName + "/" + bassNoteName
                #c = Chord(chordName)
                #del c

    def testComparison(self):
        self.assertEqual(Chord("C7alt") == Chord("C7alt"), True)
        self.assertEqual(Chord("C7alt") != Chord("C7alt"), False)
        self.assertEqual(Chord("C7alt") == Chord("C79"), False)
        self.assertEqual(Chord("C7alt") != Chord("C79"), True)
        self.assertEqual(Chord("C7alt") == None, False)
        self.assertEqual(Chord("C7alt") != None, True)
        self.assertEqual(Chord("C7alt") == 3, False)
        self.assertEqual(Chord("C7alt") != 3, True)

    def testIsMinorParallel(self):
        test1  = [[Chord("C"), Chord("F"), Chord("G")], [Chord("Am"), Chord("Dm"), Chord("Em")]]
        test2  = [[Chord("C"), Chord("F"), Chord("G")], [Chord("A"), Chord("D"), Chord("E")]]
        test3  = [[Chord("C7"), Chord("F7"), Chord("G7")], [Chord("Am"), Chord("D"), Chord("Em")]]
        test4  = [[Chord("Cj7"), Chord("Fj7"), Chord("Gj7")], [Chord("Am"), Chord("Dm"), Chord("Em")]]
        test5  = [[Chord("Cj7"), Chord("Fj7"), Chord("Gj7")], [Chord("Am7"), Chord("Dm7"), Chord("Em7")]]

        for j in range(len(test1[0])):
            self.assertEqual(test1[1][j].isMinorParallel(test1[0][j]), True)
            self.assertEqual(test1[0][j].isMinorParallel(test1[1][j]), False)
            self.assertEqual(test2[1][j].isMinorParallel(test2[0][j]), False)
            self.assertEqual(test2[0][j].isMinorParallel(test2[1][j]), False)
            self.assertEqual(test3[1][j].isMinorParallel(test3[0][j]), False)
            self.assertEqual(test3[0][j].isMinorParallel(test3[1][j]), False)
            self.assertEqual(test4[1][j].isMinorParallel(test4[0][j]), True)
            self.assertEqual(test4[0][j].isMinorParallel(test4[1][j]), False)
            self.assertEqual(test5[1][j].isMinorParallel(test5[0][j]), True)
            self.assertEqual(test5[0][j].isMinorParallel(test5[1][j]), False)

    def appendAllValidNoteNames(self, list):
        for noteLetter in self.getValidNoteLetters():
            for noteAccidental in self.getValidNoteAccidentals():
                list.append(noteLetter + noteAccidental)
        return list

    def getValidNoteLabels(self):
        """ Return valid note name labels """
        return ('C', 'C#', 'eb', 'F', 'F#', 'g', 'a#', 'Bb')

    def getNonValidNoteLabels(self):
        """ Return non-valid note name labels """
        return ('CC', '#', 'b.', 'Fis', 'h', 'H', 'a##', 'Bb#')

    def getValidNoteLetters(self):
        """ Return note letters and corresponding pitch class values """
        return ('A', 'B', 'C', 'D', 'E', 'F', 'G')

    def getValidNoteAccidentals(self):
        """ Return note accidentals and corresponding pitch class values """
        return ('b', '', '#')

    def getValidTriadTypeValues(self):
        """ Return valid values for triad type """
        return ("aug", "maj", "dim", "min", "sus", "DIM", "AUG", "MIN", "MAJ", "SUS", "m", "+", "-")

    def getValidStartBarValues(self):
        """ Return valid values for chord start in bars """
        return (0, 1, 2, 3, 4, 5)

    def getNonValidStartBarValues(self):
        """ Return non-valid values for chord start in bars """
        return (-1, 'ere', 0.2, 3.22222, 5.00001)

    def getValidStartBeatValues(self):
        """ Return valid values for chord start in beats """
        return (1, 2, 3.5, 4.1, 5)

    def getNonValidStartBeatValues(self):
        """ Return non-valid values for chord start in beats """
        return (0, -1, 'ere', 0.9)

    def getValidLengthBeatValues(self):
        """ Return valid values for chord length in beats """
        return (0.5, 1, 2, 3.5, 4, 5)

    def getNonValidLengthBeatValues(self):
        """ Return non-valid values for chord length in beats """
        return (0, -1, 'ere')


if __name__ == "__main__":
    unittest.main()
