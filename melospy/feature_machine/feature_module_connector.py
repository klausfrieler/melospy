class MelopyFeatureModuleConnector(object):
    """ Base class for Melopy feature module connectors """

    """ Global module ID count to assure unique model IDs """
    connectorIDCount = 0
    
    def __init__(self,sourceModuleID=None,sourceParameterLabel=None,targetModuleID=None,targetParameterLabel=None):
        # initialize connector ID
        self.setID()

        self.setSourceModuleID(sourceModuleID)
        self.setSourceParameterLabel(sourceParameterLabel)
        self.setTargetModuleID(targetModuleID)
        self.setTargetParameterLabel(targetParameterLabel)
    
    def getSourceModuleID(self):
        return self.__sourceModuleID
    
    def setSourceModuleID(self, val):
        if isinstance(val, int):
            self.__sourceModuleID = val
        else:
            raise Exception("Source module ID must be an integer!")
    
    def getSourceParameterLabel(self):
        return self.__sourceParameterLabel
    
    def setSourceParameterLabel(self, val):
        if isinstance(val, str):
            if len(val) == 0:
                raise Exception("Source parameter label must not be empty!")
            self.__sourceParameterLabel = val
        else:
            raise Exception("Source parameter label must be given as string!")
    
    def getTargetModuleID(self):
        return self.__targetModuleID
    
    def setTargetModuleID(self, val):
        if isinstance(val, int):
            self.__targetModuleID = val
        else:
            raise Exception("Target module ID must be an integer!")
    
    def getTargetParameterLabel(self):
        return self.__targetParameterLabel
    
    def setTargetParameterLabel(self, val):
        if isinstance(val, str):
            if len(val) == 0:
                raise Exception("Target parameter label must not be empty!")
            self.__targetParameterLabel = val
        else:
            raise Exception("Target parameter label must be given as string!")
    
    def setID(self,val=[]):
        self.__id = MelopyFeatureModuleConnector.connectorIDCount
        # assure that internal id count always gives unique ids
        MelopyFeatureModuleConnector.connectorIDCount += 1;
 
    def getID(self):
        return self.__id

    """ ID of connector source module """
    sourceModuleID        = property(getSourceModuleID, setSourceModuleID)
    
    """ Label of connector source parameter """
    sourceParameterLabel  = property(getSourceParameterLabel, setSourceParameterLabel)
    
    """ ID of connector target module """
    targetModuleID        = property(getTargetModuleID, setTargetModuleID)
    
    """ Label of connector target parameter """
    targetParameterLabel  = property(getTargetParameterLabel, setTargetParameterLabel)
    
    """ ID of connector """
    id                    = property(getID, setID)
