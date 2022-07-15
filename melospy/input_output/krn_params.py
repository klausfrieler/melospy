""" Class implementation of Configuration values for **kern params (read)"""

from melospy.basic_representations.config_param import *
from melospy.basic_representations.jm_util import safe_set

#from melospy.basic_representations.metrical_annotation_param import FlexQParams

class KernReaderParams(ConfigParameter):
    """KernReader parameters"""
    field_names = ["diagnostic", "metadata_file", "part_no", "only_solos"]
    def __init__(self, diagnostic=False,
                 metadata_file="",
                 only_solos=False,
                 part_no=0
                 ):
        self.setValue("diagnostic",  diagnostic, (bool))
        self.setValue("metadata_file", metadata_file, (str))
        self.setValue("part_no", part_no, (int))
        self.setValue("only_solos", only_solos, (bool))

    @staticmethod
    def fromDict(params, allowNone=False):
        if isinstance(params, KernReaderParams):
            params = params.__dict__
        if not isinstance(params, dict):
            raise TypeError("Expected dictionary for 'params', got {}".format(type(params)))
        cp = KernReaderParams()
        for e in params:
            if e not in KernReaderParams.field_names:
                print("KernReaderParams: Invalid field name:{}".format(e))
            cp.setValue(e, params[e], type(params[e]), allowNone)
        return cp
