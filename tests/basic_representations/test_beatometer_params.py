#!/usr/bin/env python

""" Unit test for class ConfigParameter"""

import unittest

from melospy.basic_representations.beatometer_param import *


class TestBeatometerParameter( unittest.TestCase ):

    def testConstructors(self):
        self.assertEqual(def_sigma.sigma, 0.03)
        setDefaultSigma(0.04)
        self.assertEqual(def_sigma.sigma, 0.04)

        wr = WeightRules()
        self.assertEqual(wr.params["a_maj"], 3)
        self.assertEqual(wr.params["a_min"], 2)
        self.assertEqual(wr.params["baseAccent"], 1)
        self.assertEqual(wr.method, "gauss-standard")
        self.assertEqual(wr.a_maj, 3)
        self.assertEqual(wr.a_min, 2)
        self.assertEqual(wr.baseAccent, 1)

        self.assertRaises(Exception, WeightRules.__init__, "crap")

        gb = GaussBeatParameters()
        self.assertEqual(gb.sigma, def_sigma.sigma)
        self.assertEqual(gb.deltaT, 0.01)
        self.assertEqual(gb.beta, 2.)
        self.assertEqual(gb.spontaneous_tempo, .5)
        self.assertEqual(gb.subjective_presence, 2.0)
        self.assertDictEqual(gb.weight_rules.__dict__, wr.__dict__)
        self.assertEqual(gb.min_ioi, 2.0*def_sigma.sigma)
        self.assertEqual(gb.domain, "folk")
        self.assertEqual(gb.min_tempo, 1.)
        self.assertEqual(gb.max_grad_cut, .2)

        self.assertRaises(Exception, gb.__init__, "crap")

        bmp = BeatometerParameters()
        self.assertEqual(bmp.method, "gaussification")
        self.assertEqual(bmp.window_size, 6.)
        self.assertEqual(bmp.hop_size, 1.)
        self.assertEqual(bmp.glue_sigma, .1)
        self.assertEqual(bmp.glue_threshold, 1.8)
        self.assertEqual(bmp.single_meter, False)
        self.assertEqual(bmp.propagate, True)
        self.assertEqual(list(bmp.params.__dict__.keys()), list(gb.__dict__.keys()))

        self.assertRaises(Exception, gb.__init__, "crap")

if __name__ == "__main__":
    unittest.main()
