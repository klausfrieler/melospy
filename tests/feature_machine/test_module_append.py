#!/usr/bin/env python

import unittest

import numpy as np

from melospy.feature_machine.feature_module_append import MelopyFeatureModuleAppend


class TestModuleAppend( unittest.TestCase ):
    """ Unit test for append module """
  
    def testAbsModuleFunctionality(self):
        """ Test append module """
        m = MelopyFeatureModuleAppend()
        m.setParameterValue("inputVec", [np.array([26, 1, -1, -23])])
        m.setParameterValue("value", 0)
        m.process()
        self.assertEqual(np.array_equal(m.getParameterValue("outputVec")[0], np.array([26, 1, -1, -23, 0])), True)

        m.setParameterValue("inputVec", [np.array([26, 1, -1, -23])])
        m.setParameterValue("mode", "first")
        m.process()
        self.assertEqual(np.array_equal(m.getParameterValue("outputVec")[0], np.array([26, 1, -1, -23, 26])), True)
        
        m.setParameterValue("inputVec", [np.array([26, 1, -1, -23])])
        m.setParameterValue("mode", "last")
        m.process()
        self.assertEqual(np.array_equal(m.getParameterValue("outputVec")[0], np.array([26, 1, -1, -23, -23])), True)
        

if __name__ == "__main__":
    unittest.main()
