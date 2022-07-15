""" Sink module """

import numpy as np

from melospy.feature_machine.feature_module_base import MelopyFeatureModuleBase
from melospy.feature_machine.feature_module_parameter import MelopyFeatureModuleParameter
from melospy.feature_machine.test_help_functions import isEncapsulatedSequence


class MelopyFeatureModuleSink(MelopyFeatureModuleBase):

    def __init__(self, ):
        """ Initialize module """
        MelopyFeatureModuleBase.__init__(self, "sink")
        # define module parameters
        self.addInputParameter(MelopyFeatureModuleParameter("input", True))
        self.addInputParameter(MelopyFeatureModuleParameter("aggregationMethod", False, None))
        self.addInputParameter(MelopyFeatureModuleParameter("index", False, None))
        self.addOutputParameter(MelopyFeatureModuleParameter("outputVec"))

    def process(self):
        self.checkInputParameters()
        inputList = self.getParameterValue("input")
        aggregationMethod = self.getParameterValue("aggregationMethod")

        # TODO rewrite this!!
        if isinstance(inputList, str):
            output = inputList
        elif isinstance(inputList[0], str):
            output = inputList
        elif len(inputList) == 1:
            index = self.getParameterValue("index")
            if index == "last":
                index = -1
            if index == "first":
                index = 0
            if index == None:
                output = inputList[0]
            else:
                try:
                    output = inputList[0][index]
                except IndexError:
                    output = inputList[0]
#         elif
        else:
            if isEncapsulatedSequence(inputList):
#                 print type(inputList), inputList
                raise ValueError("Aggregation not feasible for nested arrays")

            inputList = np.array(inputList)
            if aggregationMethod == "mean":
                output = np.mean(inputList)
            elif aggregationMethod == "sum":
                output = np.sum(inputList)
            elif aggregationMethod == "std":
                output = np.std(inputList)
            elif aggregationMethod == "var":
                output = np.var(inputList)
            elif aggregationMethod == None:
                output = inputList
            else:
                raise ValueError("'{}' is not implemented so far as aggregation method".format(aggregationMethod))
        self.setParameterValue("outputVec", output)
