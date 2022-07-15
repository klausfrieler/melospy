#!/usr/bin/env python

""" Test for class KernReader """

import unittest

import pytest

from melospy.basic_representations.melody import *
from melospy.input_output.krn_params import *
from melospy.input_output.krn_reader import *
from tests.rootpath import * 

class TestKernReader( unittest.TestCase ):

    #@pytest.mark.skip(reason="Path mismatch")
    def testKernReader(self):
        """ Initialize module """
        f = add_data_path("Warming_Up_A_Riff.krn")
        kern_params = KernReaderParams(diagnostic=True, metadata_file="", part_no=0, only_solos=True)
        mr = KernReader(params=kern_params)
        f = "e:/data/MTC-FS-INST-2.0/krn/NLB184198_01.krn"
        solo = mr.readKernFile(f)
        self.assertEqual(len(solo), 853)
   
        #f = "c:/Users/klaus/Projects/science/jazzomat/projects/omnibook/parker_kern/Ballade.krn"
        #solo = mr.readKernFile(f)
        #f = "c:/Users/klaus/Projects/science/jazzomat/projects/omnibook/parker_kern/Klaun_Stance.krn"
        #solo = mr.readKernFile(f)
        #print solo.beattrack.getChords(True)
        #print data[0].meter
        #print data[1].meter
        #data[1].calc_beat_and_tatums()
        #print data[1]
        #data[1].calc_metrical_positions()
        #print data[1].convert_to_annotated_beat_track()
        #data[0].convert_to_melody()
        #for d in data:
        #    print (d)
        #self.assertEqual(msi.nParts, 4)
        #self.assertEqual(msi.isMetered, True)
        #self.assertEqual(msi.nVoices, [1,1,1,1])
        #self.assertEqual(msi.streamTypes[0], ['melody'])
        #self.assertRaises(ValueError, mr.readKernFile, "test1.krn")
        ##mel = mr.readKernFile("test1.krn", 0)
        #self.assertEqual(isinstance(mel, Melody), True)
        ##print mel.getPitches()
        #self.assertEqual(mel.getPitches(), [45, 57, 56, 57, 54, 55, 57, 50, 45, 52, 54, 52, 50, 52, 54, 56, 57, 49, 50, 52, 52, 45, 45, 52, 53, 54, 59, 57, 56, 54, 52, 49, 54, 52, 54, 56, 57, 59, 57, 56, 54, 49, 50, 52, 52])
        #self.assertmel.getPitches()
        #mel = mr.readKernFile("http://kern.ccarh.org/cgi-bin/ksdata?location=musedata/bach/chorales&file=chor-001.krn&format=kern", 0)
        #mel = mr.readKernFile("http://kern.ccarh.org/cgi-bin/ksdata?location=essen/asia/china/han&file=han0478.krn&format=kern")
        #print mel

""" Function calls all unit tests """
if __name__ == '__main__':
    alltests = unittest.TestSuite([unittest.TestLoader().loadTestsFromTestCase(TestKernReader)])
    unittest.main()
