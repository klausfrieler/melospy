""" Class implementation of Configuration values for Metrical Annotation"""

from melospy.basic_representations.config_param import *
from melospy.basic_representations.jm_util import safe_set


class FlexQParams(ConfigParameter):
    """base class for parameter settings"""
    field_names = ["oddDivisionPenalty",
                   "mismatchPenalty",
                   "distPenalty",
                   "spreadPenalty",
                   "optimize",
                   "rhythmThreshold",
                   "scaleFactor",
                   "tolerance",
                   "adapt_beat_track"]

    def __init__(self,
                 oddDivisionPenalty=1.,
                 mismatchPenalty=1.,
                 distPenalty=8.,
                 spreadPenalty=10.,
                 optimize=True,
                 rhythmThreshold=0.02,
                 scaleFactor=.85,
                 tolerance=.03,
                 adapt_beat_track=False):
# Alt:
#  oddDivisionPenalty: 1.2
#  mismatchPenalty: 1.1
#  distPenalty: 7.3
#  spreadPenalty: 10.2
#  optimize: True
#  rhythmThreshold: 0.05
#  scaleFactor: .8
#  tolerance: .015

        self.setValue("oddDivisionPenalty",  oddDivisionPenalty, (float))
        self.setValue("distPenalty",         distPenalty, (float))
        self.setValue("mismatchPenalty",     mismatchPenalty, (float))
        self.setValue("spreadPenalty",       spreadPenalty, (float))
        self.setValue("optimize",            optimize, bool)
        self.setValue("rhythmThreshold",     rhythmThreshold, (float))
        self.setValue("scaleFactor",         scaleFactor, (float))
        self.setValue("tolerance",           tolerance, (float))
        self.setValue("adapt_beat_track",    adapt_beat_track, bool)

    @staticmethod
    def fromDict(params, allowNone=False):
        if isinstance(params, FlexQParams):
            params = params.__dict__
        if not isinstance(params, dict):
            raise TypeError("Expected dictionary for 'FlexQParams', got {}".format(type(params)))
        cp = FlexQParams()
        for e in params:
            if e not in FlexQParams.field_names:
                print("FlexqParams: Invalid field name:{}".format(e))
            cp.setValue(e, params[e], type(params[e]), allowNone)
        return cp
