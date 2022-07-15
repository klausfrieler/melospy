""" Class implementation of Accents """

import melospy.basic_representations.jm_stats as jm_stats
import melospy.basic_representations.jm_util as jm_util
from melospy.basic_representations.rhythm import *


class AccentsBase(object):
    """(Virtual) Base class for various accents"""

    def __init__(self, baseAccent=1., noAccent=0.):
        """ Initialize AccentsBase object """
        self.baseAccent = baseAccent
        self.noAccent = noAccent

    def setBaseAccent(self, ba):
        self.baseAccent = ba

    def setNoAccent(self, na):
        self.noAccent = na

    def getMaxValue(self):
        return self.baseAccent

    def setParams(self, params):
        #print "setParam: ", params
        for key in self.__dict__:
            #print "Key: ", key
            try:
                self.__dict__[key] = params[key]
            except:
                pass

    def calculate(self, rhythm):
        return NotImplemented

class AccentFactory(object):
    """Factory class for create Accent objects"""
    def __init__(self):
        pass

    def create(self, accent_id, **kwargs):
        accent_id = accent_id.lower().replace("_", "-")
        accent_obj = None
        if accent_id == "const":
            accent_obj = ConstantAccent(**kwargs)
        elif accent_id == "external":
            accent_obj = ExternalAccents(**kwargs)
        elif accent_id == "gauss-standard":
            accent_obj= GaussificationStandardAccents(**kwargs)
        elif accent_id == "periodic":
            accent_obj= PeriodicAccents(**kwargs)
        elif accent_id == "threshold":
            accent_obj= ThresholdAccents(**kwargs)
        elif accent_id == "jumpbef3":
            accent_obj= JumpAccents(threshold=3, abs_mode=True, position="before")
        elif accent_id == "jumpbef4":
            accent_obj= JumpAccents(threshold=4, abs_mode=True, position="before")
        elif accent_id == "jumpbef5":
            accent_obj= JumpAccents(threshold=5, abs_mode=True, position="before")
        elif accent_id == "jumpbef":
            accent_obj= JumpAccents(abs_mode=True, position="before", **kwargs)
        elif accent_id == "jumpaft3":
            accent_obj= JumpAccents(threshold=3, abs_mode=True, position="after")
        elif accent_id == "jumpaft4":
            accent_obj= JumpAccents(threshold=4, abs_mode=True, position="after")
        elif accent_id == "jumpaft5":
            accent_obj= JumpAccents(threshold=5, abs_mode=True, position="after")
        elif accent_id == "jumpaft":
            accent_obj= JumpAccents(abs_mode=True, position="after", **kwargs)
        elif accent_id == "jumpbea3":
            accent_obj= JumpAccents(threshold=3, abs_mode=True, position=["before", "after"])
        elif accent_id == "jumpbea4":
            accent_obj= JumpAccents(threshold=4, abs_mode=True, position=["before", "after"])
        elif accent_id == "jumpbea5":
            accent_obj= JumpAccents(threshold=5, abs_mode=True, position=["before", "after"])
        elif accent_id == "jumpbea":
            accent_obj= JumpAccents(abs_mode=True, position=["before", "after"], **kwargs)
        elif accent_id == "jumploc":
            accent_obj= JumpLocalAccents(**kwargs)
        elif accent_id == "jumploc2":
            accent_obj= JumpLocalAccents(threshold=2, direction_change=False)
        elif accent_id == "pextrem":
            accent_obj= PitchExtremaAccents(type="plain", **kwargs)
        elif accent_id == "pextrmf":
            accent_obj= PitchExtremaAccents(type="mf", **kwargs)
        elif accent_id == "pextrst":
            accent_obj= PitchExtremaAccents(type="steinbeck", **kwargs)
        elif accent_id == "thom":
            accent_obj= ThomassenAccents(**kwargs)
        elif accent_id == "thom-thr":
            accent_obj= ThomassenAccents(threshold=.75)
        elif accent_id == "longpr":
            accent_obj= DurationAccents(mode="ioi", threshold=1, window_size=1, offset=0, classes=None)
        elif accent_id == "long2pr":
            accent_obj= DurationAccents(mode="ioi", threshold=2, window_size=1, offset=0, classes=None)
        elif accent_id == "longmod":
            accent_obj= DurationAccents(mode="ioi", threshold=1, window_size=-1, offset=0, classes=None)
        elif accent_id == "long2mod":
            accent_obj= DurationAccents(mode="ioi", threshold=2, window_size=-1, offset=0, classes=None)
        elif accent_id == "longpr-rel":
            accent_obj= DurationAccents(mode="ioi", threshold=1, window_size=1, offset=0, classes="rel")
        elif accent_id == "long2pr-rel":
            accent_obj= DurationAccents(mode="ioi", threshold=2, window_size=1, offset=0, classes="rel")
        elif accent_id == "longmod-rel":
            accent_obj= DurationAccents(mode="ioi", threshold=1, window_size=-1, offset=0, classes="rel")
        elif accent_id == "long2mod-rel":
            accent_obj= DurationAccents(mode="ioi", threshold=2, window_size=-1, offset=0, classes="rel")
        elif accent_id == "longpr-abs":
            accent_obj= DurationAccents(mode="ioi", threshold=1, window_size=1, offset=0, classes="abs")
        elif accent_id == "long2pr-abs":
            accent_obj= DurationAccents(mode="ioi", threshold=2, window_size=1, offset=0, classes="abs")
        elif accent_id == "longmod-abs":
            accent_obj= DurationAccents(mode="ioi", threshold=1, window_size=-1, offset=0, classes="abs")
        elif accent_id == "long2mod-abs":
            accent_obj= DurationAccents(mode="ioi", threshold=2, window_size=-1, offset=0, classes="abs")
        elif accent_id == "long-ioi":
            accent_obj= DurationAccents(mode="ioi", **kwargs)
        elif accent_id == "long-dur":
            accent_obj= DurationAccents(mode="dur", **kwargs)
        elif accent_id == "phrasbeg":
            accent_obj= StructureAccents(section_type="PHRASE", positions=["first"])
        elif accent_id == "phrasend":
            accent_obj= StructureAccents(section_type="PHRASE", positions=["last"])
        elif accent_id == "phrasbor":
            accent_obj= StructureAccents(section_type="PHRASE", positions=["first", "last"])
        elif accent_id == "phrase":
            accent_obj= StructureAccents(section_type="PHRASE", **kwargs)
        elif accent_id == "chorus":
            accent_obj= StructureAccents(section_type="CHORUS", **kwargs)
        elif accent_id == "form":
            accent_obj= StructureAccents(section_type="FORM", **kwargs)
        elif accent_id == "chords":
            accent_obj= StructureAccents(section_type="CHORD", **kwargs)
        elif accent_id == "bars":
            accent_obj= StructureAccents(section_type="BAR", **kwargs)
        elif accent_id == "beat1":
            accent_obj= MetricalAccents(positions=["primary"])
        elif accent_id == "beat3":
            accent_obj= MetricalAccents(positions=["secondary"])
        elif accent_id == "beat13":
            accent_obj= MetricalAccents(positions=["primary", "secondary"])
        elif accent_id == "beatall":
            accent_obj= MetricalAccents(positions=["all"])
        elif accent_id == "sync1":
            accent_obj= SyncopationAccents(positions=["primary"], anticipation_only=True)
        elif accent_id == "sync3":
            accent_obj= SyncopationAccents(positions=["secondary"], anticipation_only=True)
        elif accent_id == "sync13":
            accent_obj= SyncopationAccents(positions=["primary", "secondary"], anticipation_only=True)
        elif accent_id == "sync1234":
            accent_obj= SyncopationAccents(positions=["all"], anticipation_only=True)
        elif accent_id == "syncall":
            accent_obj= SyncopationAccents(positions=["all"], anticipation_only=False)
        elif accent_id == "sync":
            accent_obj= SyncopationAccents(**kwargs)
        elif accent_id == "swing-markers":
            accent_obj= SwingMarkers(**kwargs)
        elif accent_id == "triad":
            accent_obj= HarmonyAccents(include_upper=False, inverted=False)
        elif accent_id == "inchord":
            accent_obj= HarmonyAccents(include_upper=True, inverted=False)
        elif accent_id == "outchord":
            accent_obj= HarmonyAccents(include_upper=True, inverted=True)
        elif accent_id == "harmony":
            accent_obj= HarmonyAccents(**kwargs)
        elif accent_id == "monster":
            accent_obj= MonsterAccent(**kwargs)
        elif accent_id == "combi-accent":
            accent_obj= AccentCombinator(**kwargs)
        else:
            raise ValueError("Unknown accent type: {}".format(accent_id))

        return accent_obj

