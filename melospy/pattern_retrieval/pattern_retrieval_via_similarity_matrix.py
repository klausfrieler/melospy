'''
Created on 10.05.2013

@author: Jakob
'''
import numpy as np

import melospy.feature_machine.test_help_functions as thf
from melospy.pattern_retrieval.pattern import Pattern


class PatternRetrievalViaSimilarityMatrix(object):
    '''
    Class for repeating pattern retrieval via similarity matrix
    '''
    def __init__(self):
        pass

    def process(self, inputVec, minPatternLen=4, patternType='pitch'):
        """ Function detects patterns by analyzing the self-similarity matrix and tracking diagonal tracks of zero-distsance """

        # convert input into numeric vector using codebook
        inputVecNumeric, codebook = self.convert_vector_to_codebook_indices(inputVec)

        # compute binary similarity matrix
        L = len(inputVecNumeric)
        m = np.tile(inputVecNumeric, (L, 1))

        simMat = np.abs(m-m.transpose())==0

        # find diagonal tracks in similarity matrix that at least are minPatternLen elements long
        startCoordinates = self.trace_diagonal_tracks(simMat, minPatternLen)

        # remove entries on main and above the main diagonal (redundant information)
        idx2Delete = np.where(startCoordinates[0]<=startCoordinates[1])
        x = np.delete(startCoordinates[0], idx2Delete)
        y = np.delete(startCoordinates[1], idx2Delete)

        # now track all potential patterns in their "full length"
        pairPatterns = []
        count1 = 0
        while count1 < len(x):
            trackEndFound = False
            x0 = x[count1]
            y0 = y[count1]
            # start tracking in diagonal direction
            for offset in range(L-x0):
                # remove other pattern candidates which are only sub-patterns
                idxDel = np.nonzero(np.logical_and(x==x0+offset, y==y0+offset))[0]
                x = np.delete(x, idxDel)
                y = np.delete(y, idxDel)
                # pattern tracking finished?
                if simMat[x0+offset, y0+offset] == False:
                    x1 = x0 + offset - 1
                    y1 = y0 + offset - 1
                    trackEndFound = True
                    break;
            # define pattern end if last note was reached
            if trackEndFound == False:
                x1 = x0 + offset
                y1 = y0 + offset
            # store pattern into final list (but flip the order of appearance)
            pairPatterns.append([y0, y1, x0, x1])
            count1 += 1

        patterns = [];

        # convert results into Pattern instances and return pattern list
        for i in range(len(pairPatterns)):
            p = Pattern(np.array([pairPatterns[i][0], pairPatterns[i][2]]), \
                        np.array([pairPatterns[i][1]-pairPatterns[i][0]+1, pairPatterns[i][3]-pairPatterns[i][2]+1]), patternType)
            patterns.append(p)

        # merge patterns with 2 appearances to list of patterns with arbitrary number of appearances
        patterns = self.combine_pattern_pairs_to_pattern_lists(patterns)

        return patterns


    def convert_vector_to_codebook_indices(self, inputVec):
        """ converts arbitrary input vector into numeric vector by
            - generating a codebook of all unique elements of the input vector
            - replacing the input vector elements by codebook indices """
        if thf.isEncapsulatedSequence(inputVec):
            codebook = [];
            inputVecNumeric = [];
            for i in range(len(inputVec)):
                try:
                    idx = codebook.index(inputVec[i])
                    inputVecNumeric.append(idx)
                except (ValueError):
                    codebook.append(inputVec[i])
                    inputVecNumeric.append(len(codebook)-1)
        else:
            #"TODO: now we assume a numpy array here, implement check for list of characters!!!"
            inputVecNumeric = inputVec
            codebook = np.unique(inputVecNumeric).tolist()

        return inputVecNumeric, codebook

    def combine_pattern_pairs_to_pattern_lists(self, patternPairs):
        """ Combines patterns with 2 appearances ("pattern pairs") to list of patterns
            with arbitrary number of appearances """
        patternList = []
        # step through all pattern pairs
        for patternPair in patternPairs:
            patternPairApperanceFoundInPatternList = False
            # check all patterns in the pattern list
            if len(patternList) == 0:
                patternList.append(patternPair)
            else:
                for p in range(len(patternList)):
                    if not patternPairApperanceFoundInPatternList:
                        if self.pattern_pair_appearance_found_in_pattern(patternPair, patternList[p]):
                            self.add_all_pattern_pair_appearances_into_pattern(patternPair, patternList[p])
                            patternPairApperanceFoundInPatternList = True
                if not patternPairApperanceFoundInPatternList:
                    patternList.append(patternPair)

        # finally check through pattern list for redundant patterns (patterns that are "included" in other patterns)
        patternList = self.check_for_redundant_patterns(patternList)

        return patternList

    def pattern_pair_appearance_found_in_pattern(self, patternPair, pattern):
        """ Checks if at least one appearance of a pattern is include in another pattern """
        for i in range(len(patternPair.patternStarts)):
            for m in range(len(pattern.patternStarts)):
                if patternPair.patternStarts[i] == pattern.patternStarts[m] and \
                   patternPair.patternLengths[i] == pattern.patternLengths[i]:
                    return True
        return False

    def add_all_pattern_pair_appearances_into_pattern(self, patternPair, pattern):
        """ Merges appearances of an existing pattern with all appearances in another pattern """
        for k in range(len(patternPair.patternStarts)):
            if not patternPair.patternStarts[k] in pattern.patternStarts:
                pattern.patternStarts = np.append(pattern.patternStarts, patternPair.patternStarts[k])
                pattern.patternLengths = np.append(pattern.patternLengths, patternPair.patternLengths[k])

    def check_for_redundant_patterns(self, patternList):
        """ Checks all pairs in a pattern list if some of the patterns are redundant (i.e. contained in different patterns) """
        N = len(patternList)
        elements2delete = []
        for k in range(N):
            for m in range(N):
                if k != m:
                    if self.pattern_contains_pattern_as_subpattern(patternList[k], patternList[m]):
                        elements2delete.append(m)
        
        if len(patternList) > 0 and len(elements2delete) > 0:
            patternList = np.delete(patternList, elements2delete)
            
        return patternList

    def pattern_contains_pattern_as_subpattern(self, p1, p2):
        """ Checks if pattern p1 contains p2 as subpattern """
        allPatternAppearancesIncludedInOtherPattern = True
        for p in range(len(p2.patternStarts)):
            patternApperanceIncludedInOtherPattern = False
            for m in range(len(p1.patternStarts)):
                start1 = p1.patternStarts[m]
                end1 = p1.patternStarts[m] + p1.patternLengths[m]
                start2 = p2.patternStarts[p]
                end2 = p2.patternStarts[p] + p2.patternLengths[p]
                if start2 >= start1 and end2 <= end1:
                    patternApperanceIncludedInOtherPattern = True
            allPatternAppearancesIncludedInOtherPattern = allPatternAppearancesIncludedInOtherPattern and patternApperanceIncludedInOtherPattern
        return allPatternAppearancesIncludedInOtherPattern

    def trace_diagonal_tracks(self, simMat, minPatternLen):
        """ Function tracks diagonal paths in a squared boolean matrix simMat
            with adjacent true values and a minimum length of minPatternLen.
            Function returns start coordinates of found tracks in the given matrix. """

        numNotes = simMat.shape[0]
        N2 = numNotes+minPatternLen

        checkMat = simMat.copy()

        tempMat = np.zeros((N2, N2))==1
        tempMat[0:numNotes, 0:numNotes] = simMat

        # iteratively apply AND operation between simMat and diagonal shifted version of simMat
        for k in range(minPatternLen):
            checkMat = np.logical_and(checkMat, tempMat[k:k+numNotes, k:k+numNotes])

        return np.where(checkMat)
