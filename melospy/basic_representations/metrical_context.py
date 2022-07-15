""" Class implementation of NoteEvent """

from melospy.basic_representations.beat_info import *
from melospy.basic_representations.jm_util import type_check
from melospy.basic_representations.meter_info import *


class MetricalContext(object):

    def __init__(self, beatInfo, meterInfo):
        """ Initialize module """
        self.setMeterInfo(meterInfo)
        self.setBeatInfo(beatInfo)

    def clone(self):
        """ Returns a deep copy"""
        return MetricalContext(self.getBeatInfo().clone(), self.getMeterInfo().clone())

    def rescale(self, factor, force=False, upscale=True):
        return self.setBeatInfo(self.getBeatInfo().rescale(factor, force, upscale))

    def setBeatInfo(self, beatInfo):
        type_check(beatInfo, BeatInfo)
        self.__beatinfo = beatInfo

        return self

    def getBeatInfo(self):
        return self.__beatinfo

    def setMeterInfo(self, meterInfo):
        self.__meterinfo = meterInfo
        return self

    def getMeterInfo(self):
        return self.__meterinfo

    def getPeriod(self):
        return self.__meterinfo.getPeriod()

    def getDivision(self):
        return self.__beatinfo.getTatums()

    def getBeatDuration(self):
        return self.__beatinfo.beatDurationSec

    def getSignature(self):
        return self.__meterinfo.getSignature()

    def estimateBarLengthSeconds(self):
        beatDur = self.__beatinfo.beatDurationSec
        period  = self.__meterinfo.period
        if self.__meterinfo.getBeatProportions() != None:
            #TODO something cleaver
            return sum(self.__meterinfo.getBeatProportions())*beatDur/2
        return period*beatDur

    def toString(self, sep="--"):
        if not isinstance(sep, str):
            sep = "--"
        return sep.join(["" + self.getBeatInfo().toString(), "" + self.getMeterInfo().toString()])

    def __str__(self):  return self.toString()
    #def __repr__(self): return self.toString()

    beatinfo  = property(getBeatInfo, setBeatInfo)
    meterinfo = property(getMeterInfo, setMeterInfo)
