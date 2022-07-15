#!/usr/bin/env python

""" Unit test for hist module """

import unittest

import numpy as np
import pytest

import melospy.feature_machine.test_help_functions as thf
from melospy.feature_machine.feature_module_hist import MelopyFeatureModuleHist


class TestModuleHist( unittest.TestCase ):
    """ Unit test for hist module """

    def testOrdinalHistogramDensityFalseRemoveEmptyBins(self):
        """ Test ordinal histogram for density=false """
        m = MelopyFeatureModuleHist()
        m.setParameterValue("histogramType", "ordinal")
        m.setParameterValue("removeEmptyBins", True)
        m.setParameterValue("inputVec", [np.array([1, 2, 2, 3, 3, 3, 5, 5, 5, 5, 5])])
        m.process()
        self.assertEqual(np.array_equal(m.getParameterValue("bins")[0], np.array([1, 2, 3, 5])), True)
        self.assertEqual(np.array_equal(m.getParameterValue("histVec")[0], np.array([1, 2, 3, 5])), True)

    def testOrdinalHistogramDensityFalseRemoveEmptyBinsFalse(self):
        """ Test ordinal histogram for density=false but with remaining empty bins (here: for the value 4)"""
        m = MelopyFeatureModuleHist()
        m.setParameterValue("histogramType", "ordinal")
        m.setParameterValue("removeEmptyBins", False)
        m.setParameterValue("inputVec", [np.array([1, 2, 2, 3, 3, 3, 5, 5, 5, 5, 5])])
        m.process()
        self.assertEqual(np.array_equal(m.getParameterValue("bins")[0], np.array([1, 2, 3, 4, 5])), True)
        self.assertEqual(np.array_equal(m.getParameterValue("histVec")[0], np.array([1, 2, 3, 0, 5])), True)

    def testOrdinalHistogramDensityTrue(self):
        """ Test ordinal histogram for density=true """
        m = MelopyFeatureModuleHist()
        m.setParameterValue("histogramType", "ordinal")
        m.setParameterValue("density", "true")
        m.setParameterValue("inputVec", [np.array([1, 2, 2, 3, 3, 3, 4, 4, 4, 4, 4])])
        m.process()
        self.assertEqual(np.array_equal(m.getParameterValue("bins")[0], np.array([1, 2, 3, 4])), True)
        self.assertEqual(thf.my_array_equal(m.getParameterValue("histVec")[0], np.array([0.09090909, 0.18181818, 0.27272727, 0.45454545]), 1E-8), True)

    #@pytest.mark.skip(reason="Assertion mismatch")
    def testMetricalHistogramDensityFalse(self):
        """ Test metrical histogram for density=false """
        m = MelopyFeatureModuleHist()
        m.setParameterValue("histogramType", "metrical")
        m.setParameterValue("inputVec", [np.array([1, 2, 2, 3, 3, 3, 4, 4, 4, 4])])
        m.setParameterValue("fixed-bins", np.array([.5, 1.5, 2.5, 3.5, 4.5]))
        m.process()
        self.assertEqual(np.array_equal(m.getParameterValue("histVec")[0], np.array([1, 2, 3, 4])), True)
        self.assertEqual(np.array_equal(m.getParameterValue("bins")[0], np.array([.5, 1.5, 2.5, 3.5, 4.5])), True)

    #@pytest.mark.skip(reason="Assertion mismatch")
    def testMetricalHistogramDensityTrue(self):
        """ Test metrical histogram for density=true """
        m = MelopyFeatureModuleHist()
        m.setParameterValue("histogramType", "metrical")
        m.setParameterValue("inputVec", [np.array([1, 2, 2, 3, 3, 3, 4, 4, 4, 4])])
        m.setParameterValue("fixed-bins", np.array([.5, 1.5, 2.5, 3.5, 4.5]))
        m.setParameterValue("density", True)
        m.process()
        self.assertEqual(np.array_equal(m.getParameterValue("histVec")[0], np.array([.1, .2, .3, .4])), True)
        self.assertEqual(np.array_equal(m.getParameterValue("bins")[0], np.array([.5, 1.5, 2.5, 3.5, 4.5])), True)

    def testNominalHistogram1(self):
        """ Test nominal histogram for different data types """
        m = MelopyFeatureModuleHist()
        m.setParameterValue("histogramType", "nominal")
        m.setParameterValue("inputVec", ['AABCCCD'])
        m.process()
        self.assertEqual(np.array_equal(m.getParameterValue("histVec")[0], np.array([3, 2, 1, 1])), True)
        self.assertEqual(all(m.getParameterValue("bins")[0]==['C', 'A', 'B', 'D']), True)

    def testNominalHistogram2(self):
        """ Test nominal histogram for different data types """
        m = MelopyFeatureModuleHist()
        m.setParameterValue("histogramType", "nominal")
        m.setParameterValue("inputVec", [['AB', 'BC', 'CC', 'CC', 'AB', 'AB']])
        m.process()
        self.assertEqual(all(m.getParameterValue("histVec")[0]==[3, 2, 1]), True)
        self.assertEqual(all(m.getParameterValue("bins")[0]==['AB', 'CC', 'BC']), True)

    def testNominalHistogram3(self):
        """ Test nominal histogram for different data types """
        m = MelopyFeatureModuleHist()
        m.setParameterValue("histogramType", "nominal")
        m.setParameterValue("inputVec", [[[-1, 1], [-1, 1], [1, 2], [1, 3]]])
        m.process()
        self.assertEqual(all(m.getParameterValue("histVec")[0]==[2, 1, 1]), True)
        a = m.getParameterValue("bins")[0]==[[-1, 1], [1, 2], [1, 3]]
        self.assertEqual(a.all(), True)

    def testNominalHistogram4(self):
        """ Test nominal histogram for different data types """
        m = MelopyFeatureModuleHist()
        m.setParameterValue("histogramType", "nominal")
        m.setParameterValue("inputVec", [[(1.5, 1), (1.5, 1), (1.5, 2), (2, 3)]])
        m.process()
        self.assertEqual(all(m.getParameterValue("histVec")[0]==[2, 1, 1]), True)
        a = m.getParameterValue("bins")[0]==[(1.5, 1), (1.5, 2), (2, 3)]
        self.assertEqual(a.all(), True)


if __name__ == "__main__":
    unittest.main()
