#!/usr/bin/env python

""" Unit test for ngram module """

import unittest

import numpy as np
import pytest

from melospy.feature_machine.feature_module_ngram import MelopyFeatureModuleNGram
from melospy.feature_machine.test_help_functions import my_array_equal


class TestModuleNGram( unittest.TestCase ):
    """ Unit test for ngram module """

    def testNGramModuleFunctionality(self):
        """ Test ngram module """
        m = MelopyFeatureModuleNGram()
        m.setParameterValue("N", 2)
        m.setParameterValue("inputVec", [[1, 2, 3, 4, 5]])
        m.process()
        self.assertEqual(m.getParameterValue("outputVec")[0], [[1, 2], [2, 3], [3, 4], [4, 5]])

        m.setParameterValue("inputVec", [np.array([1, 2, 3, 4])])
        m.setParameterValue("N", 3)
        m.process()
        output = m.getParameterValue("outputVec")[0]
        self.assertEqual(my_array_equal(output[0], np.array([1, 2, 3])) and my_array_equal(output[1], np.array([2, 3, 4])), True)

        m.setParameterValue("inputVec", ['AABCCD'])
        m.setParameterValue("N", 4)
        m.process()
        self.assertEqual(m.getParameterValue("outputVec")[0], ['AABC', 'ABCC', 'BCCD'])

    #@pytest.mark.skip(reason="Assertion mismatch")
    #Obsolete, we return empy lists now
    #def testNGramModuleErrorForEmptyList(self):
    #    """ Tests if module raises error if inputVec is empty """
    #    m = MelopyFeatureModuleNGram()
    #    m.setParameterValue("N", 2)
    #    m.setParameterValue("inputVec", [''])
    #    self.assertRaises(ValueError,m.process)

    #    m.setParameterValue("inputVec", [[]])
    #    self.assertRaises(ValueError,m.process)

    #    m.setParameterValue("inputVec", [np.array([])])
    #    self.assertRaises(ValueError,m.process)

    #@pytest.mark.skip(reason="Assertion mismatch")
    #def testNGramModuleErrorForTooHighNValues(self):
    #    """ Tests if module raises error if N is larger than inputVec length """
    #    m = MelopyFeatureModuleNGram()
    #    m.setParameterValue("N", 4)
    #    m.setParameterValue("inputVec", [[1,2,3]])
    #    self.assertRaises(ValueError,m.process)

    #    m = MelopyFeatureModuleNGram()
    #    m.setParameterValue("N", 7)
    #    m.setParameterValue("inputVec", ['ABCDDE'])
    #    self.assertRaises(ValueError,m.process)

    #    m = MelopyFeatureModuleNGram()
    #    m.setParameterValue("N", 8)
    #    m.setParameterValue("inputVec", [np.array([30,30,21,30,25,25,26])])
    #    self.assertRaises(ValueError,m.process)



if __name__ == "__main__":
    unittest.main()
