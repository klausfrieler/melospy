#!/usr/bin/env python

""" Unit test for NoteName class """

import unittest

from melospy.basic_representations.note_name import *


class TestNoteName( unittest.TestCase ):
    """ Unit test for NoteName class """

    def testConstructorWithParameters(self):
        """ Test constructor with initial note name label """
        for noteName in self.getValidNoteLetterValues():
            n = NoteName(noteName)
            self.assertEqual(noteName, n.getNoteName(), "Error in constructor of NoteName class, note label is not set properly!")

    def testConstructorNoteNameWithOctave(self):
        """ Test constructor with initial note name label """
        noteName1 = "Ab"
        noteName2 = "A"
        for octaves in self.getValidOctaveLabels():
            if octaves != None:
                n = NoteName(noteName1 + octaves)
                self.assertEqual(noteName1 + octaves, n.getNoteName())
                n = NoteName(noteName2 + octaves)
                self.assertEqual(noteName2 + octaves, n.getNoteName())

        for octaves in self.getInvalidOctaveLabels():
            self.assertRaises(Exception, NoteName.__init__, noteName1 + octaves)

    def testConstructorNoteNameGeneric(self):
        """ Test constructor with initial note name label """
        self.assertEqual(NoteName("Ab", generic = True).getNoteName(), "Ab")
        self.assertEqual(NoteName("bb", generic = True).getNoteName(), "Bb")
        self.assertEqual(NoteName("bb", generic = True).isGeneric(), True)
        self.assertEqual(NoteName("Gb-1").isGeneric(), False)
        self.assertRaises(Exception, NoteName.__init__, "Ab7", generic = True)

    def testSetNoteLabel(self):
        """ Test set function for note name via note label """
        n = NoteName("Ab")
        # valid calls
        for val in self.getValidNoteLabels():
            n.setNoteLabel(val)
        # non-valid calls
        for val in self.getNonValidNoteLabels()[3:]:
            self.assertRaises(ValueError, n.setNoteLabel, val)

    def testGetPitchClass(self):
        """ Test function to convert note name to corresponding pitch class value """
        self.assertEqual(NoteName("C").getPitchClass(), 0)
        self.assertEqual(NoteName("C4").getPitchClass(), 0)
        self.assertEqual(NoteName("C").getPitchClass(), 0)
        self.assertEqual(NoteName("C-1").getPitchClass(), 0)
        self.assertEqual(NoteName("B9").getPitchClass(), 11)

        self.assertEqual(NoteName("C").getPitchClass(circle_of_fifths=True), 0)
        self.assertEqual(NoteName("Db").getPitchClass(circle_of_fifths=True), 7)
        self.assertEqual(NoteName("D").getPitchClass(circle_of_fifths=True), 2)
        self.assertEqual(NoteName("Gb").getPitchClass(circle_of_fifths=True), 6)
        self.assertEqual(NoteName("F#").getPitchClass(circle_of_fifths=True), 6)

    def testGetMIDIPitch(self):
        """ Test function to convert note name of NoteNameoOctve to corresponding MIDI pitch """
        self.assertEqual(NoteName("C").getMIDIPitch(), 0)
        self.assertEqual(NoteName("C4").getMIDIPitch(), 60)
        self.assertEqual(NoteName("C").getMIDIPitch(), 0)
        self.assertEqual(NoteName("C-1").getMIDIPitch(), NoteName("C").getPitchClass())
        self.assertEqual(NoteName("B9").getMIDIPitch(), 131)
        self.assertEqual(NoteName("C#6").getMIDIPitch(), 85)
        #print n.getMIDIPitch()

    def testGetLilyPondPitch(self):
        """ Test function to convert note name of NoteNameoOctvae to corresponding LilyPond name"""
        self.assertEqual(NoteName("C").getLilypondName(), "c")
        self.assertEqual(NoteName("C8").getLilypondName(), "c'''''")
        self.assertEqual(NoteName("C7").getLilypondName(), "c''''")
        self.assertEqual(NoteName("C6").getLilypondName(), "c'''")
        self.assertEqual(NoteName("C5").getLilypondName(), "c''")
        self.assertEqual(NoteName("C4").getLilypondName(), "c'")
        self.assertEqual(NoteName("C3").getLilypondName(), "c")
        self.assertEqual(NoteName("C2").getLilypondName(), "c,")
        self.assertEqual(NoteName("C1").getLilypondName(), "c,,")
        self.assertEqual(NoteName("C0").getLilypondName(), "c,,,")
        self.assertEqual(NoteName("C-1").getLilypondName(), "c,,,,")
        self.assertEqual(NoteName("C#4").getLilypondName(), "cis'")
        self.assertEqual(NoteName("C#4").getLilypondName(flat=True), "des'")
        self.assertEqual(NoteName("Bb4").getLilypondName(flat=True), "bes'")
        self.assertEqual(NoteName("Bb4").getLilypondName(flat=False), "ais'")
        self.assertEqual(NoteName("Bb", generic=True).getLilypondName(), "bes")
        self.assertEqual(NoteName("F#", generic=True).getLilypondName(flat=True), "fis")

        #self.assertEqual(NoteName("C-1").getLilypondName(), NoteName("C").getPitchClass())
        #self.assertEqual(NoteName("B9").getLilypondName(), 131)
        #self.assertEqual(NoteName("C#6").getLilypondName(), 85)
        #print n.getMIDIPitch()

    def testFromMIDIPitch(self):
        """ Test function to convert MIDI pitch note name to NoteName object"""
        #print NoteName(NoteName(65))
        self.assertEqual(NoteName(64).getPitchClass(), 4)
        self.assertEqual(NoteName.fromMIDIPitch(67).getPitchClass(), 7)
        self.assertEqual(NoteName(48).getNoteName(), "C3")
        self.assertRaises(TypeError, NoteName(12).__init__, NoteName(65))
        self.assertRaises(ValueError, NoteName(12).__init__, 165)

    def testFromAccidental(self):
        self.assertEqual(NoteName.fromAccidentals(0, True), NoteName("C"))
        self.assertEqual(NoteName.fromAccidentals(0, False), NoteName("C"))
        self.assertEqual(NoteName.fromAccidentals(1, True), NoteName("G"))
        self.assertEqual(NoteName.fromAccidentals(1, False), NoteName("F"))
        self.assertEqual(NoteName.fromAccidentals(6, True), NoteName("F#"))
        self.assertEqual(NoteName.fromAccidentals(6, False), NoteName("Gb"))

    def testFlatSide(self):
        results = (False, False, True, True, False, False, False, True)
        vnl = self.getValidNoteLabels()
        for i in range(len(vnl)):
            #print vnl[i], NoteName(vnl[i]), NoteName(vnl[i]).onTheFlatSide()
            self.assertEqual(NoteName(vnl[i]).onTheFlatSide(), results[i])

    def testEnharmonic(self):
        tests   = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        results = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B']
        for i in range(len(tests)):
             test_note = NoteName(tests[i])
             result_note = NoteName(results[i])
             self.assertEqual(test_note.getEnharmonic(), result_note)
             self.assertEqual(result_note.getEnharmonic(), test_note)

    def getValidNoteLetterValues(self):
        """ Return valid note letter values """
        return ('A', 'B', 'C', 'D', 'E', 'F', 'G')

    def getNonValidNoteLetterValues(self):
        """ Return non-valid note letter values """
        return ('H', 'AA', '')

    def getValidNoteAccidentalSigns(self):
        """ Return valid note accidentals """
        return ('b', '', '#')

    def getNonValidNoteAccidentalSigns(self):
        """ Return non-valid note accidentals """
        return ('bb', 'B', '#+', '-', '.')

    def getValidNoteLabels(self):
        """ Return valid note name labels """
        return ('C', 'C#', 'eb', 'F', 'F#', 'g', 'a#', 'Bb')

    def getNonValidNoteLabels(self):
        """ Return non-valid note name labels """
        return ('CC', '#', 'b.', 'Fis', 'h', 'H', 'a##', 'Bb#')

    def getNoteLetterAndCorrespondingPitchClass(self):
        """ Return note letters and corresponding pitch class values """
        return ('A', 'B', 'C', 'D', 'E', 'F', 'G'), ( 9, 11, 0, 2, 4, 5, 7 )

    def getNoteAccidentalAndCorrespondingPitchClassShift(self):
        """ Return note accidentals and corresponding pitch class values """
        return ('b', '', '#'), ( -1, 0, 1)

    def getValidOctaveLabels(self):
        """ Return valid note name labels """
        return ('-1', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', None)

    def getInvalidOctaveLabels(self):
        """ Return valid note name labels """
        return ('10', 'r', '1.1')


if __name__ == "__main__":
    unittest.main()
