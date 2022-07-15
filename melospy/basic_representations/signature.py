""" Class implementation of Signature """

from fractions import Fraction

from melospy.basic_representations.jm_util import all_the_same, two_three_partition, type_check


class Signature(object):

    def __init__(self, numerator=4, denominator=4, partition=None):
        """ Initialize module """
        self.setNumerator(numerator)
        self.setDenominator(denominator)
        self.setPartition(partition)

    @staticmethod
    def fromString(signature):
        """ Initialize a Signature object from a string of form M/N"""
        num = str(signature).partition("/")[0]
        parts = num.split("+")
        if len(parts) == 1:
            num = int(num)
            partition = None
        else:
            partition = [int(v) for v in parts]
            num = sum(partition)
        return Signature(num, int(str(signature).partition("/")[2]), partition)

    def clone(self):
        """ Return a deep copy"""
        return Signature(self.__numerator, self.__denominator)

    def setNumerator(self, val):
        """ Set function for Numerator """
        type_check(val, int)
        if val > 0:
            #Allow all numerators > 0
            self.__numerator = val
        else:
            raise ValueError("Signature: Invalid meter numerator {}".format(val))
        return self

    def getNumerator(self):
        """ Get meter numerator """
        return self.__numerator

    def setDenominator(self, val):
        """ Set meter denominator """
        #Allow all powers of 2 > 1

        if val > 1 and ((val & (val  - 1)) == 0) :
            self.__denominator = val
        else:
            raise ValueError("Expected power of 2 as meter denominator, got: {}".format(val))
        return self

    def getDenominator(self):
        """ Get meter denominator """
        return self.__denominator

    def getPartition(self):
        """ Get meter partition"""
        return self.__partition

    def setPartition(self, val):
        """ Set meter partition"""
        if val and sum(val) != self.__numerator:
            raise ValueError("Partitions values must sum to {}, but sum to {}".format(self.__numerator, sum(val)))
        self.__partition = val
        return self

    def getPrimaryBeatDivision(self):
        #if self.denominator < 8:
        #    return "binary"
        #print "getPrimaryBeatDivision", self.__partition, self.beatProportions
        elements = None

        if self.partition:
            elements = set(self.partition)

        try:
            if self.beatProportions:
                elements = set(self.beatProportions)
        except:
            pass

        if elements:
            if len(elements) > 1:
                return "asymmetric"
            if len(self.partition) > 1 and list(elements)[0] % 3 == 0:
                return "ternary"
            return "binary"
        #if self.numerator > 3 and self.numerator % 3 == 0:
        if self.numerator % 3 == 0 and self.denominator > 4:
            return "ternary"
        return "binary"

    def getBeatFactor(self, music21Mode=False, as_fraction=False):
        beat_type = self.getPrimaryBeatDivision()
        #print "Beat type: ", beat_type
        beat_factor = 1.0
        if beat_type == "ternary":
            beat_factor = 3./2.

        elif beat_type == "asymmetric":
            raise RuntimeError("Asymmetric beats (odd quaver meters) not supported yet")
        if music21Mode:
            if self.denominator == 2:
                beat_factor = 2
            if self.denominator == 1:
                beat_factor = 4
        #print "BF: ", beat_factor
        if as_fraction:
            beat_factor = Fraction(beat_factor)
        return beat_factor

    def getQuarterLength(self, music21Mode=False, as_fraction=False):
        if as_fraction:
            return Fraction(self.numerator * 4, self.denominator)
        return (self.numerator * 4.)/self.denominator

    def getMeterInfo(self):
        """
            Get standard interpretation of classical signatures as
            tuple (period, beatproportions) or the partition as
            provided in the additive signature.

            Beat proportions 'None' means equal proportions.
        """
        #num = self.numerator
        #nom = self.denominator
        #print "getStandardInterpretation. nom:{}, num:{}".format(nom, num)
        if self.denominator == 1 or self.denominator == 2 or self.denominator == 4:
            return self.numerator, None
        elif self.denominator == 8 or self.denominator == 16:
            #TO DO: Fix this hot fix
            if self.numerator == 3:
                return 3, None

            if self.partition:
                return self.numerator, self.partition
            part = two_three_partition(self.numerator, twoleads=False)
            #print part
            if all_the_same(part):
                #beat
                return len(part), None
            else:
                return len(part), part
        else:
            raise RuntimeError("Something weird happened... " + str(self))


    def toString(self):
        if self.__partition:
            numerator = "+".join([str(v) for v in self.__partition])
        else:
            numerator  =str(self.getNumerator())
        return  numerator + "/" + str(self.getDenominator())

    def __eq__(self, other):
        if not isinstance(other, Signature):
            return False
        return self.__numerator == other.__numerator  and self.__denominator == other.__denominator

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return self.toString()

    numerator   = property(getNumerator, setNumerator)
    denominator = property(getDenominator, setDenominator)
    partition   = property(getPartition, setPartition)
