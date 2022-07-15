""" Class implementation of configuration values for LilypondWriterParams"""

from melospy.basic_representations.config_param import *
from melospy.basic_representations.jm_util import safe_set


class LilypondWriterParams(ConfigParameter):
    """LilypondWriter parameters"""
    field_names = ["transpose", 
                   "tempo", 
                   "upbeat", 
                   "idea_annotation", 
                   "phrase_annotation", 
                   "clef", 
                   "post_process", 
                   "measure_check"]

    def __init__(self, transpose=0, tempo="auto", upbeat=True, idea_annotation=None, chorus_annotation=None, phrase_annotation=None, measure_check=True, clef="auto", post_process=""):
        self.setValue("transpose",  transpose, (int))
        self.setValue("tempo",  tempo)
        self.setValue("upbeat",  upbeat)
        self.setValue("idea_annotation",  idea_annotation)
        self.setValue("phrase_annotation",  phrase_annotation)
        self.setValue("clef",  clef)
        self.setValue("post_process",  post_process)
        self.setValue("measure_check",  measure_check)

    @staticmethod
    def fromDict(params, allowNone=False):
        if isinstance(params, LilypondWriterParams):
            params = params.__dict__
        if not isinstance(params, dict):
            raise TypeError("Expected dictionary for 'params', got {}".format(type(params)))
        cp = LilypondWriterParams()
        for e in params:
            if e not in LilypondWriterParams.field_names:
                print("LilypondWriterParams: Invalid field name:{}".format(e))
                #raise RuntimeError("LilypondWriterParams: Invalid field name:{}".format(e))
            cp.setValue(e, params[e], type(params[e]), allowNone)
        return cp
