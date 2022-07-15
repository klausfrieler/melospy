#!/usr/bin/env python

""" Unit test for pattern module """
import sys
import unittest

import numpy as np
import pytest

from melospy.feature_machine.feature_module_pattern import MelopyFeatureModulePattern


class TestModulePattern( unittest.TestCase ):
    """ Unit test for pattern module """

    def testPattermModuleFunctionality(self):
        """ Test computation of mean pattern length & mean pattern distance """
        m = MelopyFeatureModulePattern()
        m.setParameterValue("inputVec", [np.array([1, 1, 1, 3, 3, 4, 1, 1, 1, 5, 5, 3, 3, 4])])
        m.setParameterValue("method", "similarityMatrix")
        m.setParameterValue("minPatternLength", 3)
        m.process()
        self.assertEqual(m.getParameterValue("meanPatternLength")[0], 3)
        self.assertEqual(m.getParameterValue("meanPatternDistance")[0], 6)

    def testPatternExtractionForThreeAppearances(self):
        """ Checks if a pattern with three exact repetitions is found correctly """
        m = MelopyFeatureModulePattern()         # 0,1,2,3,4,5,6,7,8,9,0,1,2,3,4,5,6, 7,8,9,0,1,2,3
        m.setParameterValue("inputVec", [np.array([1, 1, 2, 2, 3, 3, 5, 3, 8, 1, 1, 2, 2, 3, 3, 4, 66, 3, 1, 1, 2, 2, 3, 3])])
        m.setParameterValue("method", "similarityMatrix")
        m.setParameterValue("minPatternLength", 3)
        m.process()
        p = m.getParameterValue("patterns")[0]
        self.assertEqual(len(p), 1)
        self.assertEqual(np.array_equal(p[0].patternStarts, np.array([0, 9, 18])), True)
        self.assertEqual(np.array_equal(p[0].patternLengths, np.array([6, 6, 6])), True)

    #@pytest.mark.skip(reason="Index mismatch")
    def testPatternExtractionForNonNumericInputVector(self):
        """ Tests pattern extraction for non-numeric input data """
        m = MelopyFeatureModulePattern()         # 0,1,2,3,4,5,6,7,8,9,0,1,2,3,4,5,6, 7,8,9,0,1,2,3
        iv = [(1, 1), (1, 1), (1, 2), (3, 4), (1, 1), (1, 1), (1, 2)]
        m.setParameterValue("inputVec", [iv])
        m.setParameterValue("method", "similarityMatrix")
        m.setParameterValue("minPatternLength", 3)
        m.process()
        p = m.getParameterValue("patterns")[0]
        self.assertEqual(len(p), 1)
        self.assertEqual(np.array_equal(p[0].patternStarts, np.array([0, 4])), True)
        self.assertEqual(np.array_equal(p[0].patternLengths, np.array([3, 3])), True)

        iv = [[1, 1], [1, 1], [1, 2], [3, 4], [1, 1], [1, 1], [1, 2]]
        m.setParameterValue("inputVec", [iv])
        m.setParameterValue("method", "similarityMatrix")
        m.setParameterValue("minPatternLength", 3)
        m.process()
        p = m.getParameterValue("patterns")[0]
        self.assertEqual(len(p), 1)
        self.assertEqual(np.array_equal(p[0].patternStarts, np.array([0, 4])), True)
        self.assertEqual(np.array_equal(p[0].patternLengths, np.array([3, 3])), True)

        iv = ([1, 1], [1, 1], [1, 2], [3, 4], [1, 1], [1, 1], [1, 2])
        m.setParameterValue("inputVec", [iv])
        m.setParameterValue("method", "similarityMatrix")
        m.setParameterValue("minPatternLength", 3)
        m.process()
        p = m.getParameterValue("patterns")[0]
        self.assertEqual(len(p), 1)
        self.assertEqual(np.array_equal(p[0].patternStarts, np.array([0, 4])), True)
        self.assertEqual(np.array_equal(p[0].patternLengths, np.array([3, 3])), True)


if __name__ == "__main__":
    unittest.main()
