""" thresholder module """

import numpy as np

from melospy.feature_machine.feature_module_base import MelopyFeatureModuleBase
from melospy.feature_machine.feature_module_parameter import MelopyFeatureModuleParameter


class MelopyFeatureModuleThreshold(MelopyFeatureModuleBase):

    def __init__(self):
        """ Initialize module """
        MelopyFeatureModuleBase.__init__(self, "thresholder")
        # define module parameters
        self.addInputParameter(MelopyFeatureModuleParameter("inputVec", True))
        self.addInputParameter(MelopyFeatureModuleParameter("threshold", False, 0))
        self.addInputParameter(MelopyFeatureModuleParameter("operator", False, "ge"))
        self.addOutputParameter(MelopyFeatureModuleParameter("outputVec"))

    def process(self):
        inputVec = self.getParameterValue("inputVec")
        threshold = self.getParameterValue("threshold")
        operator = self.getParameterValue("operator")

        outputVec = []
        for vec in inputVec:
            outputVec.append(self.processSingle(vec, threshold, operator))
        self.setParameterValue("outputVec", outputVec)

    def processSingle(self, inputVec, threshold, operator):

        # check operator
        if operator not in ("eq", "ne", "gt", "ge", "lt", "le"):
            raise Exception("Value of parameter operator is not valid must be one of (e,ne,g,ge,l,le)")
        if operator == "eq":
            outputVec = inputVec == threshold
        elif operator == "ne":
            outputVec = inputVec != threshold
        elif operator == "gt":
            outputVec = inputVec > threshold
        elif operator == "ge":
            outputVec = inputVec >= threshold
        elif operator == "lt":
            outputVec = inputVec < threshold
        elif operator == "le":
            outputVec = inputVec <= threshold
        return outputVec.astype(np.float64)
