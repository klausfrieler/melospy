#!/usr/bin/env python

import os
import sys
import unittest

import numpy as np
import pytest

from melospy.feature_machine.feature_module_exportMIDI import MelopyFeatureModuleExportMIDI


class TestModuleExportMIDI( unittest.TestCase ):
    """ Unit test for exportMIDI module """

    #@pytest.mark.skip(reason="Much too much for a unit test")
    def testAbsModuleFunctionality(self):
        """ Test exportMIDI module """
        m = MelopyFeatureModuleExportMIDI()
        m.setParameterValue("pitch", [np.array([33, 35, 36, 38])])
        m.setParameterValue("onset", [np.array([1, 1.5, 2, 2.5])])
        m.setParameterValue("duration", [np.array([.5, .5, .5, .5])])
        m.setParameterValue("label", "test.sv")
        m.process()

    def teardown_method(self, method):
        filename = "t"
        if os.path.exists(filename):
            os.remove(filename)


if __name__ == "__main__":
    unittest.main()
