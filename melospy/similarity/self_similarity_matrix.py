import numpy as np

from melospy.similarity.similarity_edit_distance import SimilarityEditDistance


class SelfSimilarityMatrix:
    """ Class to compute self similarity matrix using different distance metrics """

    def __init__(self):
        pass

    def process(self,inputVec,groupingVec,distanceMetric="editDistance", threshold=None):
        if distanceMetric == "editDistance":
            numGroupIDs = len(np.unique(groupingVec))
            #we need offsset since ID not always start at zero, as in the case for
            #phrase ID's if a solo is cut in choruses
            minGroupID = np.min(groupingVec)
            selfSimMat = np.ones((numGroupIDs, numGroupIDs))
            extractor = SimilarityEditDistance()
            #print "threshold", threshold
            for i in range(numGroupIDs):
                for k in range(i+1, numGroupIDs):
                    vec1 = inputVec[np.where(groupingVec==i+minGroupID)]
                    vec2 = inputVec[np.where(groupingVec==k+minGroupID)]
                    if len(vec1) > 0 and len(vec2) > 0:
                        val = extractor.process(vec1, vec2)
                        if threshold != None:
                            val = 1.0 if val>=threshold else 0.0
                        selfSimMat[i][k] = val
                        selfSimMat[k][i] = selfSimMat[i][k]

            return selfSimMat
        else:
            raise Exception("Distance metric is not supported until now!")
