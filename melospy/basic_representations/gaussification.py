""" Class implementation of Gaussification """

from melospy.basic_representations.accents import *
from melospy.basic_representations.beatometer_param import WeightRules
from melospy.basic_representations.timeseries import *


class Gaussification(TimeSeries):

    def __init__(self, onsets=None, sigma=.04, deltaT=.01, weightRules=None):
        """ Initialize Gaussification object """
        TimeSeries.__init__(self, deltaT=deltaT)

        self.__sigma = sigma

        if onsets == None:
            self.__onsets = []
        elif isinstance(onsets, TimeSeries):
            self.__onsets = onsets.times
        elif isinstance(onsets, Rhythm):
            self.__onsets = onsets.onsets
        else:
            self.__onsets = onsets

        if weightRules == None:
            weightRules = WeightRules()
            weightRules.sigma = sigma
            weightRules["params"]["sigma"] = sigma
        elif weightRules == "const":
            weightRules = WeightRules(method="const")

        self.setWeightRules(weightRules)

    def clone(self):
        """ Provides deep copy """
        g = Gaussification([t for t in self.__onsets], self.sigma, self.deltaT)
        g.setTimeSeries([t for t in self.getTimeSeries()])
        if self.__weightRules != None:
            wr =  {"method" : self.__weightRules["methods"], "params" : self.__weightRules["params"]}
            g.setWeightRules(wr)
        return g


    def clear(self):
        self.__onsets = []
        return self

    def getSigma(self):
        return self.__sigma

    def setSigma(self, sigma):
        self.__sigma = sigma
        return self

    def getWeightRules(self):
        return self.__weightRules

    def getWeightRulesMethod(self):
        return self.__weightRules["method"]

    def getWeightRulesParams(self):
        return self.__weightRules["params"]

    def setWeightRules(self, wr):
        if wr != None and not isinstance(wr, WeightRules):
            raise TypeError("Expected WeightRules object or None, got {} {}".format(wr, type(wr)))
        self.__weightRules = wr

        if len(self.__onsets) > 0 and wr != None:
            af = AccentFactory()
            a = af.create(wr["method"])
            try:
                a.setParams(wr["params"])
            except:
                pass
            #print "="*60
            #print a
            #print wr
            #a.calcultRhythm.fromOnsets(self.__onsets))
            self.__weights = a.calculate(Rhythm.fromOnsets(self.__onsets))
        return self

    def getWeights(self):
        return self.__weights

    def gaussify(self, start=None, end=None):
        onsets = self.onsets
        sigma = self.__sigma
        deltaT = self.deltaT
        if start == None:
            start= min(onsets)-2*sigma
        if end == None:
            end = max(onsets)+2*sigma

        #print "start = {}, end = {}, deltaT = {}".format(start,end, deltaT)

        t = start
        times = []
        vals = []
        while t<end:
            factor = -.5/sigma/sigma
            tmp = [exp(factor * (t_ - t)* (t_- t)) for t_ in onsets]
            val = scalar_prod(self.__weights, tmp)
            vals.append(val)
            times.append(t)
            #print "({},{}) ".format(t, round(val, 3))
            t += deltaT
        self.setTimeSeries(list(zip(times, vals)))
        return self

    def _getWeightTensor(self):
        if self.__weights == None or len(self.__weights) == 0:
            return None
        w = self.__weights
        N = len(w)
        mat = [[0 for _ in w] for _ in range(N)]
        for i in range(N):
            mat[i][i] = w[i]*w[i]
            for j in range(i+1, N):
                mat[i][j] = w[i]*w[j]
                mat[j][i] = mat[i][j]
        return mat

    def _getWeightTensor2(self, weights):
        if self.__weights == None or len(self.__weights) == 0:
            return None
        if weights == None or len(weights) == 0:
            return None
        w1 = self.__weights
        w2 = weights
        N1 = len(w1)
        N2 = len(w2)
        mat = [[0 for _ in w1] for _ in w2]
        for i in range(N1):
            for j in range(N2):
                mat[i][j] = w1[i]*w2[j]
        return mat


    def _getOnsetDiffMatrix(self):
        if self.__onsets == None or len(self.__onsets) == 0:
            return None
        O = self.__onsets
        N = len(O)
        mat = [[0 for _ in O] for _ in range(N)]
        for i in range(N):
            mat[i][i] = 0
            for j in range(i+1, N):
                mat[i][j] = O[i]-O[j]
                mat[j][i] = -mat[i][j]
        return mat

    def _prepareAutocorrelation(self):
        if self.__weights == None or len(self.__weights) == 0:
            return None
        if self.__onsets == None or len(self.__onsets) == 0:
            return None
        w = self.__weights
        O = self.__onsets
        N = len(O)
        dm = [[0 for _ in O] for _ in range(N)]
        tw = [[0 for _ in O] for _ in range(N)]
        for i in range(N):
            dm[i][i] = 0
            tw[i][i] = w[i]*w[i]
            for j in range(i+1, N):
                dm[i][j] = O[i]-O[j]
                dm[j][i] = -dm[i][j]
                tw[i][j] = w[i]*w[j]
                tw[j][i] = tw[i][j]
        return tw, dm

    def _prepareCrossCorrelation(self, other):
        if self.__weights == None or len(self.__weights) == 0:
            return None
        if self.__onsets == None or len(self.__onsets) == 0:
            return None
        if other.weights == None or len(other.weights) == 0:
            return None
        if other.onsets == None or len(other.onsets) == 0:
            return None
        w1 = self.__weights
        w2 = other.weights
        O1 = self.__onsets
        N1 = len(O1)
        O2 = other.onsets
        N2 = len(O2)

        dm = [[0 for _ in range(N2)] for _ in range(N1)]
        tw = [[0 for _ in range(N2)] for _ in range(N1)]
        for i in range(N1):
            for j in range(N2):
                dm[i][j] = O1[i]-O2[j]
                tw[i][j] = w1[i]*w2[j]
        return tw, dm

    def autocorrelation(self, max_lag=3.0, deltaT=None, norm=True):
        tau = 0
        ts = []
        s = 0
        if self.isEmpty():
            endTime = max(self.__onsets) + 2*self.__sigma
        else:
            endTime = self.endTime()

        mat, od = self._prepareAutocorrelation()
        factor = 2*self.__sigma
        if deltaT == None:
            deltaT = self.deltaT

        if max_lag>endTime:
            max_lag = endTime

        norm_factor = 1.
        while tau<max_lag:
            #print "="*40
            s = 0
            for i in range(len(self.__onsets)):
                for j in range(len(self.__onsets)):
                    q = (od[i][j]-tau)/factor
                    s += mat[i][j]*exp(-q*q)
            if norm and tau == 0:
                norm_factor = s
            ts.append((tau, s/norm_factor))
            tau += deltaT
        ret = TimeSeries(deltaT=deltaT)
        ret.setTimeSeries(ts)
        return ret

    def crosscorrelation(self, other, start=0, end=3.0, deltaT=None, norm=True):
        tau = 0
        ts = []
        if start>=end:
            raise ValueError("End time should be greater than start time." )

        #if self.isEmpty():
        #    self.gaussify()
        #if other.isEmpty():
        #    other.gaussifiy()

        mat, od = self._prepareCrossCorrelation(other)
        factor = 2*self.__sigma

        if deltaT == None:
            deltaT = min(self.deltaT, other.deltaT)
        norm_factor = 1.
        tau = start
        while tau<end:
            #print "="*40
            s = 0
            for i in range(len(self.__onsets)):
                for j in range(len(other.__onsets)):
                    q = (od[i][j]-tau)/factor
                    s += mat[i][j]*exp(-q*q)
                    #print i, j, tau, q, exp(q*q*factor)
            if norm and tau == 0:
                norm_factor = s
            ts.append((tau, s/norm_factor))
            tau += deltaT

        ret = TimeSeries(deltaT=deltaT)
        ret.setTimeSeries(ts)
        return ret

    def getOnsets(self):
        """ Return onsets as list"""
        return self.__onsets

    def setOnsets(self, onsets):
        """ Set onsets """
        self.__onsets = onsets
        return self

    onsets  = property(getOnsets, setOnsets)
    sigma   = property(getSigma, setSigma)
    weightrules  = property(getWeightRules, setWeightRules)
    weights = property(getWeights)
