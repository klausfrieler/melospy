#!/usr/bin/env python

""" Unit test for Similarity class """

import unittest

import numpy as np

from melospy.similarity.similarity_edit_distance import SimilarityEditDistance


def is_equal(v1, v2):
    return np.abs(v1-v2) < 1E-3

class TestSimilarityClass( unittest.TestCase ):
    """ Unit test for similarity class """
    
    def testFunctionality(self):
        """ Check class functionality """
        s = SimilarityEditDistance()
        
        self.assertEqual(s.editDistance(np.array([1, 1, 1]), np.array([1, 1, 1])), 0)
        self.assertEqual(s.editDistance(np.array([1, 1, 11]), np.array([1, 1, 1])), 1)
        self.assertEqual(s.editDistance(np.array([1, 1, 1]), np.array([1, 1, 1, 1, 2])), 2)
        self.assertEqual(s.editDistance(np.array([1, 1, 1]), np.array([0, 0, 0])), 3)
        
        self.assertEqual(s.process(np.array([1, 1, 1]), np.array([1, 1, 1])), 1)
        self.assertEqual(s.process(np.array([]), np.array([1, 1, 1])), 0)
        
        
        
        

if __name__ == "__main__":
    unittest.main()
