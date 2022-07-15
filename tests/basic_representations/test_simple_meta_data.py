#!/usr/bin/env python

""" Unit test for class SimpleMetaData"""

import unittest

import pytest

from melospy.basic_representations.simple_meta_data import *


class TestSimpleMetaData( unittest.TestCase ):

    def testConstructor(self):
        ci = CompositionInfo("All the Things Your Are", "Johnny Mercer", [("A1", 8), ("A2", 8), ("B1", 8), ("A3", 8)])

        smd = SimpleMetaData(ci)

        self.assertEqual(smd.getCompositionInfo(), ci)
        self.assertEqual(smd.getSubInfo("CompositionInfo"), ci)
        self.assertRaises(TypeError, smd.__init__, 0)

        smd = SimpleMetaData(None)
        self.assertEqual(smd.getCompositionInfo(), None)

if __name__ == "__main__":
    unittest.main()
