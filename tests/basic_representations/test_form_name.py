#!/usr/bin/env python

""" Unit test for FormName class """

import unittest

from melospy.basic_representations.form_name import *


class TestFormName( unittest.TestCase ):
    """ Unit test for FormName class """

    def testConstructor(self):
        """ Test constructor with initial form name label """
        #valid stuff
        s = "B'''177788787"
        fm = FormName(s)
        self.assertEqual(fm.getLabel(), s)
        self.assertEqual(fm.getLetter(), "B")
        self.assertEqual(fm.getModifier(), "'''")
        self.assertEqual(fm.getModifierCount(), 3)
        self.assertEqual(fm.hasWildcard(), False)
        self.assertEqual(FormName("*A1").hasWildcard(), True)
        self.assertEqual(FormName("A1").getModifierCount(), 0)
        self.assertEqual(fm.getNumber(), 177788787)
        self.assertEqual(str(fm), s)

        #invalid stuff
        self.assertRaises(TypeError,  fm.__init__, 2.)
        self.assertRaises(ValueError, fm.__init__, "K")
        self.assertRaises(ValueError, fm.__init__, "A ")
        self.assertRaises(ValueError, fm.__init__, "AA")
        self.assertRaises(ValueError, fm.__init__, "AA1")
        self.assertRaises(ValueError, fm.__init__, "'''")
        self.assertRaises(ValueError, fm.__init__, "'''1")
        self.assertRaises(ValueError, fm.__init__, "A'''B")

        a1 = FormName("A1")
        a2 = FormName("A2")
        a3 = FormName("A'2")
        b1 = FormName("B1")
        b2 = FormName("*B1")

        self.assertEqual(a1 == a1.clone(), True)
        self.assertEqual(b1 == b2, False)
        self.assertEqual(b2 == b2.clone(), True)
        self.assertEqual(a1 >= a1.clone(), True)
        self.assertEqual(a1 > a1.clone(), False)

        self.assertEqual(a2 > a1, True)
        self.assertEqual(a2 >= a1, True)
        self.assertEqual(a2 < a1, False)
        self.assertEqual(a2 <= a1, False)

        self.assertEqual(a3 > a2, True)
        self.assertEqual(a3 >= a2, True)
        self.assertEqual(a3 < a2, False)
        self.assertEqual(a3 <= a2, False)

        self.assertEqual(b1 > a2, True)
        self.assertEqual(b1 >= a2, True)
        self.assertEqual(b1 < a2, False)
        self.assertEqual(b1 <= a2, False)

    def testSetFormLabel(self):
        """ Test set function for note name via note label """
        fm = FormName("A1")
        # valid calls
        s = "B'''177788787"
        fm.setLabel(s)
        self.assertEqual(fm.getLabel(), s)
        self.assertEqual(fm.getLetter(), "B")
        self.assertEqual(fm.getModifier(), "'''")
        self.assertEqual(fm.getNumber(), 177788787)
        self.assertEqual(str(fm), s)

        self.assertRaises(TypeError,  fm.setLabel, 2.)
        self.assertRaises(ValueError, fm.setLabel, "AA")
        self.assertRaises(ValueError, fm.setLabel, "AA1")
        self.assertRaises(ValueError, fm.setLabel, "'''")
        self.assertRaises(ValueError, fm.setLabel, "'''1")
        self.assertRaises(ValueError, fm.setLabel, "A'''B")

        # non-valid calls


class TestFormPart( unittest.TestCase ):
    """ Unit test for FormName class """

    def getTestChordsSeqElements(self):
        c = [Chord("C7"), Chord("Fmaj7"), Chord("E-6"), Chord("A79#")]
        return [ChordSequenceElement(c[0], 4, 1, 2),
                ChordSequenceElement(c[1], 4, 3, 8),
                ChordSequenceElement(c[2], 4, 3, 2),
                ChordSequenceElement(c[3], 4, 1, 4)]*2

    def testConstructor(self):
        """ Test constructor with initial form name label """
        #valid stuff
        s = "B'''177788787"
        fm = FormPart(s, 8)
        self.assertEqual(fm.getLabel(), s)
        self.assertEqual(fm.getLetter(), "B")
        self.assertEqual(fm.getModifier(), "'''")
        self.assertEqual(fm.getModifierCount(), 3)
        self.assertEqual(FormName("A1").getModifierCount(), 0)
        self.assertEqual(fm.getNumber(), 177788787)
        self.assertEqual(fm.getLength(), 8)
        self.assertEqual(str(fm), "(" + s + ",8)")

        #invalid stuff
        self.assertRaises(TypeError,  fm.__init__, 2., 8)
        self.assertRaises(ValueError, fm.__init__, "A ", 8)
        self.assertRaises(ValueError, fm.__init__, "AA", 8)
        self.assertRaises(ValueError, fm.__init__, "AA1", 8)
        self.assertRaises(ValueError, fm.__init__, "'''", 8)
        self.assertRaises(ValueError, fm.__init__, "'''1", 8)
        self.assertRaises(ValueError, fm.__init__, "A'''B", 8)
        self.assertRaises(TypeError, fm.__init__, "A1", "t")
        self.assertRaises(TypeError, fm.__init__, "A1", 8.1)

        a1 = FormPart("A1", 8)
        a2 = FormPart("A2", 8)
        a3 = FormPart("A'2", 8)
        b1 = FormPart("B1", 8)
        b2 = FormName("*B1")

        self.assertEqual(a1 == a1.clone(), True)
        self.assertEqual(b1 == b2, False)
        self.assertEqual(b2 == b2.clone(), True)
        self.assertEqual(a1 >= a1.clone(), True)
        self.assertEqual(a1 > a1.clone(), False)

        self.assertEqual(a2 > a1, True)
        self.assertEqual(a2 >= a1, True)
        self.assertEqual(a2 < a1, False)
        self.assertEqual(a2 <= a1, False)

        self.assertEqual(a3 > a2, True)
        self.assertEqual(a3 >= a2, True)
        self.assertEqual(a3 < a2, False)
        self.assertEqual(a3 <= a2, False)

        self.assertEqual(b1 > a2, True)
        self.assertEqual(b1 >= a2, True)
        self.assertEqual(b1 < a2, False)
        self.assertEqual(b1 <= a2, False)

        a_wc = FormPart("A1", 8, self.getTestChordsSeqElements())
        a_wc = FormPart("A1", 8, self.getTestChordsSeqElements())
        self.assertEqual(a_wc.chords.length_in_bars(), 8)
        #print a_wc.chords
