""" Class implementation of BeatInfo """

class BeatInfo(object):
    
    def __init__(self, tatums=2, beatDurationSec=.5, tatumProportions=None):
        """ Initialize module. 
            Note: TatumProportions can be either a tuple of length of tatum division 
            or None, which implies equal proportions 
        """
        self.setTatums(tatums)
        self.setBeatDurationSec(beatDurationSec)
        self.setTatumProportions(tatumProportions)

    def clone(self):
        """ Returns a deep copy"""
        return BeatInfo(self.getTatums(), self.getBeatDurationSec(), self.getTatumProportions())

    def hasEqualProportions(self):
        """ Initialize module """
        return self.getTatumProportions() == None or self.getTatumProportions() == self.makeNTuple(self.getTatums())

    def rescale(self, factor, force=False, upscale=True):
        if not force and not self.hasEqualProportions():
            raise RuntimeError("Rescale not possible due to non-equal tatum proportions.")
        tatums = self.getTatums()
        if upscale:
           self.setTatums(tatums*factor)
        else:
            if tatums % factor != 0:
                raise ValueError("Factor {} is no divisor of tatums {}".format(factor, tatums))
            else:
                self.setTatums(tatums/factor)                
        self.setTatumProportions(None)           
        return self

        
    def setTatums(self, val):
        """ Set tatums. Does no(!) consistency check on tatum proportions!"""
        if int(val) > 0:
            self.__tatums = int(val)
        else:
            raise ValueError("Non-valid value for tatums {}".format(val))
            
        return self
        
    def getTatums(self):
        """ Get tatums """
        return self.__tatums
    
    def setBeatDurationSec(self, val):
        """ Set beat duration in seconds """
        if val >= 0:
            self.__beatDurationSec = float(val)
        else:
            raise ValueError("Invalid value ({}) for beat duration!".format(val))
        return self 

    def getBeatDurationSec(self):
        """ Get beat duration in seconds """
        return self.__beatDurationSec

    def setTatumProportions(self, val):
        """ Set tatum proportions. Must be consistent with tatum number"""
        if val == None:
            self.__tatumProportions = None                
        elif isinstance(val, tuple):
            if len(val) == self.__tatums:
                self.__tatumProportions = val
            else:
                raise ValueError("Expected length {}, got {} ".format(self.__tatums, len(val)))
        else:
            raise ValueError("Expected tuple for tatum proportion.")
        return self

    def getTatumProportions(self):
        """ Get tatum proportion """
        return self.__tatumProportions
    
    def fractions(self, closeIt = True):      
        """ Calculates tatum proportions represented as a list of points in the interval 0..1"""
        fractions = [0]
        if self.__tatumProportions == None:
            units = (self.__tatums)
            for i in range(1, self.__tatums): 
                fractions.append(float(i)/units)
        else:
            units = sum(self.__tatumProportions) 
            for i in range(1, len(self.__tatumProportions)): 
                fractions.append(float(sum(self.__tatumProportions[0:i]))/units)
        if closeIt:
            fractions.append(1)
        return fractions

    def __eq__(self, bi):
        """ Compare two BeatInfo objects for equality """
        if not isinstance(bi, BeatInfo):
            return False
        if self.getTatums() == bi.getTatums() and self.getBeatDurationSec() == bi.getBeatDurationSec() and self.getTatumProportions() == bi.getTatumProportions():
            return True
        return False

    def __ne__(self, bi):
        """ Compare two BeatInfo objects for inequality """
        return not self.__eq__(bi)        

    def makeNTuple(self, n, val = 1):
        t = ()
        for i in range(n):
            t = t + (val,) 
        return t          

    def toString(self, sep="|"):
        if not isinstance(sep, str):
            sep = "|"
        return sep.join([str(self.getTatums()), str(self.getBeatDurationSec()), str(self.getTatumProportions())])

    def __str__(self):  return self.toString()

    tatums          = property(getTatums, setTatums)
    beatDurationSec = property(getBeatDurationSec, setBeatDurationSec)
    tatumProportion = property(getTatumProportions, setTatumProportions)
