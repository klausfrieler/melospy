class MelopyFeatureModuleParameter(object):
    """ Base class for Melopy module parameters """
    
    def __init__(self, label="", isMandatory=True, defaultValue=None):
        self.__value = None
        self.setLabel(label)
        self.setIsMandatory(isMandatory)
        self.setDefaultValue(defaultValue)

    def setLabel(self, val):
        if isinstance(val, str):
            self.__label = val
        else:
            raise Exception("Parameter label must be a string!")
        
    def getLabel(self):
        return self.__label

    def setValue(self, val):
        self.__value = val
    
    def getValue(self):
        return self.__value
    
    def setIsMandatory(self, val):
        self.__isMandatory = val
        
    def getIsMandatory(self):
        return self.__isMandatory
    
    def setDefaultValue(self, val):
        self.__defaultValue = val
    
    def getDefaultValue(self):
        return self.__defaultValue
        

    """ parameter label """
    label       = property(getLabel, setLabel)   
    
    """ parameter value(s) """
    value       = property(getValue, setValue)
    
    """ switch if parameter value must be set in order to call the process function of the corresponding module """
    isMandatory = property(getIsMandatory, setIsMandatory)
    
    """ default value (only necessary if parameter is not a mandatory parameter """
    defaultValue = property(getDefaultValue, setDefaultValue)
    def __str__(self):
        s = "Label:{}\nValue:{}\nMandatory:{}".format(self.__label, self.__value, self.__isMandatory)
        return s
