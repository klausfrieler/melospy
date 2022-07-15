""" indexer module """

import numpy as np

import melospy.feature_machine.test_help_functions as thf
from melospy.feature_machine.feature_module_base import MelopyFeatureModuleBase
from melospy.feature_machine.feature_module_parameter import MelopyFeatureModuleParameter


class MelopyFeatureModuleIndexer(MelopyFeatureModuleBase):

    def __init__(self):
        """ Initialize module """
        MelopyFeatureModuleBase.__init__(self, "indexer")
        # define module parameters
        self.addInputParameter(MelopyFeatureModuleParameter("inputVec", True))
        self.addOutputParameter(MelopyFeatureModuleParameter("outputVec"))

    def process(self):
        self.checkInputParameters()
        inputVec = self.getParameterValue("inputVec")
        outputVec = []

        for vec in inputVec:
            outputVec.append(self.processSingle(vec))

        self.setParameterValue("outputVec", outputVec)

    def processSingle(self, inputVec):
        return np.arange(thf.size(inputVec))
