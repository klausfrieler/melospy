#!/usr/bin/env python

""" Unit test for class SVReaderParams"""

import unittest

from melospy.input_output.sv_params import *


class TestSVReaderParams( unittest.TestCase ):
    
    def testConstructors(self):

        svr = SVReaderParams()
        self.assertEqual(svr.getValue("diagnostic"), False)
        self.assertEqual(svr.getValue("normalize"), False)
        self.assertDictEqual(svr.getValue("flexq").__dict__, FlexQParams().__dict__)
        self.assertEqual(svr.getValue("metadata_file"), "")
        self.assertEqual(svr.getValue("start_times_file"), "")
        self.assertEqual(svr.getValue("loudness_dir"), "")
        self.assertEqual(svr.getValue("walkingbass_dir"), "")

        #s = SVReaderParams.fromDict({'add_dummy_phrases': True, flexq=})
        #self.assertEqual(s.getValue("add_dummy_phrases"), True)
        
if __name__ == "__main__":
    unittest.main()