class TestFormDefinition( unittest.TestCase ):
    """ Unit test for FormDefintion class """

    def testConstructor(self):
        fp = FormDefinition([])


        fp.append(FormName("I1"))
        self.assertEqual(fp[0].getLabel(), "I1")

        fp.append(FormName("A1"))
        self.assertEqual(fp[0].getLabel(), "I1")

        fp.append("A'2")
        self.assertEqual(fp[0].getLabel(), "I1")

        fp.append("I'2")
        self.assertEqual(fp[0].getLabel(), "I1")

        fp.clear()
        self.assertEqual(fp.isEmpty(), True)

        fp = FormDefinition([FormName("A1"), FormName("A2"), FormName("B1"), FormName("A3")])
        self.assertEqual(fp[0].getLabel(), "A1")

        fp.clear()

        fp.append(FormPart("A1", 8))
        self.assertEqual(fp[0].getLabel(), "A1")
        self.assertEqual(fp[0].getLength(), 8)

        fp.append(FormPart("B1", 8))
        self.assertRaises(ValueError, fp.append, FormPart("A3", 8))
        self.assertRaises(ValueError, fp.append, FormPart("A1", 8))
        self.assertRaises(ValueError, fp.append, FormPart("A''2", 8))
        self.assertRaises(ValueError, fp.append, FormPart("B'3", 8))

        fp.append(FormPart("*D''3", 8))
        self.assertEqual(fp.getLength(), 24)

        fp = FormDefinition([("A1", 8), ("A2", 8), ("B1", 8), ("A3", 8)])

        self.assertEqual(fp[0].getLabel(), "A1")
        self.assertEqual(fp[0].getLength(), 8)

        fp = FormDefinition([("*B1", 8), ("A3", 8)])
        self.assertEqual(fp[0].getLabel(), "B1")
        self.assertEqual(fp[0].getLength(), 8)

        #fp = FormDefinition([("A1", 8), ("A2", 8), ("B1", 8), ("A3", 8), ("A1", 8), ("A2", 8), ("B'1", 8), ("A3", 8)])
        #print fp
        self.assertRaises(ValueError, fp.__init__, [("A1", 8), ("A2", 8), ("B'1", 8), ("A3", 8)])
        self.assertRaises(ValueError, fp.__init__, [("A1", 8), ("A3", 8), ("B1", 8), ("A3", 8)])
        self.assertRaises(ValueError, fp.__init__, [("A2", 8), ("A3", 8), ("B1", 8), ("A4", 8)])
        self.assertRaises(ValueError, fp.__init__, [("A1", 8), ("A2", 8), ("B1", 8), ("AC3", 8)])

        self.assertRaises(ValueError, fp.__init__, [("*A1", 8), ("A3", 8), ("B1", 8)])
        self.assertRaises(ValueError, fp.__init__, [("*A1", 8), ("B2", 8), ("B1", 8)])
        self.assertRaises(ValueError, fp.__init__, [("*A1", 8), ("B2", 8), ("A3", 8)])
        self.assertRaises(ValueError, fp.__init__, [("*A1", 8), ("B2", 8), ("A3", 8)])
        #fp.append(FormName("A''3"))
        #print fp
        self.assertEqual(str(FormDefinition.fromString("AABA")), str(FormDefinition([("A1", 8), ("A2", 8), ("B1", 8), ("A3", 8)])))
        self.assertEqual(str(FormDefinition.fromString("A8B16")), str(FormDefinition([("A1", 8), ("B1", 16)])))
        self.assertRaises(ValueError, fp.fromString, "BCD")
        fp = FormDefinition.fromString("A8A'16B16A12")
        self.assertEqual(fp.getShortForm(withLengths = True), "A8A'16B16A12")
        self.assertEqual(fp.getShortForm(withLengths = False), "AA'BA")
        self.assertEqual(FormDefinition().getShortForm(withLengths = False), "")
        self.assertEqual(str(FormDefinition.fromString("")), "")

if __name__ == "__main__":
    unittest.main()
