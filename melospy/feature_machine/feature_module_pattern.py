""" pattern module """

import numpy as np

from melospy.feature_machine.feature_module_base import MelopyFeatureModuleBase
from melospy.feature_machine.feature_module_parameter import MelopyFeatureModuleParameter
from melospy.pattern_retrieval.pattern import Pattern
from melospy.pattern_retrieval.pattern_retrieval_via_similarity_matrix import \
    PatternRetrievalViaSimilarityMatrix


class MelopyFeatureModulePattern(MelopyFeatureModuleBase):

    def __init__(self):
        """ Initialize module """
        MelopyFeatureModuleBase.__init__(self, "pattern")
        # define module parameters
        self.addInputParameter(MelopyFeatureModuleParameter("inputVec", True))
        self.addInputParameter(MelopyFeatureModuleParameter("method", False, "similarityMatrix"))
        self.addInputParameter(MelopyFeatureModuleParameter("minPatternLength", False, 4))
        self.addOutputParameter(MelopyFeatureModuleParameter("patterns"))
        self.addOutputParameter(MelopyFeatureModuleParameter("patternSequences"))
        self.addOutputParameter(MelopyFeatureModuleParameter("meanPatternLength"))
        self.addOutputParameter(MelopyFeatureModuleParameter("meanPatternDistance"))
        self.addOutputParameter(MelopyFeatureModuleParameter("patternStart"))
        self.addOutputParameter(MelopyFeatureModuleParameter("patternEnd"))



    def process(self):
        self.checkInputParameters()
        patterns = []
        patternSequences = []
        meanPatternLength = []
        meanPatternDistance = []

        patStartIdx = []
        patEndIdx = []

        inputVec = self.getParameterValue("inputVec")
        if len(inputVec) > 1:
            raise Exception('Pattern module currently can only be used WITHOUT SEGMENTATION')

        for vec in inputVec:
            currPatterns = self.processSingle(vec, self.getParameterValue("method"), self.getParameterValue("minPatternLength"))
            patLen = np.array([])
            patDist = np.array([])
            patSeq = []
            currPatStartIdx = []
            currPatEndIdx = []
            for i in range(len(currPatterns)):
                patLen = np.append(patLen, currPatterns[i].getMeanPatternLength())
                patDist = np.append(patDist, currPatterns[i].getMeanPatternDistance())
                if type(vec) in (list, tuple):
                    currSeq = [vec[j] for j in currPatterns[i].getIndicesOfFirstOccurance()]
                else:
                    currSeq = vec[currPatterns[i].getIndicesOfFirstOccurance()]
                patSeq.append(currSeq)
                starts = list(currPatterns[i].getPatternStarts())
                ends = list(currPatterns[i].getPatternStarts()+currPatterns[i].getPatternLengths())
                currPatStartIdx.append(starts)
                currPatEndIdx.append(ends)

            patStartIdx.append(currPatStartIdx)
            patEndIdx.append(currPatEndIdx)
            patterns.append(currPatterns)
            meanPatternLength.append(np.mean(patLen))
            meanPatternDistance.append(np.mean(patDist))
            patternSequences.append(patSeq)

        self.setParameterValue("patternStart", patStartIdx)
        self.setParameterValue("patternEnd", patEndIdx)

        self.setParameterValue("meanPatternLength", meanPatternLength)
        self.setParameterValue("meanPatternDistance", meanPatternDistance)
        self.setParameterValue("patterns", patterns)
        self.setParameterValue("patternSequences", patternSequences)

#         # TODO: this results in a 2D list consisting of tuples, which right now cannot be stored by melfeature!!! this needs to be changed otherwise it will only work for no segmentation chosen
#         self.setParameterValue("patternBorders", [currPatBorders])

    def processSingle(self, inputVec, method, minPatternLength):

        # select pattern extractor
        if method == "similarityMatrix":
            extractor = PatternRetrievalViaSimilarityMatrix()
        else:
            raise Exception("No other method implemented yet")

        return extractor.process(inputVec, minPatternLength)
