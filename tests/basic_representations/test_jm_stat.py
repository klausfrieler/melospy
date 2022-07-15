#!/usr/bin/env python

""" Unit test for stat module """


import unittest

from melospy.basic_representations.jm_stats import *


class TestModuleStat( unittest.TestCase ):
    """ Unit test for stat module """

    def testStatModuleHelpers(self):
        test = [1, 2, 3]*10000
        vec = np.array([1, 1, 2, 2, 3, 3, 4, 4, 5, 5])
        test.append(3)
        test.append(3)
        test.append(2)
        vec = np.array(test)
        self.assertEqual(simple_histogram(vec), [(1, 10000.0), (2, 10001.0), (3, 10002.0)])
        self.assertEqual(simple_histogram([1, 2, 3, 4], density=True), [(1, 0.25), (2, 0.25), (3, 0.25), (4, .25)])
        self.assertEqual(simple_histogram(vec, order="inc"), [(1, 10000.0), (2, 10001.0), (3, 10002.0)])
        self.assertEqual(simple_histogram(vec, order="dec"), [(3, 10002.0), (2, 10001.0), (1, 10000.0)])
        self.assertEqual(simple_histogram(vec, order="dec", counts_only=True), [10002.0, 10001.0, 10000.0])
        self.assertEqual(simple_histogram([], order="dec", counts_only=True), None)
        self.assertEqual(simple_histogram(None, order="dec", counts_only=True), None)
        self.assertAlmostEqual(entropy([1, 2, 3, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3]), 0.755927929263)
        self.assertEqual(mode([1, 2, 3, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3]), 3.)
        #self.assertEqual(zipf_coefficient([1,2,3, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3]), 1.)
        red_freq = [20, 10,  7,  5,  4,  3,  3,  2,  2,  2]
        red_noise = []
        for i in range(len(red_freq)):
            red_noise.extend([i-5]*red_freq[i])

        self.assertAlmostEqual(zipf_coefficient(red_noise), 1.0471089717544801)
        self.assertAlmostEqual(zipf_coefficient([1, 1, 2, 2, 3, 3, 4, 4, 5, 5]), 0)
        zipf_coefficient([1]*680)
        self.assertEqual(mean([1, 2, 3, 4, 5]), 3.)
        self.assertEqual(var([1, 2, 3, 4, 5]), 2.5)
        self.assertEqual(sd([1, 2, 3, 4, 5]), sqrt(2.5))
        fVec = [1.1, 1.2, 1.3]
        self.assertAlmostEqual(mean_frac(fVec), 0.2, 10)
        fVec = [0.9, 1.0, 1.1]
        self.assertAlmostEqual(mean_frac(fVec), 0.0, 10)
        fVec = [1, 2, 3, 4, 5]
        self.assertAlmostEqual(geometric_mean(fVec), 2.6051710846973521)
        self.assertAlmostEqual(harmonic_mean(fVec), 2.189781)
        fVec = [1, 2, 2, 3, 3, 3, 4, 4, 4, 4, 5, 5, 5, 5, 5]
        self.assertAlmostEqual(flatness(fVec), 0.8683904)
        print(entropy(fVec), zipf_coefficient(fVec), flatness(fVec))
if __name__ == "__main__":
    unittest.main()
