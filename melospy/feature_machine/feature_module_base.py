class MelopyFeatureModuleBase(object):
    """ Base class for Melopy Feature Machine modules """
    
    """ Global module ID count to assure unique model IDs """
    moduleIDCount = 0
    
    def __init__(self, moduleType=None):
        """ Initialize module """
        # initialize unique model ID
        self.setID()
        self.__label = None
        self.__moduleType = (moduleType if moduleType != None else "")
        
        # we start with empty parameter lists
        self.__inputParameters = [];
        self.__outputParameters = [];
        # input and output parameters need to be defined in the __init__ function in the derived module classes!
        # module type need to be defined in the __init__ function as well
        
    def process(self):
        # TODO: Implement this in the derived feature classes, this is the key functionality of the module!!!
        pass
    
    def checkInputParameters(self):
        """ Check function to be called in the beginning of the module process() functions.
            Function checks if the parameter values are set and fit to the required parameter value data type 
        """
        for param in self.__inputParameters:
            if param.value is None:
                if param.isMandatory:
                    raise Exception("Value of mandatory parameter '" + param.label + "' is not defined!")
                else:
                    param.value = param.defaultValue
    
    def getParameterValue(self, label):
        for param in self.__inputParameters:
            if param.label == label:
                return param.value
        for param in self.__outputParameters:
            if param.label == label:
                return param.value
        raise Exception("Parameter label <{}> could not be found!".format(label))    

    def setParameterValue(self, paramLabel, val):
        """ Function to set parameter values """
        for param in self.__inputParameters:
            if param.label == paramLabel:
                param.value = val
                return
        for param in self.__outputParameters:
            if param.label == paramLabel:
                param.value = val
                return
        raise Exception("Parameter label '{}' could not be found!".format(paramLabel))    

    def setID(self):
        """ Set (unique) module ID """
        self.__id = MelopyFeatureModuleBase.moduleIDCount
        # assure that internal id count always gives unique ids
        MelopyFeatureModuleBase.moduleIDCount += 1;
 
    def getID(self):
        """ Get module ID """
        return self.__id
    
    def setInputParameters(self, val):
        """ Sets input parameters, currently, this is only allowed using addInputParameters() """
        print("Input parameters can only be set within a class!")
    
    def getInputParameters(self):
        """ Returns input parameters """
        return self.__inputParameters

    def setOutputParameters(self, val):
        """ Sets output parameters, currently, this is only allowed using addOutputParameters() """
        print("Output parameters can only be set within a class!")
    
    def getOutputParameters(self):
        """ Returns output parameters """
        return self.__outputParameters

    def addInputParameter(self, param):
        """ Adds a parameter to the list of input parameters """
        self.addParameterToParameterList(param, self.__inputParameters)
        
    def addOutputParameter(self, param):
        """ Adds a parameter to the list of output parameters """
        self.addParameterToParameterList(param, self.__outputParameters)

    def addParameterToParameterList(self, par, paramList):
        """ Adds parameter to parameter list """
        # TODO check if val is instance of the right class
        # check if parameter label is set
        if len(par.label) == 0:
            raise Exception("Parameter label must not be empty!")
        # check no other input parameter has this label
        for param in paramList:
            if par.label == param.label:
                raise Exception("Parameter label " + par.label + " is already used for another input parameter!")
        paramList.append(par)
        
    def setModuleType(self, val):
        print("Module types are set in the init function and cannot be changed afterwards!")
        
    def getModuleType(self):
        return self.__moduleType
    
    def setLabel(self, val):
        self.__label = val
        
    def getLabel(self):
        return self.__label
    
    """ Module ID """            
    id          = property(getID, setID)
    
    """ Module label """            
    label          = property(getLabel, setLabel)
    
    """ Module type """
    moduleType      = property(getModuleType, setModuleType)
    
    """ Module input parameter list """
    inputParameters = property(getInputParameters, setInputParameters)
    
    """ Module output parameter list """
    outputParameters = property(getOutputParameters, setOutputParameters)
