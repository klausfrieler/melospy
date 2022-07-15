#!/usr/bin/env python

import unittest

import numpy as np

from melospy.feature_machine.feature_module_arithmetic import MelopyFeatureModuleArithmetic
from melospy.feature_machine.test_help_functions import my_array_equal


class TestModuleArithmetic( unittest.TestCase ):
    """ Unit test for arithmetic module """
 
    def testArithmeticModuleFunctionalityAddition(self):
        """ Test arithmetic module for addition """
        # test vector + vector
        m = MelopyFeatureModuleArithmetic()
        m.setParameterValue("inputVec1", [np.array([1, 2, 3])])
        m.setParameterValue("inputVec2", [np.array([1, 2, 3])])
        m.setParameterValue("operator", "+")
        m.process()
        self.assertEqual(np.array_equal(m.getParameterValue("outputVec")[0], np.array([2, 4, 6])), True)
         
        # test vector + scalar
        m.setParameterValue("inputVec1", [np.array([1, 2, 3])])
        m.setParameterValue("inputVec2", [np.array([1.1])])
        m.setParameterValue("operator", "+")
        m.process()
        self.assertEqual(np.array_equal(m.getParameterValue("outputVec")[0], np.array([2.1, 3.1, 4.1])), True)
         
        # test scalar + scalar
        m.setParameterValue("inputVec1", [np.array([1])])
        m.setParameterValue("inputVec2", [np.array([1.1])])
        m.setParameterValue("operator", "+")
        m.process()
        self.assertEqual(np.array_equal(m.getParameterValue("outputVec")[0], np.array([2.1])), True)
         
    def testArithmeticModuleFunctionalitySubtraction(self):
        """ Test arithmetic module for subtraction """
        # test vector - vector
        m = MelopyFeatureModuleArithmetic()
        m.setParameterValue("inputVec1", [np.array([1, 2, 3])])
        m.setParameterValue("inputVec2", [np.array([1, 2, 3])])
        m.setParameterValue("operator", "-")
        m.process()
        self.assertEqual(my_array_equal(m.getParameterValue("outputVec")[0], np.array([0, 0, 0])), True)
         
        # test vector - scalar
        m.setParameterValue("inputVec1", [np.array([1, 2, 3])])
        m.setParameterValue("inputVec2", [np.array([1.1])])
        m.setParameterValue("operator", "-")
        m.process()
        self.assertEqual(my_array_equal(m.getParameterValue("outputVec")[0], np.array([-.1, .9, 1.9])), True)
         
        # test scalar - scalar
        m.setParameterValue("inputVec1", [np.array([1])])
        m.setParameterValue("inputVec2", [np.array([1.1])])
        m.setParameterValue("operator", "-")
        m.process()
        self.assertEqual(my_array_equal(m.getParameterValue("outputVec")[0], np.array([-.1])), True)
         
    def testArithmeticModuleFunctionalityMultiplication(self):
        """ Test arithmetic module for multiplication """
        # test vector * vector
        m = MelopyFeatureModuleArithmetic()
        m.setParameterValue("inputVec1", [np.array([1, 2, 3])])
        m.setParameterValue("inputVec2", [np.array([1, 2, 3])])
        m.setParameterValue("operator", "*")
        m.process()
        self.assertEqual(my_array_equal(m.getParameterValue("outputVec")[0], np.array([1, 4, 9])), True)
         
        # test vector * scalar
        m.setParameterValue("inputVec1", [np.array([1, 2, 3])])
        m.setParameterValue("inputVec2", [np.array([4])])
        m.setParameterValue("operator", "*")
        m.process()
        self.assertEqual(my_array_equal(m.getParameterValue("outputVec")[0], np.array([4, 8, 12])), True)
         
        # test scalar * scalar
        m.setParameterValue("inputVec1", [np.array([2])])
        m.setParameterValue("inputVec2", [np.array([1.1])])
        m.setParameterValue("operator", "*")
        m.process()
        self.assertEqual(my_array_equal(m.getParameterValue("outputVec")[0], np.array([2.2])), True)
         
    def testArithmeticModuleFunctionalityDivision(self):
        """ Test arithmetic module for division """
        # test vector / vector
        m = MelopyFeatureModuleArithmetic()
        m.setParameterValue("inputVec1", [np.array([1, 2, 3])])
        m.setParameterValue("inputVec2", [np.array([1, 2, 3])])
        m.setParameterValue("operator", "/")
        m.process()
        self.assertEqual(my_array_equal(m.getParameterValue("outputVec")[0], np.array([1, 1, 1])), True)
         
        # test vector / scalar
        m.setParameterValue("inputVec1", [np.array([1, 2, 3])])
        m.setParameterValue("inputVec2", [np.array([2])])
        m.setParameterValue("operator", "/")
        m.process()
        self.assertEqual(my_array_equal(m.getParameterValue("outputVec")[0], np.array([.5, 1, 1.5])), True)
         
        # test scalar / scalar
        m.setParameterValue("inputVec1", [2])
        m.setParameterValue("inputVec2", [4])
        m.setParameterValue("operator", "/")
        m.process()
        self.assertEqual(m.getParameterValue("outputVec")[0], .5)
         
        # test scalar / scalar with NaN avoidance
        m.setParameterValue("inputVec1", [2])
        m.setParameterValue("inputVec2", [0])
        m.setParameterValue("operator", "/")
        m.setParameterValue("divisionByZeroResultsInZero", True)
        m.process()
        self.assertEqual(m.getParameterValue("outputVec")[0], 0)
         
    def testArithmeticModuleFunctionalityLog(self):
        """ Test arithmetic module for log """
        m = MelopyFeatureModuleArithmetic()
        m.setParameterValue("inputVec1", [np.array([np.e, np.e**2])])
        m.setParameterValue("operator", "log")
        m.process()
        self.assertEqual(my_array_equal(m.getParameterValue("outputVec")[0], np.array([1, 2])), True)
 
if __name__ == "__main__":
    unittest.main()
