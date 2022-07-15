""" Class implementation of Configuration values for MIDI params (read and write)"""

from melospy.basic_representations.config_param import *
from melospy.basic_representations.jm_util import safe_set


class MIDIReaderParams(ConfigParameter):
    """MIDIReader parameters"""
    field_names = ["add_dummy_phrases"]
    def __init__(self, add_dummy_phrases=True):

        self.setValue("add_dummy_phrases",  add_dummy_phrases, (bool))

    @staticmethod
    def fromDict(params, allowNone=False):
        if isinstance(params, MIDIReaderParams):
            params = params.__dict__
        if not isinstance(params, dict):
            raise TypeError("Expected dictionary for 'params', got {}".format(type(params)))
        cp = MIDIReaderParams()
        for e in params:
            if e not in MIDIReaderParams.field_names:
                print("MIDIReaderParams: Invalid field name:{}".format(e))
            cp.setValue(e, params[e], type(params[e]), allowNone)
        return cp

class MIDIWriterParams(ConfigParameter):
    """MIDIWriter parameters"""
    field_names = ["transpose", "tempo", "quantize", "quantize_duration", "track", "channel", "instrument", "ticks_per_beat", "volume"]

    def __init__(self, transpose=0, tempo="auto", quantize=True, quantize_duration=True, track=0, channel=0, instrument="", ticks_per_beat=0, volume="log_range"):
        self.setValue("transpose",  transpose, (int))
        self.setValue("tempo",  tempo)
        self.setValue("quantize",  quantize, (bool))
        self.setValue("quantize_duration",  quantize_duration, (bool))
        self.setValue("channel",  channel, (int))
        self.setValue("track",  track, (int))
        self.setValue("volume",  volume)
        self.setValue("instrument",  instrument)
        self.setValue("ticks_per_beat",  ticks_per_beat, (int))

    @staticmethod
    def fromDict(params, allowNone=False):
        if isinstance(params, MIDIWriterParams):
            params = params.__dict__
        if not isinstance(params, dict):
            raise TypeError("Expected dictionary for 'params', got {}".format(type(params)))
        cp = MIDIWriterParams()
        for e in params:
            if e not in MIDIWriterParams.field_names:
                print("MIDIWriterParams: Invalid field name:{}".format(e))
            cp.setValue(e, params[e], type(params[e]), allowNone)
        return cp
