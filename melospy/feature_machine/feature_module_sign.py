""" sign module """

import numpy as np

from melospy.feature_machine.feature_module_base import MelopyFeatureModuleBase
from melospy.feature_machine.feature_module_parameter import MelopyFeatureModuleParameter


class MelopyFeatureModuleSign(MelopyFeatureModuleBase):

    def __init__(self):
        """ Initialize module """
        MelopyFeatureModuleBase.__init__(self, "sign")
        # define module parameters
        self.addInputParameter(MelopyFeatureModuleParameter("inputVec", True))
        self.addOutputParameter(MelopyFeatureModuleParameter("outputVec"))

    def process(self):
        self.checkInputParameters()
        outputVec = []
        inputVec = self.getParameterValue("inputVec")
        for vec in inputVec:
            outputVec.append(self.processSingle(vec))
        self.setParameterValue("outputVec", outputVec)

    def processSingle(self, inputVec):
        return np.sign(inputVec)
