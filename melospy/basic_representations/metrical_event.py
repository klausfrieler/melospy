""" Class implementation of MetricalEvent """

from melospy.basic_representations.metrical_position import *
from melospy.basic_representations.rhythm_event import *


class MetricalEvent(RhythmEvent):

    def __init__(self, onsetSec, metricalPosition=None, durationSec=0, durationTatum=None):
        """ Initialize module """
        # MetricalPosition has to be set first since constructor
        #of rhythm events calls setDurationSec,
        #which calls calcDurationTatum, which needs __mp
        self.setMetricalPosition(metricalPosition)
        RhythmEvent.__init__(self, onsetSec, durationSec)

        if durationTatum == None:
            self.__setDurationTatum(self.calcDurationTatum())
        else:
            self.__setDurationTatum(durationTatum)

    def clone(self):
        """ Returns a deep copy """
        return MetricalEvent(self.getOnsetSec(), self.getMetricalPosition().clone(), self.getDurationSec(), self.getDurationTatum())

    def calcDurationTatum(self):
        """ Calc duration tatum based on durationSec and current metrical context
            current tatum length is beat duration divided by tatums per beat
        """
        #print("MetricalEvent:calcDurationTatum")
        #print type(self)
        tatumDurationSec = float(self.getMetricalContext().getBeatInfo().getBeatDurationSec())/self.getDivision()
        durationTatum = int(round(self.getDurationSec()/tatumDurationSec))
        return durationTatum

    def getDurationTatum(self):
        """ Get function for durationTatum"""
        return self.__durtatum

    def setDurationSec(self, durSec):
        """ Set duration Sec (overrides setDurationSec from RhythmEvent)"""
        #print("MetricalEvent:setDurationSec")
        #print type(self)
        RhythmEvent.setDurationSec(self, durSec)
        self.__setDurationTatum(self.calcDurationTatum())
        return self

    #made a private function to prevent inconsistency,
    #durationTatum should always be calculated from setDurationSec()
    #or by rescale()
    def __setDurationTatum(self, durationTatum=None):
        #testtatum = calcDurationTatum()

        if isinstance(durationTatum, (int, float)):
            self.__durtatum = round(durationTatum*100)/100
        else:
            raise TypeError("Expected numerical value for duration tatum, got " + str(durationTatum))
        return self

    def setMetricalPosition(self, mp):
        """ Set function for metrical position """
        if isinstance(mp, MetricalPosition):
            self.__mp = mp
        else:
            raise Exception("MetricalEvent: Invalid value for metrical position! {}".format(mp))
        return self

    def rescale(self, newDivision, force=False):
        """ Rescale according to new beat tatums.
            New division must be a multiple of old one.
        """
        self.getMetricalPosition().rescale(newDivision, force)
        self.__setDurationTatum(self.calcDurationTatum())
        #print(self.toString())
        return self

    def getMetricalPosition(self):
        return self.__mp

    def getMetricalPositionDecimal(self, debug=False):
        return self.__mp.toDecimal(debug)

    def getQuarterPositionFractional(self):
        return self.__mp.quarterPositionFractional()

    def getQuarterPeriod(self):
        return self.__mp.getQuarterPeriod()

    def getMCM(self, MCM_division):
        return self.__mp.getMCM(MCM_division)

    def getMetricalContext(self):
        """ Getter for MetricalContext of associated MetricalPosition"""
        return self.__mp.getMetricalContext()

    def getMeterInfo(self):
        """ Getter for MeterInfo of associated MetricalPosition"""
        return self.__mp.getMetricalContext().getMeterInfo()

    def getBeatInfo(self):
        """ Getter for BeatInfo of associated MetricalPosition"""
        return self.__mp.getMetricalContext().getBeatInfo()

    def getBar(self):
        """ Getter for bar of associated MetricalPosition"""
        return self.__mp.getBar()

    def getBeat(self):
        """ Getter for beat of associated MetricalPosition"""
        return self.__mp.getBeat()

    def getTatum(self):
        """ Getter for tatum of associated MetricalPosition"""
        return self.__mp.getTatum()

    def getSubtatum(self):
        """ Getter for subtatum of associated MetricalPosition"""
        return self.__mp.getSubtatum()

    def getPeriod(self):
        """ Getter for period of associated MetricalPosition"""
        return self.__mp.getPeriod()

    def getDivision(self):
        """ Getter for dvision of associated MetricalPosition"""
        return self.__mp.getDivision()

    def getTempoBPM(self):
        """ Get tempo in BPM as provided in the beat info of associated MetricalPosition"""
        return round(60/self.getMetricalContext().getBeatInfo().getBeatDurationSec()*10)/10

    def getBeatDuration(self):
        """ Get tempo as beat duration from BeatInfo of associated MetricalPosition"""
        return self.getMetricalContext().getBeatInfo().getBeatDurationSec()

    def getSignature(self):
        """ Get Signture form MeterInfo associated MetricalPosition"""
        return self.getMetricalContext().getSignature()

    def getMetricalWeight(self):
        return self.__mp.getMetricalWeight()

    def consistent(self, me):
        """ Consitency check of underlying MetricalPositions. Cf. according methods of MetricalPosition"""
        return self.getMetricalPosition().consistent(me.getMetricalPosition())

    def toString(self, sep ="|"):
        """ Make a nice string"""
        mps = self.getMetricalPosition().toString()
        if not isinstance(sep, str):
            sep = "|"
        res = RhythmEvent.toString(self)
        mps = sep.join([res, "pos:" + mps, "dtat:"+ str(self.getDurationTatum())])
        return(mps)

    def toMCSV(self, quote=""):
        """ Make a nice string"""
        mps = self.getMetricalPosition().toString()
        res = RhythmEvent.toMCSV(self, quote)
        mps = ";".join([res, mps, str(int(round(self.getDurationTatum())))])
        return(mps)

    def __str__(self):
        return self.toString()
    #def __repr__(self): return self.toString()

    mp        = property(getMetricalPosition, setMetricalPosition)
    durtatum  = property(getDurationTatum)
    bar       = property(getBar)
    beat      = property(getBeat)
    tatum     = property(getTatum)
    subtatum  = property(getSubtatum)
    division  = property(getDivision)
    period    = property(getPeriod)
