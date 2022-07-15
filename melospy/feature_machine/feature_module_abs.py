""" abs module """

import numpy as np

from melospy.feature_machine.feature_module_base import MelopyFeatureModuleBase
from melospy.feature_machine.feature_module_parameter import MelopyFeatureModuleParameter


class MelopyFeatureModuleAbs(MelopyFeatureModuleBase):

    def __init__(self):
        """ Initialize module """
        MelopyFeatureModuleBase.__init__(self, "abs")
        self.addInputParameter(MelopyFeatureModuleParameter("inputVec", True))
        self.addOutputParameter(MelopyFeatureModuleParameter("outputVec"))

    def process(self):
        self.checkInputParameters()
        outputVec = []
        for vec in self.getParameterValue("inputVec"):
            outputVec.append(self.processSingle(vec))
        self.setParameterValue("outputVec", outputVec)

    def processSingle(self, inputVec):
        return np.abs(inputVec)
