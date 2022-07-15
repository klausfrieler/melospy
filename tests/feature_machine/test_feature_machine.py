#!/usr/bin/env python

import os
import sys
import unittest

import numpy as np
import pytest

from melospy.feature_machine.feature_machine_main import FeatureMachine
from tests.rootpath import *

class TestFeatureMachine( unittest.TestCase ):
    """ Unit test for feature machine """

    def export(self,var,aggregationOver=None,optParams=None):
        """ Dummy export function that will be called from feature source module """
        if var == "pitch":
            return [np.array([30, 30, 30, 32, 34, 38, 34, 30])]

    #@pytest.mark.skip(reason="Path mismatch")
    def testCreateFeatureFromYAML(self):
        """ Test constructor of feature base class"""
        data_path = add_data_path("pitch_range.yml")
        feature = FeatureMachine().createFeatureFromYAMLFile(data_path)
        feature.process(self)
        sinkModuleValues = feature.getSinkModuleValues()
        self.assertEqual(sinkModuleValues['pitch_range'], 8)

if __name__ == "__main__":
    unittest.main()
