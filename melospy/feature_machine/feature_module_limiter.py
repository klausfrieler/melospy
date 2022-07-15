""" thresholder module """

import numpy as np

from melospy.feature_machine.feature_module_base import MelopyFeatureModuleBase
from melospy.feature_machine.feature_module_parameter import MelopyFeatureModuleParameter


class MelopyFeatureModuleLimiter(MelopyFeatureModuleBase):

    def __init__(self):
        """ Initialize module """
        MelopyFeatureModuleBase.__init__(self, "limiter")
        # define module parameters
        self.addInputParameter(MelopyFeatureModuleParameter("inputVec", True))
        self.addInputParameter(MelopyFeatureModuleParameter("max", False, None))
        self.addInputParameter(MelopyFeatureModuleParameter("min", False, None))
        self.addOutputParameter(MelopyFeatureModuleParameter("outputVec"))

    def process(self):
        inputVec = self.getParameterValue("inputVec")
        max_val = self.getParameterValue("max")
        min_val = self.getParameterValue("min")

        outputVec = []
        for vec in inputVec:
            outputVec.append(self.processSingle(vec, min_val, max_val))
        self.setParameterValue("outputVec", outputVec)

    def processSingle(self, inputVec, min_val, max_val):

        # check operator
        #if operator not in ("eq","ne","gt","ge", "lt", "le"):
        #    raise Exception("Value of parameter operator is not valid must be one of (e,ne,g,ge,l,le)")
        outputVec = inputVec
        for  i in range(len(inputVec)):
            if max_val is not None and outputVec[i]>=max_val:
                outputVec[i] = max_val
            if min_val is not None and outputVec[i]<=min_val:
                outputVec[i] = min_val


        return outputVec.astype(np.float64)
