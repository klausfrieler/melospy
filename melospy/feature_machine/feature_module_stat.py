""" stat module """

import itertools

import numpy as np

from melospy.basic_representations.jm_stats import *
from melospy.feature_machine.feature_module_base import MelopyFeatureModuleBase
from melospy.feature_machine.feature_module_parameter import MelopyFeatureModuleParameter


class MelopyFeatureModuleStat(MelopyFeatureModuleBase):

    def __init__(self):
        """ Initialize module """
        MelopyFeatureModuleBase.__init__(self, "stat")
        # define module parameters
        self.addInputParameter(MelopyFeatureModuleParameter("inputVec", True))
        self.addInputParameter(MelopyFeatureModuleParameter("measure", False, "mean"))
        self.addInputParameter(MelopyFeatureModuleParameter("circ_max", False, None))
        self.addInputParameter(MelopyFeatureModuleParameter("normalizeToDensity", False, True))
        self.addInputParameter(MelopyFeatureModuleParameter("numberClasses", False, None))
        self.addInputParameter(MelopyFeatureModuleParameter("normalizeEntropy", False, False))
        self.addOutputParameter(MelopyFeatureModuleParameter("outputVec"))

    def process(self):
        self.checkInputParameters()
        inputVec = self.getParameterValue("inputVec")
        measure = self.getParameterValue("measure")

        if measure not in ("mean", "median", "mode", "std", "var", "entropy", "entropy_hist", "zipf_coefficient", "min", "max", "range", "circ_mean_angle", "circ_mean_length", "circ_var", "circ_std", "circ_disp", "flatness"):
            raise Exception("Value of parameter measure is not valid!")

        outputVec = []
        for vec in inputVec:
            outputVec.append(self.processSingle(vec, measure))
        self.setParameterValue("outputVec", outputVec)
        #print self.getParameterValue("outputVec")

    def entropy_wrapper(self, p):
        if p<=np.finfo(float).eps:
            return 0
        return p * np.log2(p)

    def processSingle(self, inputVec, measure):
        #inputVec = inputVec.astype(float)
        # for some methods a list is required
        try:
            l = len(inputVec)
        except:
            inputVec = [inputVec]
        #print "Measure: ", measure
        #print type(inputVec)
        # normalize to density
        # do always for entropies
        #if self.getParameterValue("normalizeToDensity") or measure == "entropy":
        #    inputVec = inputVec / np.sum(inputVec)
        # process
        #print measure, len(inputVec)
        circ_max = self.getParameterValue("circ_max")
        if measure == "min":
            outputVec = np.min(inputVec)
        elif measure == "max":
            outputVec = np.max(inputVec)
        elif measure == "range":
            outputVec = np.max(inputVec) - np.min(inputVec)
        elif measure == "mean":
            if len(inputVec) == 0:
                return None
            outputVec = np.mean(inputVec)
        elif measure == "circ_mean_angle":
            outputVec = circ_stats(inputVec, circ_max)[0]
        elif measure == "circ_mean_length":
            outputVec = circ_stats(inputVec, circ_max)[1]
        elif measure == "circ_var":
            outputVec = circ_stats(inputVec, circ_max)[2]
        elif measure == "circ_std":
            outputVec = circ_stats(inputVec, circ_max)[3]
        elif measure == "circ_disp":
            outputVec = circ_stats(inputVec, circ_max)[4]
        elif measure == "median":
            outputVec = np.median(inputVec)
        elif measure == "std":
            outputVec = np.std(inputVec)
        elif measure == "var":
            outputVec = np.var(inputVec)
        elif measure == "mode":
            outputVec = mode(inputVec)
        elif measure == "zipf_coefficient":
            outputVec = zipf_coefficient(inputVec)
        elif measure == "flatness":
            outputVec = flatness(inputVec)
        elif measure == "entropy_hist":
            #works with rel. or abs. frequency histograms ONLY
            if len(inputVec) == 0:
                return None
            if self.getParameterValue("normalizeToDensity"):
                if np.min(np.abs(np.sum(inputVec)))>np.finfo(float).eps:
                    inputVec = inputVec / np.sum(inputVec).astype(np.float32)

            # add small epsilon to avoid numerical problems
            inputVec += np.finfo(float).eps
            outputVec = -1.0*np.sum(np.fromiter((self.entropy_wrapper(p) for p in inputVec), float))

            #TODO: Allow TRUE number of classes instead of observed ones
            if self.getParameterValue("normalizeEntropy"):
                n_classes=self.getParameterValue("numberClasses")
                if n_classes == None:
                    n_classes = len(inputVec)
                outputVec = outputVec/np.log2(n_classes) if n_classes>0 else 0.0
        elif measure == "entropy":
            #works with RAW data ONLY
            unit = "bit"
            n_classes=self.getParameterValue("numberClasses")
            if self.getParameterValue("normalizeEntropy") or n_classes != None:
                unit = "norm"
            outputVec = entropy(inputVec, unit=unit, n_classes=n_classes)
        #print "OUTPUT", outputVec
        return outputVec
