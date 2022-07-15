""" Class implementation of Configuration values for MelodyImporterParams"""

from melospy.basic_representations.config_param import *
from melospy.basic_representations.jm_util import safe_set


class MelodyImporterParams(ConfigParameter):
    """MelodyImporterParams parameters"""
    field_names = ["use_cache", "samples", "seed"]

    def __init__(self, use_cache=True, samples=0, seed=0):
        self.setValue("samples",  samples, (int))
        self.setValue("use_cache",  use_cache, (bool))
        self.setValue("seed",  seed, (int))


    @staticmethod
    def fromDict(params, allowNone=False):
        if isinstance(params, MelodyImporterParams):
            params = params.__dict__
        if not isinstance(params, dict):
            raise TypeError("Expected dictionary for 'params', got {}".format(type(params)))
        cp = MelodyImporterParams()
        for e in params:
            if e not in MelodyImporterParams.field_names:
                print("MelodyImporterParams: Invalid field name:{}".format(e))
            cp.setValue(e, params[e], type(params[e]), allowNone)
        return cp
