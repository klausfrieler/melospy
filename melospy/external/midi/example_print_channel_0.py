from .MidiInFile import MidiInFile
from .MidiOutStream import MidiOutStream


"""
This prints all note on events on midi channel 0
"""


class Transposer(MidiOutStream):
    
    "Transposes all notes by 1 octave"
    
    def note_on(self, channel=0, note=0x40, velocity=0x40):
        if channel == 0:
            print(channel, note, velocity, self.rel_time())

    def time_signature(self, nn, dd, cc, bb):
        print(nn, dd, cc, bb)

    def key_signature(self, sf, mi):
        print(sf, mi)
        
event_handler = Transposer()

in_file = "C:/Users/klaus/Projects/science/jazzomat/support/20141217/midi30doyou.mid"
midi_in = MidiInFile(event_handler, in_file)
midi_in.read()
print(midi_in)
