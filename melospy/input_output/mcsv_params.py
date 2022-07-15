""" Class implementation of Configuration values for MCSV params (read)"""

from melospy.basic_representations.config_param import *
from melospy.basic_representations.jm_util import safe_set


class MCSVReaderParams(ConfigParameter):
    """MCSVReader parameters"""
    field_names = ["requantize", "max_div", "tolerance", "metadata_file"]

    def __init__(self, requantize=True, max_div=6, tolerance=.1, metadata_file=""):
        self.setValue("requantize",  requantize, (bool))
        self.setValue("max_div",  max_div, (int))
        self.setValue("tolerance",  tolerance, (float))
        self.setValue("metadata_file", metadata_file, (str))

    @staticmethod
    def fromDict(params, allowNone=False):
        if isinstance(params, MCSVReaderParams):
            params = params.__dict__
        if not isinstance(params, dict):
            raise TypeError("Expected dictionary for 'params', got {}".format(type(params)))
        cp = MCSVReaderParams()
        for e in params:
            if e not in MCSVReaderParams.field_names:
                print("MCSVReaderParams: Invalid field name:{}".format(e))
            cp.setValue(e, params[e], type(params[e]), allowNone)
        return cp

class MCSVWriterParams(ConfigParameter):
    """MCSVWriter parameters"""
    field_names = ["ticks_per_beat", "add_phrases", "segmenter"]

    def __init__(self, ticks_per_beat=0, add_phrases=False, segmenter=""):
        self.setValue("ticks_per_beat",  ticks_per_beat, (int))
        self.setValue("add_phrases",  add_phrases, (bool))
        self.setValue("segmenter",  segmenter, (str))

    @staticmethod
    def fromDict(params, allowNone=False):
        if isinstance(params, MCSVWriterParams):
            params = params.__dict__
        if not isinstance(params, dict):
            raise TypeError("Expected dictionary for 'params', got {}".format(type(params)))
        cp = MCSVWriterParams()
        for e in params:
            if e not in MCSVWriterParams.field_names:
                print("MCSVWriterParams: Invalid field name:{}".format(e))

            cp.setValue(e, params[e], type(params[e]), allowNone)
        return cp
