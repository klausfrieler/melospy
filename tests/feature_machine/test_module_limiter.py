#!/usr/bin/env python

""" Unit test for threshold module """

import unittest

import numpy as np
import pytest

from melospy.feature_machine.feature_module_limiter import MelopyFeatureModuleLimiter


class TestModuleLimit( unittest.TestCase ):
    """ Unit test for threshold module """

    #@pytest.mark.skip(reason="Assertion mismatch")
    def testModuleFunctionality(self):
        """ tests module functionality """
        m = MelopyFeatureModuleLimiter()
        m.setParameterValue("inputVec", [np.array([1, 2, 3])])

        m.setParameterValue("min", 2)
        m.setParameterValue("max", 2)

        m.process()
        self.assertEqual(np.array_equal(m.getParameterValue("outputVec")[0], np.array([2., 2., 2.])), True)

        m.setParameterValue("inputVec", [np.array([1, 2, 3])])
        m.setParameterValue("min", 2)
        m.setParameterValue("max", None)

        m.process()
        self.assertEqual(np.array_equal(m.getParameterValue("outputVec")[0], np.array([2., 2., 3.])), True)

        m.setParameterValue("inputVec", [np.array([1, 2, 3])])
        m.setParameterValue("min", None)
        m.setParameterValue("max", 2)

        m.process()
        self.assertEqual(np.array_equal(m.getParameterValue("outputVec")[0], np.array([1., 2., 2.])), True)

        m.setParameterValue("inputVec", [np.array([1, 2, 3])])
        m.setParameterValue("min", None)
        m.setParameterValue("max", None)

        m.process()
        self.assertEqual(np.array_equal(m.getParameterValue("outputVec")[0], np.array([1., 2., 3.])), True)


if __name__ == "__main__":
    unittest.main()
