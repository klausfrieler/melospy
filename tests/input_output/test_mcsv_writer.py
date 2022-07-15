#!/usr/bin/env python

""" Class implementation of MCSV writer"""

import unittest

import pytest

from melospy.basic_representations.melody import *
from melospy.input_output.mcsv_writer import *

from tests.rootpath import *

class TestMCSVWriter( unittest.TestCase ):
    def constructDummyMelody(self):
        C4 = 60

        #4/4 signature, period = 4, equal beat proportions
        mi = MeterInfo(4, 4)
        #four sixteenth per Beat, .5 sec per beat = 120 bpm
        bi = BeatInfo(4, .5)
        mc = MetricalContext(bi, mi)
        mel = Melody()

        #add a lot more of events
        bis = [BeatInfo(2, .5), BeatInfo(3, .5), BeatInfo(5, .5), BeatInfo(6, .5)]
        for i in range(16):
            duration = 1./8
            onset    = 1 + i*duration
            mc = mc.clone().setBeatInfo(bis[i % len(bis)].clone())
            mp1 = MetricalPosition( i + 1, 1, 2, 0, mc)
            me = MetricalNoteEvent(onset, C4, mp1, duration/2)
            mel.append(me)
        return mel

    #@pytest.mark.skip(reason="Index mismatch")
    def testMCSVWriter(self):
        """ Initialize module """
        mel = self.constructDummyMelody()
        mcsvw = MCSVWriter(mel)
        mcsvw.write(add_data_path("test_melody.csv"))

    def teardown_method(self, method):
        filenames = ["test_melody.csv"]
        for filename in filenames:
            if os.path.exists(add_data_path(filename)):
                os.remove(add_data_path(filename))

""" Function calls all unit tests """
if __name__ == '__main__':
    alltests = unittest.TestSuite([unittest.TestLoader().loadTestsFromTestCase(TestMCSVWriter)])
    unittest.main()
