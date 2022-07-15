#!/usr/bin/env python

""" Unit test for diff module """

import unittest

import numpy as np

from melospy.feature_machine.feature_module_diff import MelopyFeatureModuleDiff


class TestModuleDiff( unittest.TestCase ):
    """ Unit test for diff module """
  
    def testDiffModuleFunctionality(self):
        """ Test diff module """
        m = MelopyFeatureModuleDiff()
        m.setParameterValue("inputVec", [np.array([26, 26, 28, 24, 22, 28, 22, 23, 24, 47, 11])])
        m.process()
        self.assertEqual(np.array_equal(m.getParameterValue("outputVec")[0], np.array([0, 2, -4, -2, 6, -6, 1, 1, 23, -36])), True)
        
    def testDiffModuleNonValidInputParameters(self):
        """ Checks that module returns None if input vector has only one element"""
        m = MelopyFeatureModuleDiff()
        m.setParameterValue("inputVec", [np.array([26])])
        m.process()
        self.assertEqual(m.getParameterValue("outputVec")[0], None)

if __name__ == "__main__":
    unittest.main()
