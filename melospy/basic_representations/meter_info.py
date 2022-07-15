""" Class implementation of MeterInfo """

from melospy.basic_representations.signature import *


class MeterInfo(Signature):

    def __init__(self, numerator=4, denominator=4, beatProportionsOrPeriod=None):
        """
            Signature super class represents classical signature information,
            which encapsulates and sometime hides the true underlying different
            metrical conception which is captured in the fields 'period' and
            'beatproportions'. 'period' is the grouping unit of the cental
            beats. However, the beats are do not have to be equal  (in an
            idealized sense) but might be of different length, the ratio of
            which are stored in 'beatproportion'. Beat proportions
            are represented as integer values of an hypothetical underlying
            level (not necessarily equal to actually used tatums).
            E.g. a 5/8 measure can be conceived either as a period 5 grouping
            with equal beat proportions or as a period 2 grouping of inequal
            beats either 3+2 or 2+3 grouping.
            Internally 'beatproportion' is either None, representing equal
            beats, or a tuple of integers of length period

            Three cases of for beatProportionOrPeriod arguments can be differentiated
            * beatProportionOrPeriod = None:
                The constructor retrieves the standard interpretation of the
                classical signature and sets 'period' and 'beatproportion'
                accordingly.
            * beatProportionOrPeriod = int > 0:
                Interpreted as a period which must be a divisor of
                meterNumerator. beatproportion is set to
                None for equal proportions.
            * beatProportionOrPeriod = tuple(int):
                Interpreted as proportions.
                Period is set to length of beatProportionOrPeriod which must
                be a divisor of meterNumerator.

        """
        Signature.__init__(self, numerator, denominator)
        self.__period = None
        self.__beatProportions = None
        if beatProportionsOrPeriod == None:
            period, beatproportion = Signature.getMeterInfo(self)
            #print "period, beatproportion ", period, beatproportion
            self.setPeriod(period)
            self.setBeatProportions(beatproportion)
        elif isinstance(beatProportionsOrPeriod, (list, tuple)):
            self.__period = len(beatProportionsOrPeriod)
            self.setBeatProportions(beatProportionsOrPeriod)
            Signature.setPartition(self, beatProportionsOrPeriod)
        elif isinstance(beatProportionsOrPeriod, int):
            self.setBeatProportions(None)
            self.setPeriod(beatProportionsOrPeriod)
        else:
            raise TypeError("Expected tuple of integer or int, got {}".format(type(beatProportionsOrPeriod)))



    @staticmethod
    def fromString(s):
        """ Returns a MeterInfo object from a Signature string"""
        sig = Signature.fromString(s)
        return MeterInfo(sig.numerator, sig.denominator, sig.partition)

    @staticmethod
    def fromSignature(sig):
        """ Returns a MeterInfo object from a Signature object"""
        return MeterInfo(sig.numerator, sig.denominator, sig.partition)

    def clone(self):
        """ Returns a deep copy"""
        beatProportionsOrPeriod = self.getBeatProportions() if  self.getBeatProportions()!= None else self.getPeriod()
        return MeterInfo(self.getNumerator(), self.getDenominator(), beatProportionsOrPeriod )

    def setPeriod(self, val):
        """ Set function for period """

        if self.getNumerator() != None:
            if val > self.getNumerator():
                raise ValueError("Period must not be greater than the meter numerator.")

        if self.getBeatProportions() != None:
            if val != len(self.getBeatProportions()):
                raise ValueError("Period cannot differ from number of elements in beat proportions.")

        self.__period= val

        return self

    def getPeriod(self):
        """ Get beats """
        return self.__period

    def setBeatProportions(self, val):
        """ Set beat proportions """
        # ! Note that in case of numerator = 1, we have to set the beat proportions as (1,) and not as (1) since
        # the latter one is not recognized as a tuple but as an int !
        # BeatProportions must have no common denominator except 1
        # The length of  BeatProportions must be equal the period, the sum must be *smaller* or equal to signatures numerator
        #type_check(val, tuple, allowNone = True)
        if val != None:
            val = tuple(val)
            if self.getPeriod() != None:
                if len(val) != self.getPeriod():
                    raise ValueError("Length of beatProportions ({}) must equal period {}".format(len(val), self.getPeriod()))
            else:
                try:
                    self.setPeriod(len(val))
                except Exception as e:
                    raise ValueError(e.args)
        self.__beatProportions = val

        return self

    def getBeatProportions(self):
        """ Get beat proportions """
        return self.__beatProportions

    def getSuperBeatProportions(self):
        """ Get standard interpretation of classical signatures as
            superbeat proportions or the partition as provided in the
            additive signature
            Beat proportions == None means equal proportions (no halfbar level)
        """
        #num = self.meterNumerator
        #nom = self.meterDenominator
        #print "getStandardInterpretation. nom:{}, num:{}".format(nom, num)

        if self.denominator < 8 and self.partition:
            return tuple(self.partition)
        else:
            part = two_three_partition(self.period, twoleads=False)
            #print "Period, part", self.period, part
            return part

    def getAccentedPositions(self):
        pos = [1]
        if self.numerator == 1:
            return pos

        sbp = self.getSuperBeatProportions()
        for i in range(len(sbp)-1):
            pos.append(pos[-1]+ sbp[i])
        return pos

    def fractions(self, closeIt=True):
        """
            Calculates beat proportions represented as
            a list of points in the interval 0..1
        """
        if self.__beatProportions == None:
            fractions = [float(i)/self.period for i in range(self.period)]
        else:
            units = sum(self.__beatProportions)
            fractions = [0]
            for i in range(1, len(self.__beatProportions)):
                fractions.append(float(sum(self.__beatProportions[0:i]))/units)
        if closeIt:
            fractions.append(1)
        return fractions


    def getSignature(self):
        return Signature(self.numerator, self.denominator, self.partition)

    def __eq__(self, mi):
        """ Compare two MeterInfo objects for equality """
        if not isinstance(mi, MeterInfo):
            return False
        return self.getPeriod() == mi.getPeriod() and self.getBeatProportions() == mi.getBeatProportions()

    def __ne__(self, mi):
        """ Compare two MeterInfo objects for inequality """
        return not self.__eq__(mi)


    def toString(self, sep="|"):
        if not isinstance(sep, str):
            sep = "|"
        bstr = str(self.getBeatProportions()) if self.getBeatProportions() != None else "Equal"
        return sep.join([Signature.toString(self), str(self.getPeriod()), bstr])

    def __str__(self):
        return self.toString()
    #def __repr__(self): return self.toString()#


    period          = property(getPeriod, setPeriod)
    beatProportions = property(getBeatProportions, setBeatProportions)
