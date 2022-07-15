#!/usr/bin/env python

""" Unit test for sign module """

import unittest

import numpy as np

from melospy.feature_machine.feature_module_sign import MelopyFeatureModuleSign


class TestModuleSign( unittest.TestCase ):
    """ Unit test for sign module """
  
    def testSignModuleFunctionality(self):
        """ Test sign module """
        m = MelopyFeatureModuleSign()
        m.setParameterValue("inputVec", [np.array([26, 0, -1, -23])])
        m.process()
        self.assertEqual(np.array_equal(m.getParameterValue("outputVec")[0], np.array([1, 0, -1, -1])), True)
        

if __name__ == "__main__":
    unittest.main()
