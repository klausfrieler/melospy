#!/usr/bin/env python

""" Unit test for sum module """

import unittest

import numpy as np

from melospy.feature_machine.feature_module_sum import MelopyFeatureModuleSum


class TestModuleSum( unittest.TestCase ):
    """ Unit test for sum module """
  
    def testAbsModuleFunctionality(self):
        """ Test abs module """
        m = MelopyFeatureModuleSum()
        m.setParameterValue("inputVec", [np.array([1, 2, 3, 4])])
        m.process()
        self.assertEqual(np.array_equal(m.getParameterValue("outputVec")[0], 10), True)

if __name__ == "__main__":
    unittest.main()
