#!/usr/bin/env python

import unittest

import numpy as np

from melospy.feature_machine.feature_module_abs import MelopyFeatureModuleAbs


class TestModuleAbs( unittest.TestCase ):
    """ Unit test for abs module """
  
    def testAbsModuleFunctionality(self):
        """ Test abs module """
        m = MelopyFeatureModuleAbs()
        m.setParameterValue("inputVec", [np.array([26, 1, -1, -23])])
        m.process()
        self.assertEqual(np.array_equal(m.getParameterValue("outputVec")[0], np.array([26, 1, 1, 23])), True)
        

if __name__ == "__main__":
    unittest.main()
