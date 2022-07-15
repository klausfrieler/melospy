""" sort module """

import numpy as np

import melospy.feature_machine.test_help_functions as thf
from melospy.feature_machine.feature_module_base import MelopyFeatureModuleBase
from melospy.feature_machine.feature_module_parameter import MelopyFeatureModuleParameter


class MelopyFeatureModuleSort(MelopyFeatureModuleBase):

    def __init__(self):
        """ Initialize module """
        MelopyFeatureModuleBase.__init__(self, "sort")
        self.addInputParameter(MelopyFeatureModuleParameter("inputVec", True))
        self.addInputParameter(MelopyFeatureModuleParameter("descending", False, False))
        self.addOutputParameter(MelopyFeatureModuleParameter("outputVec"))

    def process(self):
        self.checkInputParameters()
        outputVec = []
        descending = self.getParameterValue("descending")
        for vec in self.getParameterValue("inputVec"):
            outputVec.append(self.processSingle(vec, descending))
        self.setParameterValue("outputVec", outputVec)

    def processSingle(self, inputVec, descending):
        try:
            return sorted(inputVec, reverse=descending)
        except TypeError:
            return np.array(sorted(inputVec, reverse=descending))
