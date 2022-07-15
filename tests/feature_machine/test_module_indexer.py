#!/usr/bin/env python

""" Unit test for indexer module """

import unittest

import numpy as np

from melospy.feature_machine.feature_module_indexer import MelopyFeatureModuleIndexer


class TestModuleIndexer( unittest.TestCase ):
    """ Unit test for indexer module """
  
    def testIndexerModuleFunctionality(self):
        """ Test basic functionality """
        m = MelopyFeatureModuleIndexer()
        
        m.setParameterValue("inputVec", ['AABCCCD'])
        m.process()
        self.assertEqual(np.array_equal(m.getParameterValue("outputVec")[0], np.array([0, 1, 2, 3, 4, 5, 6])), True)
        
        m.setParameterValue("inputVec", [['A', 'A', 'B', 'C', 'C', 'C', 'D']])
        m.process()
        self.assertEqual(np.array_equal(m.getParameterValue("outputVec")[0], np.array([0, 1, 2, 3, 4, 5, 6])), True)
        
        m.setParameterValue("inputVec", [['AB', 'BC', 'CC']])
        m.process()
        self.assertEqual(np.array_equal(m.getParameterValue("outputVec")[0], np.array([0, 1, 2])), True)
        
        m.setParameterValue("inputVec", [[('A', 1), ('A', 1), ('A', 2), ('B', 3)]])
        m.process()
        self.assertEqual(np.array_equal(m.getParameterValue("outputVec")[0], np.array([0, 1, 2, 3])), True)
        
        m.setParameterValue("inputVec", [[(1.5, 1), (1.5, 1), (1.5, 2), (2, 3)]])
        m.process()
        self.assertEqual(np.array_equal(m.getParameterValue("outputVec")[0], np.array([0, 1, 2, 3])), True)

if __name__ == "__main__":
    unittest.main()
