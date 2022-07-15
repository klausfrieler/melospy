#!/usr/bin/env python

""" Unit test for logic module """

import unittest

import numpy as np

from melospy.feature_machine.feature_module_logic import MelopyFeatureModuleLogic


class TestModuleLogic( unittest.TestCase ):
    """ Unit test for logic module """
 
    def testLogicModuleExceptionForWrongInputVectorSize(self):
        """ tests that module raises exception if input vectors are not scalars but have different lengths """
        m = MelopyFeatureModuleLogic()
        m.setParameterValue("inputVec1", [np.array([1, 0, 0, 1])])
        m.setParameterValue("inputVec2", [np.array([1, 0, 1])])
        m.setParameterValue("operator", "and")
        self.assertRaises(Exception, m.process)
        m.setParameterValue("inputVec1", [[1, 0, 0, 1]])
        m.setParameterValue("inputVec2", [[1, 0, 1]])
        m.setParameterValue("operator", "and")
        self.assertRaises(Exception, m.process)
  
    def testLogicModuleFunctionality(self):
        """ Test logic module functionality """
        m = MelopyFeatureModuleLogic()
        m.setParameterValue("inputVec1", [np.array([1, 1, 0, 0])])
        m.setParameterValue("inputVec2", [np.array([1, 0, 1, 0])])
        m.setParameterValue("operator", "and")
        m.process()
        self.assertEqual(np.array_equal(m.getParameterValue("outputVec")[0], np.array([1, 0, 0, 0])), True)
        
        m.setParameterValue("inputVec1", [[1, 1, 0, 0]])
        m.setParameterValue("inputVec2", [[1, 0, 1, 0]])
        m.setParameterValue("operator", "and")
        m.process()
        self.assertEqual(np.array_equal(m.getParameterValue("outputVec")[0], np.array([1, 0, 0, 0])), True)

        m.setParameterValue("inputVec1", [np.array([1, 1, 0, 0])])
        m.setParameterValue("inputVec2", [np.array([1, 0, 1, 0])])
        m.setParameterValue("operator", "or")
        m.process()
        self.assertEqual(np.array_equal(m.getParameterValue("outputVec")[0], np.array([1, 1, 1, 0])), True)

        m.setParameterValue("inputVec1", [np.array([1, 1, 0, 0])])
        m.setParameterValue("inputVec2", [np.array([1, 0, 1, 0])])
        m.setParameterValue("operator", "xor")
        m.process()
        self.assertEqual(np.array_equal(m.getParameterValue("outputVec")[0], np.array([0, 1, 1, 0])), True)
        del m
        
        m = MelopyFeatureModuleLogic()
        m.setParameterValue("inputVec1", [np.array([1, 1, 0, 0])])
        m.setParameterValue("operator", "not")
        m.process()
        self.assertEqual(np.array_equal(m.getParameterValue("outputVec")[0], np.array([0, 0, 1, 1])), True)


if __name__ == "__main__":
    unittest.main()
