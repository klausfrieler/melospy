#!/usr/bin/env python

""" Unit test for stat module """

import unittest

import numpy as np

from melospy.feature_machine.feature_module_stat import *
from melospy.feature_machine.test_help_functions import my_array_equal


class TestModuleStat( unittest.TestCase ):
    """ Unit test for stat module """

    def testStatModuleMean(self):
        """ tests mean measure """
        m = MelopyFeatureModuleStat()
        m.setParameterValue("inputVec", [np.array([1, 1, 2, 5, 7])])
        m.setParameterValue("measure", "mean")
        m.process()
        self.assertEqual(my_array_equal(m.getParameterValue("outputVec")[0], np.array([3.2])), True)

    def testStatModuleMedian(self):
        """ tests median measure """
        m = MelopyFeatureModuleStat()
        m.setParameterValue("inputVec", [np.array([1, 1, 2, 5, 7])])
        m.setParameterValue("measure", "median")
        m.process()
        self.assertEqual(my_array_equal(m.getParameterValue("outputVec")[0], np.array([2.0])), True)
        m.setParameterValue("inputVec", [np.array([1, 1, 2, 5])])
        m.process()
        self.assertEqual(my_array_equal(m.getParameterValue("outputVec")[0], np.array([1.5])), True)

    def testStatModuleMode(self):
        """ tests mode """
        m = MelopyFeatureModuleStat()
        m.setParameterValue("inputVec", [np.array([1, 2, 2, 2, 3, 3, 3, 5, 7])])
        m.setParameterValue("measure", "mode")
        m.process()
        self.assertEqual(my_array_equal(m.getParameterValue("outputVec"), np.array([2., 3.])), True)
        m.setParameterValue("inputVec", [np.array([1, 2, 2, 2, 2, 3, 3, 3, 5, 7])])
        m.process()
        self.assertEqual(m.getParameterValue("outputVec")[0], 2)
        m.setParameterValue("inputVec", [np.array([])])
        m.process()
        self.assertEqual(m.getParameterValue("outputVec")[0], None)

    def testStatModuleVar(self):
        """ tests mean measure """
        m = MelopyFeatureModuleStat()
        m.setParameterValue("inputVec", [np.array([1, 1, 2, 5, 7])])
        m.setParameterValue("measure", "var")
        m.process()
        # numpy uses 1/(n-1) * sum( (xi- mean(x))**2 ) !!!
        # matlab uses 1/n * sum( (xi- mean(x))**2 ) !!!
        self.assertEqual(my_array_equal(m.getParameterValue("outputVec")[0], np.array([5.76])), True)

    def testStatModuleStd(self):
        """ tests standard deviation """
        m = MelopyFeatureModuleStat()
        m.setParameterValue("inputVec", [np.array([1, 1, 2, 5, 7])])
        m.setParameterValue("measure", "std")
        m.process()
        self.assertEqual(my_array_equal(m.getParameterValue("outputVec")[0], np.array([2.4])), True)

    def testStatModuleEntropyHist(self):
        """ tests entropy measure for histograms"""
        m = MelopyFeatureModuleStat()
        m.setParameterValue("measure", "entropy_hist")
        m.setParameterValue("inputVec", [np.array([2, 2, 1])])
        m.setParameterValue("normalizeToDensity", True)
        m.process()
        self.assertEqual(my_array_equal(m.getParameterValue("outputVec")[0], np.array([1.52192809489])), True)
                
        m.setParameterValue("inputVec", [np.array([.4, .4, .2])])
        m.setParameterValue("normalizeToDensity", False)
        m.process()
        self.assertEqual(my_array_equal(m.getParameterValue("outputVec")[0], np.array([1.52192809489])), True)

        m.setParameterValue("inputVec", [np.array([.4, .4, .2])])
        m.setParameterValue("normalizeToDensity", False)
        m.setParameterValue("normalizeEntropy", True)
        m.process()
        self.assertEqual(my_array_equal(m.getParameterValue("outputVec")[0], np.array([0.960229717861])), True)

    def testStatModuleEntropy(self):
        """ tests entropy measure for raw data"""
        m = MelopyFeatureModuleStat()
        m.setParameterValue("measure", "entropy")
        m.setParameterValue("inputVec", [np.array([1, 2, 3, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3])])
        m.process()
        self.assertAlmostEqual(m.getParameterValue("outputVec")[0], 1.1981174211304033)
        m.setParameterValue("normalizeEntropy", True)
        m.process()
        self.assertAlmostEqual(m.getParameterValue("outputVec")[0], 0.75592792926347541)
        m.setParameterValue("numberClasses", 4)
        m.process()
        self.assertAlmostEqual(m.getParameterValue("outputVec")[0], 0.59905871056520166)
        m.setParameterValue("inputVec", [np.array([1])])
        m.process()
        self.assertAlmostEqual(m.getParameterValue("outputVec")[0], 0.)
        m.setParameterValue("inputVec", [np.array([])])
        m.process()
        self.assertEqual(m.getParameterValue("outputVec")[0], None)
        
    def testStatModuleZipf(self):
        """ Test zipf-coefficient function in stat module """
        m = MelopyFeatureModuleStat()
        m.setParameterValue("inputVec", [np.array([1, 1, 2, 2, 3, 3])])
        m.setParameterValue("measure", "zipf_coefficient")
        m.process()
        self.assertAlmostEqual(m.getParameterValue("outputVec")[0], 0.0)

        m.setParameterValue("inputVec", [np.array([])])
        m.process()
        self.assertEqual(m.getParameterValue("outputVec")[0], None)

        m.setParameterValue("inputVec", [np.array([1]*680)])
        m.process()
        self.assertEqual(m.getParameterValue("outputVec")[0], None)

    def testStatModuleFlatness(self):
        """ Test flatness function in stat module """
        m = MelopyFeatureModuleStat()
        m.setParameterValue("inputVec", [np.array([1, 1, 2, 2, 3, 3])])
        m.setParameterValue("measure", "flatness")
        m.process()
        self.assertEqual(m.getParameterValue("outputVec")[0], 1.0)

        m.setParameterValue("inputVec", [np.array([])])
        m.process()
        self.assertEqual(m.getParameterValue("outputVec")[0], None)

        m.setParameterValue("inputVec", [np.array([1]*680)])
        m.process()
        self.assertEqual(m.getParameterValue("outputVec")[0], 1)

    def testStatModuleMin(self):
        """ Test min function in stat module """
        m = MelopyFeatureModuleStat()
        m.setParameterValue("inputVec", [np.array([26, 1, -1, 7.5])])
        m.setParameterValue("measure", "min")
        m.process()
        self.assertEqual(np.array_equal(m.getParameterValue("outputVec")[0], -1), True)
        
    def testStatModuleMax(self):
        """ Test max function in stat module """
        m = MelopyFeatureModuleStat()
        m.setParameterValue("inputVec", [np.array([26, 1, -1, 7.5])])
        m.setParameterValue("measure", "max")
        m.process()
        self.assertEqual(np.array_equal(m.getParameterValue("outputVec")[0], 26), True)
        
    def testStatModuleRange(self):
        """ Test range function in stat module """
        m = MelopyFeatureModuleStat()
        m.setParameterValue("inputVec", [np.array([26, 1, -1, 7.5])])
        m.setParameterValue("measure", "range")
        m.process()
        self.assertEqual(np.array_equal(m.getParameterValue("outputVec")[0], 27), True)
        
    def testStatModuleCircStats(self):
        """ Test range function in stat module """
        m = MelopyFeatureModuleStat()
        m.setParameterValue("circ_max", 12)
        m.setParameterValue("inputVec", [np.array([0, 3, 6, 9])])
        m.setParameterValue("measure", "circ_mean_angle")
        m.process()
        res = m.getParameterValue("outputVec")[0]
        self.assertEqual(res, None)
        m.setParameterValue("measure", "circ_mean_length")
        m.process()
        res = m.getParameterValue("outputVec")[0]
        self.assertAlmostEqual(res, 0.)
        m.setParameterValue("measure", "circ_var")
        m.process()
        res = m.getParameterValue("outputVec")[0]
        self.assertAlmostEqual(res, 1.)

        m.setParameterValue("measure", "circ_std")
        m.process()
        res = m.getParameterValue("outputVec")[0]
        self.assertEqual(res, None)

        m.setParameterValue("measure", "circ_disp")
        m.process()
        res = m.getParameterValue("outputVec")[0]
        self.assertEqual(res, None)

        m.setParameterValue("inputVec", [np.array([0, 3, 6])])
        m.setParameterValue("measure", "circ_mean_angle")
        m.process()
        res = m.getParameterValue("outputVec")[0]
        self.assertEqual(res, 3.0)
        m.setParameterValue("measure", "circ_mean_length")
        m.process()
        res = m.getParameterValue("outputVec")[0]
        self.assertAlmostEqual(res, 1.0/3.0)
        m.setParameterValue("measure", "circ_var")
        m.process()
        res = m.getParameterValue("outputVec")[0]
        self.assertAlmostEqual(res, 2./3.0)

        m.setParameterValue("measure", "circ_std")
        m.process()
        res = m.getParameterValue("outputVec")[0]
        self.assertAlmostEqual(res, 1.4823038073675108)

        m.setParameterValue("measure", "circ_disp")
        m.process()
        res = m.getParameterValue("outputVec")[0]
        self.assertAlmostEqual(res, 4.)
if __name__ == "__main__":
    unittest.main()