class AccentAggregator(AccentsBase):
    """
        Class for aggregating accents using different methods.
        Extends AccentsBase so allows nesting of aggregators.
    """

    def __init__(self):
        AccentsBase.__init__(self)
        self.accents = []
        self.type = "aggregator"
        self.max_val = None

    def getMaxValue(self):
        return self.max_val

    def add(self, accent_obj, weight=1.0):
        if not hasattr(accent_obj, "calculate"):
            raise ValueError("Expect Accent object, got {}".format(type(accent_obj)))
        self.accents.append((accent_obj, weight))

    def createAndAdd(self, accent_id, weight=1.0, **kwargs):
        af = AccentFactory()
        a = af.create(accent_id, **kwargs)
        self.add(a, weight=weight)

    def sumAccents(self, rhythm, normalize=None):
        total = [0 for _ in rhythm]
        for acc in self.accents:
            vals = acc[0].calculate(rhythm)
            total = [p + q for p, q, in zip(total, vals)]
            #print "Total:", total
        if normalize == "intrinsic":
            max_val = max(total)
            total = [p/max_val for p in total]
        elif normalize == "extrinsic":
            max_val = self._upper_limit()
            total = [p/max_val for p in total]
        return total

    def maxAccents(self, rhythm):
        total = [0 for _ in rhythm]
        for acc in self.accents:
            vals = acc[0].calculate(rhythm)
            total = [max(p, q) for p, q, in zip(total, vals)]
            #print "Total:", total
        return total

    def minAccents(self, rhythm):
        total = [0 for _ in rhythm]
        for acc in self.accents:
            vals = acc[0].calculate(rhythm)
            total = [min(p, q) for p, q, in zip(total, vals)]
            #print "Total:", total
        return total

    def threshold(self, rhythm, thresh=.5):
        total = [0 for _ in rhythm]
        for acc in self.accents:
            vals = acc[0].calculate(rhythm)
            if len(vals) == 0:
                total = vals
            else:
                for p, q, in zip(total, vals):
                    total = [p if p>thresh else q]
            #print "Total:", total
        return total

    def _upper_limit(self, type="sum"):
        total = 0
        for acc in self.accents:
            #print acc[0]
            if type=="sum":
                total += acc[0].getMaxValue()
            elif type=="max":
                total = max(total, acc[0].getMaxValue())
            elif type=="min":
                total = min(total, acc[0].getMaxValue())
            else:
                raise ValueError("Invalid type: {}".format(type))
        return total

    def calculate(self, rhythm, method="sum"):
        self.max_val = 1.
        if method == "sum":
            self.max_val = self._upper_limit(type="sum")
            return self.sumAccents(rhythm)
        elif method == "sum-norm":
            return self.sumAccents(rhythm, normalize="intrinsic")
        elif method == "sum-norm2":
            return self.sumAccents(rhythm, normalize="extrinsic")
        elif method == "max":
            self.max_val = self._upper_limit(type="max")
            return self.maxAccents(rhythm)
        elif method == "min":
            self.max_val = self._upper_limit(type="min")
            return self.minAccents(rhythm)
        else:
            raise ValueError("Unkown method: {}".format(method))

    def __str__(self):
        comp = "\n".join(" - " + str(acc[0]) for acc in self.accents)
        return "Accent aggregator:\n{}".format(comp)

