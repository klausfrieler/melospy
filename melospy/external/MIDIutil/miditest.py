#-----------------------------------------------------------------------------
# Name:        miditest.py
# Purpose:     Unit testing harness for midiutil
#
# Author:      Mark Conway Wirt <emergentmusics) at (gmail . com>
#
# Created:     2008/04/17
# Copyright:   (c) 2009, Mark Conway Wirt
# License:     Please see License.txt for the terms under which this
#              software is distributed.
#-----------------------------------------------------------------------------



# Next few lines are necessary owing to limitations of the IDE and the
# directory structure of the project.

import struct
import sys
import unittest

from midiutil.MidiFile import (MIDIFile, MIDIHeader, MIDITrack, frequencyTransform,
                               returnFrequency, writeVarLength)

sys.path.append('..')


class TestMIDIUtils(unittest.TestCase):

    def testWriteVarLength(self):
        self.assertEqual(writeVarLength(0x70), [0x70])
        self.assertEqual(writeVarLength(0x80), [0x81, 0x00])
        self.assertEqual(writeVarLength(0x1FFFFF), [0xFF, 0xFF, 0x7F])
        self.assertEqual(writeVarLength(0x08000000), [0xC0, 0x80, 0x80, 0x00])

    def testAddNote(self):
        MyMIDI = MIDIFile(1)
        MyMIDI.addNote(0, 0, 100, 0, 1, 100)
        self.assertEqual(MyMIDI.tracks[0].eventList[0].type, "note")
        self.assertEqual(MyMIDI.tracks[0].eventList[0].pitch, 100)
        self.assertEqual(MyMIDI.tracks[0].eventList[0].time, 0)
        self.assertEqual(MyMIDI.tracks[0].eventList[0].duration, 1)
        self.assertEqual(MyMIDI.tracks[0].eventList[0].volume, 100)

    def testDeinterleaveNotes(self):
        MyMIDI = MIDIFile(1)
        MyMIDI.addNote(0, 0, 100, 0, 2, 100)
        MyMIDI.addNote(0, 0, 100, 1, 2, 100)
        MyMIDI.close()
        self.assertEqual(MyMIDI.tracks[0].MIDIEventList[0].type, 'NoteOn')
        self.assertEqual(MyMIDI.tracks[0].MIDIEventList[0].time,  0)
        self.assertEqual(MyMIDI.tracks[0].MIDIEventList[1].type, 'NoteOff')
        self.assertEqual(MyMIDI.tracks[0].MIDIEventList[1].time,  128)
        self.assertEqual(MyMIDI.tracks[0].MIDIEventList[2].type, 'NoteOn')
        self.assertEqual(MyMIDI.tracks[0].MIDIEventList[2].time,  0)
        self.assertEqual(MyMIDI.tracks[0].MIDIEventList[3].type, 'NoteOff')
        self.assertEqual(MyMIDI.tracks[0].MIDIEventList[3].time,  256)

    def testTimeShift(self):

        # With one track
        MyMIDI = MIDIFile(1)
        MyMIDI.addNote(0, 0, 100, 5, 1, 100)
        MyMIDI.close()
        self.assertEqual(MyMIDI.tracks[0].MIDIEventList[0].type, 'NoteOn')
        self.assertEqual(MyMIDI.tracks[0].MIDIEventList[0].time,  0)
        self.assertEqual(MyMIDI.tracks[0].MIDIEventList[1].type, 'NoteOff')
        self.assertEqual(MyMIDI.tracks[0].MIDIEventList[1].time,  128)

        # With two tracks
        MyMIDI = MIDIFile(2)
        MyMIDI.addNote(0, 0, 100, 5, 1, 100)
        MyMIDI.addNote(1, 0, 100, 6, 1, 100)
        MyMIDI.close()
        self.assertEqual(MyMIDI.tracks[0].MIDIEventList[0].type, 'NoteOn')
        self.assertEqual(MyMIDI.tracks[0].MIDIEventList[0].time,  0)
        self.assertEqual(MyMIDI.tracks[0].MIDIEventList[1].type, 'NoteOff')
        self.assertEqual(MyMIDI.tracks[0].MIDIEventList[1].time,  128)
        self.assertEqual(MyMIDI.tracks[1].MIDIEventList[0].type, 'NoteOn')
        self.assertEqual(MyMIDI.tracks[1].MIDIEventList[0].time,  128)
        self.assertEqual(MyMIDI.tracks[1].MIDIEventList[1].type, 'NoteOff')
        self.assertEqual(MyMIDI.tracks[1].MIDIEventList[1].time,  128)

        # Negative Time
        MyMIDI = MIDIFile(1)
        MyMIDI.addNote(0, 0, 100, -5, 1, 100)
        MyMIDI.close()
        self.assertEqual(MyMIDI.tracks[0].MIDIEventList[0].type, 'NoteOn')
        self.assertEqual(MyMIDI.tracks[0].MIDIEventList[0].time,  0)
        self.assertEqual(MyMIDI.tracks[0].MIDIEventList[1].type, 'NoteOff')
        self.assertEqual(MyMIDI.tracks[0].MIDIEventList[1].time,  128)

        # Negative time, two tracks

        MyMIDI = MIDIFile(2)
        MyMIDI.addNote(0, 0, 100, -1, 1, 100)
        MyMIDI.addNote(1, 0, 100, 0, 1, 100)
        MyMIDI.close()
        self.assertEqual(MyMIDI.tracks[0].MIDIEventList[0].type, 'NoteOn')
        self.assertEqual(MyMIDI.tracks[0].MIDIEventList[0].time,  0)
        self.assertEqual(MyMIDI.tracks[0].MIDIEventList[1].type, 'NoteOff')
        self.assertEqual(MyMIDI.tracks[0].MIDIEventList[1].time,  128)
        self.assertEqual(MyMIDI.tracks[1].MIDIEventList[0].type, 'NoteOn')
        self.assertEqual(MyMIDI.tracks[1].MIDIEventList[0].time,  128)
        self.assertEqual(MyMIDI.tracks[1].MIDIEventList[1].type, 'NoteOff')
        self.assertEqual(MyMIDI.tracks[1].MIDIEventList[1].time,  128)

    def testFrequency(self):
        freq = frequencyTransform(8.1758)
        self.assertEqual(freq[0],  0x00)
        self.assertEqual(freq[1],  0x00)
        self.assertEqual(freq[2],  0x00)
        freq = frequencyTransform(8.66196) # 8.6620 in MIDI documentation
        self.assertEqual(freq[0],  0x01)
        self.assertEqual(freq[1],  0x00)
        self.assertEqual(freq[2],  0x00)
        freq = frequencyTransform(440.00)
        self.assertEqual(freq[0],  0x45)
        self.assertEqual(freq[1],  0x00)
        self.assertEqual(freq[2],  0x00)
        freq = frequencyTransform(440.0016)
        self.assertEqual(freq[0],  0x45)
        self.assertEqual(freq[1],  0x00)
        self.assertEqual(freq[2],  0x01)
        freq = frequencyTransform(439.9984)
        self.assertEqual(freq[0],  0x44)
        self.assertEqual(freq[1],  0x7f)
        self.assertEqual(freq[2],  0x7f)
        freq = frequencyTransform(8372.0190)
        self.assertEqual(freq[0],  0x78)
        self.assertEqual(freq[1],  0x00)
        self.assertEqual(freq[2],  0x00)
        freq = frequencyTransform(8372.062) #8372.0630 in MIDI documentation
        self.assertEqual(freq[0],  0x78)
        self.assertEqual(freq[1],  0x00)
        self.assertEqual(freq[2],  0x01)
        freq = frequencyTransform(13289.7300)
        self.assertEqual(freq[0],  0x7F)
        self.assertEqual(freq[1],  0x7F)
        self.assertEqual(freq[2],  0x7E)
        freq = frequencyTransform(12543.8760)
        self.assertEqual(freq[0],  0x7F)
        self.assertEqual(freq[1],  0x00)
        self.assertEqual(freq[2],  0x00)
        freq = frequencyTransform(8.2104) # Just plain wrong in documentation, as far as I can tell.
        #self.assertEquals(freq[0],  0x0)
        #self.assertEquals(freq[1],  0x0)
        #self.assertEquals(freq[2],  0x1)

        # Test the inverse
        testFreq = 15.0
        accuracy = 0.00001
        x = returnFrequency(frequencyTransform(testFreq))
        delta = abs(testFreq - x)
        self.assertEqual(delta < (accuracy*testFreq), True)
        testFreq = 200.0
        x = returnFrequency(frequencyTransform(testFreq))
        delta = abs(testFreq - x)
        self.assertEqual(delta < (accuracy*testFreq), True)
        testFreq = 400.0
        x = returnFrequency(frequencyTransform(testFreq))
        delta = abs(testFreq - x)
        self.assertEqual(delta < (accuracy*testFreq), True)
        testFreq = 440.0
        x = returnFrequency(frequencyTransform(testFreq))
        delta = abs(testFreq - x)
        self.assertEqual(delta < (accuracy*testFreq), True)
        testFreq = 1200.0
        x = returnFrequency(frequencyTransform(testFreq))
        delta = abs(testFreq - x)
        self.assertEqual(delta < (accuracy*testFreq), True)
        testFreq = 5000.0
        x = returnFrequency(frequencyTransform(testFreq))
        delta = abs(testFreq - x)
        self.assertEqual(delta < (accuracy*testFreq), True)
        testFreq = 12000.0
        x = returnFrequency(frequencyTransform(testFreq))
        delta = abs(testFreq - x)
        self.assertEqual(delta < (accuracy*testFreq), True)


    def testSysEx(self):
        MyMIDI = MIDIFile(1)
        MyMIDI.addSysEx(0, 0, 0, struct.pack('>B', 0x01))
        MyMIDI.close()
        self.assertEqual(MyMIDI.tracks[0].MIDIEventList[0].type, 'SysEx')
        self.assertEqual(struct.unpack('>B', MyMIDI.tracks[0].MIDIdata[0])[0], 0x00)
        self.assertEqual(struct.unpack('>B', MyMIDI.tracks[0].MIDIdata[1])[0], 0xf0)
        self.assertEqual(struct.unpack('>B', MyMIDI.tracks[0].MIDIdata[2])[0], 3)
        self.assertEqual(struct.unpack('>B', MyMIDI.tracks[0].MIDIdata[3])[0], 0x00)
        self.assertEqual(struct.unpack('>B', MyMIDI.tracks[0].MIDIdata[4])[0], 0x01)
        self.assertEqual(struct.unpack('>B', MyMIDI.tracks[0].MIDIdata[5])[0], 0xf7)

    def testUniversalSysEx(self):
        MyMIDI = MIDIFile(1)
        MyMIDI.addUniversalSysEx(0, 0, 1, 2, struct.pack('>B', 0x01))
        MyMIDI.close()
        self.assertEqual(MyMIDI.tracks[0].MIDIEventList[0].type, 'UniversalSysEx')
        self.assertEqual(struct.unpack('>B', MyMIDI.tracks[0].MIDIdata[0])[0], 0x00)
        self.assertEqual(struct.unpack('>B', MyMIDI.tracks[0].MIDIdata[1])[0], 0xf0)
        self.assertEqual(struct.unpack('>B', MyMIDI.tracks[0].MIDIdata[2])[0], 6)
        self.assertEqual(struct.unpack('>B', MyMIDI.tracks[0].MIDIdata[3])[0], 0x7E)
        self.assertEqual(struct.unpack('>B', MyMIDI.tracks[0].MIDIdata[4])[0], 0x7F)
        self.assertEqual(struct.unpack('>B', MyMIDI.tracks[0].MIDIdata[5])[0], 0x01)
        self.assertEqual(struct.unpack('>B', MyMIDI.tracks[0].MIDIdata[6])[0], 0x02)
        self.assertEqual(struct.unpack('>B', MyMIDI.tracks[0].MIDIdata[7])[0], 0x01)
        self.assertEqual(struct.unpack('>B', MyMIDI.tracks[0].MIDIdata[8])[0], 0xf7)

    def testTuning(self):
        MyMIDI = MIDIFile(1)
        MyMIDI.changeNoteTuning(0, [(1, 440), (2, 880)])
        MyMIDI.close()
        self.assertEqual(MyMIDI.tracks[0].MIDIEventList[0].type, 'UniversalSysEx')
        self.assertEqual(struct.unpack('>B', MyMIDI.tracks[0].MIDIdata[0])[0], 0x00)
        self.assertEqual(struct.unpack('>B', MyMIDI.tracks[0].MIDIdata[1])[0], 0xf0)
        self.assertEqual(struct.unpack('>B', MyMIDI.tracks[0].MIDIdata[2])[0], 15)
        self.assertEqual(struct.unpack('>B', MyMIDI.tracks[0].MIDIdata[3])[0], 0x7E)
        self.assertEqual(struct.unpack('>B', MyMIDI.tracks[0].MIDIdata[4])[0], 0x7F)
        self.assertEqual(struct.unpack('>B', MyMIDI.tracks[0].MIDIdata[5])[0], 0x08)
        self.assertEqual(struct.unpack('>B', MyMIDI.tracks[0].MIDIdata[6])[0], 0x02)
        self.assertEqual(struct.unpack('>B', MyMIDI.tracks[0].MIDIdata[7])[0], 0x00)
        self.assertEqual(struct.unpack('>B', MyMIDI.tracks[0].MIDIdata[8])[0], 0x2)
        self.assertEqual(struct.unpack('>B', MyMIDI.tracks[0].MIDIdata[9])[0], 0x1)
        self.assertEqual(struct.unpack('>B', MyMIDI.tracks[0].MIDIdata[10])[0], 69)
        self.assertEqual(struct.unpack('>B', MyMIDI.tracks[0].MIDIdata[11])[0], 0)
        self.assertEqual(struct.unpack('>B', MyMIDI.tracks[0].MIDIdata[12])[0], 0)
        self.assertEqual(struct.unpack('>B', MyMIDI.tracks[0].MIDIdata[13])[0], 0x2)
        self.assertEqual(struct.unpack('>B', MyMIDI.tracks[0].MIDIdata[14])[0], 81)
        self.assertEqual(struct.unpack('>B', MyMIDI.tracks[0].MIDIdata[15])[0], 0)
        self.assertEqual(struct.unpack('>B', MyMIDI.tracks[0].MIDIdata[16])[0], 0)
        self.assertEqual(struct.unpack('>B', MyMIDI.tracks[0].MIDIdata[17])[0], 0xf7)

MIDISuite = unittest.TestLoader().loadTestsFromTestCase(TestMIDIUtils)

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=1).run(MIDISuite)
