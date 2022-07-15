#!/usr/bin/env python

""" Unit test for sink module """

import unittest

import numpy as np

from melospy.feature_machine.feature_module_sink import MelopyFeatureModuleSink


class TestModuleSink( unittest.TestCase ):
    """ Unit test for sink module """
  
    def testSinkModuleBasicFunctionality(self):
        """ Test forwarding functionality of sink module """
        m = MelopyFeatureModuleSink()
        m.setParameterValue("input", [np.array([1, 2, 3, 4])])
        m.process()
        self.assertEqual(np.array_equal(m.getParameterValue("outputVec"), np.array([1, 2, 3, 4])), True)
        
    def testSinkModuleIndex(self):
        """ Test indexing functionality of sink module """
        m = MelopyFeatureModuleSink()
        m.setParameterValue("input", [np.array([1, 2, 3, 4])])
        m.setParameterValue("index", 1)
        m.process()


if __name__ == "__main__":
    unittest.main()
