""" Class implementation of MetricalPosition """

from fractions import *
from math import floor

from melospy.basic_representations.jm_util import find_position
from melospy.basic_representations.metrical_context import *


class MetricalPosition(object):

    def __init__(self, bar, beat, tatum, subtatum, metricalContext):
        """ Initialize module """
        self.setMetricalContext(metricalContext)
        self.setBar(bar)
        self.setBeat(beat)
        self.setTatum(tatum)
        self.setSubtatum(subtatum)

    def clone(self, tatum = None, beat = None, bar = None):
        """ Deep copy with option of setting new tatum, bar, beat values.
            Leaves subtatum unchanged.
        """
        newTatum = self.getTatum()
        if tatum != None and isinstance(tatum, int):
            newTatum = tatum
        newBeat= self.getBeat()
        if beat != None and isinstance(beat, int):
            newBeat= beat
        newBar = self.getBar()
        if bar != None and isinstance(bar, int):
            newBar= bar

        #print " {0} {1} {2}".format(newTatum, newBeat, newBar)
        mp = MetricalPosition(newBar, newBeat, newTatum, self.getSubtatum(), self.getMetricalContext().clone())
        return(mp)

    def change(self, bar, beat, tatum, subtatum = 0):
        """ Construct a new Metrical Position with the same MetricalContext but different index values"""
        mp = MetricalPosition(bar, beat, tatum, subtatum, self.__mc.clone())
        return(mp)


    def rescale(self, newDivision, force=False):
        """ Rescale according to new beat tatums. New division muist be a multiple or divisor of old one."""
        oldDivision = self.getMetricalContext().getBeatInfo().getTatums()
        upscale = True
        if oldDivision > newDivision:
            upscale = False
            remainder = oldDivision % newDivision
            factor = oldDivision/newDivision
        else:
            remainder = newDivision % oldDivision
            factor = newDivision/oldDivision
        if remainder != 0:
            raise Exception("Rescale not possible. New tatum (" + str(newDivision) + ") is no multiple of old division (" + str(oldDivision)+ ")")
        #print "----------------------------------------"
        #print self
        #print "Old:{} new:{} factor: {}".format(oldDivision, newDivision, factor)
        #print self.getMetricalContext()
        mc = self.getMetricalContext().rescale(factor, force, upscale)
        self.setMetricalContext(mc)
        #print mc
        #print "Before: {}, factor: {}".format(self.getTatum(), factor)
        if upscale:
            self.setTatum((self.getTatum()-1)*factor+1)
        else:
            self.setTatum((self.getTatum()-1)/factor+1)

        #print "After: {}".format(self.getTatum())
        #print "----------------------------------------"
        return self

    def incSubtatum(self):
        """ Increment subtatum by one"""
        self.__subtatum += 1
        return self

    def addTatum(self, val):
        """
            Add val to tatum, increment bar & beat if necessary
            Assumes same metrical context (i.e. division
        """
        div = self.getDivision()
        tmp = self.__tatum -1 + val
        tatum = tmp % div
        beats = tmp // div
        #print "div:{}, tmp: {}, rest:{}, beats:{}".format(div, tmp, tatum, beats)
        self.addBeat(beats)
        self.__tatum = tatum + 1
        return self

    def addBeat(self, val):
        """ Add val to beats, increment bar, if necessary"""
        period = self.getPeriod()
        tmp = self.__beat -1 + val
        beat = tmp % period
        bars = tmp // period

        #print "period:{}, tmp: {}, rest:{}, bars:{}".format(period, tmp, beat, bars)
        self.__bar += bars
        self.__beat = beat + 1
        return self

    def addBar(self, bar):
        """ Add to bar """
        self.__bar += bar
        return self

    def setBar(self, bar):
        """ Set function for bar"""
        self.__bar = int(bar)
        return self

    def getBar(self):
        """ Get function for bar """
        return self.__bar

    def setBeat(self, beat):
        """ Set function for beat """

        if beat < 1:
            raise ValueError("Beat position (" + str(beat) + ") must be at least 1")

        if beat > self.__mc.getPeriod():
            raise ValueError("Beat index (" + str(beat) + ") exceeds period (" + str(self.__mc.getPeriod()) + ") of MetricalContext")

        self.__beat = int(beat)
        return self

    def getBeat(self):
        """ Get function for beat"""
        return self.__beat

    def setTatum(self, tatum):
        """ Set function for tatum """
        if tatum > self.getDivision():
            raise Exception("Tatum index exceeds beat division!")
        self.__tatum = int(tatum)
        return self

    def getTatum(self):
        """ Get function for tatum"""
        return self.__tatum

    def setSubtatum(self, st):
        """ Set function for subtatum """
        if st < 0:
            raise ValueError("Expected positive integer for subtatum, got {}.".format(st))
        self.__subtatum = st
        return self

    def getSubtatum(self):
        """ Get function for subtatum"""
        return self.__subtatum

    def setMetricalContext(self, mc):
        """ Set function for metrical context"""
        if isinstance(mc, MetricalContext):
            self.__mc = mc
        else:
            raise Exception("No MetricalContext object given!")
        return self

    def getMetricalContext(self):
        """ Get function for metrical context"""
        return self.__mc

    def getMeterInfo(self):
        """ Get function for MeterInfo of metrical context"""
        return self.__mc.getMeterInfo()


    def getBeatInfo(self):
        """ Get function for for BeatInfo of metrical context"""
        return self.__mc.getBeatInfo()

    def getDivision(self):
        """ Get function for division of metrical context"""
        return self.__mc.getDivision()

    def getPeriod(self):
        """ Get function for division of metrical context"""
        return self.__mc.getPeriod()

    def getBeatDuration(self):
        """ Get function for beat durations of metrical context"""
        return self.__mc.getBeatDuration()

    def getSignature(self):
        """ Get function for signature durations of metrical context"""
        return self.__mc.getSignature()

    def quarterPositionDecimal(self, as_fraction=False):
        beat_factor = self.getMeterInfo().getBeatFactor(music21Mode=True, as_fraction=as_fraction)
        dec = (self.toDecimal() - self.bar)*self.getMeterInfo().period
        qp = dec * beat_factor
        return qp

    def quarterPositionFractional(self):
        beat_factor = self.getMeterInfo().getBeatFactor(music21Mode=True, as_fraction=True)
        #print beat_factor, self.toFraction()-self.bar, self.getMeterInfo().period
        frac = Fraction(self.toFraction() - self.bar)*self.getMeterInfo().period
        qp = frac * beat_factor
        return qp

    def getQuarterPeriod(self):
        return self.getMeterInfo().getQuarterLength()

    def beatPositionFractional(self):
        sbpf = Fraction(self.tatum-1 + (self.beat-1)*self.division, self.division)
        return sbpf

    def toNumeric(self, exact=False, as_fraction=False):
        if as_fraction:
            return self.toFraction(exact)
        return self.toDecimal(exact)

    def toFraction(self):
        """ Convert to a handy decimal for various purposes.
            Bar number will be the integer place,
            sub-bar positions will be a Fraction between 0 < x <1.
            Ignores subtatum
        """
        #print "="*40
        #print self
        base = Fraction(self.getBar())
        #print base
        beatProps = self.getMetricalContext().getMeterInfo().beatProportions
        #print "beatProps", beatProps
        if beatProps == None:
            beatProps = [1]*self.getMetricalContext().getMeterInfo().period
            #print "beatProps", beatProps
            denom = self.getMetricalContext().getMeterInfo().period
        else:
            denom = self.getMetricalContext().getMeterInfo().numerator
        #print "Denom", denom
        #print "sum(beatProps[0:self.getBeat()-1])", sum(beatProps[0:self.getBeat()-1])
        beatFrac = Fraction(sum(beatProps[0:self.getBeat()-1]), denom)
        #print "Beatfrac", beatFrac
        #print "Beat", self.getBeat()
        curBeatDur = Fraction(beatProps[self.getBeat()-1], denom)
        #print "curBeatDur ", curBeatDur
        #print "division", self.division

        tatumFrac = Fraction(self.tatum-1, self.division)*curBeatDur
        #print "tatumFrac ", tatumFrac
        #print "tatum-1", self.tatum-1
        ret = base  + beatFrac + tatumFrac
        #print ret
        return ret

    def toDecimal(self, exact=False, debug=False):
        """ Convert to a handy decimal for various purposes.
            Bar number will be the integer place,
            sub-bar positions will converted to decimal places
            Ignores subtatum, since by concept no exact timing of subtatum
            positions can be given. For example 4.2.1.1.1.0, 4.2.1.1.1 and
            4.2.1.1.2 will give all the same decimal value.
        """
        base      = self.getBar()
        if debug: print("base: ", base)
        #fractions provides the relative positions of beats in the interval 0..1 representing the bar duration
        beatFrac  = self.getMetricalContext().getMeterInfo().fractions()
        if debug: print("beatFrac: ", beatFrac)

        #fractions provides the relative positions of tatums in the interval 0..1 representing the beat duration
        #if exact is False, handle case as for equal tatum proportions
        if exact:
            tatumFrac = self.getMetricalContext().getBeatInfo().fractions()
        else:
            division = self.getMetricalContext().getBeatInfo().getTatums()
            tatumFrac = [float(k)/division for k in range(division)]

        beatPos   = beatFrac[(self.getBeat()-1)]
        if debug: print("tatumFrac: ", tatumFrac)
        if debug: print("beatPos: ", beatPos)

        #relative duration of current beat in the 0..1 continuum
        beatDur   = beatFrac[(self.getBeat())]-beatFrac[(self.getBeat()-1)]
        tatumPos  = beatDur * tatumFrac[self.getTatum()-1]
        if debug: print("tatumPos: ", tatumPos)
        if debug: print("beatDur: ", beatDur)
        if debug: print("Total:", base + beatPos + tatumPos)

        #add them all up
        return base + beatPos + tatumPos


    def fromDecimal(self, val, metricalContext):
        """ Convert from a handy decimal for various purposes """
        #if not (isinstance(val, (int, float)) and isinstance(metricalContext, MetricalContext)):
        #      raise TypError("MetricalPosition.fromDecimal: Invalid argument")

        bar = int(floor(val))
        rem = val - bar
        #print "Val:", val
        beatFrac  = metricalContext.getMeterInfo().fractions()
        beat, dur = find_position(beatFrac, rem)
        #print "BeatFrac: {}, Val: {}, bar: {}, rem:{}, beat:{}, dur:{}".format(beatFrac, val, bar, rem, beat, dur)
        if beat == None or dur == None:
            raise Exception("MetricalPostion.fromDecimal: Something really weird happend")
        rem = (rem - beatFrac[beat])/dur
        metricalContext.getBeatInfo().getBeatDurationSec()
        beat += 1

        #print "Tatum:"
        tatumFrac = metricalContext.getBeatInfo().fractions()
        tatum, dur = find_position(tatumFrac, rem)
        #print "TatumFrac: {}, tatum:{}, rem:{}, dur:{}".format(tatumFrac, tatum+1, rem, dur)
        tatum += 1

        return MetricalPosition(bar, beat, tatum, 0, metricalContext)

    def getMCM(self, MCM_division):
        #mod = self.toDecimal() % 1
        #r = round(mod, 4)
        #print "MCM_divisioM:{}, mod: {}, mod*MCM:{}, floor():{}".format(MCM_division, mod, mod*MCM_division, floor(mod*MCM_division))
        return int(round((self.toDecimal() % 1)*MCM_division))

    def __eq__(self, mp):
        """ Compare two metrical positions for equality"""
        if not isinstance(mp, MetricalPosition): return False
        return self.getBar() == mp.getBar() and self.getBeat() == mp.getBeat() and self.getTatum() == mp.getTatum() and self.getSubtatum() == mp.getSubtatum()

    def __ne__(self, mp):
        """ Compare two metrical positions for inequality"""
        return not self.__eq__(mp)

    def __gt__(self, mp):
        """ Check if MetricalPositions mp is greater than the caller (=later in time)"""
        if not isinstance(mp, MetricalPosition):
              raise Exception("MetricalPostion.equal: Invalid argument")
        if (round(self.toDecimal()-mp.toDecimal(), 10) == 0):
            return self.getSubtatum()>mp.getSubtatum()
        return self.toDecimal()>mp.toDecimal()

    def __lt__(self, mp):
        """ Check if MetricalPositions mp is less than the caller (=earlier in time)"""
        if not isinstance(mp, MetricalPosition):
              raise Exception("MetricalPostion.equal: Invalid argument")
        if (round(self.toDecimal()-mp.toDecimal(), 10) == 0):
            return self.getSubtatum()<mp.getSubtatum()
        return self.toDecimal()<mp.toDecimal()

    def __le__(self, mp):
        """ Check if MetricalPositions mp is less or euqal than the caller"""
        if not isinstance(mp, MetricalPosition):
              raise Exception("MetricalPostion.equal: Invalid argument")
        return not self.__gt__(mp)

    def __ge__(self, mp):
        """ Check if MetricalPositions mp is greater or equal than the caller"""
        return not self.__lt__(mp)

    def hasConsistentBeatInfo(self, mp):
        """ Two MetricalPositions which differ only in tatum or subtatum indices must have the same BeatInfo-Values"""
        if self.getBar() != mp.getBar() or self.getBeat() != mp.getBeat():
            return True
        return self.getMetricalContext().getBeatInfo() == mp.getMetricalContext().getBeatInfo()

    def hasConsistentMeterInfo(self, mp):
        """ Two MetricalPositions in the same must have the same MeterInfo-Values"""
        if self.getBar() != mp.getBar():
            return True
        return self.getMetricalContext().getMeterInfo() == mp.getMetricalContext().getMeterInfo()

    def consistent(self, mp):
        """ Short-hand consistency check"""
        if not self.hasConsistentMeterInfo(mp) or not self.hasConsistentBeatInfo(mp):
            return False
        return True

    def toDict(self):
        """ Make a simple dict"""
        dict = {'meter':self.__mc.getPeriod(), 'division':self.__mc.getDivision(), 'bar':self.__bar, 'beat':self.__beat, 'tatum':self.__tatum, 'subtatum':self.__subtatum }
        return(dict)

    def toString(self):
        """ Make nice string"""
        bp = self.__mc.getMeterInfo().getBeatProportions()
        if  bp is not None:
            period = "(" + "+".join([str(v) for v in bp]) + ")"
        else:
            period = str(self.__mc.getPeriod())


        if self.__subtatum != 0:
            tmp = '.'.join([period, str(self.__mc.getDivision()), str(self.__bar), str(self.__beat), str(self.__tatum), str(self.__subtatum)])
        else:
            #print("Should be here:", self.bar, self.beat, self.tatum)
            tmp = '.'.join([period, str(self.__mc.getDivision()), str(self.__bar), str(self.__beat), str(self.__tatum)])

        return tmp

    def toString2(self):
        """ Make nice string"""
        bp = self.__mc.getMeterInfo().getBeatProportions()
        if  bp is not None:
            period = "(" + "+".join([str(v) for v in bp]) + ")"
        else:
            period = str(self.__mc.getPeriod())
        if self.__subtatum != 0:
            tmp = '.'.join([str(self.__bar), str(self.__beat), str(self.__tatum), str(self.__subtatum)])
        else:
            #print "Should be here:", self.bar, self.beat, self.tatum
            tmp = '.'.join([str(self.__bar), str(self.__beat), str(self.__tatum)])
        mpstr = "[{}]{}({})".format(period, tmp, str(self.__mc.getDivision()))
        return mpstr

    def getMetricalWeight(self, level="beat"):
        if self.__tatum != 1 or self.__subtatum > 1:
            return 0
        v = self.getMeterInfo().getAccentedPositions()
        #print "Pos:{}, AccPos: {}. beat:{}".format(self,v, self.__beat)

        if self.__beat in v:
            return 2
        return 1

    def __str__(self):  return self.toString()
    #def __repr__(self): return self.toString()

    bar       = property(getBar, setBar)
    period    = property(getPeriod)
    beat      = property(getBeat, setBeat)
    division  = property(getDivision)
    tatum     = property(getTatum, setTatum)
    subtatum  = property(getSubtatum, setSubtatum)
    mc        = property(getMetricalContext, setMetricalContext)
