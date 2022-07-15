""" Class implementation of Configuration values for SV params (read)"""

from melospy.basic_representations.config_param import *
from melospy.basic_representations.jm_util import safe_set
from melospy.basic_representations.metrical_annotation_param import FlexQParams


class SVReaderParams(ConfigParameter):
    """SVReader parameters"""
    field_names = ["diagnostic", "normalize", "strictly_monophonic", "flexq", 
                   "duration_threshold", "metadata_file", "loudness_dir", 
                   "walkingbass_dir", "start_times_file"]
    def __init__(self, diagnostic=False,
                 normalize=False,
                 strictly_monophonic=False,
                 duration_treshold=0.0,
                 flexq={},
                 metadata_file="",
                 loudness_dir="",
                 walkingbass_dir="",
                 start_times_file=""):
        self.setValue("diagnostic",  diagnostic, (bool))
        self.setValue("normalize",  normalize, (bool))
        self.setValue("strictly_monophonic",  strictly_monophonic, (bool))
        self.setValue("duration_threshold",  duration_treshold, (float))
        if isinstance(flexq, dict):
            flexq = FlexQParams.fromDict(flexq)

        self.setValue("flexq",  flexq, (FlexQParams))
        self.setValue("metadata_file", metadata_file, (str))
        self.setValue("loudness_dir", loudness_dir, (str))
        self.setValue("walkingbass_dir", walkingbass_dir, (str))
        self.setValue("start_times_file", start_times_file, (str))

    @staticmethod
    def fromDict(params, allowNone=False):
        if isinstance(params, SVReaderParams):
            params = params.__dict__
        if not isinstance(params, dict):
            raise TypeError("Expected dictionary for 'params', got {}".format(type(params)))
        cp = SVReaderParams()
        for e in params:
            if e not in SVReaderParams.field_names:
                print("SVReaderParams: Invalid field name:{}".format(e))
            cp.setValue(e, params[e], type(params[e]), allowNone)
        return cp
