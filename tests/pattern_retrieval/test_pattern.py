#!/usr/bin/env python

""" Unit test for Pattern class """

import unittest

import numpy as np

from melospy.pattern_retrieval.pattern import Pattern
from melospy.pattern_retrieval.pattern_retrieval_via_similarity_matrix import \
    PatternRetrievalViaSimilarityMatrix


class TestPatternClass( unittest.TestCase ):
    """ Unit test for pattern class """
    
    def testGetMeanPatternLength(self):
        """ Test functionality """
        p = Pattern(np.array([5, 10, 15]), np.array([4, 4, 3]))
        self.assertAlmostEqual(p.getMeanPatternLength(), 3 + 2./3)

    def testGetMeanPatternDistance(self):
        """ Test functionality """
        p = Pattern(np.array([5, 10, 14]), np.array([4, 4, 3]))
        self.assertAlmostEqual(p.getMeanPatternDistance(), 4.5)
        
    def testCheckPatternClassForNonNumericInputVector(self):
        """ Check method "convert_vector_to_codebook_indices()" that converts arbitrary input vectors to numeric vectors
            that can be used as input for the pattern retrieval algorithm """
        p = PatternRetrievalViaSimilarityMatrix()
        # case 1) input vector is list of tuples
        iv = [(1, 1), (1, 1), (1, 2), (3, 4), (1, 1), (1, 1), (1, 2)]
        inputVecNumeric, codebook = p.convert_vector_to_codebook_indices(iv)
        self.assertEqual(inputVecNumeric == [0, 0, 1, 2, 0, 0, 1], True)
        self.assertEqual(codebook == [(1, 1), (1, 2), (3, 4)], True)
        #p.process(inputVecNumeric)
        # case 2) input vector is numpy array
        iv = np.array([1, 1, 2, 3, 3, 5])
        inputVecNumeric, codebook = p.convert_vector_to_codebook_indices(iv)
        self.assertAlmostEqual(all(inputVecNumeric-iv), 0)
        self.assertEqual(codebook == [1, 2, 3, 5], True)
        
        # case 3) input vector is list of characters (TODO; implement this!!!)


if __name__ == "__main__":
    unittest.main()
