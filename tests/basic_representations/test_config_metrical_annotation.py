#!/usr/bin/env python

""" Unit test for class FlexQParams"""

import unittest

from melospy.basic_representations.metrical_annotation_param import *


class TestFlexQParams( unittest.TestCase ):
    
    def testConstructor(self):

        cma = FlexQParams()
        self.assertEqual(cma.getValue("optimize"), True)
        self.assertEqual(cma.getValue("rhythmThreshold"), 0.02)
        cma = FlexQParams.fromDict({'optimize':False, 'rhythmThreshold': 0.05})
        self.assertEqual(cma.getValue("optimize"), False)
        self.assertEqual(cma.getValue("rhythmThreshold"), 0.05)

if __name__ == "__main__":
    unittest.main()
