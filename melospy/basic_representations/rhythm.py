""" Class implementation of Rhythm """

from random import gauss

import pandas as pd
from pandas import DataFrame

from melospy.basic_representations.jm_util import *
from melospy.basic_representations.rhythm_event import *
from melospy.basic_representations.section_list import *
from melospy.basic_representations.signature import Signature


class Rhythm(object):

    def __init__(self, rhythm=None):
        """ Initialize module rhythm """
        if rhythm == None:
            self.__events = []
            # assure that internal id count always gives unique IDs
        else:
            if isinstance(rhythm, Rhythm):
                self.__events = rhythm.getEvents()
            elif isinstance(rhythm, list):
                type_check_vec(rhythm, RhythmEvent)
                self.__events = rhythm
            elif isinstance(rhythm, RhythmEvent):
                self.__events = [rhythm]
            else:
                raise Exception("Rhythm: Invalid value for rhythm!")
        self._recalcOnsetsAndDurations()

    def clone(self):
        """ Provides deep copy """
        r = Rhythm(None)
        for e in self.__events:
            r.append(e.clone())
        return r

    def append(self, rhythmEvent):
        """ Append a RhythmEvent object"""
        #if not isinstance(rhythmEvent, RhythmEvent):
        #    raise Exception("Expected RhythmEvent, got {}!".format(type(rhytmEvent)))

        if self.isEmpty():
            self.__events.append(rhythmEvent)
            self.__onsets.append(rhythmEvent.onsetSec)
            self.__durations.append(rhythmEvent.durationSec)
        else:
            if rhythmEvent > self.__events[-1]:
                self.__events.append(rhythmEvent)
                self.__onsets.append(rhythmEvent.onsetSec)
                self.__durations.append(rhythmEvent.durationSec)
            else:
                raise ValueError("Onset of new event {} must greater than last onset {} in list".format(s_to_hms(rhythmEvent.onsetSec), s_to_hms(self.__events[-1].onsetSec)))
        return self

    def insert(self, rhythmEvent):
        """Insert an RhythmEvent at the correct time ordered position"""

        pos = find_last_lt(self.__onsets, rhythmEvent.onsetSec, allowEqual = False)
        #print "Onset: {}, pos: {}, len {}".format(rhythmEvent.onsetSec, pos, len(self))
        if pos == None or pos == len(self)-1:
            self.append(rhythmEvent)
        else:
            if float_equal(self.__onsets[pos+1], rhythmEvent.onsetSec):
                raise ValueError("Onset {} alread in list".format(rhythmEvent.onsetSec))
            self.__events.insert(pos+1, rhythmEvent)
            self.__onsets.insert(pos+1, rhythmEvent.onsetSec)
            self.__durations.insert(pos+1, rhythmEvent.durationSec)
        return self

    def concat(self, rhythm, gap = .5):
        """ adds a rhythm to the end, such that the first onset of the appended Rhythm-object
            starts 'gap' seconds after the end (last onset + last duration) of the
            current rhythm"""
        if gap <= 0:
            raise ValueError("Expected positive gap value, got:{}".format(gap))
        start = 0
        end = 0
        try:
            start   = rhythm.startTime()
            end     = self.endTime()
        except:
            pass
        for re in rhythm:
            re.onsetSec = re.onsetSec -start + end + gap
            self.append(re)
        return self

    def slice(self, i, j):
        if j < i:
            i, j = j, i
        if i < 0:
            i = 0
        if j > len(self):
            j = len(self)-1
        #r = Rhythm()
        #TODO check if this works everywhere!
        r = self.clone()
        r.clear()
        for k in range(i, j+1):
            r.append(self.__events[k].clone())

        return r

    def without(self, idz):
        r = self.clone()
        r.clear()
        if not isinstance(idz, list):
            idz = [idz]
        for k in range(len(self)):
            if k not in idz:
                r.append(self.__events[k].clone())
        return r

    def withoutShorties(self, threshold=.05):
        iois = self.getIOIs()
        shorties = [i for i in range(len(iois)) if iois[i]<threshold]
        return self.without(shorties)

    @staticmethod
    def isochronous(N, start, ioi, duration=None):
        r = Rhythm()
        if duration == None:
            duration = ioi
        for i in range(N):
            re = RhythmEvent(start + i*ioi, duration)
            r.append(re)
        return r

    @staticmethod
    def beat_track(N, start, ioi, signature):
        r = Rhythm()
        for i in range(N):
            re = RhythmEvent(start + i*ioi, 0.0)
            r.append(re)

        if isinstance(signature, str):
            signature = Signature.fromString(signature)
        r[0].value = signature
        return r


    @staticmethod
    def fromOnsets(onsets):
        r = Rhythm()
        for t in onsets:
            re = RhythmEvent(t, 0)
            r.append(re)
        return r

    @staticmethod
    def fromString(bin_str, timebase, repeat=1, jitter=0, start=0):
        r = Rhythm()
        bin_str = bin_str.lower()
        bin_str = bin_str.replace(" ", "")
        bin_str = bin_str.replace(".", "")
        bin_str = bin_str.replace("|", "")
        bin_str = bin_str.replace("x", "1")
        bin_str = bin_str.replace("-", "0")
        t = start
        for k in range(repeat):
            for i in range(len(bin_str)):
                #print i, bin_str[i], t
                if bin_str[i]=="1":
                    onset = t + gauss(0, jitter)
                    re = RhythmEvent(onset, 0)
                    r.append(re)
                    #print t, onset, t-onset
                #elif bin_str[i] != "0":
                #    raise ValueError("Invalid rhythm string: {}".format(bin_str))
                t += timebase
        return r

    def sliceByTime(self, t0, t1):
        start, end = self.getIDsFromRegion(t0, t1, leftOpen = False, rightOpen = False)
        if start == None:
            return None
        return self.slice(start, end)

    def interpolate(self, N):
        """Add N-1 events between each two events"""
        if self.isEmpty() or N<2:
            return self
        ret = Rhythm()
        for i in range(len(self.__events)-1):
            ioi = self.__events[i+1].onsetSec-self.__events[i].onsetSec
            onset = self.__events[i].onsetSec
            dur = ioi/N
            interev = self.__events[i].clone()
            interev.durationSec = dur
            ret.append(interev)
            #print N, ioi, onset, dur, self.__events[i].getValue()
            for k in range(1, N):
                onset += k*dur
                #print onset
                rhythmEvent= RhythmEvent(onset, dur, None)
                ret.append(rhythmEvent)
        #print ret
        return ret

    def isEmpty(self):
        """ Length of event list"""
        return len(self.__events) == 0

    def clear(self):
        """ Yeah, well. Deletes all events"""
        self.__events = []
        self.__onsets = []
        self.__durations = []

        return self

    def startTime(self):
        """ Returns onset of first event"""
        if self.isEmpty():
            raise RuntimeError("Rhythm: Event list empty")
        return self.__events[0].getOnsetSec()

    def endTime(self):
        """ Returns end of last event (including duration of last event)"""
        return self.startTime()+self.totalDuration()

    def totalDuration(self):
        """ Total duration of the event list. Includes duration of last event."""
        if self.isEmpty():
            return 0.0

        start = self.__events[0].getOnsetSec()
        end   = self.__events[-1].getOnsetSec()+ self.__events[-1].getDurationSec()
        return end-start

    def shift(self, t):
        """ Shift all onsets a certain amount t."""
        for e in self.__events:
            newOnset = e.getOnsetSec() + t
            e.setOnsetSec(newOnset)
            self.__onsets.append(newOnset)
        return self

    def warp(self, factor):
        """ Shrink or expand time, keeping start time as a fix point.
            Scale durations as well
        """
        if not isinstance(factor, (int, float)):
            raise Exception("Rhythm.warp: Warp factor must be numeric")
        startTime = self.startTime()
        self.__onsets = []
        self.__durations = []
        for e in self.__events:
            newOnset    = (e.getOnsetSec()-startTime)*factor + startTime
            newDuration = e.getDurationSec()*factor
            e.setOnsetSec(newOnset)
            e.setDurationSec(newDuration)
            self.__onsets.append(newOnset)
            self.__durations.append(newDuration)

        return self

    def hasOverlap(self):
        """ Check if it's really monophonic, i.e. events shall not last longer
            past the onsets of following event.
            However, we do not check this in 'append', to not be overly strict.
        """
        if self.isEmpty():
            return False

        for i in range(len(self.__events)-1):
            if round(self.__events[i].getOnsetSec()+self.__events[i].getDurationSec()-self.__events[i+1].getOnsetSec(), 10)>0:
                return True
        return False

    def _recalcOnsetsAndDurations(self):
        l = len(self)
        self.__onsets = [0]*l
        self.__durations = [0]*l
        for i in range(len(self)):
            self.__onsets[i] = self[i].getOnsetSec()
            self.__durations[i] = self[i].getDurationSec()

    def setValues(self, val=None):
        for e in self.__events:
            e.value = val
        return self

    def getOnsets(self):
        """ Return onsets of events as list"""
        if len(self.__onsets) != len(self.__events):
            self._recalcOnsetsAndDurations()
        return self.__onsets

    def getNormalizedOnsets(self):
        """ Return normalized onsets of events as list"""
        if len(self.__onsets) != len(self.__events):
            self._recalcOnsetsAndDurations()
        tmp = self.clone().normalize()
        return tmp.getOnsets()

    def getDurations(self):
        """ Return onsets of events as a list"""
        if len(self.__durations) != len(self.__events):
            self._recalcOnsetsAndDurations()
        return self.__durations

    def getValues(self):
        """ Return event values as a list"""
        return [re.value for re in self.__events]

    def getOffsets(self):
        """ Return offsets (onset + duration) of events as a list"""
        if self.isEmpty():
            raise RuntimeError("Empty event list.")
        #if self.hasOverlap():
        #    raise RuntimeError("Rhythm.getOffsets: Events do overlap!")
        offsets = []
        for i in range(len(self.__events)):
            offsets.append(round(self.__events[i].getOnsetSec()+self.__events[i].getDurationSec(), 10))
        return(offsets)

    def getIOIs(self):
        """ Return inter-onset intervals of events as a list"""
        if self.isEmpty():
            raise RuntimeError("Empty event list.")
        iois = []
        for i in range(len(self.__events)-1):
            iois.append(round((self.__events[i+1].getOnsetSec()-self.__events[i].getOnsetSec()), 10))
        return(iois)

    def getOOIs(self):
        """ Return offset-onset intervals of events as a list"""
        if self.isEmpty():
            raise RuntimeError("Empty event list.")
        oois = []
        for i in range(len(self.__events)-1):
            oois.append(round((self.__events[i+1].getOnset()-self.__events[i].getOffset()), 10))
        return(oois)

    def getIOIRatios(self, classify=False):
        """ Return ratios of inter-onset intervals as a list"""
        return(self._getRatios(type="ioi", classify=classify))

    def getDurationRatios(self, classify=False):
        """ Return ratios of durations as a list"""
        return(self._getRatios(type="duration", classify=classify))

    def _getRatios(self, type="ioi", classify=False):
        if self.isEmpty():
            raise RuntimeError("Empty event list.")
        if type == "duration":
            durs = self.durations
        else:
            durs = self.getIOIs()
        dur_ratios = []
        for i in range(len(durs)-1):
            ratio = round((durs[i+1]/durs[i]), 10)
            if classify:
                #thresholds taken from FANTASTIC
                if ratio >1.4945858:
                    ratio = 1
                elif ratio < 0.8118987:
                    ratio = -1
                else:
                    ratio = 0
            dur_ratios.append(ratio)

        return(dur_ratios)

    def getEvents(self):
        """ Get event list"""
        return self.__events

    def setEvents(self, events):
        """ Set event list, use with care"""
        self.__events = events
        return self

    def first(self):
        """ Get first event in list"""
        if self.isEmpty():
            return None
        return self.__events[0]

    def last(self):
        """ Get last event in list"""
        if self.isEmpty():
            return None
        return self.__events[-1]

    def projection(self, dim):
        """ Projections retrieve value dimensions"""
        #print "Rhythm.projection called"
        if dim == 1 or dim =="onset":
            return self.getOnsets()
        elif dim == 2 or dim =="duration":
            return self.getDurations()
        elif dim == 3 or dim =="offset":
            return self.getOffsets()
        else:
            raise Exception("Rhythm.projection: Invalid dimension")

    def durationToIOI(self):
        """ Substitute durations by IOIs"""
        if self.isEmpty():
            return self
        #if len(self.__onsets) != len(self.__events):
        #    self._recalcOnsetsAndDurations()
        for i in range(len(self.__events)-1):
            ioi = round((self.__onsets[i+1]-self.__onsets[i]), 10)
            self.__events[i].setDurationSec(ioi)
        self.__events[-1].setDurationSec(0)

        self._recalcOnsetsAndDurations()
        return self

    def monophonize(self):
        """
            Enforce strict monophony by limiting durations by IOIs
        """
        if len(self) < 2:
            return self
        count = 0
        for i in range(len(self)-1):
            if (self[i].onset + self[i].duration) > self[i+1].onset:
                self[i].duration = self[i+1].onset-self[i].onset
                count = count +1
        self._recalcOnsetsAndDurations()
        print("Modified {} out of {} ({}%)".format(count, len(self), round(float(count)/len(self)*100, 1)))
        return self

    def normalize(self, minVal=None, maxVal=None):
        """ Scales onsets and duration such that the first onset
            will be mapped to 0.0, and last offset to 1.0.
            Durations will get scaled accordingly"""
        if self.isEmpty():
            return self

        if minVal == None:
            minVal = self.__events[0].getOnsetSec()
        if maxVal == None:
            maxVal = self.__events[-1].getOnsetSec() + self.__events[-1].getDurationSec()

        if float_equal(minVal, maxVal):
            raise ValueError("Min. ({}) and max. ({}) values should be different".format(minVal, maxVal))

        factor = 1.0/(maxVal - minVal)
        #print "min:{}, max:{}, factor:{}".format(minVal, maxVal, factor)
        if float_equal(factor, 0):
            raise RuntimeError("Something weird happened: " + str(factor))

        self.__onsets = []
        self.__durations = []
        for e in self.__events:
            newOnset    = (e.getOnsetSec() - minVal)*factor
            newDuration = e.getDurationSec()*factor
            e.setOnsetSec(newOnset)
            e.setDurationSec(newDuration)
            self.__onsets.append(newOnset)
            self.__durations.append(newDuration)

        return self

    def getIDsFromRegion(self, start, end, tolerance=0, leftOpen=False, rightOpen=True):
        """
            Retrieves ID of events for given start and end point,
            measured in absolute time (i.e. seconds)
        """
        if start >= end:
            raise ValueError("'end' must be greater then 'start'")

        if self.isEmpty():
            raise ValueError("Rhythm is empty.")

        left = find_first_gt(self.__onsets, start-tolerance, allowEqual=not leftOpen)
        if left is None or left == -1:
            return None, None

        right = find_last_lt(self.__onsets, end, allowEqual=not rightOpen)
        #print "\nLeft:{}, Right: {}, len: {}".format(left, right, len(self.__onsets))
        if right is None or right == -1:
            return None, None
        right = find_last_lt(self.__onsets, end, allowEqual=not rightOpen)
        #print(type(right), type(left))
        if right < left:
            return None, None

        return left, right
    
    def rhythmToSectionList(self, rhythm, sectType=None):
        """
            Transforms a consecutive list of starting points
            of sections (a 'Rhythm' object) to a SectionList
            object
        """
        if not isinstance(rhythm, Rhythm):
            raise TypeError("Expected 'Rhythm' object")

        if rhythm.isEmpty():
            if sectType != None:
                msg = sectType
            else:
                msg = "Rhythm"
            raise ValueError("Empty '{}' object".format(msg))

        if sectType == None:
            try:
                tmp = type(rhythm[0].getValue())
                if tmp == Chord:
                    sectType = 'CHORD'
                elif tmp == FormName or tmp == FormPart:
                    sectType = 'FORM'
                elif tmp == Key:
                    sectType = 'KEY'
                else:
                    sectType = 'PHRASE'
            except:
                raise ValueError("Expected value 'CHORD', 'FORM', or 'PHRASE for Rhythm item 0, got".format(tmp))
        try:
            sl = SectionList(sectType)
        except Exception as e:
            raise e
        #print "INcoming rhythm", rhythm
        for i in range(len(rhythm)):
            onset = rhythm[i].getOnsetSec()
            if i <(len(rhythm)-1):
                dur = rhythm[i+1].getOnsetSec()-onset
            else:
                dur = 10000
            #print "\n{}: Onset: {}, offset:{}".format(sectType, onset, onset+dur)
            start, end = self.getIDsFromRegion(onset, onset + dur)

            #print "{}: start: {}, end:{} val:{}\n".format(sectType, start, end, str(rhythm[i].getValue()))
            if start == None:
                #print "OOOPS, no elements found for {}".format(onset)
                continue
            #if sectType == "FORM":
            #    print "Form: i={}, val={}, start:{}, end:{}".format(i, rhythm[i].getValue(), start, end)
            #if sectType == "CHORD":
            #    print "Chord i:{}, val:{}, start: {}, end:{} ".format(i, rhythm[i].getValue(), start, end)
            #sl.append(Section(sectType, rhythm[i].getValue(), start, end))
            try:
                sl.append(Section(sectType, rhythm[i].getValue(), start, end))
                pass
            except Exception as e:
                msg = "Error during section appending at onset {} : {}".format(rhythm[i].onsetSec, e.args[0])
                raise ValueError(msg)
        return sl

    def getRegionFromIDs(self, startid, endid):
        start_onset = None
        end_onset = None
        dur  = None
        try:
            start_onset = self.__onsets[startid]
            end_onset   = self.__onsets[endid]
            max_dur     = self.__durations[endid]
            dur = end_onset + max_dur - start_onset
        except:
            pass
        return  start_onset, dur

    def findEvent(self, t):
        left = find_last_lt(self.__onsets, t, allowEqual=True)
        if self.__events[left].inSpan(t):
            return left
        return None

    def magneticMove(self, rhythm, max_dist=None):
        from melospy.basic_representations.timeseries import TimeSeries

        ts1 = TimeSeries(self)
        ts2 = TimeSeries(rhythm)
        ts1.magneticMove(ts2, max_dist=max_dist)
        for i, e in enumerate(self.__events):
            e.onset = ts1[i][0]
        return self

    def eventDensity(self, windowSize, hopSize=.5):
        type_check(windowSize, float)
        type_check(hopSize, float)
        if hopSize<=0. or hopSize>=1:
            raise ValueError("Hopsize must be a fraction between 0 and 1")
        if self.isEmpty():
            raise RuntimeError("Rhythm is empty.")
        t0 = self.__events[0].getOnsetSec()
        t = t0
        densities = Rhythm()
        while True:
            t = t + hopSize*windowSize
            dur = windowSize
            start, end = self.getIDsFromRegion(t, t+dur)
            if start == None:
                break
            length = end - start + 1
            densities.append(RhythmEvent(t, dur, value = length))

        return densities

    def durationClassification(self, type="ioi"):
        durationClasses = []
        ev = self.events
        type = type[0:3].lower()

        for i in range(len(ev)):
            if type == "ioi":
                if i == len(ev)-1:
                    break
                dur = ev[i+1].getOnsetSec()-ev[i].getOnsetSec()
            elif type== "dur":
                dur = ev[i].getDurationSec()
            else:
                raise ValueError("Invalid classfication type:{}".format(type))

            if float_equal(dur, 0):
                durationClasses.append(-2)
                print(("Warning: Found zero duration at pos {} ({})".format(i, ev[i])))
                continue

            ref_dur = .5

            #print "================================="
            #print "Onset: {0:.3f}, dur: {1:.3f}".format(ev[i].getOnsetSec(), dur)

            dur_class = classify_duration(dur, ref_dur)
            durationClasses.append(dur_class)

        #print durationClasses
        return durationClasses

    def writeCSV(self, filename, delimiter=";", header=[], ignoreValue=True):
        import csv
        if len(header)==0:
            if ignoreValue:
                header = ["onset", "duration"]
            else:
                header = ["onset", "duration", "value"]

        header=delimiter.join(header)
        with open(filename, 'w') as csvfile:
            csvfile.write(header +"\n")
        with open(filename, 'a') as csvfile:
            csvwriter = csv.writer(csvfile, delimiter=';', lineterminator="\n", quotechar='|', quoting=csv.QUOTE_MINIMAL)
            for e in self.__events:
                if ignoreValue:
                    row = [e.onset, e.duration]
                else:
                    row = [e.onset, e.duration, get_NA_str(e.value)]
                csvwriter.writerow(row)

    def to_dataframe(self, ignore_values=True):
        """Convert rhythm object into a hand pandas DataFrame"""
        if len(self) == 0:
            return DataFrame()
        df = DataFrame({"onset":self.onsets})
        df["duration"] = self.durations

        if not ignore_values:
            values = [get_NA_str(_.value) for _ in self.__events]
            if len(values) > 0:
                df["values"] = values

        return df

    def toString(self):
        """ Make a nice string"""
        s = '\n'.join([e.toString() for e in self.__events])
        return(s)

    def __eq__(self, other):
        if isinstance(other, type(None)):
            return False
        if len(self.__events) != len(other.__events):
            return False
        for i in range(len(self.__events)):
            if self[i] != other[i]:
                print("i: ", i)
                return False
        return True

    def __ne__(self, other):
        return not Rhythm.__eq__(self, other)

    def __str__(self):
        return self.toString()
    #def __repr__(self): return self.toString()

    def __len__(self):
        return len(self.__events)

    def __iter__(self):
        return iter(self.__events)

    def __getitem__(self, i):
        return self.__events[i]


    events      = property(getEvents, setEvents)
    onsets      = property(getOnsets)
    durations   = property(getDurations)
    iois        = property(getIOIs)
    values      = property(getValues)