class ExternalAccents(AccentsBase):

    def __init__(self, weights=None):
        """ Initialize Accents object """
        AccentsBase.__init__(self, 0.)
        self.weights = weights
        self.type = "external"

    def getMaxValue(self):
        return max(self.weights)

    def calculate(self, rhythm):
        l = len(self.weights)
        if l != len(rhythm):
            raise ValueError("Expected: {} weights got: {}".format(len(rhythm), l))
        return self.weights

    def __str__(self):
        return "External accent: Values={}".format(self.weights)

class ConstantAccent(AccentsBase):

    def __init__(self, baseAccent=1.):
        """ Initialize Accents object """
        AccentsBase.__init__(self, baseAccent)
        self.type = "const"

    def calculate(self, rhythm):
        ba = self.baseAccent
        accents = [ba for _ in range(len(rhythm))]
        return accents

    def __str__(self):
        return "Constant accent: Value={}".format(self.baseAccent)

class PeriodicAccents(AccentsBase):

    def __init__(self, period=2, weight=1., phase=0, baseAccent=0.):
        """ Initialize PeriodicAccents object """
        AccentsBase.__init__(self, baseAccent)
        self.period = period
        self.weight = weight
        self.phase  = phase
        self.type = "periodic"

    def calculate(self, rhythm):
        accents = []
        for i in range(len(rhythm)):
            if i % self.period == self.phase:
                accents.append(self.weight)
            else:
                accents.append(self.baseAccent)
        return accents

    def __str__(self):
        return "Periodic accent: Period={}, phase={}, w={}".format(self.period, self.phase, self.weight)

