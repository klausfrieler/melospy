""" exportMIDI module """

import sys

from melospy.basic_representations.note_event import NoteEvent
from melospy.basic_representations.note_track import NoteTrack
from melospy.feature_machine.feature_module_base import MelopyFeatureModuleBase
from melospy.feature_machine.feature_module_parameter import MelopyFeatureModuleParameter
from melospy.input_output.midi_writer import MIDIWriter


class MelopyFeatureModuleExportMIDI(MelopyFeatureModuleBase):

    def __init__(self):
        """ Initialize module """
        MelopyFeatureModuleBase.__init__(self, "exportMIDI")
        self.addInputParameter(MelopyFeatureModuleParameter("pitch", True))
        self.addInputParameter(MelopyFeatureModuleParameter("onset", True))
        self.addInputParameter(MelopyFeatureModuleParameter("duration", True))
        self.addInputParameter(MelopyFeatureModuleParameter("label", True))

    def process(self):
        self.checkInputParameters()
        label = self.getParameterValue("label")
        pitch = self.getParameterValue("pitch")
        onset = self.getParameterValue("onset")
        duration = self.getParameterValue("duration")
        for i in range(len(pitch)):
            self.processSingle(pitch[i], onset[i], duration[i], str(label[i]))

    def processSingle(self, pitch, onset, duration, label):
        # Derive MIDI file name from SV file name
        fnMIDI = label.replace(".sv", ".mid")
        # convert vectors to note events
        n = NoteTrack()
        for i in range(len(pitch)):
            r = NoteEvent(pitch[i], onset[i], duration[i])
            n.append(r)
        m = MIDIWriter()
        m.writeMIDIFile(n, fnMIDI)
