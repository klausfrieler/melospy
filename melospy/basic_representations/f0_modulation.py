""" Class implementation of F0Modulation """
modulations = ["fall-off", "vibrato", "bend", "straight", "slide", ""]
modulations_short = ["fal", "vib", "ben", "str", "sli", ""]

class F0Modulation(object):
    """Class for F0Modulation values"""
    def __init__(self, annotated = None, range_cents=None, freq_hz=None, median_dev=None):
        """ Initialize object """
        #annotated modulation string
        self.set_modulation(annotated)
        #modulation range (cents)
        self.range_cents = range_cents
        #mdulation freq (Hz)
        self.freq_hz = freq_hz
        #median f0 deviation
        self.median_dev= median_dev

    @staticmethod
    def fromStruct(values):
        if values == None:
            return F0Modulation()
        elif isinstance(values, F0Modulation):
            return F0Modulation(values.annotated, values.range_cents, values.freq_hz, values.median_dev)
        elif isinstance(values, list):
            return F0Modulation.fromList(values)
        elif isinstance(values, dict):
            return F0Modulation.fromDict(values)
        elif isinstance(values, str):
            return F0Modulation(values)
        raise ValueError("Expected list or dict, got {}".format(type(values)))
        
    @staticmethod
    def fromList(values):
        ret = F0Modulation()
        if not isinstance(values, list):
            raise ValueError("Expected list, got {}".format(type(values)))
        if len(values) > 0:
            ret.set_modulation(values[0])
        if len(values) > 1:
            ret.range_cents = values[1]
        if len(values) > 2:
            ret.freq_hz = values[2]
        if len(values) > 3:
            ret.median_dev = values[3]
        return ret

    @staticmethod
    def fromDict(values):
        ret = F0Modulation()
        if not isinstance(values, dict):
            raise ValueError("Expected dict, got {}".format(type(values)))
        for k in values:
            ret.__dict__[k] = values[k]
        return ret

    def _find_modulation(self, value):
        if value is None:
            return None
        if value.lower() in modulations:
            return value.lower()
        try:
            idx = modulations_short.index(str(value).lower()[0:3])
        except:
            return "invalid"
        return modulations[idx]
  
    def set_modulation(self, value):
        """ Set function for modulation"""
        val = self._find_modulation(value)
        if val != "invalid":
            self.annotated = val
        else:
            raise Exception("Invalid modulation: {}".format(value))
               
    def __eq__(self, other):
        try:
            return self.__dict__ == other.__dict__
        except:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)
        
    def __str__(self, short=True):
        try:
            freq_hz = round(self.freq_hz, 2)
        except:
            freq_hz = None            
        try:
            range_cents = round(self.range_cents, 2)
        except:
            range_cents = None
        try:
            med_dev = round(self.median_dev, 2)
        except:
            med_dev = None
        s = "Annotated: {} |Range: {} cents|Freq: {} Hz|Dev: {} cents".format(self.annotated, range_cents, freq_hz, med_dev)
        s = s.replace("None", "--")
        return s
