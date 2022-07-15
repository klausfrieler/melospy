""" append module """

import numpy as np

from melospy.feature_machine.feature_module_base import MelopyFeatureModuleBase
from melospy.feature_machine.feature_module_parameter import MelopyFeatureModuleParameter


class MelopyFeatureModuleAppend(MelopyFeatureModuleBase):

    def __init__(self):
        """ Initialize module """
        MelopyFeatureModuleBase.__init__(self, "append")
        self.addInputParameter(MelopyFeatureModuleParameter("inputVec", True))
        self.addInputParameter(MelopyFeatureModuleParameter("value", False, 0))
        self.addInputParameter(MelopyFeatureModuleParameter("mode", False, "value"))
        self.addOutputParameter(MelopyFeatureModuleParameter("outputVec"))

    def process(self):
        self.checkInputParameters()
        outputVec = []
        for vec in self.getParameterValue("inputVec"):
            outputVec.append(self.processSingle(vec, self.getParameterValue("mode"), self.getParameterValue("value")))
        self.setParameterValue("outputVec", outputVec)

    def processSingle(self, inputVec, mode, val):
        if mode == "value":
            vec = np.append(inputVec, val)
        elif mode == "last":
            vec = np.append(inputVec, inputVec[len(inputVec)-1])
        elif mode == "first":
            vec = np.append(inputVec, inputVec[0])
        else:
            raise Exception("Value for mode is not valid!")
        return vec
