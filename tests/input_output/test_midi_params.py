#!/usr/bin/env python

""" Unit test for class MIDIParams"""

import unittest

import pytest

from melospy.input_output.midi_params import *


class TestMIDIPrams( unittest.TestCase ):

    #@pytest.mark.skip(reason="Assertion mismatch")
    def testConstructors(self):
        mrp = MIDIReaderParams()
        self.assertEqual(mrp.getValue("add_dummy_phrases"), True)
        mwp = MIDIWriterParams()
        self.assertEqual(mwp.getValue("transpose"), 0)
        self.assertEqual(mwp.getValue("tempo"), "auto")
        self.assertEqual(mwp.getValue("channel"), 0)
        self.assertEqual(mwp.getValue("instrument"), "")
        self.assertEqual(mwp.getValue("volume"), 'log_range')
        s = MIDIReaderParams.fromDict({'add_dummy_phrases': False})
        self.assertEqual(s.getValue("add_dummy_phrases"), False)

if __name__ == "__main__":
    unittest.main()
