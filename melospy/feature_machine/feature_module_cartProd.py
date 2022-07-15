from melospy.feature_machine.feature_module_base import MelopyFeatureModuleBase
from melospy.feature_machine.feature_module_parameter import MelopyFeatureModuleParameter


class MelopyFeatureModuleCartProd(MelopyFeatureModuleBase):
    """ cardProd module """

    def __init__(self):
        """ Initialize module """
        MelopyFeatureModuleBase.__init__(self, "cartProd")
        # define module parameters
        self.addInputParameter(MelopyFeatureModuleParameter("inputVec1", True))
        self.addInputParameter(MelopyFeatureModuleParameter("inputVec2", True))
        self.addInputParameter(MelopyFeatureModuleParameter("inputVec3", False, None))
        self.addInputParameter(MelopyFeatureModuleParameter("inputVec4", False, None))
        self.addInputParameter(MelopyFeatureModuleParameter("inputVec5", False, None))
        self.addInputParameter(MelopyFeatureModuleParameter("paddingMode", False, "front"))
        self.addInputParameter(MelopyFeatureModuleParameter("paddingValue", False, 0))
        self.addOutputParameter(MelopyFeatureModuleParameter("outputVec"))

    def process(self):
        self.checkInputParameters()

        # get input vectors
        inputVecs = []
        for i in range(5):
            inputVec = self.getParameterValue("inputVec%i" % (i+1))
            if inputVec is not None:
                # TODO check if inputVec is numpy array
                inputVecs.append(inputVec)

        paddingMode = self.getParameterValue("paddingMode")
        paddingValue = self.getParameterValue("paddingValue")

        # rearrange inputVecs
        nSegments = len(inputVecs[0])
        nVecs = len(inputVecs)
        inputVecsRearranged = []

        for i in range(nSegments):
            dummy = []
            for k in range(nVecs):
                dummy.append(inputVecs[k][i])
            inputVecsRearranged.append(dummy)

        outputVec = []
        for vecs in inputVecsRearranged:
            outputVec.append(self.processSingle(vecs, paddingMode, paddingValue))

        self.setParameterValue("outputVec", outputVec)


    def processSingle(self, inputVecs, paddingMode, paddingValue):

        # get vector lengths
        vecLen = [len(a) for a in inputVecs]
        maxLen = max(vecLen)

        # padding required?
        paddingRequired = [x < maxLen for x in vecLen]

        # initialize cartesian product as list of empty tuples
        cartProd =tuple([] for _ in range(maxLen))

        # fill up cartesian product
        for i in range(len(inputVecs)):
            for m in range(maxLen):
                if paddingRequired[i]:
                    if paddingMode == "front":
                        if m < maxLen - vecLen[i]:
                            cartProd[m].append(paddingValue)
                        else:
                            cartProd[m].append(inputVecs[i][m - maxLen + vecLen[i]])
                    elif paddingMode == "back":
                        if m < vecLen[i]:
                            cartProd[m].append(inputVecs[i][m])
                        else:
                            cartProd[m].append(paddingValue)
                        pass
                    else:
                        raise Exception("Non-valid value for padding mode !")
                else:
                    cartProd[m].append(inputVecs[i][m])

        return cartProd
