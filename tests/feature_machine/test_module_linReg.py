#!/usr/bin/env python

import unittest

import numpy as np

import melospy.feature_machine.test_help_functions as thf
from melospy.feature_machine.feature_module_linReg import MelopyFeatureModuleLinReg


class TestModuleLinReg( unittest.TestCase ):
    """ Unit test for linReg module """
  
    def testLinRegModuleFunctionality(self):
        """ Test linReg module """
        m = MelopyFeatureModuleLinReg()
        # simple linear function: intercept = 1, slope = 1
        m.setParameterValue("inputVec", [np.array([1, 2, 3, 4])])
        m.process()
        self.assertEqual(thf.my_array_equal(m.getParameterValue("outputVec")[0], np.array([1, 1])), True)
        
        # simple linear function: intercept = 1, slope = 0
        m.setParameterValue("inputVec", [np.array([1, 1, 1, 1])])
        m.process()
        self.assertEqual(thf.my_array_equal(m.getParameterValue("outputVec")[0], np.array([0, 1])), True)
        
        # simple linear function: intercept = 2, slope = -0.5
        m.setParameterValue("inputVec", [np.array([2, 1.5, 1, .5, 0])])
        m.process()
        self.assertEqual(thf.my_array_equal(m.getParameterValue("outputVec")[0], np.array([-.5, 2])), True)
        
        m.setParameterValue("inputVec", [np.array([1, -2, -3, -4])])
        m.process()
        self.assertEqual(thf.my_array_equal(m.getParameterValue("outputVec")[0], np.array([-1.6, .4])), True)

if __name__ == "__main__":
    unittest.main()
