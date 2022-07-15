#!/usr/bin/env python

""" Unit test for markov module """

import unittest

import numpy as np

import melospy.feature_machine.test_help_functions as thf
from melospy.feature_machine.feature_module_markov import MelopyFeatureModuleMarkov


class TestModuleMarkov( unittest.TestCase ):
    """ Unit test for markov module """
  
    def testFunctionality(self):
        """ Test functionality of markov module """
        m = MelopyFeatureModuleMarkov()
        m.setParameterValue("inputVec", [np.array([1, 1, 4, 4, 5, 5])])
        m.setParameterValue("bins", [np.array([1, 4, 5])])
        m.process()
        self.assertEqual(np.array_equal(m.getParameterValue("transitionMatrix")[0], np.array([[0.5, 0.5, 0], [0, 0.5, 0.5], [0, 0, 1]])), True)
        
if __name__ == "__main__":
    unittest.main()
