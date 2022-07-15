""" Class implementation of Configuration values for Segmenter"""

from melospy.basic_representations.config_param import *
from melospy.basic_representations.jm_util import safe_set


class SegmenterParams(ConfigParameter):
    """base class for parameter settings"""
    field_names = ["method",
                   "gap_seconds",
                   "gap_factor",
                   "rhythm"
                   ]

    def __init__(self,
                 method="simple_segmenter",
                 gap_seconds=2.,
                 gap_factor=2.,
                 output_format="rhythm"):

        self.setValueWithDomainCheck("method",  method.lower(), ["simple_segmenter", "relative_simple_segmenter"])
        self.setValueWithDomainCheck("output_format",  output_format.lower(), ["rhythm", "section_list"])
        self.setValue("gap_seconds",  gap_seconds, (float))
        self.setValue("gap_factor",  gap_factor, (float))

    @staticmethod
    def fromDict(params, allowNone=False):
        if isinstance(params, SegmenterParams):
            params = params.__dict__
        if not isinstance(params, dict):
            raise TypeError("Expected dictionary for 'SegmenterParams', got {}".format(type(params)))
        cp = SegmenterParams()
        for e in params:
            if e not in SegmenterParams.field_names:
                print("SegmenterParams: Invalid field name:{}".format(e))
            cp.setValue(e, params[e], type(params[e]), allowNone)
        return cp
