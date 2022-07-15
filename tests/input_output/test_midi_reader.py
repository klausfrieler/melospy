#!/usr/bin/env python

""" Test for class MIDIReader2 """
import os
import unittest

import pytest

from melospy.basic_representations.melody import *
from melospy.input_output.midi_reader import *

from tests.rootpath import *

class TestMIDIReader2( unittest.TestCase ):
    supportPath = "e:/Users/klaus/projects/science/jazzomat/support"

    @pytest.mark.skip(reason="irrelevant")
    def testMidiToMelody(self):
        #in_file = "C:/Users/klaus/Projects/science/jazzomat/support/20141217/midi30doyou.mid"
        #in_file = "C:/Users/klaus/Projects/science/jazzomat/melopy/input_output/test/bizet.mid"
        #in_file = os.path.join(data_path,"test1.mid")

        #mtm = MidiToMelody()
        #midiIn = MidiInFile(mtm, in_file)
        #print "\n".join([str(_) for _ in mtm.tempo_map])
        pass
    
    #@pytest.mark.skip(reason="Path mismatch")
    def testSingleFile(self):        
        return
        mr = MIDIReader2()
        mel = mr.readMIDIFile(add_data_path("test1.mid"))
        self.assertEqual(len(mel), 30)
        self.assertRaises(Exception, mr.readMIDIFile, add_data_path("test2.mid"))
        self.assertRaises(Exception, mr.readMIDIFile, add_data_path("test3.mid"))

    @pytest.mark.skip(reason="only for debugging")
    def testMIDIFile(self):
        """ Initialize module """
        mr = MIDIReader2()
        mel = mr.readMIDIFile("e:/projects/science/jazzomat/support/Kopiez/barlow/Barlow-midis-bearbeitet/Midi-fix/Midi2788fix.mid")
        #mel = mr.readMIDIFile("e:/projects/science/jazzomat/projects/walkingbass/bugert/ESP/ESP Miles SoloMIDI.mid")
        ##mel = mr.readMIDIFile("e:/projects/science/jazzomat/projects/walkingbass/bugert/Congeniality/Congeniality  Bass MiDi.mid")
        #mel = mr.readMIDIFile("e:/projects/science/jazzomat/projects/walkingbass/bugert/So What/so what Walkling.mid")
        #mel = mr.readMIDIFile("e:/projects/science/jazzomat/projects/walkingbass/bugert/ESP/ESP.mid")
        #mel = mr.readMIDIFile("e:/projects/science/jazzomat/projects/walkingbass/bugert/I'llBeSeeingYou/I'llBeSeeingYou.mid")
        
        #mel = mr.readMIDIFile("e:/projects/science/jazzomat/projects/walkingbass/bugert/Congeniality/Congeniality.mid")
        print(mel)
        #mr = MIDIReader("K0001.mid")
        #mr = MIDIReader("fornoone.mid")
        #mel = mr.melody

""" Function calls all unit tests """
if __name__ == '__main__':
    alltests = unittest.TestSuite([unittest.TestLoader().loadTestsFromTestCase(TestMIDIReader2)])
    unittest.main()
