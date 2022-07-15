#!/usr/bin/env python

""" Unit test for class Key """

import unittest

from melospy.basic_representations.chord import *
from melospy.basic_representations.key import *
from melospy.basic_representations.scale import *


class TestKey( unittest.TestCase ):

    def testConstructor(self):
        # test with valid initialization
        n = NoteName("Ab", )
        k = Key("Ab", 'maj')
        self.assertEqual(str(k), "Ab-maj")

        k = Key(n, 'maj')
        self.assertEqual(str(k), "Ab-maj")

        k = Key("C#", 'min')
        self.assertEqual(str(k), "C#-min")

        k = Key("Eb", 'wtht')
        self.assertEqual(str(k), "Eb-wtht")

        k = Key("Fb", 'none')
        self.assertEqual(str(k), "Fb")
        k1 = k.clone()
        self.assertEqual(k == k1, True)

        k1 = Key.fromString("E wt")
        self.assertEqual(str(k1), "E-wt")

        k1 = Key.fromString("E-chrom")
        self.assertEqual(str(k1), "E-chrom")

        self.assertEqual(Key.fromString("E - maj"), Key.fromString("E-maj"))
        self.assertEqual(Key.fromString("?"), Key.fromString(""))

        self.assertEqual(Key.fromString("Eb-maj").getChordByScaleStep("I"), Chord("Eb"))
        self.assertEqual(Key.fromString("Eb:min").getChordByScaleStep("I"), Chord("Eb-"))

        self.assertEqual(Key.fromString("C-maj").getPitchClasses(), {0, 2, 4, 5, 7, 9, 11})
        self.assertEqual(Key.fromString("C#-maj").getPitchClasses(), {1, 3, 5, 6, 8, 10, 0})

        self.assertEqual(Key.fromAccidentals(0, True), Key("C"))
        self.assertEqual(Key.fromAccidentals(0, False), Key("C"))
        self.assertEqual(Key.fromAccidentals(1, True), Key("G"))
        self.assertEqual(Key.fromAccidentals(1, False), Key("F"))
        self.assertEqual(Key.fromAccidentals(6, True), Key("F#"))
        self.assertEqual(Key.fromAccidentals(6, False), Key("Gb"))

        # test with non-valid initialization
        self.assertRaises(Exception, k.__init__, "Ab", k)
        self.assertRaises(Exception, k.__init__, "Ab4", k)
        self.assertRaises(Exception, k.__init__, "Abb", k)
        self.assertRaises(Exception, k.__init__, "Ab", "Major")
        self.assertRaises(Exception, k.__init__, n, "Ionian")

    def testMethods(self):
        k = Key("Ab", 'maj')
        self.assertEqual(k.getChordByScaleStep("I"), Chord("Ab"))
        self.assertEqual(k.getPitchClasses(), {0, 1, 3, 5, 7, 8, 10})
        self.assertEqual(k.getRootPitchClass(), 8)
        self.assertEqual(k.getMIDIKeyEvent(), (-4, 0))
        self.assertEqual(Key("Eb", "dor").getMIDIKeyEvent(), (-5, 0))
        self.assertEqual(Key("F", "aeol").getMIDIKeyEvent(), (-1, 1))
        self.assertEqual(Key("F", "htwt").getMIDIKeyEvent(), (-1, 0))
        self.assertEqual(Key.fromString("Fb-dorb2").getMIDIKeyEvent(), (2, 0))
        self.assertEqual(Key.fromString("C-maj").getMajorEquivalent(), Key("C", "maj"))
        self.assertEqual(Key.fromString("C-min").getMajorEquivalent(), Key("Eb", "maj"))
        self.assertEqual(Key.fromString("C-dor").getMajorEquivalent(), Key("Bb", "maj"))
        self.assertEqual(Key.fromString("C-harmmin").getMajorEquivalent(), Key("Eb", "maj"))
        self.assertEqual(Key.fromString("C#-mixo").getMajorEquivalent(), Key("F#", "maj"))
        self.assertEqual(Key.fromString("Db-phr").getMajorEquivalent(), Key("A", "maj"))
        self.assertEqual(Key.fromString("C#-mixo").getLilypondString(), r"fis \major")
        self.assertEqual(Key.fromString("Bb-min").getLilypondString(), r"bes \minor")
        self.assertEqual(Key.fromString("F-blues").getLilypondString(), r"f \major")
        self.assertEqual(Key.fromString("G-min").getLilypondString(), r"g \minor")
        k = Key("F", "chrom").getMIDIKeyEvent()


if __name__ == "__main__":
    unittest.main()
