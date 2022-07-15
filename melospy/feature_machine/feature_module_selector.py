""" selector module """

import numpy as np

from melospy.feature_machine.feature_module_base import MelopyFeatureModuleBase
from melospy.feature_machine.feature_module_parameter import MelopyFeatureModuleParameter


class MelopyFeatureModuleSelector(MelopyFeatureModuleBase):

    def __init__(self):
        """ Initialize module """
        MelopyFeatureModuleBase.__init__(self, "selector")
        # define module parameters
        self.addInputParameter(MelopyFeatureModuleParameter("inputVec", True))
        self.addInputParameter(MelopyFeatureModuleParameter("selectVec", True))
        self.addInputParameter(MelopyFeatureModuleParameter("boolMask", False, True))
        self.addOutputParameter(MelopyFeatureModuleParameter("outputVec"))

    def process(self):
        self.checkInputParameters()
        inputVec = self.getParameterValue("inputVec")
        selectVec = self.getParameterValue("selectVec")
        boolMask = self.getParameterValue("boolMask")
        outputVec = []

        for k in range(len(inputVec)):
            try:
                outputVec.append(self.processSingle(inputVec[k], selectVec[k], boolMask))
            except:
                outputVec.append([])
        self.setParameterValue("outputVec", outputVec)

    def processSingle(self, inputVec, selectVec, boolMask):
        # in this case: item indices are given
        if not boolMask:
            return inputVec[selectVec]
        # in this case: we have a boolean mask for item selection
        if len(inputVec) > 1 and len(selectVec) > 1 and len(inputVec) != len(selectVec):
            raise Exception("Vector lengths do not match!")
        if len(selectVec) == 1:
            return inputVec[selectVec[0]]
        else:
            return inputVec[selectVec.nonzero()[0]]
