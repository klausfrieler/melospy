#!/usr/bin/env python
import sys
import unittest

import numpy as np
import pytest

from melospy.feature_machine.feature_module_self_similarity import MelopyFeatureModuleSelfSimilarity


def is_equal(v1, v2):
    return np.sum(np.abs(v1-v2)) < 1E-3

class TestModuleSelfSimilarity( unittest.TestCase ):
    """ Unit test for Self Similarity module class """

    def testFunctionality(self):
        """ Check class functionality """
        s = MelopyFeatureModuleSelfSimilarity()
        inputVec = np.array([1, 2, 3, 4, 1, 2, 3, 5, 1, 2, 5, 6, 1, 7, 8, 9])
        groupVec = np.array([0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3])
        s.setParameterValue("inputVec", [inputVec])
        s.setParameterValue("groupingVec", [groupVec])
        s.process()
        ssm = s.getParameterValue("selfSimilarityMatrix")
        refSSM = np.array([[1., 0.75, 0.5, 0.25], [0.75, 1., 0.5, 0.25], [0.5, 0.5, 1., 0.25], [0.25, 0.25, 0.25, 1.]])
        self.assertEqual(is_equal(ssm, refSSM), True)




if __name__ == "__main__":
    unittest.main()
