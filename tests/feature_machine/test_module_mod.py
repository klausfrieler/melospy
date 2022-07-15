#!/usr/bin/env python

""" Unit test for mod module """

import unittest

import numpy as np
import pytest

from melospy.feature_machine.feature_module_mod import MelopyFeatureModuleMod
from melospy.feature_machine.test_help_functions import my_array_equal


class TestModuleMod( unittest.TestCase ):
    """ Unit test for mod module """

    #@pytest.mark.skip(reason="Signature mismatch")
    def testDiffModuleFunctionality(self):
        """ Test mod module """
        m = MelopyFeatureModuleMod()
        m.setParameterValue("inputVec", [np.array([0, 1, 5, 7, 11, 12, 24, -1])])
        m.setParameterValue("N", 12)
        m.process()
        self.assertEqual(np.array_equal(m.getParameterValue("outputVec")[0], np.array([0, 1, 5, 7, 11, 0, 0, 11])), True)
        m.setParameterValue("wrap", False)
        m.process()
        self.assertEqual(np.array_equal(m.getParameterValue("outputVec")[0], np.array([0, 1, 5, 7, 11, 0, 0, -1])), True)
        m.setParameterValue("circDist", True)
        m.process()
        self.assertEqual(my_array_equal(m.getParameterValue("outputVec")[0], np.array([0, 1, 5, 5, 1, 0, 0, 1])), True)


if __name__ == "__main__":
    unittest.main()
