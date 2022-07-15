""" truncate module """

import numpy as np

from melospy.feature_machine.feature_module_base import MelopyFeatureModuleBase
from melospy.feature_machine.feature_module_parameter import MelopyFeatureModuleParameter


class MelopyFeatureModuleTruncate(MelopyFeatureModuleBase):

    def __init__(self):
        """ Initialize module """
        MelopyFeatureModuleBase.__init__(self, "truncate")
        self.addInputParameter(MelopyFeatureModuleParameter("inputVec", True))
        self.addInputParameter(MelopyFeatureModuleParameter("value", True, 1))
        self.addInputParameter(MelopyFeatureModuleParameter("mode", False, "front"))
        self.addOutputParameter(MelopyFeatureModuleParameter("outputVec"))

    def process(self):
        self.checkInputParameters()
        outputVec = []
        for vec in self.getParameterValue("inputVec"):
            outputVec.append(self.processSingle(vec, self.getParameterValue("mode"), self.getParameterValue("value")))
        self.setParameterValue("outputVec", outputVec)

    def processSingle(self, inputVec, mode, val):
        if val>len(inputVec):
            val = len(inputVec)
        if mode == "back":
            vec = np.delete(inputVec, list(range(len(inputVec)-val, len(inputVec))))
        elif mode == "front":
            vec = np.delete(inputVec, list(range(0, val)))
        else:
            raise Exception("Invalid truncate mode: '{}'".format(mode))
        return vec
