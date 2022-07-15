""" Class implementation of Loudness """

class Loudness(object):
    """Class for loudness values"""
    def __init__(self, maximum=None, median=None, stddev=None, rel_peak_pos=None, temp_centroid=None, s2b=None):
        """ Initialize object """
        #max rel. dB
        self.max = maximum
        #max rel. dB
        self.median = median
        #max rel. dB
        self.stddev = stddev
        #relative peak position [0..1]
        self.rel_peak_pos = rel_peak_pos 
        #temporal centroid [0..1]
        self.temp_centroid = temp_centroid
        #signal to backing track ratio (of medians)
        self.s2b = s2b

    @staticmethod
    def fromStruct(values):
        if values == None:
            return Loudness()
        elif isinstance(values, Loudness):
            return Loudness(values.max, values.median, values.stddev, values.rel_peak_pos, values.temp_centroid, values.s2b)
        elif isinstance(values, list):
            return Loudness.fromList(values)
        elif isinstance(values, dict):
            return Loudness.fromDict(values)

        raise ValueError("Expected list or dict, got {}".format(type(values)))
        
    @staticmethod
    def fromList(values):
        ret = Loudness()
        if not isinstance(values, list):
            raise ValueError("Expected list, got {}".format(type(values)))
        if len(values) > 0:
            ret.max = values[0]
        if len(values) > 1:
            ret.median = values[1]
        if len(values) > 2:
            ret.stddev = values[2]
        if len(values) > 3:
            ret.rel_peak_pos = values[3]
        if len(values) > 4:
            ret.temp_centroid = values[4]
        if len(values) > 5:
            ret.s2b = values[5]
        return ret

    @staticmethod
    def fromDict(values):
        ret = Loudness()
        if not isinstance(values, dict):
            raise ValueError("Expected dict, got {}".format(type(values)))
        for k in values:
            ret.__dict__[k] = values[k]
        return ret
        
    def __eq__(self, other):
        try:
            return self.__dict__ == other.__dict__
        except:
            return False
    def __ne__(self, other):
        return not self.__eq__(other)
        
    def __str__(self, short=True):
        if short:
             s= "{} dB".format(self.median)
        else:
            s = "Max: {} dB | Med: {} dB | SD: {} dB | Peak: {} | TC: {} | SNB: {}".format(self.max, self.median, self. stddev, self.rel_peak_pos, self.temp_centroid, self.s2b)
        s = s.replace("None", "--")
        return s
