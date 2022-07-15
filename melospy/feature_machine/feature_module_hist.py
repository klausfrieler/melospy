import numpy as np

import melospy.feature_machine.test_help_functions as thf
from melospy.feature_machine.feature_module_base import MelopyFeatureModuleBase
from melospy.feature_machine.feature_module_parameter import MelopyFeatureModuleParameter


class MelopyFeatureModuleHist(MelopyFeatureModuleBase):
    """ Histogram module """

    def __init__(self):
        """ Initialize module """
        MelopyFeatureModuleBase.__init__(self, "hist")

        # define module parameters
        self.addInputParameter(MelopyFeatureModuleParameter("inputVec", True))
        self.addInputParameter(MelopyFeatureModuleParameter("fixed-bins", False, None))
        self.addInputParameter(MelopyFeatureModuleParameter("histogramType", True))
        self.addInputParameter(MelopyFeatureModuleParameter("min", False))
        self.addInputParameter(MelopyFeatureModuleParameter("max", False))
        self.addInputParameter(MelopyFeatureModuleParameter("density", False, False))
        self.addInputParameter(MelopyFeatureModuleParameter("sort", False, "descending"))
        self.addInputParameter(MelopyFeatureModuleParameter("removeEmptyBins", False))

        # define output parameters
        self.addOutputParameter(MelopyFeatureModuleParameter("histVec"))
        self.addOutputParameter(MelopyFeatureModuleParameter("bins"))

    def get_nominal_histogram(self, inputVec, bins=None):
        density = self.getParameterValue("density")
        sort    = self.getParameterValue("sort")
        uniqueValues = []
        histVec = []
        coerced = False
        #print "bins before:", bins, type(bins[0])
        #if any segmentations is used, the bins here are set to numpy arrays,
        #since bins are used for output also
        #TODO: better fix
        if isinstance(bins[0], np.ndarray):
            bins = list(bins[0])
        try:
            tmpVec = [k.tolist() for k in inputVec]
            coerced = True
        except AttributeError:
            tmpVec = inputVec

        if bins[0] is not None:
            uniqueValues = bins
            histVec = [0 for k in bins]
        #print "bins after:", bins, type(bins[0])

        for i in range(len(tmpVec)):
            try:
                idx = uniqueValues.index(tmpVec[i])
                histVec[idx] += 1
            except ValueError:
                if bins[0] is None:
                    uniqueValues.append(tmpVec[i])
                    histVec.append(1)
                    #print "Added ", tmpVec[i]

        if sort != None and sort != "None":
            tmp = thf.dict_from_keys_vals(list(range(len(uniqueValues))), histVec)
            if sort:
                if sort == "descending":
                    reverse = True
                else:
                    reverse = False
                idz = sorted(tmp, key = tmp.get, reverse = reverse)
            else:
                idz = tmp
            uniqueValues = [uniqueValues[i] for i in idz]
            histVec = [histVec[i] for i in idz]

        if coerced:
            uniqueValues = [np.array(k) for k in uniqueValues]
        if density:
            s = sum(histVec)
            if s != 0:
                histVec = np.array([np.float(v)/s for v in histVec])

        #print "get_nominal_histogram", histVec, uniqueValues

        return histVec, uniqueValues

    def get_metrical_histogram(self, inputVec, histBins):

        if not (isinstance(inputVec, np.ndarray) or \
           ( thf.includesOnlyNumericItems(inputVec) and not thf.isEncapsulatedSequence(inputVec))):
            raise ValueError("Data must be float-compatible")
        if histBins is None:
            histBins = inputVec.max() - inputVec.min() + 1
        else:
            # sort bins
            histBins.sort()

        histVec, bin_edges = np.histogram(inputVec, bins=histBins, density=self.getParameterValue("density"))
        return histVec, bin_edges

    def get_ordinal_histogram(self, inputVec, minVal=None, maxVal=None, removeEmptyBinsBins=False):
        density = self.getParameterValue("density")
        inputVec = inputVec.astype(int)
        if minVal == None:
            minVal = inputVec.min()
        if maxVal == None:
            maxVal = inputVec.max()
        if maxVal < minVal:
            maxVal, minVal = minVal, maxVal
        histVec = [0 for _ in range(maxVal -minVal + 1)]
        bins = [_ for _ in range(minVal, maxVal + 1)]
        for v in inputVec:
            try:
                histVec[v - minVal] += 1
            except Exception:
                pass
                #print ("Warning data {} exceeds range {}--{}.".format(v, minVal, maxVal))
        if removeEmptyBinsBins:
            tmpBins = []
            tmpHist = []
            for b in range(len(histVec)):
                if histVec[b] > 0:
                    tmpHist.append(histVec[b])
                    tmpBins.append(bins[b])
            bins = tmpBins
            histVec = tmpHist

        if density:
            s = sum(histVec)
            if s != 0:
                histVec = np.array([np.float(v)/s for v in histVec])

        return histVec, bins

    def process(self):
        self.checkInputParameters()
        inputVec = self.getParameterValue("inputVec")
        histogramType = self.getParameterValue("histogramType")
        bins = self.getParameterValue("fixed-bins")
        #print "call process", bins
        if bins is None:
            bins = [None]*len(inputVec)
        histVec = []
        binsOut = []
        for k in range(len(inputVec)):
            histVecCurr, binsCurr = self.processSingle(inputVec[k], bins, histogramType)
            histVec.append(np.array(histVecCurr))
            binsOut.append(np.array(binsCurr))
            #binsOut.append(np.array(binsCurr))
        #print "\n".join([str(_) for _ in self.getOutputParameters()])
        #print "\n".join([str(_) for _ in self.getInputParameters()])

        self.setParameterValue("histVec", histVec)
        self.setParameterValue("bins", binsOut)
        #print "Fixed-bins:", self.getParameterValue("fixed-bins")
        #print "Bins:", self.getParameterValue("bins")

    def processSingle(self, inputVec, bins, histogramType):
        if histogramType == "nominal":
            histVec, bins = self.get_nominal_histogram(inputVec, bins)
        elif histogramType == "ordinal":
            histVec, bins = self.get_ordinal_histogram(inputVec, self.getParameterValue("min"), self.getParameterValue("max"), self.getParameterValue("removeEmptyBins"))
        elif histogramType == "metrical":
            histVec, bins = self.get_metrical_histogram(inputVec, bins)
        return histVec, bins