class ThresholdAccents(AccentsBase):
    """
        Threshold accents. Abstract base class.
        Generates an accent if a certain threshold is exceeded.
        Typical example are interval jumps.
        The accent can apply to different positions:
            'on-site': The accent is given to the position where the threshold is crossed.
            'before': The accent is given to the position right before the threshold is crossed.
            'after': The accent is given to the position right after the threshold is crossed.
        All theses values can be combined in using a list of position parameters
        Furthermore, threshold passing can be defined on absolute or true values.
        """

    def __init__(self, threshold=1, abs_mode=True, position="onsite", baseAccent=1.):
        AccentsBase.__init__(self, baseAccent)
        self.threshold = threshold
        self.abs_mode = abs_mode
        self.setPosition(position)

    def _preprocess(self, rhythm, **kwargs):
        """Quasi-virtual method to be overridden in derived classes"""
        return rhythm
        #return NotImplemented

    def _position_adjust(self, accents):
        ret = [self.noAccent for _ in accents]
        positions = list(set(self.position))
        for pos in positions:
            tmp = []
            #print "Evaluating:", pos
            if pos == "before":
                tmp = accents[1:]
                tmp.append(self.noAccent)
            elif pos == "after":
                tmp = [self.noAccent]
                tmp.extend(accents[:-1])
            elif pos == "onsite":
                tmp = accents
            ret = [max(p, q) for p, q in zip(ret, tmp)]
        return ret

    def _postprocess(self, accents, **kwargs):
        """Quasi-virtual method to be overridden in derived classes"""
        ret = self._position_adjust(accents)
        return ret

    def setPosition(self, position):
        self.position = position
        if not isinstance(self.position, list):
            self.position = [self.position]

    def addPosition(self, position):
        self.position.append(position)

    def calculate(self, rhythm):
        accents = []
        try:
            abstraction = self._preprocess(rhythm)
        except Exception as e:
            raise e
        threshold = self.threshold
        if threshold < 0 and not self.abs_mode:
            threshold = -threshold
        for v in abstraction:
            if self.abs_mode:
                val = abs(v)
            else:
                val = v if self.threshold>0 else -v

            if val>=threshold:
                accents.append(self.baseAccent)
            else:
                accents.append(self.noAccent)
        accents = self._postprocess(accents)
        return accents

    def __str__(self):
        return "Threshold accent: Abs_mode={}, threshold={}, position={}".format(self.abs_mode, self.threshold, self.position)

class JumpAccents(ThresholdAccents):

    def __init__(self, threshold=1, abs_mode=True, position="onsite", baseAccent=1.):
        ThresholdAccents.__init__(self, threshold, abs_mode, position, baseAccent)

    def _position_adjust(self, accents):
        ret = [self.noAccent for _ in range(len(accents)+1)]

        positions = list(set(self.position))
        for pos in positions:
            tmp = []
            #print "Evaluating:", pos
            if pos == "after":
                tmp = [self.noAccent]
                tmp.extend(accents)
            elif pos == "before":
                tmp = accents
                tmp.append(self.noAccent)
            ret = [max(p, q) for p, q in zip(ret, tmp)]
        return ret

    def _postprocess(self, accents, **kwargs):
        """Quasi-virtual method to be overridden in derived classes"""
        ret = self._position_adjust(accents)
        return ret

    def _preprocess(self, rhythm, **kwargs):
        """Quasi-virtual method to be overridden in derived classes"""
        intervals = rhythm.intervals()
        try:
            intervals = rhythm.intervals()
        except:
            raise ValueError("Expected at least NoteTrack object. Got: {}".format(type(rhythm)))
        return intervals

    def __str__(self):
        return "Jump accent: Abs_mode={}, threshold={}, position={}".format(self.abs_mode, self.threshold, self.position)

