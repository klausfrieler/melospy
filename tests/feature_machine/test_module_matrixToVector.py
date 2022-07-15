#!/usr/bin/env python

import unittest

import numpy as np

from melospy.feature_machine.feature_module_matrixToVector import MelopyFeatureModuleMatrixToVector


def is_equal(v1, v2):
    return np.sum(np.abs(v1-v2)) < 1E-3

class TestModuleMatrixToVector( unittest.TestCase ):
    """ Unit test for matrixToVector module """
  
    def testAbsModuleFunctionality(self):
        """ Test matrixToVector module """
        m = MelopyFeatureModuleMatrixToVector()
        
        # mode = "diag"
        m.setParameterValue("inputVec", [np.array([[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, 16]])])
        m.setParameterValue("mode", "diag")
        m.setParameterValue("diagOffset", 0)
        m.process()
        self.assertEqual(is_equal(m.getParameterValue("outputVec")[0], np.array([1, 6, 11, 16])), True)
                         
        m.setParameterValue("inputVec", [np.array([[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, 16]])])
        m.setParameterValue("mode", "diag")
        m.setParameterValue("diagOffset", 1)
        m.process()
        self.assertEqual(is_equal(m.getParameterValue("outputVec")[0], np.array([2, 7, 12])), True)
                         
        m.setParameterValue("inputVec", [np.array([[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, 16]])])
        m.setParameterValue("mode", "diag")
        m.setParameterValue("diagOffset", -1)
        m.process()
        self.assertEqual(is_equal(m.getParameterValue("outputVec")[0], np.array([5, 10, 15])), True)
                         
        # mode = "upperTriangular"
        m.setParameterValue("inputVec", [np.array([[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, 16]])])
        m.setParameterValue("mode", "upperTriangular")
        m.setParameterValue("diagOffset", 0)
        m.process()
        self.assertEqual(is_equal(m.getParameterValue("outputVec")[0], np.array([1, 2, 3, 4, 6, 7, 8, 11, 12, 16])), True)

        m.setParameterValue("inputVec", [np.array([[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, 16]])])
        m.setParameterValue("mode", "upperTriangular")
        m.setParameterValue("diagOffset", 1)
        m.process()
        self.assertEqual(is_equal(m.getParameterValue("outputVec")[0], np.array([2, 3, 4, 7, 8, 12])), True)
                         
        # mode = "lowerTriangular"
        m.setParameterValue("inputVec", [np.array([[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, 16]])])
        m.setParameterValue("mode", "lowerTriangular")
        m.setParameterValue("diagOffset", 0)
        m.process()
        self.assertEqual(is_equal(m.getParameterValue("outputVec")[0], np.array([1, 5, 6, 9, 10, 11, 13, 14, 15, 16])), True)

        m.setParameterValue("inputVec", [np.array([[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, 16]])])
        m.setParameterValue("mode", "lowerTriangular")
        m.setParameterValue("diagOffset", -1)
        m.process()
        self.assertEqual(is_equal(m.getParameterValue("outputVec")[0], np.array([5, 9, 10, 13, 14, 15])), True)
                         
        # mode = "stackToVector"
        m.setParameterValue("inputVec", [np.array([[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, 16]])])
        m.setParameterValue("mode", "stackToVector")
        m.setParameterValue("stackOrientation", "rows")
        m.process()
        self.assertEqual(is_equal(m.getParameterValue("outputVec")[0], np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16])), True)

        m.setParameterValue("inputVec", [np.array([[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, 16]])])
        m.setParameterValue("mode", "stackToVector")
        m.setParameterValue("stackOrientation", "cols")
        m.process()
        self.assertEqual(is_equal(m.getParameterValue("outputVec")[0], np.array([1, 5, 9, 13, 2, 6, 10, 14, 3, 7, 11, 15, 4, 8, 12, 16])), True)
                         
        

if __name__ == "__main__":
    unittest.main()
