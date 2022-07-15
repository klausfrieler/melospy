#!/usr/bin/env python

""" Unit test for selector module """

import unittest

import numpy as np

from melospy.feature_machine.feature_module_selector import MelopyFeatureModuleSelector


class TestModuleSelector( unittest.TestCase ):
    """ Unit test for selector module """
  
    def testSelectorModuleFunctionality(self):
        """ Test for item selection via boolean mask """
        m = MelopyFeatureModuleSelector()
        m.setParameterValue("inputVec", [np.array([0.1, 1, 2.1, 3, 4.1, 5])])
        m.setParameterValue("selectVec", [np.array([1, 1, 0, 0, 1, 1])])
        m.process()
        self.assertEqual(np.array_equal(m.getParameterValue("outputVec")[0], np.array([0.1, 1, 4.1, 5])), True)
         
        m.setParameterValue("inputVec", [np.array([0.1, 1, 2.1, 3, 4.1, 5])])
        m.setParameterValue("selectVec", [np.array([True, True, False, False, True, True])])
        m.process()
        self.assertEqual(np.array_equal(m.getParameterValue("outputVec")[0], np.array([0.1, 1, 4.1, 5])), True)
         
 
    def testSelectorModuleWithSingleIndex(self):
        """ Test for item selection via boolean mask with one element """
        m = MelopyFeatureModuleSelector()
        m.setParameterValue("inputVec", [np.array([1, 2, 3, 4])])
        m.setParameterValue("selectVec", [np.array([2])])
        m.process()
        self.assertEqual(m.getParameterValue("outputVec")[0], 3)

    def testSelectorModuleWithBinsInsteadOfBoolMask(self):
        """ Test for item selection via indices """
        m = MelopyFeatureModuleSelector()
        m.setParameterValue("inputVec", [np.array([1, 2, 3, 4])])
        m.setParameterValue("selectVec", [np.array([3, 2, 1, 0])])
        m.setParameterValue("boolMask", False)
        m.process()
        self.assertEqual(np.array_equal(m.getParameterValue("outputVec")[0], np.array([4, 3, 2, 1])), True)

        
        
        
if __name__ == "__main__":
    unittest.main()
