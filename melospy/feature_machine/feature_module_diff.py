import numpy as np

from melospy.feature_machine.feature_module_base import MelopyFeatureModuleBase
from melospy.feature_machine.feature_module_parameter import MelopyFeatureModuleParameter


class MelopyFeatureModuleDiff(MelopyFeatureModuleBase):
    """ Diff module """

    def __init__(self):
        """ Initialize module """
        MelopyFeatureModuleBase.__init__(self, "diff")
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
        if len(inputVec) == 1:
            return None
        else:
            return np.diff(inputVec)
