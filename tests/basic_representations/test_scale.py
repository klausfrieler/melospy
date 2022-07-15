#!/usr/bin/env python

""" Unit test for class Scale """
import argparse
import unittest

from melospy.basic_representations.chord import *
from melospy.basic_representations.jm_util import dict_from_keys_vals
from melospy.basic_representations.scale import *


class TestScale( unittest.TestCase ):

    def testConstructor(self):
        # test with valid initialization
        c = Scale("Major", (2, 2, 1, 2, 2, 2, 1))
        self.assertEqual(c.getDescription(), "Major")
        self.assertEqual(c.getIntervalStructure(), (2, 2, 1, 2, 2, 2, 1))

        # test with non-valid initialization
        #self.assertRaises(Exception, c.__init__, 1,(2,2,1,2,2,2,1),'Ionian')
        self.assertRaises(Exception, c.__init__, "Major", (2, 2, 11, 2, 2, 2, 1), 'Ionian')
        #self.assertRaises(Exception, c.__init__, "Majror",(2,2,1,2,2,2,1),2)

    def testSetDescription(self):
        """ test label set function """
        c = Scale()
        # valid calls
        c.setDescription("Major")
        self.assertEqual(c.getDescription(), "Major")
        # non-valid calls

    def testSetIntervalStructure(self):
        """ test interval structure set function """
        c = Scale()
        # valid calls
        for val in self.getValidIntervalStructureValues():
            c.intervalStructure = val
        # non-valid calls
        for val in self.getNonValidIntervalStructureValues():
            self.assertRaises(Exception, c.setIntervalStructure, val)

    def testPitchStuff(self):
        """ test pitch set calculation"""
        scale = theScaleManager('maj')

        #getMIDIPitches
        self.assertEqual(scale.getMIDIPitches(0, 7), [0, 2, 4, 5, 7, 9, 11])
        self.assertEqual(scale.getMIDIPitches(0, 0), [0, 2, 4, 5, 7, 9, 11])
        self.assertEqual(scale.getMIDIPitches(0), [0, 2, 4, 5, 7, 9, 11])
        self.assertEqual(scale.getMIDIPitches(), [0, 2, 4, 5, 7, 9, 11])
        self.assertEqual(scale.getMIDIPitches(125, 7), [125, 127])
        self.assertEqual(scale.getMIDIPitches(125, 7, False), [125, 127, 129, 130, 132, 134, 136])


        self.assertRaises(Exception, scale.getMIDIPitches, -1)
        self.assertRaises(Exception, scale.getMIDIPitches, "r")
        self.assertRaises(Exception, scale.getMIDIPitches, -1)
        self.assertRaises(Exception, scale.getMIDIPitches, 0, -1)

        # pitch classes
        self.assertEqual(scale.getPitchClasses(125), [0, 2, 4, 5, 7, 9, 10])
        self.assertEqual(scale.getPitchClasses(65), scale.getPitchClasses(125))

        #inside

        self.assertEqual(scale.inside(0), True)
        self.assertEqual(scale.inside(1), False)
        self.assertEqual(scale.inside(11+12), True)
        self.assertEqual(scale.inside([0, 2, 3, 4]), 3)
        self.assertEqual(scale.inside([0, 2, 3, 4, 14]), 3)
        self.assertEqual(scale.inside([1, 3, 6, 8, 10]), 0)

        self.assertEqual(scale.__len__(), 7)

        #self.assertRaises(Exception, scale.inside, 1.)
        #self.assertRaises(Exception, scale.inside, "r")
        #print "\n{}".format(set(theScaleManager("alt").getMIDIPitches() + theScaleManager("wtht").getMIDIPitches()))

    def getValidIntervalStructureValues(self):
        return ((3, 3, 3, 3), (2, 2, 1, 2, 2, 2, 1), (1, 2, 1, 2, 1, 2, 1, 2))

    def getNonValidIntervalStructureValues(self):
        return (1.2332, 12, "IntervalStructure", [4, 4, 4, 4], (4, 4, 4, 3), (1, 2, 1, 2, 1, 2, 1, 1))


class TestScaleManager( unittest.TestCase ):
    def calcCompatibility(self, c):
        compats = {}
        for root in range(60, 72):
            print("Root: {}".format(NoteName(root).setOctave(None)))
            print("---------------------------------------")
            for k in scale_list:
                if not scale_list[k]:  continue
                comp = theScaleManager.calcCompatibility(k, root, c.getPitchClassSet())[0]
                compats[k] = comp
            sort_comp = sorted(compats, key=compats.get, reverse=True)
            values =  [(compats[s], len(scale_list[s])) for s in sort_comp]
            compats = dict_from_keys_vals(sort_comp, values)
            chordLen = len(c)
            maxVal = chordLen
            for s in sort_comp:
                if compats[s][0]<maxVal:
                    break
                else:
                    maxVal= compats[s][0]
                print(s, compats[s], round(float(compats[s][0])/compats[s][1], 2))
            print("==================================")

    def testConstructor(self):
        # test with valid initialization
        #self.assertRaises(Exception, theScaleManager.__call__, "XXX")
        scale = theScaleManager("maj")
        self.assertEqual(scale.getDescription(), "Major")
        self.assertEqual(scale.getIntervalStructure(), (2, 2, 1, 2, 2, 2, 1))
        scale = theScaleManager("MAJ")
        self.assertEqual(scale.getDescription(), "Major")
        #theScaleManager.calcScaleCompatibilities()
    def testMethods(self):
        c = Chord("C")
        self.assertEqual(theScaleManager.calcCompatibility('min', "C", c.getPitchClassSet()), (2, 7))
        self.assertEqual(theScaleManager.calcCompatibility('min', "C", [0, 0, 3, 3, 7, 7, 7, 7, 8], weighted = True), (9, 7))
        self.assertEqual(theScaleManager.calcCompatibility('min', "C", c.getPitchClassSet(), normed = True), 2.0/7)
        self.assertEqual(theScaleManager.calcCompatibility('min', "C", [0, 0, 3, 3, 7, 7, 7, 9], weighted = True, normed = True), 1.0)
        #print theScaleManager.matchScale([0,10,9,7], "F")

if __name__ == "__main__":
    unittest.main()
