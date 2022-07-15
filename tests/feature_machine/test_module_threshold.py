#!/usr/bin/env python

""" Unit test for threshold module """

import unittest

import numpy as np

from melospy.feature_machine.feature_module_threshold import MelopyFeatureModuleThreshold


class TestModuleThreshold( unittest.TestCase ):
    """ Unit test for threshold module """
 
    def testArithmeticModuleFunctionality(self):
        """ tests module functionality """
        m = MelopyFeatureModuleThreshold()
        m.setParameterValue("inputVec", [np.array([1, 2, 3])])
        m.setParameterValue("threshold", 2)

        m.setParameterValue("operator", "gt")
        m.process()
        self.assertEqual(np.array_equal(m.getParameterValue("outputVec")[0], np.array([0., 0., 1.])), True)
        
        m.setParameterValue("operator", "ge")
        m.process()
        self.assertEqual(np.array_equal(m.getParameterValue("outputVec")[0], np.array([0., 1., 1.])), True)
        
        m.setParameterValue("operator", "lt")
        m.process()
        self.assertEqual(np.array_equal(m.getParameterValue("outputVec")[0], np.array([1., 0., 0.])), True)
        
        m.setParameterValue("operator", "le")
        m.process()
        self.assertEqual(np.array_equal(m.getParameterValue("outputVec")[0], np.array([1., 1., 0.])), True)
        
        m.setParameterValue("operator", "eq")
        m.process()
        self.assertEqual(np.array_equal(m.getParameterValue("outputVec")[0], np.array([0., 1., 0.])), True)
        
        m.setParameterValue("operator", "ne")
        m.process()
        self.assertEqual(np.array_equal(m.getParameterValue("outputVec")[0], np.array([1., 0., 1.])), True)
        
 
if __name__ == "__main__":
    unittest.main()
