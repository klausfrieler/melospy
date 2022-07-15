#!/usr/bin/env python

""" Unit test for cartProd module """

import unittest

import numpy as np

from melospy.feature_machine.feature_module_cartProd import MelopyFeatureModuleCartProd


class TestModuleCartProd( unittest.TestCase ):
    """ Unit test for cartProd module """
  
    def testCartProdModuleFunctionality(self):
        """ Test module functionality """
        m = MelopyFeatureModuleCartProd()
        m.setParameterValue("inputVec1", [np.array([1, 2, 3, 4, 5, 6])])
        m.setParameterValue("inputVec2", [np.array([11, 22, 33, 44, 55])])
        m.setParameterValue("inputVec3", [np.array([111, 222, 333, 444])])
        
        # front padding
        m.setParameterValue("paddingMode", "front")
        m.process()
        self.assertEqual(m.getParameterValue("outputVec")[0], ([1, 0, 0], [2, 11, 0], [3, 22, 111], [4, 33, 222], [5, 44, 333], [6, 55, 444]))
        
        # back padding
        m.setParameterValue("paddingMode", "back")
        m.process()
        self.assertEqual(m.getParameterValue("outputVec")[0], ([1, 11, 111], [2, 22, 222], [3, 33, 333], [4, 44, 444], [5, 55, 0], [6, 0, 0]))
        


if __name__ == "__main__":
    unittest.main()
