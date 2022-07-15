""" similarity module """
import sys

import numpy as np

from melospy.basic_representations.jm_util import simmat2form
from melospy.feature_machine.feature_module_base import MelopyFeatureModuleBase
from melospy.feature_machine.feature_module_parameter import MelopyFeatureModuleParameter
from melospy.similarity.self_similarity_matrix import SelfSimilarityMatrix


class MelopyFeatureModuleSelfSimilarity(MelopyFeatureModuleBase):

    def __init__(self):
        """ Initialize module """
        MelopyFeatureModuleBase.__init__(self, "selfSimilarity")
        # define module parameters
        self.addInputParameter(MelopyFeatureModuleParameter("inputVec", True))
        self.addInputParameter(MelopyFeatureModuleParameter("groupingVec", True))
        self.addInputParameter(MelopyFeatureModuleParameter("outputType", False, "ssm"))
        self.addInputParameter(MelopyFeatureModuleParameter("threshold", False, 0))
        self.addInputParameter(MelopyFeatureModuleParameter("id-thresh", False, "0.8"))
        self.addInputParameter(MelopyFeatureModuleParameter("var-thresh", False, "0.6"))
        self.addOutputParameter(MelopyFeatureModuleParameter("selfSimilarityMatrix"))

    def process(self):
        self.checkInputParameters()
        inputVec = self.getParameterValue("inputVec")
        groupingVec = self.getParameterValue("groupingVec")
        #print groupingVec
        outputType  = self.getParameterValue("outputType")
        thresh = self.getParameterValue("threshold")
        thresh1 = self.getParameterValue("id-thresh")
        thresh2 = self.getParameterValue("var-thresh")
        ssm = []
        if thresh <=0 or outputType == "form":
            thresh = None
        for i in range(len(inputVec)):
            currSSM = self.processSingle(inputVec[i], groupingVec[i], thresh)
            if outputType == "form":
                form = simmat2form(currSSM, thresh1, thresh2)
                ssm.append(form)
            else:
                ssm.append(currSSM)
        #print ssm
        self.setParameterValue("selfSimilarityMatrix", ssm)

    def processSingle(self, inputVec, groupVec, threshold):

        # select pattern extractor
        extractor = SelfSimilarityMatrix()
        return extractor.process(inputVec, groupVec, threshold=threshold)
