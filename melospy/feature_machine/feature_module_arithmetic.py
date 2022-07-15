""" arithmetic module """

import numpy as np

from melospy.feature_machine.feature_module_base import MelopyFeatureModuleBase
from melospy.feature_machine.feature_module_parameter import MelopyFeatureModuleParameter


def adjust_numpy_array(vec, N):
    l = vec.size
    ret = np.array([])
    if l == N:
        ret = vec
    elif l<N:
        for i in range(N):
            ret = np.append(ret, vec[i % l])
    elif l>N:
        ret = vec[0:N]
    return ret

class MelopyFeatureModuleArithmetic(MelopyFeatureModuleBase):

    def __init__(self):
        """ Initialize module """
        MelopyFeatureModuleBase.__init__(self, "arithmetic")
        self.addInputParameter(MelopyFeatureModuleParameter("inputVec1", True))
        self.addInputParameter(MelopyFeatureModuleParameter("inputVec2", False, None))
        self.addInputParameter(MelopyFeatureModuleParameter("operator", False, "+"))
        self.addInputParameter(MelopyFeatureModuleParameter("divisionByZeroResultsInZero", False, True))
        self.addOutputParameter(MelopyFeatureModuleParameter("outputVec"))

    def process(self):
        self.checkInputParameters()
        inputVec1 = self.getParameterValue("inputVec1")
        inputVec2 = self.getParameterValue("inputVec2")
        if inputVec2 == None:
            inputVec2 = inputVec1
        divisionByZeroResultsInZero = self.getParameterValue("divisionByZeroResultsInZero")
        operator = self.getParameterValue("operator")

        # if inputVec's are scalar instead of vector -> convert them to one-dimensional vectors
        try:
            dummy = len(inputVec1)
        except TypeError:
            inputVec1 = [inputVec1]

        try:
            dummy = len(inputVec2)
        except TypeError:
            inputVec2 = [inputVec2]

        outputVec = []

        for k in range(len(inputVec1)):
            outputVec.append(self.processSingle(inputVec1[k], inputVec2[k], operator, divisionByZeroResultsInZero))
        self.setParameterValue("outputVec", outputVec)

    def processSingle(self, inputVec1, inputVec2, operator, divisionByZeroResultsInZero):
        # check operator
        if operator not in ("+", "-", "/", "*", 'log'):
            raise Exception("Value of parameter operator is not valid must be +,-,/, or *!")

        # guarantee numpy.ndarrays
        if not isinstance(inputVec1, np.ndarray):
            inputVec1 = np.array(inputVec1)
        if not isinstance(inputVec2, np.ndarray):
            inputVec2 = np.array(inputVec2)
        # check input vector size
        try:
            if inputVec1.size > 1 and inputVec2.size > 1 and inputVec1.size != inputVec2.size:
                #raise Exception("If both input vectors have more than one element, they need to have the same size!")
                print(("Warning input vectors have different size {}<->{}!".format(inputVec1.size, inputVec2.size)))
                if inputVec1.size < inputVec2.size:
                    inputVec1 = adjust_numpy_array(inputVec1, inputVec2.size)
                if inputVec2.size < inputVec1.size:
                    inputVec2 = adjust_numpy_array(inputVec2, inputVec1.size)
        except:
            pass

        if operator == "+":
            outputVec = inputVec1 + inputVec2
        elif operator == "-":
            outputVec = inputVec1 - inputVec2
        elif operator == "*":
            outputVec = inputVec1 * inputVec2
        elif operator == "/":
            try:
                if divisionByZeroResultsInZero and np.float(inputVec2) == .0:
                    outputVec = 0.0
                else:
                    outputVec = np.float(inputVec1) / np.float(inputVec2)
            except TypeError:
                inputVec1 = inputVec1.astype(np.float64)
                inputVec2 = inputVec2.astype(np.float64)
                #print inputVec1/inputVec2
                outputVec = inputVec1 / inputVec2
                if divisionByZeroResultsInZero:
                    outputVec[np.isinf(outputVec)]=0.
        elif operator == 'log':
            outputVec = np.log(inputVec1+np.spacing(1))
        return outputVec
