""" NormalizeToSumN module """

import numpy as np

from melospy.feature_machine.feature_module_base import MelopyFeatureModuleBase
from melospy.feature_machine.feature_module_parameter import MelopyFeatureModuleParameter


class MelopyFeatureModuleNormalizeToSumN(MelopyFeatureModuleBase):

    def __init__(self):
        """ Initialize module """
        MelopyFeatureModuleBase.__init__(self, "normalizeToSumN")
        # define module parameters
        self.addInputParameter(MelopyFeatureModuleParameter("inputVec", True))
        self.addInputParameter(MelopyFeatureModuleParameter("N", False, 1))
        self.addOutputParameter(MelopyFeatureModuleParameter("outputVec"))

    def process(self):
        self.checkInputParameters()
        N = np.float(self.getParameterValue("N"))
        inputVec = self.getParameterValue("inputVec")

        outputVec = []
        for vec in inputVec:
            outputVec.append(self.processSingle(vec, N))

        self.setParameterValue("outputVec", outputVec)

    def processSingle(self, inputVec, N):
        return inputVec / (inputVec.sum() / N )
