#!/usr/bin/env python

import unittest

from melospy.feature_machine.feature_module_base import MelopyFeatureModuleBase
from melospy.feature_machine.feature_module_parameter import MelopyFeatureModuleParameter


class TestModuleFeatureBase( unittest.TestCase ):
    """ Unit test for feature module base class """
  
    def testConstructor(self):
        """ Test constructor """
        p1 = MelopyFeatureModuleParameter("processingThreshold1", False, 1.3)
        p2 = MelopyFeatureModuleParameter("processingThreshold2", False, 100)
        p3 = MelopyFeatureModuleParameter("processingSwitch1", False, True)
        p4 = MelopyFeatureModuleParameter("processingSwitch2", False, False)
        
        m = MelopyFeatureModuleBase()
        m.addInputParameter(p1)
        m.addInputParameter(p2)
        m.addInputParameter(p3)
        m.addInputParameter(p4)
      
        self.assertEqual(len(m.inputParameters), 4)
        
    def testAddParameterWithSameLabel(self):
        """ Test adding of parameter to module with a label that is already used causes Exception """
        p = MelopyFeatureModuleParameter("processingSwitch2", False, False)
        m = MelopyFeatureModuleBase()
        m.addInputParameter(p)
        self.assertRaises(Exception, m.addInputParameter, p)
        
    def testAddParameterWithEmptyLabel(self):
        """ Test adding of parameter to module with an empty label causes Exception"""
        p = MelopyFeatureModuleParameter("", False, False)
        m = MelopyFeatureModuleBase()
        self.assertRaises(Exception, m.addInputParameter, p)
        
        
if __name__ == "__main__":
    unittest.main()
