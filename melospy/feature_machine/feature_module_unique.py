""" unique module """

import numpy as np

import melospy.feature_machine.test_help_functions as thf
from melospy.feature_machine.feature_module_base import MelopyFeatureModuleBase
from melospy.feature_machine.feature_module_parameter import MelopyFeatureModuleParameter


class MelopyFeatureModuleUnique(MelopyFeatureModuleBase):

    def __init__(self):
        """ Initialize module """
        MelopyFeatureModuleBase.__init__(self, "unique")
        self.addInputParameter(MelopyFeatureModuleParameter("inputVec", True))
        self.addOutputParameter(MelopyFeatureModuleParameter("outputVec"))

    def process(self):
        self.checkInputParameters()
        outputVec = []
        for vec in self.getParameterValue("inputVec"):
            outputVec.append(self.processSingle(vec))
        self.setParameterValue("outputVec", outputVec)

    def processSingle(self, inputVec):
        if len(inputVec) == 0:
            return []
        elif len(inputVec) == 1:
            return inputVec
        else:
            if thf.includesOnlyNumericItems(inputVec):
                return np.unique(inputVec)
            else:
                return thf.unique(inputVec)
