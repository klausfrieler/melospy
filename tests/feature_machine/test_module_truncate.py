#!/usr/bin/env python

import unittest

import numpy as np

from melospy.feature_machine.feature_module_truncate import MelopyFeatureModuleTruncate


class TestModuleTruncate( unittest.TestCase ):
    """ Unit test for append module """
  
    def testAbsModuleFunctionality(self):
        """ Test append module """
        m = MelopyFeatureModuleTruncate()
        m.setParameterValue("inputVec", [np.array([26, 1, -1, -23])])
        m.setParameterValue("value", 0)
        m.process()
        self.assertEqual(np.array_equal(m.getParameterValue("outputVec")[0], np.array([26, 1, -1, -23])), True)

        m.setParameterValue("inputVec", [np.array([26, 1, -1, -23])])
        m.setParameterValue("mode", "front")
        m.setParameterValue("value", 2)
        m.process()
        self.assertEqual(np.array_equal(m.getParameterValue("outputVec")[0], np.array([-1, -23])), True)
        
        m.setParameterValue("inputVec", [np.array([26, 1, -1, -23])])
        m.setParameterValue("mode", "back")
        m.setParameterValue("value", 2)
        m.process()
        self.assertEqual(np.array_equal(m.getParameterValue("outputVec")[0], np.array([26, 1])), True)
        

if __name__ == "__main__":
    unittest.main()
