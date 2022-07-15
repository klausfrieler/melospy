""" Class implementation of Pattern """

import numpy as np


class Pattern(object):
    
    """ valid pattern types """
    validTypes = ('pitch', 'pc')
    
    def __init__(self,patternStarts=None, patternLen = None, patternType="pitch"):
        """ Initialize module """
        if patternStarts is not None:
            self.setPatternStarts(patternStarts)
        if patternLen is not None:
            self.setPatternLengths(patternLen)
        self.setPatternType(patternType)
        
    def getPatternStarts(self):
        return self.__patternStarts
    
    def setPatternStarts(self, patternStarts):
        # TODO check for increasing values!
        self.__patternStarts = patternStarts
        
    def getPatternLengths(self):
        return self.__patternLengths
    
    def setPatternLengths(self, patternLengths):
        self.__patternLengths = patternLengths
        
    def getPatternType(self):
        return self.__patternType
    
    def setPatternType(self, patternType):
        if patternType in self.validTypes:
            self.__patternType = patternType
        else:
            raise Exception("Pattern type not valid")
        
    def getMeanPatternLength(self):
        return np.mean(self.getPatternLengths())
    
    def getMeanPatternDistance(self):
        return np.mean(np.diff(self.getPatternStarts()))
    
    def getIndicesOfFirstOccurance(self):
        indices = np.array([])
        start = self.__patternStarts[0]
        for i in range(self.__patternLengths[0]):
            indices = np.append(indices, start+i)
        return indices.astype(int)
            
#    def addAppearance(self,start,length):
#        print "start ",start    
#        np.append(self.__patternStarts,start)
##        print "AFTER ",self.__patternStarts
            
    def show(self):
        print("PATTERN")
        print("pattern lengths ", self.__patternLengths)
        print("self.__patternStarts ", self.__patternStarts)
#        for i in range(len(self.__patternLengths)):
#            for m in range(self.__patternLengths[i]):
#                print self.__patternStarts[i] + m
#        print "---"
        
    """ List of pattern start indices """
    patternStarts = property(getPatternStarts, setPatternStarts)

    """ List of pattern lengths """
    patternLengths = property(getPatternLengths, setPatternLengths)
    
    """ Pattern type """
    patternType = property(getPatternType, setPatternType)
