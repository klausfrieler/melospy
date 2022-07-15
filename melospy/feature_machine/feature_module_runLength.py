""" runlength module """

import numpy as np

from melospy.feature_machine.feature_module_base import MelopyFeatureModuleBase
from melospy.feature_machine.feature_module_parameter import MelopyFeatureModuleParameter


class MelopyFeatureModuleRunLength(MelopyFeatureModuleBase):

    def __init__(self):
        """ Initialize module """
        MelopyFeatureModuleBase.__init__(self, "runLength")
        # define module parameters
        self.addInputParameter(MelopyFeatureModuleParameter("inputVec", True))
        self.addOutputParameter(MelopyFeatureModuleParameter("boolMask"))
        self.addOutputParameter(MelopyFeatureModuleParameter("segStartIdx"))
        self.addOutputParameter(MelopyFeatureModuleParameter("segLen"))
        self.addOutputParameter(MelopyFeatureModuleParameter("segVal"))

    def process(self):
        self.checkInputParameters()
        inputVec = self.getParameterValue("inputVec")

        boolMaskAll = []
        segStartIdxAll = [];
        segValAll = []
        segLenAll = []

        for vec in inputVec:
            [boolMask, segStartIdx, segVal, segLen] = self.processSingle(vec)
            boolMaskAll.append(boolMask)
            segStartIdxAll.append(segStartIdx)
            segValAll.append(segVal)
            segLenAll.append(segLen)

        self.setParameterValue("segStartIdx", segStartIdxAll)
        self.setParameterValue("segVal", segValAll)
        self.setParameterValue("segLen", segLenAll)
        self.setParameterValue("boolMask", boolMaskAll)

    def processSingle(self, inputVec):
        boolMask = np.not_equal(inputVec, np.append(inputVec[1:], inputVec[-1]+1))
        tempVec = np.append(inputVec[0]+1, inputVec)
        testVec = np.sign(np.abs(np.diff(tempVec)))
        segStartIdx = np.where(testVec == 1)[0]
        segVal = inputVec[segStartIdx]
        segLen = np.append(np.diff(segStartIdx), inputVec.size - segStartIdx[-1])
        return boolMask, segStartIdx, segVal, segLen
