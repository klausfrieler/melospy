""" mod module """

import numpy as np

from melospy.feature_machine.feature_module_base import MelopyFeatureModuleBase
from melospy.feature_machine.feature_module_parameter import MelopyFeatureModuleParameter


class MelopyFeatureModuleMod(MelopyFeatureModuleBase):

    def __init__(self):
        """ Initialize module """
        MelopyFeatureModuleBase.__init__(self, "mod")
        # define module parameters
        self.addInputParameter(MelopyFeatureModuleParameter("inputVec", True))
        self.addInputParameter(MelopyFeatureModuleParameter("N", False, 1))
        self.addInputParameter(MelopyFeatureModuleParameter("wrap", False, True))
        self.addInputParameter(MelopyFeatureModuleParameter("circDist", False, False))
        self.addOutputParameter(MelopyFeatureModuleParameter("outputVec"))

    def process(self):
        self.checkInputParameters()
        # get input parameters and convert to float
        inputVec = self.getParameterValue("inputVec")
        outputVec = []

        for vec in inputVec:
            outputVec.append(self.processSingle(vec))

        self.setParameterValue("outputVec", outputVec)

    def processSingle(self, inputVec):
        if inputVec.dtype == int:
            inputVec = inputVec.astype(np.float64)

        N = np.float(self.getParameterValue("N"))
        if self.getParameterValue("circDist"):
            val = np.arccos(np.cos(2*np.pi/N*np.abs(inputVec)))/np.pi*N*.5
        # compute output parameter
        else:
            val = np.fmod(inputVec, N)
            if self.getParameterValue("wrap"):
                val = np.fmod(inputVec+N, N)
        return np.round(val)
