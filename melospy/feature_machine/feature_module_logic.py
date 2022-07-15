""" logic module """

import numpy as np

import melospy.feature_machine.test_help_functions as thf
from melospy.feature_machine.feature_module_base import MelopyFeatureModuleBase
from melospy.feature_machine.feature_module_parameter import MelopyFeatureModuleParameter


class MelopyFeatureModuleLogic(MelopyFeatureModuleBase):

    def __init__(self):
        """ Initialize module """
        MelopyFeatureModuleBase.__init__(self, "logic")
        # define module parameters
        self.addInputParameter(MelopyFeatureModuleParameter("inputVec1", True))
        self.addInputParameter(MelopyFeatureModuleParameter("inputVec2", False))
        self.addInputParameter(MelopyFeatureModuleParameter("operator", False, "and"))
        self.addOutputParameter(MelopyFeatureModuleParameter("outputVec"))

    def process(self):
        self.checkInputParameters()
        inputVec1 = self.getParameterValue("inputVec1")
        inputVec2 = self.getParameterValue("inputVec2")
        operator = self.getParameterValue("operator")

        # check operator
        if operator not in ("and", "or", "xor", "not"):
            raise Exception("Value of paramter operator is not valid must be and, or, xor, or not")

        outputVec = []
        if inputVec2 is None:
            inputVec2 = [None]*len(inputVec1)

        for k in range(len(inputVec1)):
            outputVec.append(self.processSingle(inputVec1[k], inputVec2[k], operator))

        self.setParameterValue("outputVec", outputVec)


    def processSingle(self, inputVec1, inputVec2, operator):

        # convert to numpy array if necessary
        if isinstance(inputVec1, list):
                inputVec1 = np.array(inputVec1)
                inputVec2 = np.array(inputVec2)

        if operator == "not":
            # check for numeric input vectors
            if not thf.includesOnlyNumericItems(inputVec1):
                raise ValueError("Input vector must be numeric!")
            outputVec = np.logical_not(inputVec1)
        else:

            # check input vector size
            if not isinstance(inputVec1, type(inputVec2)):
                raise Exception("Both input vectors must have the same datatype")
            if inputVec1.size > 1 and inputVec2.size > 1 and inputVec1.size != inputVec2.size:
                raise Exception("If both input vectors have more than one element, they need to have the same size!")

            # check for numeric input vectors
            if not thf.includesOnlyNumericItems(inputVec1) and thf.includesOnlyNumericItems(inputVec2):
                raise ValueError("Input vectors must be numeric!")

            if operator == "and":
                outputVec = np.logical_and(inputVec1, inputVec2)
            elif operator == "or":
                outputVec = np.logical_or(inputVec1, inputVec2)
            elif operator == "xor":
                outputVec = np.logical_xor(inputVec1, inputVec2)
            elif operator == "neg":
                outputVec = np.logical_not(inputVec1, inputVec2)

        return outputVec
