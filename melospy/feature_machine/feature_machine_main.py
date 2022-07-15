import copy

import yaml

from .feature import MelopyFeature
from .feature_module_abs import MelopyFeatureModuleAbs
from .feature_module_append import MelopyFeatureModuleAppend
from .feature_module_arithmetic import MelopyFeatureModuleArithmetic
from .feature_module_cartProd import MelopyFeatureModuleCartProd
from .feature_module_connector import MelopyFeatureModuleConnector
from .feature_module_diff import MelopyFeatureModuleDiff
from .feature_module_exportMIDI import MelopyFeatureModuleExportMIDI
from .feature_module_hist import MelopyFeatureModuleHist
from .feature_module_id import MelopyFeatureModuleId
from .feature_module_indexer import MelopyFeatureModuleIndexer
from .feature_module_length import MelopyFeatureModuleLength
from .feature_module_limiter import MelopyFeatureModuleLimiter
from .feature_module_linReg import MelopyFeatureModuleLinReg
from .feature_module_localExtrema import MelopyFeatureModuleLocalExtrema
from .feature_module_logic import MelopyFeatureModuleLogic
from .feature_module_markov import MelopyFeatureModuleMarkov
from .feature_module_matrixToVector import MelopyFeatureModuleMatrixToVector
from .feature_module_mod import MelopyFeatureModuleMod
from .feature_module_ngram import MelopyFeatureModuleNGram
from .feature_module_normalizeToSumN import MelopyFeatureModuleNormalizeToSumN
from .feature_module_pattern import MelopyFeatureModulePattern
from .feature_module_runLength import MelopyFeatureModuleRunLength
from .feature_module_selector import MelopyFeatureModuleSelector
from .feature_module_self_similarity import MelopyFeatureModuleSelfSimilarity
from .feature_module_sign import MelopyFeatureModuleSign
from .feature_module_sink import MelopyFeatureModuleSink
from .feature_module_sort import MelopyFeatureModuleSort
from .feature_module_source import MelopyFeatureModuleSource
from .feature_module_stat import MelopyFeatureModuleStat
from .feature_module_sum import MelopyFeatureModuleSum
from .feature_module_threshold import MelopyFeatureModuleThreshold
from .feature_module_truncate import MelopyFeatureModuleTruncate
from .feature_module_unique import MelopyFeatureModuleUnique


