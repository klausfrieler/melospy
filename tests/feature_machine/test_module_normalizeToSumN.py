#!/usr/bin/env python

""" Unit test for normalizeToSumN module """

import unittest

import numpy as np

from melospy.feature_machine.feature_module_normalizeToSumN import MelopyFeatureModuleNormalizeToSumN


class TestModuleNormalizeToSumN( unittest.TestCase ):
    """ Unit test for normalizeToSumN module """
  
    def testNormalizeToSumNModuleFunctionality(self):
        """ Test normalizeToSumN module """

        m = MelopyFeatureModuleNormalizeToSumN()
        m.setParameterValue("inputVec", [np.array([2., 1., 2., 0.])])
        m.setParameterValue("N", np.array([1]))
        m.process()
        self.assertEqual(np.array_equal(m.getParameterValue("outputVec")[0], np.array([.4, .2, .4, 0])), True)
 
if __name__ == "__main__":
    unittest.main()
