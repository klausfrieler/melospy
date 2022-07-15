#!/usr/bin/env python

""" Unit test for Loudness class """

import unittest

import pytest

from melospy.basic_representations.loudness import *


class TestLoudness( unittest.TestCase ):

    #@pytest.mark.skip(reason="Assertion mismatch")
    def testConstructor(self):
        """ test constructor """
        loudness = Loudness()
        self.assertEqual(loudness.__str__(False), "Max: -- dB | Med: -- dB | SD: -- dB | Peak: -- | TC: -- | SNB: --")

        loudness = Loudness.fromDict({})
        self.assertEqual(loudness.__str__(False), "Max: -- dB | Med: -- dB | SD: -- dB | Peak: -- | TC: -- | SNB: --")

        loudness = Loudness.fromList([])
        self.assertEqual(loudness.__str__(False), "Max: -- dB | Med: -- dB | SD: -- dB | Peak: -- | TC: -- | SNB: --")

        loudness = Loudness.fromStruct(Loudness())
        self.assertEqual(loudness.__str__(False), "Max: -- dB | Med: -- dB | SD: -- dB | Peak: -- | TC: -- | SNB: --")

        loudness = Loudness(1.2, temp_centroid=.5)
        self.assertEqual(loudness.__str__(False), "Max: 1.2 dB | Med: -- dB | SD: -- dB | Peak: -- | TC: 0.5 | SNB: --")

        values = [1.2, 2.3]
        loudness = Loudness.fromList(values)
        self.assertEqual(loudness.__str__(False), "Max: 1.2 dB | Med: 2.3 dB | SD: -- dB | Peak: -- | TC: -- | SNB: --")

        values = [1.2, 2.3, .5, .5, .5]
        loudness = Loudness.fromList(values)
        self.assertEqual(loudness.__str__(False), "Max: 1.2 dB | Med: 2.3 dB | SD: 0.5 dB | Peak: 0.5 | TC: 0.5 | SNB: --")

        values = {'max': 1.2, 'median': 2.3, 'stddev': .5, 'rel_peak_pos':.5, 'temp_centroid':.5}
        loudness = Loudness.fromDict(values)
        self.assertEqual(loudness.__str__(False), "Max: 1.2 dB | Med: 2.3 dB | SD: 0.5 dB | Peak: 0.5 | TC: 0.5 | SNB: --")

        values = {'max': 1.2, 'median': 2.3, 'stddev': .5, 'rel_peak_pos':.5, 'temp_centroid':.5}
        loudness = Loudness.fromStruct(values)
        self.assertEqual(loudness.__str__(False), "Max: 1.2 dB | Med: 2.3 dB | SD: 0.5 dB | Peak: 0.5 | TC: 0.5 | SNB: --")

        values_l = [1.2, 2.3, .5, .5, .5]
        values_d = {'max': 1.2, 'median': 2.3, 'stddev': .5, 'rel_peak_pos':.5, 'temp_centroid':.5}
        l1 = Loudness.fromStruct(values_l)
        l2 = Loudness.fromStruct(values_d)
        self.assertEqual(l1.__ne__(l2), False)
        self.assertEqual(l2.__eq__(l1), True)
        self.assertEqual(Loudness().__eq__(Loudness()), True)

        self.assertRaises(ValueError, Loudness.fromDict, [])
        self.assertRaises(ValueError, Loudness.fromList, {})

if __name__ == "__main__":
    unittest.main()
