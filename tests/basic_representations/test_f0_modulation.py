#!/usr/bin/env python

""" Unit test for F0Modulation class """

import unittest

import pytest

from melospy.basic_representations.f0_modulation import *


class TestF0Modulation( unittest.TestCase ):

    #@pytest.mark.skip(reason="Assertion mismatch")
    def testConstructor(self):
        """ test constructor """
        f0mod = F0Modulation()
        self.assertEqual(str(f0mod), "Annotated: -- |Range: -- cents|Freq: -- Hz|Dev: -- cents")

        f0mod= F0Modulation.fromDict({})
        self.assertEqual(str(f0mod), "Annotated: -- |Range: -- cents|Freq: -- Hz|Dev: -- cents")

        f0mod= F0Modulation.fromList([])
        self.assertEqual(str(f0mod), "Annotated: -- |Range: -- cents|Freq: -- Hz|Dev: -- cents")

        f0mod= F0Modulation.fromStruct(F0Modulation())
        self.assertEqual(str(f0mod), "Annotated: -- |Range: -- cents|Freq: -- Hz|Dev: -- cents")

        f0mod= F0Modulation("vib", range_cents=100.0)
        self.assertEqual(str(f0mod), "Annotated: vibrato |Range: 100.0 cents|Freq: -- Hz|Dev: -- cents")

        values = ['', 12.0, 2.3]
        f0mod= F0Modulation.fromList(values)
        self.assertEqual(str(f0mod), "Annotated:  |Range: 12.0 cents|Freq: 2.3 Hz|Dev: -- cents")


        values = {'annotated': 'vibrato', 'range_cents': 23.0, 'freq_hz': .5, 'median_dev':.5}
        f0mod= F0Modulation.fromDict(values)
        self.assertEqual(str(f0mod), "Annotated: vibrato |Range: 23.0 cents|Freq: 0.5 Hz|Dev: 0.5 cents")


        values_l = ['vib', 23.0, .5, .5]
        values_d = {'annotated': 'vibrato', 'range_cents': 23, 'freq_hz': .5, 'median_dev':.5}
        l1 = F0Modulation.fromStruct(values_l)
        l2 = F0Modulation.fromStruct(values_d)
        self.assertEqual(l1.__ne__(l2), False)
        self.assertEqual(l2.__eq__(l1), True)
        self.assertEqual(F0Modulation().__eq__(F0Modulation()), True)

        self.assertRaises(ValueError, F0Modulation.fromDict, [])
        self.assertRaises(ValueError, F0Modulation.fromList, {})

if __name__ == "__main__":
    unittest.main()
