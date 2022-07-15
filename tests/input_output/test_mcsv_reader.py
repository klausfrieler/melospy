#!/usr/bin/env python

""" Class implementation of MCSV reader"""

import os
import unittest

import pytest

from melospy.input_output.mcsv_params import MCSVReaderParams
from melospy.input_output.mcsv_reader import MCSVReader

from tests.rootpath import *

class TestMCSVReader( unittest.TestCase ):


    def testMCSVReader(self):
        """ Initialize module """
        #mcsvr = MCSVReader("c:\\Users\\klaus\\Data\\EsacDB\\Kinderlieder\\csv\\complete\\K0025.csv")
        fname = add_data_path("test_solo.csv")
        mcsvr = MCSVReader(fname, MCSVReaderParams(), csv_format="mcsv1")
        #mcsvr = MCSVReader("c:\\Users\\klaus\\Data\\BGG\\csv\\complete\\BGG27_en.csv")
        test_solo = mcsvr.melody
        self.assertEqual(len(test_solo), 645)
        
    def testMCSV2Reader(self):
        """ Initialize module """
        #mcsvr = MCSVReader("c:\\Users\\klaus\\Data\\EsacDB\\Kinderlieder\\csv\\complete\\K0025.csv")
        fname = add_data_path("RexStewart_Perdido_FINAL.csv")
        mcsvr = MCSVReader(fname, MCSVReaderParams(), csv_format = "mcsv2")        
        #mcsvr = MCSVReader("c:\\Users\\klaus\\Data\\BGG\\csv\\complete\\BGG27_en.csv")
        test = mcsvr.melody
        self.assertEqual(len(test), 277)

""" Function calls all unit tests """
if __name__ == '__main__':
    alltests = unittest.TestSuite([unittest.TestLoader().loadTestsFromTestCase(TestMCSVReader)])
    unittest.main()
