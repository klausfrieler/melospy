"""
This is an example that uses the MidiToText eventhandler. When an 
event is triggered on it, it prints the event to the console.

It gets the events from the MidiInFile.

So it prints all the events from the infile to the console. great for 
debugging :-s
"""


# get data
#test_file = 'test/midifiles/minimal-cubase-type0.mid'
test_file = 'WoodyShaw_InACapricornianWay_PREFINAL.mid'
test_file = 'WyntonMarsalis_JohnnyComeLately_PREFINAL.mid'
in_file = "C:/Users/klaus/Projects/science/jazzomat/support/20141217/midi30doyou.mid"

# do parsing
from .MidiInFile import MidiInFile
from .MidiToText import MidiToText  # the event handler

midiIn = MidiInFile(MidiToText(), in_file)
midiIn.read()
