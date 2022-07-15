#!/usr/bin/env python

import unittest

from melospy.feature_machine.feature import MelopyFeature
from melospy.feature_machine.feature_module_base import MelopyFeatureModuleBase
from melospy.feature_machine.feature_module_connector import *
from melospy.feature_machine.feature_module_diff import *
from melospy.feature_machine.feature_module_parameter import MelopyFeatureModuleParameter


class TestFeature( unittest.TestCase ):
    """ Unit test for feature class """
  
    def testConstructor(self):
        """ Test constructor of feature base class"""
        # create a bunch of parameters
        p1 = MelopyFeatureModuleParameter("processingThreshold1", False, 1.3)
        p2 = MelopyFeatureModuleParameter("processingThreshold2", False, 100)
        p3 = MelopyFeatureModuleParameter("processingSwitch1", False, True)
        p4 = MelopyFeatureModuleParameter("processingSwitch2", False, False)
        p5 = MelopyFeatureModuleParameter("output1", False, False)
        
        # create 2 modules with some parameters
        m1 = MelopyFeatureModuleBase()
        m1.setLabel("Mod1")
        m1.addInputParameter(p3)
        m1.addInputParameter(p4)
        m1.addOutputParameter(p5)
        m2 = MelopyFeatureModuleBase()
        m1.setLabel("Mod2")
        m2.addInputParameter(p1)
        m2.addInputParameter(p2)

        # connect output parameter of module m1 with input parameter of module m2
        c = MelopyFeatureModuleConnector(m1.getID(), "output1", m2.getID(), "processingThreshold1")

        # generate feature with two modules and one connector
        f = MelopyFeature()
        f.addModule(m1)
        f.addModule(m2)
        f.addConnector(c)
        del f
        
    def testGetModuleProcessingOrder(self):
        """ Tests if the correct processing order will be computed for a given set of connected modules """
        p1out = MelopyFeatureModuleParameter("p1out", True)
        p2in = MelopyFeatureModuleParameter("p2in", True)
        p2out = MelopyFeatureModuleParameter("p2out", True)
        p3in = MelopyFeatureModuleParameter("p3in", True)
        p3out = MelopyFeatureModuleParameter("p3out", True)
        p4in = MelopyFeatureModuleParameter("p4in", True)
        p4out = MelopyFeatureModuleParameter("p4out", True)
        
        # create modules
        m1 = MelopyFeatureModuleBase()
        m1.setLabel("Mod1")
        m2 = MelopyFeatureModuleBase()
        m2.setLabel("Mod2")
        m3 = MelopyFeatureModuleBase()
        m3.setLabel("Mod3")
        m4 = MelopyFeatureModuleBase()
        m4.setLabel("Mod4")
        
        # add parameters to modules
        m1.addOutputParameter(p1out)
        m2.addInputParameter(p2in)
        m2.addOutputParameter(p2out)
        m3.addInputParameter(p3in)
        m3.addOutputParameter(p3out)
        m4.addInputParameter(p4in)
        m4.addOutputParameter(p4out)
   
        # create feature 
        f = MelopyFeature()
        
        # add modules to feature
        f.addModule(m1)
        f.addModule(m2)
        f.addModule(m3)
        f.addModule(m4)

        # add connectors to feature
        f.addConnector(MelopyFeatureModuleConnector(m1.getID(), "p1out", m2.getID(), "p2in"))
        f.addConnector(MelopyFeatureModuleConnector(m2.getID(), "p2out", m3.getID(), "p3in"))
        f.addConnector(MelopyFeatureModuleConnector(m3.getID(), "p3out", m4.getID(), "p4in"))
        
        self.assertEqual(f.computeProcessModuleProcessingOrder(), [0, 1, 2, 3])

if __name__ == "__main__":
    unittest.main()
