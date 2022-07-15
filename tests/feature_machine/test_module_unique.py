#!/usr/bin/env python

import unittest

import numpy as np

from melospy.feature_machine.feature_module_unique import MelopyFeatureModuleUnique


class TestModuleUnique( unittest.TestCase ):
    """ Unit test for unique module """
  
    def testModuleFunctionality(self):
        """ Test unique module """
        m = MelopyFeatureModuleUnique()
        
        m.setParameterValue("inputVec", [np.array([1, 1, 1, 2, 3])])
        m.process()
        self.assertEqual(np.array_equal(m.getParameterValue("outputVec")[0], np.array([1, 2, 3])), True)
        
        m.setParameterValue("inputVec", [np.array([1.12, 1.12, 1.12])])
        m.process()
        self.assertEqual(np.array_equal(m.getParameterValue("outputVec")[0], np.array([1.12])), True)
        
        m.setParameterValue("inputVec", [[]])
        m.process()
        self.assertEqual(m.getParameterValue("outputVec")[0], [])
        
        m.setParameterValue("inputVec", [['a', 'b', 'b']])
        m.process()
        self.assertEqual(m.getParameterValue("outputVec")[0], ['a', 'b'])
        

if __name__ == "__main__":
    unittest.main()
