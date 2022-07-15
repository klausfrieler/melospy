""" Class implementation of RhythmEvent """

from melospy.basic_representations.jm_util import float_equal, s_to_hms


class RhythmEvent(object):

    def __init__(self, onsetSec, durationSec=0, value=None):
        """ Initialize module """
        # initialize event ID
        self.__onsetSec = onsetSec + 0.0
        if durationSec >= 0:
            self.__durationSec = durationSec + 0.0
        else:
            raise ValueError("Duration must not be negative")
        self.__value = value

    def clone(self):
        """ Returns a deep copy"""
        return RhythmEvent(self.onsetSec, self.durationSec, self.value)

    def setOnsetSec(self, val):
        """ Set onset in seconds """
        if isinstance(val, (int, float)):
            self.__onsetSec = float(val)
        else:
            raise Exception("Expected numeric value for onset. Got: "+str(val))
        return self

    def getOnset(self):
        """ Get onset in seconds (equals getOnsetSec)"""
        return self.__onsetSec

    def getOnsetSec(self):
        """ Get onset in seconds """
        return self.__onsetSec

    def setDurationSec(self, val):
        """
            Set duration in seconds
        """
        if isinstance(val, (int, float)) and val >= 0:
            self.__durationSec = float(val)
        else:
            raise Exception("RhythmEvent: Non-valid value for durationSec!")
        return self

    def getDuration(self):
        """
            Get onset in seconds (equals getDurationSecs)
        """
        return self.__durationSec

    def getDurationSec(self):
        """ Get onset in seconds """
        return self.__durationSec

    def getOffset(self):
        """
            Get offset of event in seconds. Offset is onset + duration
        """
        return self.__onsetSec + self.__durationSec

    def setValue(self, val):
        """ Set value of a rhythm event. Value can ANY object."""
        self.__value = val
        return self

    def getValue(self):
        """ Returns event value """
        return self.__value

    def inSpan(self, t):
        if t>=self.__onsetSec and t<=self.getOffset():
            return True
        return False

    def __eq__(self, other):
        if not isinstance(other, RhythmEvent):
            return False
        return float_equal(self.onsetSec, other.onsetSec)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __le__(self, other):
        return self.onsetSec <= other.onsetSec
    def __ge__(self, other):
        return self.onsetSec >= other.onsetSec
    def __lt__(self, other):
        return self.onsetSec < other.onsetSec
    def __gt__(self, other):
        return self.onsetSec > other.onsetSec

    def toString(self, sep = "|"):
        """Convert to a readable string"""
        if not isinstance(sep, str):
            sep = "|"
        base = ["t:" + str(s_to_hms(self.getOnsetSec())), "d:" + str(round(self.getDurationSec(), 3))]
        if self.__value != None and len(str(self.__value))>0:
            base.append("val:\'"+str(self.__value)+ "\'")
        s = sep.join(base)
        return(s)

    def toMCSV(self, quote=""):
        """returns a line in MCSV format"""
        base = [str(round(self.getOnsetSec(), 3)), str(round(self.getDurationSec(), 3))]
        if self.__value != None and len(str(self.__value))>0:
            base.append(quote+str(self.__value)+ quote)
        s = ";".join(base)
        return(s)


    def __str__(self):
        return self.toString()
    #def __repr__(self): return self.toString()

    onsetSec    = property(getOnsetSec, setOnsetSec)
    onset       = property(getOnsetSec, setOnsetSec)
    offset      = property(getOffset)
    durationSec = property(getDurationSec, setDurationSec)
    duration    = property(getDurationSec, setDurationSec)
    value       = property(getValue, setValue)
