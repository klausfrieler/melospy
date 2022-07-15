""" Class implementation of TimeSeries """
from functools import cmp_to_key

from melospy.basic_representations.jm_util import find_first_gt, find_last_lt, get_huron_code_raw
from melospy.basic_representations.note_track import *
from melospy.basic_representations.rhythm import *


class TimeSeries(object):

    def __init__(self, other=None, deltaT=None):
        """ Initialize TimeSeries object """
        self.__deltaT = deltaT
        #print "TS::init", deltaT, self.__deltaT
        self.__ts = []
        if isinstance(other, TimeSeries):
            self.__deltaT = other.__deltaT
            self.__ts= [e for e in other.__ts]
        elif isinstance(other, NoteTrack):
            self.__ts= [(e.onset, e.pitch) for e in other.getEvents()]
        elif isinstance(other, Rhythm):
            self.__ts= [(e.onset, e.duration) for e in other.getEvents()]
        elif isinstance(other, list):
            try:
                tmp = [(t, v) for t, v in other]
                self.__ts = tmp
            except:
                pass

    def clone(self):
        """ Provides deep copy """
        ts = TimeSeries()
        tmp = []
        for t in self.__ts:
            tmp.append(t)
        ts.__ts= tmp
        return ts

    @staticmethod
    def fromValues(values, start, deltaT):
        ts = TimeSeries(deltaT=deltaT)
        t = start
        tmp = []
        for v in values:
            tmp.append((t, v))
            t += deltaT
        ts.setTimeSeries(tmp)
        return ts

    def toRhythm(self):
        r = Rhythm()
        for e in self.__ts:
            r.append(RhythmEvent(e[0], 0, e[1]))
        return r

    def toDict(self):
        r = {}
        for e in self.__ts:
            r[e[0]] = e[1]
        return r

    def append(self, v):
        self.__ts.append(v)
        return self

    def extend(self, ts):
        if isinstance(ts, TimeSeries):
            self.__ts.extend(ts.timeseries)
        else:
            self.__ts.extend(ts)
        return self

    def merge(self, ts, resolve=""):
        self.extend(ts)
        return self.sortByTime()

    def _fuse_func(self, x, y, wt, wv):
        t = wt[0]*x[0] + wt[1]*y[0]
        v = wv[0]*x[1] + wv[1]*y[1]

        return (t, v)

    def _get_fuse_weights(self, fuse="linear"):
        if fuse == "linear":
            wt = (0.5, 0.5)
        elif fuse == "left":
            wt = (1.0, 0.0)
        elif fuse == "right":
            wt = (0.0, 1.0)
        return wt

    def fuse(self, min_dt, fuse_t="linear", fuse_v="linear"):
        ts = TimeSeries()
        wt = self._get_fuse_weights(fuse_t)
        wv = self._get_fuse_weights(fuse_v)
        skip_next  = False
        for i in range(len(self)-1):

            d = self.__ts[i+1][0]-self.__ts[i][0]
            if d > min_dt:
                if not skip_next:
                    ts.append(self.__ts[i])
                skip_next = False
            else:
                ip = self._fuse_func(self.__ts[i], self.__ts[i+1], wt, wv)
                ts.append(ip)
                skip_next = True
        if not skip_next:
            ts.append(self.__ts[-1])
        return ts

    def isEmpty(self):
        """ Length of event list"""
        return len(self.__ts) == 0

    def getDeltaT(self):
        return self.__deltaT

    def setDeltaT(self, deltaT):
        self.__deltaT = deltaT
        return self

    def startTime(self):
        """ Returns onset of first event"""
        if self.isEmpty():
            raise RuntimeError("Timseries empty")
        return self.__ts[0][0]

    def endTime(self):
        """ Returns end of last event"""
        if self.isEmpty():
            raise RuntimeError("Timseries empty")
        return self.__ts[-1][0]

    def getTimes(self):
        """ Return onsets as list"""
        return [t[0] for t in self.__ts]

    def getValues(self):
        """ Return values as list"""
        return [t[1] for t in self.__ts]

    def getTimeSeries(self):
        """ Get (t, y(t)) list"""
        return self.__ts

    def setTimeSeries(self, ts):
        """ Set (t, y(t)) list"""
        self.__ts = ts
        return self

    def first(self):
        """ Get first value pair in list"""
        if self.isEmpty():
            return None
        return self.__ts[0]

    def last(self):
        """ Get last value pair in list"""
        if self.isEmpty():
            return None
        return self.__ts[-1]

    def _getExtremaType(self, v1, v2, v3, mode="strict"):
        c = 3* get_huron_code_raw(v1, v2) + get_huron_code_raw(v2, v3)
        #The Huron Code:
        #str_codes = ["desc", "desc-hor", "concave", "hor-desc", "hor", "hor-asc", "convex", "asc-hor", "asc"]
        if mode == "strict":
            ext_codes = ["", "", "min", "", "", "", "max", "", ""]
        else:
            ext_codes = ["", "min", "min", "max", "", "min", "max", "max", ""]

        return ext_codes[c+4]

    def extrema(self, mode="strict"):
        if mode.lower() not in ["strict", "relaxed"]:
            raise ValueError("Invalid extrema mode. Expected 'strict' or 'relaxed', got {}".format(mode))
        if self.isEmpty():
            return None
        extrema = []
        tmp = 0
        l = len(self)
        if l==1:
            return [(0, self.__ts[0][1], "min")]
        if l==2:
            v1 = self.__ts[0][1]
            v2 = self.__ts[1][1]

            c = get_huron_code_raw(v1, v2)
            if c == -1:
                extrema.append((0, v1, "max"))
                extrema.append((1, v2, "min"))
            elif c == 1:
                extrema.append((0, v1, "min"))
                extrema.append((1, v2, "max"))
            elif c == 0:
                if mode != "strict":
                    extrema.append((0, v1, "min"))
                    extrema.append((1, v2, "min"))

            return extrema

        for i in range(l-1):
            ext_t = "min"
            v1 = self.__ts[i][1]
            if i == 0:
                v2 = self.__ts[1][1]
                c = get_huron_code_raw(v1, v2)
                if c == -1:
                    extrema.append((0, v1, "max"))
                elif c == 1:
                    extrema.append((0, v1, "min"))
                elif c == 0:
                    if mode != "strict":
                        extrema.append((0, v1, "min"))
                continue
            v1 = self.__ts[i-1][1]
            v2 = self.__ts[i][1]
            v3 = self.__ts[i+1][1]
            ext_t = self._getExtremaType(v1, v2, v3, mode)

            if len(ext_t)>0:
                extrema.append((i, v2, ext_t))

        v1 = self.__ts[-2][1]
        v2 = self.__ts[-1][1]
        c = get_huron_code_raw(v1, v2)
        if c==-1:
            extrema.append((l-1, v2, "min"))
        elif c==1:
            extrema.append((l-1, v2, "max"))

        return extrema

    def _argext(self, ext_t="", mode="strict"):
        ext = self.extrema(mode)
        args = []
        if ext==None or len(ext)==0:
            return args
        for e in ext:
            found = False
            if len(ext_t)>0:
                if e[2] == ext_t:
                    found = True
            else:
                found = True
            if found:
                args.append(e[0])
        return args

    def argmin(self, mode="strict"):
        return self._argext("min", mode)

    def argmax(self, mode="strict"):
        return self._argext("max", mode)

    def maxvals(self, mode="strict", as_ts=True):
        argmax = self.argmax(mode)
        if as_ts:
            vals = TimeSeries()
        else:
            vals = []
        for i in argmax:
            vals.append(self[i])
        return vals

    def minvals(self, mode="strict", as_ts=True):
        argmin = self.argmin(mode)
        if as_ts:
            vals = TimeSeries()
        else:
            vals = []
        for i in argmin:
            vals.append(self[i])
        return vals

    def approxGradient(self, pos):
        try:
            p1 = self[pos]
            p2 = self[pos+1]
        except:
            return None
        return (p2[1]-p1[1])/(p2[0]-p1[0])

    def gradientList(self, mode="relaxed", format="simple"):
        ret = []
        ext = self.extrema(mode)
        if ext[0][0] !=0:
            ext.insert(0, (0, self[0][1], "min"))
            #print "Front", ext
        if ext[-1][0] !=len(self)-1:
            ext.append((len(self)-1, self[len(self)-1][1], "min"))
            #print "Back", ext
        for i in range(len(ext)-1):
            p1 = self[ext[i][0]]
            p2 = self[ext[i+1][0]]
            if format == "with-time" or format=="simple":
                l = (p2[1]-p1[1])/(p2[0]-p1[0])
            elif format == "with-index":
                l = (p2[1]-p1[1])/(ext[i+1][0]-ext[i][0])
            #if l==0:
            #    print "i:{}, p1: {}, p2:{}, l:{}".format(i,p1, p2, l)
            if format == "simple":
                ret.append(l)
            elif format == "with-time":
                ret.append((p1, l))
            elif format == "with-index":
                #ret.append((ext[i][0], l))
                ret.append(l)
            else:
                raise ValueError("Invalid format. Expected 'simple', 'with-time' or 'with-index'. Got:{}".format(format))
        return ret

    def peakSaliences(self, mode="strict", as_ts=True):
        argmax = self.argmax(mode)
        if as_ts:
            vals = TimeSeries()
        else:
            vals = []
        for i in argmax:
            l = self.approxGradient(i-1)
            r = self.approxGradient(i+1)
            if l == None:
                l = r
            if r == None:
                r = l
            try:
                val = .5*(abs(l) + abs(r))
            except:
                val = None
            vals.append((self[i][0], val))
        return vals

    def maxsals(self, mode="strict"):
        max_v = self.maxvals(mode)
        sal = self.peakSaliences(mode)
        return max_v.mult(sal)

    def apply(self, func):
        vals = TimeSeries(deltaT=self.deltaT)
        tmp = list(map(func, self))
        try:
            tmp = list(map(func, self))
        except:
            raise ValueError("Function does not fit")
        try:
            t, v = tmp[0]
        except:
            raise ValueError("Function does not return timeseries")

        vals.timeseries = tmp
        return vals


    def mult(self, other):
        if self.deltaT != other.deltaT or  len(self) != len(other):
            raise ValueError("Attempt to multiply incompatible objects")
        ts = TimeSeries(deltaT=self.deltaT)
        for i in range(len(self)):
            if self[i][0] != other[i][0]:
                raise ValueError("Attempt to multiply incompatible objects")
            ts.append((self[i][0], self[i][1]*other[i][1]))
        return ts

    def scale(self, factor):
        return self.apply(lambda e: (e[0], e[1]*factor))

    def sortByVal(self, reverse=False):
        if reverse:
            self.__ts.sort(key=cmp_to_key(lambda x, y: get_huron_code_raw(x[1], y[1])))
        else:
            self.__ts.sort(key=cmp_to_key(lambda x, y: get_huron_code_raw(y[1], x[1])))
        return self

    def sortByTime(self, reverse=False):
        if reverse:
            self.__ts.sort(key=cmp_to_key(lambda x, y: get_huron_code_raw(x[0], y[0])))
        else:
            self.__ts.sort(key=cmp_to_key(lambda x, y: get_huron_code_raw(y[0], x[0])))
        return self

    def moveElement(self, which, new_time, max_dist=None):
        d = self.__ts[which][0]-new_time
        if float_equal(d, 0):
            #print "Not moved, |d|=0"
            return 0

        if max_dist != None and abs(d)>abs(max_dist):
                #print "Not moved, since |d|={:0.3f}>|max_d|={:0.3f}".format(abs(d), abs(max_dist))
                return 0
        #print "Moved {:0.3f} -> {:0.3f} (d={:0.3f})".format(self.__ts[which][0], new_time, d)
        self.__ts[which] = (new_time, self.__ts[which][1])
        return d

    def magneticMove(self, ts, max_dist=None):
        closest = self.findClosest(ts)
        #print closest
        assert(len(closest) == len(ts))
        closest.sort()
        min_d = -1
        min_idx = 0
        i = 0
        closest.append(-1)
        total_d = 0
        n_moved = 0
        while i<len(closest)-1:
            cur = closest[i]
            next = closest[i+1]
            d = ts[i][0]-self.__ts[cur][0]
            #print "-"*50
            #print "Cur: {}, next:{}, t.self:{:0.3f}, t.other:{:0.3f}".format(cur, next, self.__ts[cur][0], ts[i][0])
            #print "d:{:0.3f}, min_d:{:0.3f}, min_idx:{}".format(d, min_d, min_idx)
            if next == cur:
                if min_d < 0 or abs(d)<min_d:
                    min_d = abs(d)
                    min_idx = i
                    #print "UPDATE: min_d:{:0.3f}, min_idx:{}".format(min_d, min_idx)
            else:
                if min_d == None:
                    move_d = self.moveElement(cur, ts[i][0], max_dist)
                    if move_d>0:
                        total_d += abs(move_d)
                        n_moved += 1
                else:
                    if abs(d)<abs(min_d):
                        min_d = d
                        min_idx = i
                    move_d = self.moveElement(closest[min_idx], ts[min_idx][0], max_dist)
                    if move_d>0:
                        total_d += abs(move_d)
                        n_moved += 1
                    min_d   = -1
                    min_idx = 0
                    #print "RESET: min_d:{}, min_idx:{}".format(min_d, min_idx)
            i += 1
        #print self
        #print "Moved {} elements for {}".format(n_moved, total_d)
        return self

    def findClosest(self, t):

        if isinstance(t, list):
            return [self.findClosest(_) for _ in t]
        elif isinstance(t, TimeSeries):
            return self.findClosest(t.times)

        vec = self.times

        first_gt = find_first_gt(vec, t, allowEqual=True)
        last_lt  = find_last_lt(vec, t, allowEqual=True)

        if first_gt == None or last_lt == None:
            return None

        if abs(vec[first_gt]-t)<abs(vec[last_lt]-t):
            return first_gt
        return last_lt

    def writeCSV(self, filename, delimiter=";", header=[]):
        import csv
        mode ="w"

        if header != None:
            if len(header)==0:
                header = ["t", "val"]
            header=delimiter.join(header)
            with open(filename, 'w') as csvfile:
                csvfile.write(header +"\n")
                mode = "a"

        with open(filename, mode) as csvfile:
            csvwriter = csv.writer(csvfile, delimiter=delimiter, lineterminator="\n", quotechar='|', quoting=csv.QUOTE_MINIMAL)
            for e in self.__ts:
                row = [e[0], get_NA_str(e[1])]
                csvwriter.writerow(row)

    def toString(self, digits=5):
        """ Make a nice string"""

        s = '\n'.join(["("+str(round(t, digits)) + ", " + str(round(v, digits)) + ")" for t, v in self.__ts])
        return(s)

    def __str__(self):
        return self.toString()
    #def __repr__(self): return self.toString()

    def __len__(self):
        return len(self.__ts)

    def __iter__(self):
        return iter(self.__ts)

    def __getitem__(self, i):
        return self.__ts[i]

    def __eq__(self, other):
        if isinstance(other, type(None)):
            return False
        if not isinstance(other, TimeSeries):
            return False

        if len(other) != len(self):
            return False
        for i in range(len(self)):
            if self[i] != other[i]:
                return False

    def __ne__(self, other):
        return not self.__eq__(other)

    timeseries  = property(getTimeSeries, setTimeSeries)
    times       = property(getTimes)
    values      = property(getValues)
    deltaT      = property(getDeltaT)
