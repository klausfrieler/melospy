""" ngram module """

from melospy.feature_machine.feature_module_base import MelopyFeatureModuleBase
from melospy.feature_machine.feature_module_parameter import MelopyFeatureModuleParameter


class MelopyFeatureModuleNGram(MelopyFeatureModuleBase):

    def __init__(self):
        """ Initialize module """
        MelopyFeatureModuleBase.__init__(self, "ngram")
        # define module parameters
        self.addInputParameter(MelopyFeatureModuleParameter("inputVec", True))
        self.addInputParameter(MelopyFeatureModuleParameter("N", True))
        self.addOutputParameter(MelopyFeatureModuleParameter("outputVec"))

    def process(self):
        self.checkInputParameters()
        # get input parameters and convert to float
        inputVec = self.getParameterValue("inputVec")
        N = self.getParameterValue("N")
        ngrams = []

        for vec in inputVec:
            ngrams.append(self.processSingle(vec, N))

        self.setParameterValue("outputVec", ngrams)

    def processSingle(self, inputVec, N):

        ngrams = []

        # check for empty vector / list
        L = len(inputVec)
        if not L:
            return []
            #raise ValueError("Cannot compute n-grams from empty input vector / list")

        # check for valid N
        if N > L:
            return []
            #raise ValueError("Cannot compute n-grams since N > vector / list length")

        # compute n-grams
        for k in range(L-(N-1)):
            ngrams.append(inputVec[k:k+N])

        return ngrams
