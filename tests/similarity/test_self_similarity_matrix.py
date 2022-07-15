#!/usr/bin/env python

import unittest

import numpy as np

from melospy.similarity.self_similarity_matrix import SelfSimilarityMatrix


def is_equal(v1, v2):
    return np.sum(np.abs(v1-v2)) < 1E-3

class TestSelfSimilarityMatrixClass( unittest.TestCase ):
    """ Unit test for Self Similarity Matrix class """
    
    def testFunctionality(self):
        """ Check class functionality """
        s = SelfSimilarityMatrix()
        inputVec = np.array([1, 2, 3, 4, 1, 2, 3, 5, 1, 2, 5, 6, 1, 7, 8, 9])
        groupVec = np.array([0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3])
        ssm = s.process(inputVec, groupVec, 'editDistance')
        
        refSSM = np.array([[1., 0.75, 0.5, 0.25], [0.75, 1., 0.5, 0.25], [0.5, 0.5, 1., 0.25], [0.25, 0.25, 0.25, 1.]])
        self.assertEqual(is_equal(ssm, refSSM), True)
        
        
        

if __name__ == "__main__":
    unittest.main()
