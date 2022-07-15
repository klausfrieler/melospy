""" localExtrema module """

import numpy as np

import melospy.feature_machine.test_help_functions as thf
from melospy.feature_machine.feature_module_base import MelopyFeatureModuleBase
from melospy.feature_machine.feature_module_parameter import MelopyFeatureModuleParameter


class MelopyFeatureModuleLocalExtrema(MelopyFeatureModuleBase):

    def __init__(self):
        """ Initialize module """
        MelopyFeatureModuleBase.__init__(self, "localExtrema")
        # define module parameters
        self.addInputParameter(MelopyFeatureModuleParameter("inputVec", True))
        self.addInputParameter(MelopyFeatureModuleParameter("mode", False, "max"))
        self.addOutputParameter(MelopyFeatureModuleParameter("outputVec"))

    def process(self):
        self.checkInputParameters()
        inputVec = self.getParameterValue("inputVec")
        mode = self.getParameterValue("mode")

        outputVec = []
        for vec in inputVec:
            outputVec.append(self.processSingle(vec, mode))

        self.setParameterValue("outputVec", outputVec)


    def processSingle(self, inputVec, mode):
        L = thf.size(inputVec)
        if L == 0:
            raise ValueError("Empty input vector!")
        elif L == 1:
            outputVec = np.array([True])
        else:
            shift2LeftVec = np.concatenate((inputVec[1:], np.array([inputVec[inputVec.size-1]])))
            shift2RightVec = np.concatenate((np.array([inputVec[0]]), inputVec[:inputVec.size-1]))
            if mode == "max-eq":
                outputVec = np.logical_and(np.greater_equal(inputVec, shift2LeftVec), np.greater_equal(inputVec, shift2RightVec))
            elif mode == "min-eq":
                outputVec = np.logical_and(np.less_equal(inputVec, shift2LeftVec), np.less_equal(inputVec, shift2RightVec))
            elif mode == "max":
                outputVec = np.logical_and(np.greater(inputVec, shift2LeftVec), np.greater(inputVec, shift2RightVec))
            elif mode == "min":
                outputVec = np.logical_and(np.less(inputVec, shift2LeftVec), np.less(inputVec, shift2RightVec))
            else:
                raise ValueError("Non-valid value for parameter mode!")
        return outputVec
