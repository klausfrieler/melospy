""" Unit test for class Section """
import unittest

from melospy.basic_representations.solo_info import *


class TestSoloInfo( unittest.TestCase ):

    def testConstructor(self):
        n = NoteName("Ab")
        k = Key("Ab", 'maj')

        si = SoloInfo(1, "John Coltrane", "Giant Steps", "Alternate Take",  1, "ts", 240.3, "Up", "Hardbop", "Swing", "2/2", False, Key("B", "maj"))

        # test with valid initialization
        self.assertEqual(si.getPerformer(), "John Coltrane")
        self.assertEqual(si.getTitle(), "Giant Steps")
        self.assertEqual(si.getTitleAddOn(), "Alternate Take")
        self.assertEqual(si.getSoloPart(), 1)
        self.assertEqual(si.getInstrument(), "ts")
        self.assertEqual(si.avgtempo, 240.3)
        self.assertEqual(si.getStyle(), "HARDBOP")
        self.assertEqual(si.getSignature(), Signature.fromString("2/2"))
        self.assertEqual(si.hasMeterChanges(), False)
        #print str(si.getKey())
        #print str(Key("B", "maj"))

        self.assertEqual(si.getKey().__eq__(Key("B", "maj")), True)
        self.assertEqual(si.getKey() != Key.fromString("B min"), True)

        # test with non-valid initialization
        self.assertRaises(ValueError, si.setSignature, "ABAShgs")
        self.assertRaises(TypeError, si.setSignature, 1)
        self.assertRaises(ValueError, si.setKey, "ABAShgs")
        self.assertRaises(TypeError, si.setKey, 1)
        self.assertRaises(ValueError, si.setStyle, "ABC")
        self.assertRaises(ValueError, si.setRhythmFeel, "ABC")
        self.assertRaises(ValueError, si.setTempoClass, "ABC")
        #print si

if __name__ == "__main__":
    unittest.main()
