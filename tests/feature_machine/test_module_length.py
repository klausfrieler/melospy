#!/usr/bin/env python

""" Unit test for length module """

import unittest

import numpy as np

from melospy.feature_machine.feature_module_length import MelopyFeatureModuleLength


class TestModuleLength( unittest.TestCase ):
    """ Unit test for length module """
  
    def testLengthModuleFunctionality(self):
        """ Test length module """
        m = MelopyFeatureModuleLength()
        m.setParameterValue("inputVec", [np.array([1, 2, 3, 4])])
        m.process()
        self.assertEqual(np.array_equal(m.getParameterValue("outputVec")[0], 4), True)

        m.setParameterValue("inputVec", ['AABCCCD'])
        m.process()
        self.assertEqual(m.getParameterValue("outputVec")[0], 7)
        
        m.setParameterValue("inputVec", [['A', 'A', 'B', 'C', 'C', 'C', 'D']])
        m.process()
        self.assertEqual(m.getParameterValue("outputVec")[0], 7)
        
        m.setParameterValue("inputVec", [['AB', 'BC', 'CC']])
        m.process()
        self.assertEqual(m.getParameterValue("outputVec")[0], 3)
        
        m.setParameterValue("inputVec", [[('A', 1), ('A', 1), ('A', 2), ('B', 3)]])
        m.process()
        self.assertEqual(m.getParameterValue("outputVec")[0], 4)
        
        m.setParameterValue("inputVec", [[(1.5, 1), (1.5, 1)]])
        m.process()
        self.assertEqual(m.getParameterValue("outputVec")[0], 2)

if __name__ == "__main__":
    unittest.main()