class JumpLocalAccents(AccentsBase):

    def __init__(self, threshold=1, direction_change=False, baseAccent=1.):
        AccentsBase.__init__(self, baseAccent)
        self.dir_change = direction_change
        self.threshold = threshold

    def _preprocess(self, rhythm, **kwargs):
        """Quasi-virtual method to be overridden in derived classes"""
        intervals = rhythm.intervals()
        try:
            intervals = rhythm.intervals()
        except:
            raise ValueError("Expected at least NoteTrack object. Got: {}".format(type(rhythm)))
        return intervals

    def calculate(self, rhythm):
        intervals = self._preprocess(rhythm)
        l = len(intervals)
        if l<3:
            return [0]*(l+1)
        thresh = self.threshold
        tmp = [self.noAccent]*2
        for i in range(1, l-1):
            int_bef = intervals[i-1]
            int_on = intervals[i]
            int_aft = intervals[i+1]

            accent = self.noAccent
            if abs(int_on) >= abs(int_bef) + thresh and abs(int_on) >= abs(int_aft)+thresh:
                if self.dir_change:
                    s1 = int_bef/abs(int_bef)
                    s2 = int_on/abs(int_on)
                    s3 = int_aft/abs(int_aft)
                    if s1*s2<0 and s2*s3<0:
                        accent = self.baseAccent
                else:
                    accent = self.baseAccent
            tmp.append(accent)
        tmp.append(self.noAccent)
        assert(len(tmp) == len(rhythm))
        return tmp

    def __str__(self):
        return "JumpLocal accent: direction_change={}, threshold={}".format(self.dir_change, self.threshold)

