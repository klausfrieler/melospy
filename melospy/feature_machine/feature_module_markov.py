import numpy as np

import melospy.feature_machine.test_help_functions as thf
from melospy.feature_machine.feature_module_base import MelopyFeatureModuleBase
from melospy.feature_machine.feature_module_parameter import MelopyFeatureModuleParameter


class MelopyFeatureModuleMarkov(MelopyFeatureModuleBase):
    """ Markov module that computes the transition matrix of a Markov chain based on some observations """

    def __init__(self):
        """ Initialize module """
        MelopyFeatureModuleBase.__init__(self, "markov")

        # define module parameters
        self.addInputParameter(MelopyFeatureModuleParameter("inputVec", True))
        self.addInputParameter(MelopyFeatureModuleParameter("bins", True))

        # define output parameters
        self.addOutputParameter(MelopyFeatureModuleParameter("transitionMatrix"))


    def process(self):
        self.checkInputParameters()
        inputVec = self.getParameterValue("inputVec")
        bins = self.getParameterValue("bins")
        transMat = []

        for k in range(len(inputVec)):
            transMat.append(self.processSingle(inputVec[k], bins[k]))

        self.setParameterValue("transitionMatrix", transMat)

    def processSingle(self, inputVec, bins):
        # initialize transition matrix
        N = len(bins)
        transMat = np.zeros((N, N))

        # convert input vector to bin indices
        inputVecAsBinIndices = [np.where(bins==el)[0][0] for el in inputVec]

        # count adjacent bin index pairs in transition matrix
        for i in range(len(inputVecAsBinIndices)-1):
            transMat[inputVecAsBinIndices[i], inputVecAsBinIndices[i+1]] += 1

        # normalize
        for i in range(transMat.ndim):
            su = np.sum(transMat[i])
            if su > 0.:
                transMat[i] /= su

        return transMat