class FeatureMachine():
    
    def __init__(self):
        pass
    
    def loadModulesFromYAMLFeatureFileContent(self, content):
        # get source modules
        sourceModules = []
        contentSourceModules = content['feature']['source']
        for module in list(contentSourceModules.keys()):
            sourceModule = dict()
            # set module label
            sourceModule['label'] = module
            # set other module parameters
            for p in contentSourceModules[module]:
                sourceModule[p] =  contentSourceModules[module][p]
            sourceModules.append(copy.deepcopy(sourceModule))
        
        # get process modules
        contentProcessModules = content['feature']['process']
        processModules = []
        for module in list(contentProcessModules.keys()):
            processModule = dict()
            processModule['label'] = module
            # set other module parameters
            for p in contentProcessModules[module]:
                processModule[p] =  contentProcessModules[module][p]
            processModules.append(copy.deepcopy(processModule))

        # get sink modules
        sinkModules = []
        contentSinkModules = content['feature']['sink']
        for module in list(contentSinkModules.keys()):
            sinkModule = dict()
            # set module label
            sinkModule['label'] = module
            # set other module parameters
            for p in contentSinkModules[module]:
                sinkModule[p] =  contentSinkModules[module][p]
            sinkModules.append(copy.deepcopy(sinkModule))
            
            
        return (sourceModules, processModules, sinkModules)
    
    def createProcessModuleInstance(self, moduleType):
        if moduleType == "abs":
            return MelopyFeatureModuleAbs()
        elif moduleType == "arithmetic":
            return MelopyFeatureModuleArithmetic()
        elif moduleType == "append":
            return MelopyFeatureModuleAppend()
        elif moduleType == "truncate":
            return MelopyFeatureModuleTruncate()
        elif moduleType == "diff":
            return MelopyFeatureModuleDiff()
        elif moduleType == "exportMIDI":
            return MelopyFeatureModuleExportMIDI()
        elif moduleType == "hist":
            return MelopyFeatureModuleHist()
        elif moduleType == "indexer":
            return MelopyFeatureModuleIndexer()
        elif moduleType == "localExtrema":
            return MelopyFeatureModuleLocalExtrema()
        elif moduleType == "length":
            return MelopyFeatureModuleLength()
        elif moduleType == "logic":
            return MelopyFeatureModuleLogic()
        elif moduleType == "markov":
            return MelopyFeatureModuleMarkov()
        elif moduleType == "matrixToVector":
            return MelopyFeatureModuleMatrixToVector()
        elif moduleType == "mod":
            return MelopyFeatureModuleMod()
        elif moduleType == "ngram":
            return MelopyFeatureModuleNGram()
        elif moduleType == "normalizeToSumN":
            return MelopyFeatureModuleNormalizeToSumN()
        elif moduleType == "pattern":
            return MelopyFeatureModulePattern()
        elif moduleType == "sort":
            return MelopyFeatureModuleSort()
        elif moduleType == "selector":
            return MelopyFeatureModuleSelector()
        elif moduleType == "sign":
            return MelopyFeatureModuleSign()
        elif moduleType == "selfSimilarity":
            return MelopyFeatureModuleSelfSimilarity()
        elif moduleType == "stat":
            return MelopyFeatureModuleStat()
        elif moduleType == "sum":
            return MelopyFeatureModuleSum()
        elif moduleType == "threshold":
            return MelopyFeatureModuleThreshold()
        elif moduleType == "limiter":
            return MelopyFeatureModuleLimiter()
        elif moduleType == "unique":
            return MelopyFeatureModuleUnique()
        elif moduleType == "runlength":
            return MelopyFeatureModuleRunLength()
        elif moduleType == "cartProd":
            return MelopyFeatureModuleCartProd()
        elif moduleType == "id":
            return MelopyFeatureModuleId()
        elif moduleType == "linReg":
            return MelopyFeatureModuleLinReg()
        else:   
            raise Exception("Invalid moduleType '{}' for processing module!".format(moduleType))
        
    
    def createFeatureFromYAMLFileContent(self, sourceModules, processModules, sinkModules):
        feature = MelopyFeature()
        # create source module(s)
        for module in sourceModules:
            sourceModule = MelopyFeatureModuleSource()
            sourceModule.setParameterValue("param", module["param"])
            try:
                sourceModule.setParameterValue("aggregationOver", module["aggregationOver"])
            except: 
                pass
            try:
                sourceModule.setParameterValue("optParam", module["optParam"])
            except: 
                pass
            sourceModule.setLabel(module["label"])
            feature.addModule(copy.deepcopy(sourceModule))
            # TODO do we need a deep copy here?
            del sourceModule
        
        # create process module(s)
        for module in processModules:
            processModule = self.createProcessModuleInstance(module["type"])
            processModule.setLabel(module["label"])
            # set params
            for entry in list(module.keys()):
                if entry != "type" and entry != "label" and not (isinstance(module[entry], str) and module[entry].find(".") > -1):
#                    print "SET ",entry," = ",module[entry], "(for type ",module["type"],")" 
                    processModule.setParameterValue(entry, module[entry])
                
            # TODO do we need a deep copy here?
            feature.addModule(copy.deepcopy(processModule))
            del processModule
             
        # create sink module(s)
        for module in sinkModules:
            sinkModule = MelopyFeatureModuleSink()
            # TODO replace the following by a try catch
            try:
                sinkModule.setParameterValue("aggregationMethod", module["aggregationMethod"])
            except: 
                pass
            try:
                sinkModule.setParameterValue("index", module["index"])
            except: 
                pass
            sinkModule.setParameterValue("input", module["input"])
            sinkModule.setLabel(module["label"])
            
            feature.addModule(copy.deepcopy(sinkModule))
            del sinkModule
              
        # now 
        modules = processModules + sinkModules    

        # add connector
        for module in modules:
            for entry in list(module.keys()):
                if isinstance(module[entry], str) and module[entry].find(".") > -1:
                    entrySplit = module[entry].split('.')
                    sourceModuleLabel = entrySplit[0]
                    sourceParam = entrySplit[1]
                    targetModuleLabel = module["label"]
                    targetParam = entry
#                    print " let's connect", sourceParam, " from", sourceModuleLabel, " with ", targetParam, " from", targetModuleLabel
                    connector = MelopyFeatureModuleConnector(feature.getModuleIDFromModuleLabel(sourceModuleLabel), sourceParam, \
                                                             feature.getModuleIDFromModuleLabel(targetModuleLabel), targetParam)
                    feature.addConnector(connector)
                
        return feature     
   
    def createFeatureFromYAMLFile(self, filename):
        """ Function loads FeatureMachine configuration from YAML file and creates feature with
            all selected modules & connectors """
        
        # get content from YAML
        content = yaml.load(open(filename, 'r'))

        # get list of modules from content
        #out of try
        try:
            sourceModules, processModules, sinkModules = self.loadModulesFromYAMLFeatureFileContent(content)
        except Exception as e:
            print("Exception: ", e)
             
        # create feature
        feature = self.createFeatureFromYAMLFileContent(sourceModules, processModules, sinkModules)
        
        return feature
