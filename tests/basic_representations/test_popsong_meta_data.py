#!/usr/bin/env python

""" Unit test for class PopSongMetaData"""

import unittest

import pytest

from melospy.basic_representations.popsong_meta_data import *


class TestPopSongMetaData( unittest.TestCase ):

    def testConstructor(self):
        psi = PopSongInfo("The Beatles", "Hey Jude", 120, "MEDIUM", "4/4", Key("F", "maj"))

        smd = PopSongMetaData(psi)
        self.assertEqual(smd.getPopSongInfo(), psi)
        self.assertEqual(smd.getSubInfo("PopSongInfo"), psi)
        self.assertEqual(smd.getField("title"), "Hey Jude")
        self.assertEqual(smd.getField("artist"), "The Beatles")
        self.assertRaises(TypeError, smd.__init__, 0)

        smd = PopSongMetaData(None)
        self.assertEqual(smd.getPopSongInfo(), None)
        #print smd
if __name__ == "__main__":
    unittest.main()
