""" matrixToVector module """

import numpy as np

from melospy.feature_machine.feature_module_base import MelopyFeatureModuleBase
from melospy.feature_machine.feature_module_parameter import MelopyFeatureModuleParameter


class MelopyFeatureModuleMatrixToVector(MelopyFeatureModuleBase):

    def __init__(self):
        """ Initialize module """
        MelopyFeatureModuleBase.__init__(self, "matrixToVector")
        self.addInputParameter(MelopyFeatureModuleParameter("inputVec", True))
        self.addInputParameter(MelopyFeatureModuleParameter("mode", False, "diag"))
        self.addInputParameter(MelopyFeatureModuleParameter("diagOffset", False, 0))
        self.addInputParameter(MelopyFeatureModuleParameter("stackOrientation", False, "rows"))
        self.addOutputParameter(MelopyFeatureModuleParameter("outputVec"))

    def process(self):
        self.checkInputParameters()
        outputVec = []
        for vec in self.getParameterValue("inputVec"):
            outputVec.append(self.processSingle(vec,\
                                                self.getParameterValue("mode"),\
                                                self.getParameterValue("diagOffset"),\
                                                self.getParameterValue("stackOrientation")))
        self.setParameterValue("outputVec", outputVec)

    def processSingle(self, inputVec, mode, diagOffset, stackOrientation):
        shape = np.shape(inputVec)
        if mode == "diag":
            outputVec = np.diagonal(inputVec, diagOffset)
        elif mode == "upperTriangular":
            if shape[0] != shape[1]:
                raise Exception("Input 2D-array is not quadratic!")
            idx = np.triu_indices(shape[0], diagOffset)
            outputVec = inputVec[idx]
        elif mode == "lowerTriangular":
            if shape[0] != shape[1]:
                raise Exception("Input 2D-array is not quadratic!")
            idx = np.tril_indices(shape[0], diagOffset)
            outputVec = inputVec[idx]
        elif mode == "stackToVector":
            if stackOrientation == "rows":
                outputVec = np.reshape(inputVec, np.prod(shape))
            elif stackOrientation == "cols":
                outputVec = np.reshape(inputVec, np.prod(shape), order="F")
            else:
                raise Exception("Non-valid value for stackOrientation!")
        else:
            raise Exception("Value of mode is not valid!")
        return outputVec
