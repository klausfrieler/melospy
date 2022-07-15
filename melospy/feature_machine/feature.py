class MelopyFeature(object):
    """ Base class for Melopy features """
        
    def __init__(self, label=None, description=None):
        """ Init function """
        self.__label        = (label if label!=None else "")
        self.__description  = (description if description!=None else "")
        self.__modules      = []
        self.__connectors   = []
        
    def addModule(self, module):
        """ Adds a single module to the list of feature modules """
        # ensure that module label is unique
        for existingModule in self.__modules:
            if existingModule.getLabel() == module.getLabel():
                raise Exception("Module label " + str(module.getLabel()) +" occurs at least twice in the feature configuration file, please use unique module labels!")
        self.__modules.append(module)
        
    def addConnector(self, connector):
        """ Adds a single connector (between an output parameter of one module and an input parameter of a different module)
            to the list of connectors """
        # check if source and target module & parameter exist
        sourceFound = False
        targetFound = False
        for module in self.__modules:
            if module.id == connector.sourceModuleID:
                for param in module.outputParameters:
                    if connector.sourceParameterLabel == param.label:
                        sourceFound = True
            if module.id == connector.targetModuleID:
                #print " we look for ", connector.targetParameterLabel
                for param in module.inputParameters:
                    #print "we have ", param.label
                    if connector.targetParameterLabel == param.label:
                        targetFound = True
        if not sourceFound:
            raise Exception("Source parameter with label <" + connector.sourceParameterLabel + "> of connector could not be located!")
        if not targetFound:
            raise Exception("Target parameter with label <" + connector.targetParameterLabel + "> of connector could not be located!")
        
        self.__connectors.append(connector)
        
    def computeProcessModuleProcessingOrder(self):
        """ Determines the processing order of the feature module based on the connectors between them,
            Function will also throw an exception if a loop was created using the connectors (which will not be valid)"""
        processingOrder = []

        # create list of module IDs (same order as in self.__modules)
        moduleIDs = []
        for module in self.__modules:
            moduleIDs.append(module.id)
        
        # go through connectors and create list of modules to which each module is connected to
        moduleDependsOnModules = [list([]) for _ in range(len(self.__modules))]
        for connector in self.__connectors:
            # find target module index
            targetModuleIdx = moduleIDs.index(connector.targetModuleID)
            # add connector source module to the list of module dependencies
            moduleDependsOnModules[targetModuleIdx].append(moduleIDs.index(connector.sourceModuleID))   
        
        # check for circular dependencies and throw exception in that case
        for i in range(len(moduleDependsOnModules)):
            for k in moduleDependsOnModules[i]:
                if i in moduleDependsOnModules[k] and k in moduleDependsOnModules[i]:
                    raise Exception("Circular dependencies between modules ({} <-> {}) are not allowed!".format(self.__modules[i].getLabel(), self.__modules[k].getLabel()))
        
        # TODO Is this value for the maximum number of iterations always sufficient?
        maxNumIter = len(self.__modules)
        
        # determine processing order 
        for it in range(maxNumIter):
            # step through all modules
            for count in range(len(moduleDependsOnModules)):
                # only check module if it is not already in the processingOrder list
                if not count in processingOrder:
                    if len(moduleDependsOnModules[count]) == 0:
                        processingOrder.append(count)
                    else:
                        allDependenciesResolved = True
                        # check for all modules that this module depends on if they are ALL in the processingOrder list
                        for module in moduleDependsOnModules[count]:
                            if not module in processingOrder:
                                allDependenciesResolved = False
                        # only add current module if all dependencies are resolved
                        if allDependenciesResolved:
                            processingOrder.append(count)
            # if we have the processing order for all modules, we're done
            if len(processingOrder) == len(self.__modules):
                break
        
        return processingOrder

    def getModules(self):
        """ Returns list of modules """
        return self.__modules
    
    def getConnectors(self):
        """ Returns list of connectors """
        return self.__connectors
        
    def process(self, exporter):
        
        # step through process modules in correct order
        for idx in self.computeProcessModuleProcessingOrder():
            # case 1) source module
            if self.__modules[idx].moduleType == "source":
                self.__modules[idx].process(exporter)
            # case 2) sink module
            elif self.__modules[idx].moduleType == "sink":
                self.__modules[idx].process()
            # case 3) process module
            else:
                # check input parameters
                for param in self.__modules[idx].inputParameters:
                    if param.value == None:
                        # mandatory parameter must have been set before!
                        if param.isMandatory:
                            raise Exception("Mandatory parameter with label <" + str(param.label) + "> of module with ID = " + str(self.__modules[idx].id) + " is not set!")
                        # non-mandatory parameters can be set, if they are not set -> default values are used
                        else:
                            param.value = param.defaultValue
                # call module process()
                self.__modules[idx].process()
            
            # transfer output values of current module to input values of connected module
            for connector in self.__connectors:
                if connector.sourceModuleID == self.__modules[idx].id:
                    for module in self.__modules:
                        if module.id == connector.targetModuleID:
                            module.setParameterValue(connector.targetParameterLabel, self.__modules[idx].getParameterValue(connector.sourceParameterLabel))
                
        pass

    def getSinkModuleValues(self):
        sinkModuleValues = {}
        for module in self.__modules:
            if module.moduleType == "sink":
                sinkModuleValues[module.label] = module.getParameterValue("outputVec")
        return sinkModuleValues

    def setLabel(self, val):
        self.__label = val
    
    def getLabel(self):
        return self.__label
    
    def setDescription(self, val):
        self.__description = val
        
    def getDescription(self):
        return self.__description

    def getSourceModules(self):
        """ returns source modules """
        sourceModules = []
        for module in self.__modules:
            if module.type == 'source':
                sourceModules.append(module)
        return sourceModules
    
    def getProcessModules(self):
        """ returns process modules """
        processModules = []
        for module in self.__modules:
            if module.type != 'source' and module.type != 'sink':
                processModules.append(module)
        return processModules
    
    def getSinkModules(self):
        """ returns sink modules """
        sinkModules = []
        for module in self.__modules:
            if module.type == 'sink':
                sinkModules.append(module)
        return sinkModules
    
    def getModuleIDFromModuleLabel(self, label):
        """ seeks module with given ID and returns label """
        for module in self.__modules:
            if module.label == label:
                return module.id
        raise RuntimeError("Module with label <{}> not found.".format(label))
    
    """ list of modules """
    modules = property(getModules)
    
    """ list of all connectors """
    connectors = property(getConnectors)   
    
    """ label """
    label = property(getLabel, setLabel)
    
    """ description """
    description = property(getDescription, setDescription)
