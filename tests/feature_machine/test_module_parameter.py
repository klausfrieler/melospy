#!/usr/bin/env python

import unittest

from melospy.feature_machine.feature_module_parameter import MelopyFeatureModuleParameter


class TestModuleParameter( unittest.TestCase ):
    """ Unit test for feature module parameter class """
  
    def testConstructor(self):
        """ Test constructor """
        p = MelopyFeatureModuleParameter()
        self.assertEqual(p.getLabel(), "")
        self.assertEqual(p.getIsMandatory(), True)
        self.assertEqual(p.getDefaultValue(), None)
        del p
        
        p = MelopyFeatureModuleParameter("MyParam1")
        self.assertEqual(p.getLabel(), "MyParam1")
        self.assertEqual(p.getIsMandatory(), True)
        self.assertEqual(p.getDefaultValue(), None)
        del p
        
        p = MelopyFeatureModuleParameter("MyParam1", True)
        self.assertEqual(p.getLabel(), "MyParam1")
        self.assertEqual(p.getIsMandatory(), True)
        self.assertEqual(p.getDefaultValue(), None)
        del p
        
        p = MelopyFeatureModuleParameter("someProcessingThreshold", False, 3.443)
        self.assertEqual(p.getLabel(), "someProcessingThreshold")
        self.assertEqual(p.getIsMandatory(), False)
        self.assertEqual(p.getDefaultValue(), 3.443)
        del p
        
        
        
        
if __name__ == "__main__":
    unittest.main()
