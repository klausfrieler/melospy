#!/usr/bin/env python

""" Class implementation of MCSV reader"""

import os
import unittest

import pytest

from melospy.input_output.esac_reader import *
from melospy.input_output.mcsv_writer import *
from tests.rootpath import *

class TestEsacReader( unittest.TestCase ):
    #@pytest.mark.skip(reason="Path mismatch")
    def testEsacReader(self):
        """ Initialize module """
        esac_reader = EsacReader(add_data_path("D0001.esa"))
        solo = esac_reader.getMelody()
        self.assertEqual(len(solo), 44)
        ps = solo.getPhraseSections()
        esac_info = esac_reader.getEsacInfo()
        self.assertEqual(esac_info.getEsacid(), "D0001")

""" Function calls all unit tests """
if __name__ == '__main__':
    alltests = unittest.TestSuite([unittest.TestLoader().loadTestsFromTestCase(TestEsacReader)])
    unittest.main()
