#!/usr/bin/env python

""" Unit test for runLength module """

import unittest

import numpy as np

from melospy.feature_machine.feature_module_runLength import MelopyFeatureModuleRunLength


class TestModuleRunLength( unittest.TestCase ):
    """ Unit test for runLength module """
  
    def testRunLengthModuleFunctionality(self):
        """ Test module functionality """
        m = MelopyFeatureModuleRunLength()
        m.setParameterValue("inputVec", [np.array([0, 0, 1, 0, 1, 1, 0, 1, -1, 0])])
        m.process()
        self.assertEqual(np.array_equal(m.getParameterValue("boolMask")[0], np.array([False, True, True, True, False, True, True, True, True, True])), True)
        self.assertEqual(np.array_equal(m.getParameterValue("segStartIdx")[0], np.array([0, 2, 3, 4, 6, 7, 8, 9])), True)
        self.assertEqual(np.array_equal(m.getParameterValue("segVal")[0], np.array([0, 1, 0, 1, 0, 1, -1, 0])), True)
        self.assertEqual(np.array_equal(m.getParameterValue("segLen")[0], np.array([2, 1, 1, 2, 1, 1, 1, 1])), True)
        

if __name__ == "__main__":
    unittest.main()
