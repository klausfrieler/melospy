#!/usr/bin/env python

""" Unit test for localExtrema module """

import unittest

import numpy as np

from melospy.feature_machine.feature_module_localExtrema import MelopyFeatureModuleLocalExtrema


class TestModuleLocalExtrema( unittest.TestCase ):
    """ Unit test for localExtrema module """
  
    def testLocalExtremaModuleFunctionality(self):
        """ Test module functionality """
        m = MelopyFeatureModuleLocalExtrema()
        m.setParameterValue("inputVec", [np.array([1])])
        m.setParameterValue("mode", "max")
        m.process()
        self.assertEqual(np.array_equal(m.getParameterValue("outputVec")[0], np.array([1], dtype=bool)), True)
        
        m = MelopyFeatureModuleLocalExtrema()
        m.setParameterValue("inputVec", [np.array([1])])
        m.setParameterValue("mode", "min")
        m.process()
        self.assertEqual(np.array_equal(m.getParameterValue("outputVec")[0], np.array([1], dtype=bool)), True)
        
        m = MelopyFeatureModuleLocalExtrema()
        m.setParameterValue("inputVec", [np.array([1, 1, 2, 3, 4, 3, 0, 1, 0])])
        m.setParameterValue("mode", "max")  
        m.process()
        self.assertEqual(np.array_equal(m.getParameterValue("outputVec")[0], np.array([0, 0, 0, 0, 1, 0, 0, 1, 0], dtype=bool)), True)
        
        m = MelopyFeatureModuleLocalExtrema()
        m.setParameterValue("inputVec", [np.array([1, 1, 2, 3, 4, 3, 0, 1, 0])])
        m.setParameterValue("mode", "max-eq")
        m.process()
        self.assertEqual(np.array_equal(m.getParameterValue("outputVec")[0], np.array([1, 0, 0, 0, 1, 0, 0, 1, 0], dtype=bool)), True)
        
        m.setParameterValue("inputVec", [np.array([10, 8, 1, 5, 2, 2, 5])])
        m.setParameterValue("mode", "min")
        m.process()
        self.assertEqual(np.array_equal(m.getParameterValue("outputVec")[0], np.array([0, 0, 1, 0, 0, 0, 0], dtype=bool)), True)
        
        m.setParameterValue("inputVec", [np.array([10, 8, 1, 5, 2, 2, 5])])
        m.setParameterValue("mode", "min-eq")
        m.process()
        self.assertEqual(np.array_equal(m.getParameterValue("outputVec")[0], np.array([0, 0, 1, 0, 1, 1, 0], dtype=bool)), True)
        

if __name__ == "__main__":
    unittest.main()
