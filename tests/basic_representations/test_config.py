#!/usr/bin/env python

""" Unit test for class ConfigParameter"""

import unittest

from melospy.basic_representations.config_param import *
from melospy.basic_representations.jm_util import *


class TestConfigParameter( unittest.TestCase ):

    def testConstructor(self):
        cp = ConfigParameter()
        cp.setValue("_x", 1, int)
        self.assertEqual(cp._x, 1)

        cp.setValue("optimize", False, bool)
        self.assertEqual(cp.getValue("optimize"), False)
        cp.setValue("test", {"params":1, "params2":{"a":1, "b":2}}, dict)
        self.assertDictEqual(cp.test, {"params":1, "params2":{"a":1, "b":2}})
        cp.setValueWithDomainCheck("test", "yes", ["yes", "no"])
        self.assertEqual(cp.test, "yes")
        cp.setValueWithDomainCheck("test", "YES", ["yes", "no"], case_sensitive=False)
        self.assertEqual(cp.test, "YES")
        self.assertRaises(ValueError, cp.setValueWithDomainCheck, "test", "yo", ["yes", "no"])
        #self.assertEqual(smd.getCompositionInfo(), ci)
        #self.assertEqual(smd.getSubfield("CompositionInfo"), ci)
        #self.assertRaises(cp.typecheck, "r", (int, float))

        #smd = SimpleMetaData(None)
        #self.assertEqual(smd.getCompositionInfo(), None)
        #print smd
if __name__ == "__main__":
    unittest.main()