class PitchExtremaAccents(AccentsBase):
    """
        Pitch extremum accents.
        Possible types:
            'plain'
            'mf'
            'steinbeck'
    """
    def __init__(self, type="plain", baseAccent=1.):
        AccentsBase.__init__(self, baseAccent)
        self.type = type

    def _sgn(self, v):
        return abs(v)/v if v != 0 else 0

    def _contour(self, vec):
        if self.type == "plain" or self.type == "mf":
            if len(vec) != 3:
                raise ValueError("Expected list of length 3, got {}".format(len(vec)))
            cont = jm_util.huron_contour(vec, format="redcode")
            #if self.type == "mf":
            #    print vec, cont
            if self.type == "mf" and vec[0] == vec[-1]:
                cont = ""
        elif self.type == "steinbeck":
            if len(vec) != 5:
                raise ValueError("Expected list of length 5, got {}".format(len(vec)))
            signs = [self._sgn(v) for v in jm_util.diff(vec)]
            s1 = signs[0]*signs[1]
            s2 = signs[2]*signs[3]
            #print vec, signs, s1, s2
            if s1 > 0 and s2 > 0 and signs[0] != signs[2]:
                cont = "convex" if signs[0] > 0 else "concave"
            else:
                cont = ""
        else:
            raise ValueError("Invalid contour type: {}".format(self.type))
        return cont

    def _contourify(self, notetrack, window=3):
        if window<3 or window % 2 == 0:
            raise ValueError("Window size must be at least 3 and odd, got:{}".format(window))
        try:
            pitches = notetrack.pitches
        except:
            raise ValueError("Expected at least NoteTrack object. Got: {}".format(type(notetrack)))

        if len(pitches) < window:
            return ["" for _ in range(len(pitches))]

        cut = int(round(window//2))
                    
        contours = ["" for _ in range(cut)]
        for i in range(len(pitches)-window+1):
            hc = self._contour(pitches[i:i + window])
            contours.append(hc)
            
        contours.extend(["" for _ in range(cut)])
        return contours

    def calculate(self, notetrack):
        if self.type == "plain" or self.type == "mf":
            window = 3
        elif self.type =="steinbeck":
            window = 5
        contours = self._contourify(notetrack, window)
        accents = []
        for c in contours:
            if c == "convex" or c=="concave":
                accents.append(self.baseAccent)
            else:
                accents.append(self.noAccent)
        return accents

    def __str__(self):
        return "Pitch extrema accent: Type={}".format(self.type)

class ThomassenAccents(AccentsBase):

    def __init__(self, threshold=None):
        AccentsBase.__init__(self)
        self.threshold = threshold

    def _get_weight(self, pvec, mode):
        #print pvec, len(pvec)
        assert(len(pvec) == 3)
        val = 0
        weights = [0, 0, 0, 1, .5, .71, 1, .83, .33]
        code  = jm_util.huron_contour(pvec, format="number")
        val = weights[code]
        if mode == "first" and code != 0:
            val = 1 - val;
        return val;

    def getMaxValue(self):
        return 1.

    def calculate(self, notetrack):
        try:
            pitches = notetrack.pitches
        except:
            raise ValueError("Expected at least NoteTrack object. Got: {}".format(type(notetrack)))
        pitches.insert(0, pitches[0])
        pitches.insert(0, pitches[0])
        pitches.insert(len(pitches), pitches[-1])
        accents = []

        for i in range(2, len(pitches)-1):
            p1 = self._get_weight(pitches[i-2:i+1], mode="first")
            p2 = self._get_weight(pitches[i-1:i+2], mode="second")
            val = p1*p2
            if self.threshold != None:
                val = 1 if p1*p2 > self.threshold else 0
            accents.append(round(val, 5))

        assert(len(accents) == len(notetrack))
        return accents

    def __str__(self):
        return "Thomassen accent: Threshold={}".format(self.threshold)

class DurationAccents(AccentsBase):

    def __init__(self, mode="ioi", classes=None, threshold=1, offset=0, window_size=-1, baseAccent=1.):
        AccentsBase.__init__(self, baseAccent)
        self.mode = mode
        self.classes = classes
        self.threshold = threshold
        self.window_size = window_size
        self.offset = offset
        self.cache_ref = None

    def _get_raw_data(self, rhythm):
        if self.mode == "ioi":
            try:
                vec = rhythm.iois
            except:
                raise ValueError("Expected at least Rhythm object. Got: {}".format(type(rhythm)))
        elif self.mode == "dur":
            try:
                vec = rhythm.durations
            except:
                raise ValueError("Expected at least Rhythm object. Got: {}".format(type(rhythm)))
        return vec

    def _preprocess(self, rhythm):
        if self.classes == None:
            return self._get_raw_data(rhythm)
        try:
            vec = rhythm.durationClassification(type=self.mode, mode=self.classes)
        except:
            try:
                vec = rhythm.durationClassification(type=self.mode)
            except Exception as e:
                if self.classes == "rel":
                    msg = "Expected at least MeterGrid object. Got: {}".format(type(rhythm))
                else:
                    msg = e
                raise ValueError(msg)
        return vec

    def _get_mode(self, vec):
        mode = jm_stats.mode(vec)
        try:
            ret = mode[0]
            #if mode has more than one value,
            #use the most recent in vec
            for v in reversed(vec):
                if v in list(mode):
                    return v
        except:
            ret = mode
        return ret

    def _get_mean(self, vec):
        mean = jm_stats.mean(vec)
        return mean

    def _get_ref_value(self, vec, i):

        if self.window_size<0:
            if self.cache_ref != None:
                return self.cache_ref
            past = vec
        else:
            past = vec[max(i-self.window_size, 0):i]
            #print "I:{}, past: {}".format(i, past)

        if self.classes != None:
            ref = self._get_mode(past)
        else:
            ref = self._get_mean(past)

        if self.window_size < 0:
            self.cache_ref = ref

        return ref

    def calculate(self, rhythm):
        vec = self._preprocess(rhythm)
        #print self
        if self.window_size>0:
            accents = [0.]*self.window_size
        else:
            accents = []

        start = self.window_size if self.window_size>0 else 0

        for i in range(start, len(vec)):
            ref = self._get_ref_value(vec, i)
            val = self.noAccent
            if self.classes:
                if (vec[i] - ref) >= self.threshold:
                    val = self.baseAccent
                    #print "i={}, ref={}, vec[i]={}, diff={}, th={}, val={}".format(i, ref, vec[i], vec[i]-ref,self.threshold, val)
            else:
                if vec[i] > ref * self.threshold + self.offset:
                    val = self.baseAccent
                    #print "i={}, ref={}, vec[i]={}, comp={}, th={}, val={}".format(i, ref, vec[i], ref * self.threshold + self.offset, self.threshold, val)
            accents.append(val)
        #print sum(accents)/len(accents)
        accents.append(self.baseAccent)
        #print "len(accents) ={} len(rhythm) = {}".format(len(accents), len(rhythm))
        #assert(len(accents) == len(rhythm))
        return accents

    def __str__(self):
        return "Duration accent: mode={}, classes={}, window_size={}, threshold={}, offset={}".format(self.mode, self.classes, self.window_size, self.threshold, self.offset)

class StructureAccents(AccentsBase):

    def __init__(self, section_type="PHRASES", positions=["first"], baseAccent = 1.):
        AccentsBase.__init__(self, baseAccent)
        self.section_type = section_type
        self.positions = list(set(positions))
        self.first = False
        self.last = False

    def _set_position_marker(self):
        if "first" in self.positions or "begin" in self.positions:
            self.first = True
        if "last" in self.positions or "end" in self.positions:
            self.last = True

    def _preprocess(self, rhythm):
        try:
            section = rhythm.getSection(self.section_type)
        except Exception as e:
            raise e
        return section

    def calculate(self, solo):
        accents = [self.noAccent]*len(solo)

        section = self._preprocess(solo)
        if section == None or len(section) == 0:
            print("Section {} not available".format(self.section_type))
            return accents
        self._set_position_marker()
        for sect in section:
            if self.first:
                accents[sect.startID] = self.baseAccent
            if self.last:
                accents[sect.endID] = self.baseAccent
        return accents

    def __str__(self):
        return "Structure accent: section type={}, positions={}".format(self.section_type, self.positions)

class SwingMarkers(AccentsBase):
    def __init__(self, max_div=4, only_full=False, baseAccent=1):
        self.max_div = max_div
        self.only_full = False
        AccentsBase.__init__(self, baseAccent, noAccent=0)

    def _preprocess(self, metergrid):
        try:
            mpos = metergrid.getMetricalPositions()
        except:
            raise ValueError("Expected at least MeterGrid object. Got: {}".format(type(notetrack)))
        return mpos

    def calculate(self, metergrid):
        mpos = self._preprocess(metergrid)
        accents = [self.noAccent] * len(metergrid)
        cands = metergrid.getSwingCandidates(max_div=self.max_div, only_full=self.only_full)
        for i in cands:
            accents[i] = self.baseAccent
        return accents

class MetricalAccents(AccentsBase):

    def __init__(self, positions=["primary"], baseAccent=1.0):
        AccentsBase.__init__(self, baseAccent)
        self.positions = list(set(positions))
        self.primary = False
        self.secondary = False
        self.all = False

    def _preprocess(self, metergrid):

        try:
            mpos = metergrid.getMetricalPositions()
        except:
            raise ValueError("Expected at least MeterGrid object. Got: {}".format(type(notetrack)))
        return mpos

    def _set_position_marker(self):
        #primary accent in measure
        if "primary" in self.positions or "first" in self.positions:
            self.primary = True
        #secondary accents in measure
        if "secondary" in self.positions or "second" in self.positions:
            self.secondary = True
        #all beats in measure
        if "all" in self.positions:
            self.all = True

    def _is_secondary_accent(self, mpos):
        if mpos.period < 4:
            return False
        part = two_three_partition(mpos.period, twoleads=False)
        positions = [1]
        positions.extend(part)
        cs = cumsum(positions)[1:-1]
        #print "MP={}, Period={}, Part={}, positions={}, cs={}".format(mpos, mpos.period, part, positions, cs)
        if mpos.beat in cs:
            return True
        return False

    def calculate(self, metergrid):
        mpos = self._preprocess(metergrid)
        accents = [self.noAccent] * len(metergrid)
        self._set_position_marker()
        for i, m in enumerate(mpos):
            if m.tatum != 1:
                continue
            if self.all:
                #print "All:", m
                accents[i] = self.baseAccent
                continue
            if self.primary:
                if m.beat == 1:
                    #print "First:", m
                    accents[i] = self.baseAccent
            if self.secondary:
                if self._is_secondary_accent(m):
                    #print "Second:", m
                    accents[i] = self.baseAccent
        return accents
    def __str__(self):
        return "Metrical accent: positions={}".format(self.positions)

class SyncopationAccents(MetricalAccents):

    def __init__(self, positions=["primary"], anticipation_only = False, baseAccent=1.0):
        MetricalAccents.__init__(self, positions, baseAccent)
        self.anticipation_only = anticipation_only

    def calculate(self, metergrid):
        accents = [self.noAccent] * len(metergrid)
        self._set_position_marker()

        mpos = self._preprocess(metergrid)
        syncs = metergrid.syncopations()

        assert(len(syncs)== len(mpos))

        if not self.anticipation_only:
            for i in range(len(syncs)):
                accents[i] = self.baseAccent if syncs[i]>0. else self.noAccent
            return accents

        for i, m in enumerate(mpos):
           if syncs[i] ==0 or i == len(mpos)-1:
               continue
           next_pos = mpos[i+1]
           if self.all:
               if m.beat != next_pos.beat:
                   accents[i] = self.baseAccent
           if self.primary:
               if m.beat != next_pos.beat and next_pos.beat == 1:
                   accents[i] = self.baseAccent
           if self.secondary:
               if m.beat != next_pos.beat and self._is_secondary_accent(next_pos):
                   accents[i] = self.baseAccent

        return accents
    def __str__(self):
        return "Syncopation accent: positions={}, anticipation only={}".format(self.positions, self.anticipation_only)

class HarmonyAccents(AccentsBase):

    def __init__(self, include_upper=False, inverted=False, baseAccent=1.0):
        AccentsBase.__init__(self, baseAccent)
        self.include_upper = include_upper
        self.inverted = inverted

    def _preprocess(self, solo):
        #cpt = solo.getChordalPitchTypes()
        try:
            cpt = solo.getChordalPitchTypes()
        except:
            raise ValueError("Chord annotation missing.")
        return cpt

    def calculate(self, solo):
        cpt = self._preprocess(solo)
        #print "cpt", cpt
        accent = self.baseAccent
        noAccent = self.noAccent
        if self.inverted:
            accent, noAccent = noAccent, accent

        accents = [noAccent] * len(cpt)
        inside = ['1', '3', '5', '7']
        if self.include_upper:
            inside.append('u')
        for i, c in enumerate(cpt):
            if c in inside:
                accents[i] = accent
        return accents

class GaussificationStandardAccents(AccentsBase):
    """ Standards gaussification acccents as used by the Beatometer algorithm"""

    def __init__(self, a_min=2, a_maj=3, sigma=.05, baseAccent = 1.):
        AccentsBase.__init__(self, baseAccent)
        self.a_min = a_min
        self.a_maj = a_maj
        self.sigma = sigma

    def setParams(self, params):
        try:
            self.sigma = params["sigma"]
            self.a_min = params["a_min"]
            self.a_maj = params["a_maj"]
        except:
            raise ValueError("Invalid parameters {} for Gaussification Standard Accents".format(params))

    def getMaxValue(self):
        return max([self.baseAccent, self.a_maj, self.a_min])

    def calculate(self, rhythm):
        try:
            iois = rhythm.getIOIs()
        except:
            raise ValueError("Invalid rhythm (type: {})".format(type(rhythm)))
        #first element always get minor accent
        accents = [self.a_min]
        if len(iois)<1:
            return accents
        for i in range(1, len(iois)):
            assert(iois[i] != 0)
            curr_accent = self.baseAccent
            #print "="*60
            #print iois[i-1], iois[i]
            #print (iois[i]-2*sigma)/iois[i-1], (iois[i]+sigma)/iois[i-1]

            if (iois[i]-2*self.sigma)/iois[i-1]>1.5:
                curr_accent = self.a_min
            if (iois[i]+self.sigma)/iois[i-1]>2:
                curr_accent = self.a_maj
            #print "Acc: ", curr_accent
            accents.append(curr_accent)
        accents.append(self.a_min)
        assert(len(accents) == len(rhythm))
        return accents

    def __str__(self):
        return "Gaussification standard accents: a_min={}, a_maj={}, sigma={}".format(self.a_min, self.a_maj, self.sigma)

class AccentCombinator(AccentsBase):

    def __init__(self, accents= [], weights=[], method="sum", baseAccent=1.):
        AccentsBase.__init__(self, baseAccent)
        self.method = method
        self.accents = accents
        if len(weights) == len(accents):
            self.weights = weights
        elif len(weights) == 0:
            self.weights = [1.]*len(accents)
        else:
            raise ValueError("Got {} weights, expected {}".format(len(weights), len(accents)))

    def calculate(self, solo):
        ag = AccentAggregator()
        offensives = []
        for acc in self.accents:
            try:
                ag.createAndAdd(acc)
            except:
                offensives.append(acc)
        accents = ag.calculate(solo, method=self.method)
        if len(offensives):
            print("There were {} invalid accents: {}".format(len(offensives), r"\,".join(offensives)))
        return accents

class MonsterAccent(AccentsBase):
    def __init__(self, method="sum", baseAccent=1.):
        AccentsBase.__init__(self, baseAccent)
        self.method = method

    def calculate(self, solo):
        ag = AccentAggregator()
        ag.createAndAdd("jumpaft3")
        #ag.createAndAdd("jumpbea4")
        #ag.createAndAdd("jumpbea5")
        ag.createAndAdd("jumploc2")
        ag.createAndAdd("pextrem")
        #ag.createAndAdd("pextrmf")
        #ag.createAndAdd("pextrst")
        #ag.createAndAdd("thom")
        ag.createAndAdd("longpr")
        #ag.createAndAdd("long2pr")
        ag.createAndAdd("longmod")
        #ag.createAndAdd("long2mod")
        ag.createAndAdd("phrasbor")
        ag.createAndAdd("beat1")
        ag.createAndAdd("beat13")
        ag.createAndAdd("beatall")
        ag.createAndAdd("sync1")
        ag.createAndAdd("sync13")
        ag.createAndAdd("sync1234")
        #ag.createAndAdd("syncall")
        ag.createAndAdd("inchord")
        accents = ag.calculate(solo, method=self.method)
        return accents
