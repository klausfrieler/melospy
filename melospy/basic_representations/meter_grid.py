""" Class implementation of MeterGrid """

from fractions import Fraction
from math import log

from melospy.basic_representations.jm_stats import *
from melospy.basic_representations.jm_util import *
from melospy.basic_representations.metrical_event import *
from melospy.basic_representations.rhythm import *
from melospy.pattern_retrieval.intspan import *


def tatum_grid_match(chunk, pattern):
    if pattern == None:
        return True
    if pattern == "first_last":
        if len(chunk) == 1 and chunk[0].getTatum() == 1:
            return False
        for  e in chunk:
            #print "="*50
            #print "tatum: {}, division: {}".format(e.tatum, e.division)
            if e.tatum != 1 and e.tatum != e.division:
                return False
        return True
    elif pattern == "last":
        for  e in chunk:
            #print "="*50
            #print "Last: tatum: {}, division: {}".format(e.tatum, e.division)
            if e.tatum != e.division:
                return False
        return True
    elif pattern == "first":
        for  e in chunk:
            #print "="*50
            #print "First: tatum: {}, division: {}".format(e.tatum, e.division)
            if e.tatum != 1:
                return False
    elif pattern == "full_swing":
        if len(chunk) == 2:
            #print "="*50
            #print "FULL SWING: chunk 0 : {}, chunk 1: {}".format(str(chunk[0]), str( chunk[1]))
            if chunk[0].tatum == 1 and chunk[1].tatum == chunk[1].division:
                return True
        return False
    return grid_match([e.tatum for e in chunk], pattern)

class BeatChunkFilter(object):

    def __init__(self, invert=False):
        #print "BeatChunkFilter init called with invert =", invert
        self.invert = invert
        self.filter_fun = lambda x: True

    def apply(self, chunk, *args, **kwargs):
        #print "BeatChunkFilter apply called"
        if chunk is None or len(chunk) == 0:
            return False

        val = self.filter_fun(chunk, *args, **kwargs)
        if self.invert:
            val = not val
        return val


class BeatChunkFilterDivision(BeatChunkFilter):

    def __init__(self, divisions, invert=False):
        #print "BeatChunkFilterDivision called with div=", divisions, invert
        #BeatChunkFilter.__init__(self, invert)
        if isinstance(divisions, list):
            self.divisions = divisions
        else:
            self.divisions = [divisions]
        self.invert = invert

    def filter_fun(self, chunk):
        #print "BeatChunkFilterDivision filter_fun called with", self.divisions
        ret = True
        for e in chunk:
            ret = ret and e.getDivision() in self.divisions
        return ret

class BeatChunkFilterPattern(BeatChunkFilter):

    def __init__(self, pattern, invert=False):
        #print "BeatChunkFilterPattern called with pattern=", pattern, invert
        #BeatChunkFilter.__init__(self, invert)
        self.pattern = pattern
        self.invert = invert

    def filter_fun(self, chunk):
        #print "BeatChunkFilterPattern filter_fun called"
        ret = tatum_grid_match(chunk, self.pattern)
        #tatums = "|".join([str(e.tatum) for e in chunk])
        #print "chunk: {}, ret: {} [pattern:{}]".format(tatums, ret, self.pattern)
        return ret

class BeatChunkFilterCombi(BeatChunkFilter):
    def __init__(self, beat_chunk_filters, inclusive=True, invert=False):
        if not isinstance(beat_chunk_filters, list):
            beat_chunk_filters = [beat_chunk_filters]
        self.beat_chunk_filters = beat_chunk_filters
        self.inclusive = inclusive
        self.invert = invert

    def filter_fun(self, chunk):
        #print "BeatChunkFilterCombi filter_fun called"
        if self.inclusive:
            ret = True
            for bcf in self.beat_chunk_filters:
                ret = ret and bcf.apply(chunk)
        else:
            ret = False
            for bcf in self.beat_chunk_filters:
                ret = ret or bcf.apply(chunk)
        return ret

class MeterGrid(Rhythm):

    def __init__(self, events=None):
        """ Initialize module rhythm """
        if events == None:
            Rhythm.__init__(self, events)
        else:
            if isinstance(events, MeterGrid):
                Rhythm.__init__(self, events)
            elif isinstance(events, MetricalEvent):
                Rhythm.__init__(self, events)
            else:
                raise TypeError("Invalid event type {} in init!".format(type(events)))

    def clone(self):
        """ Provides deep copy """
        r = MeterGrid(None)
        for e in Rhythm.getEvents(self):
            r.append(e.clone())
        return r

    def append(self, metricalEvent):
        """ Append a MetricalEvent object"""
        if not isinstance(metricalEvent, MetricalEvent):
            raise Exception("Expected 'MetricalEvent', got: " + str(metricalEvent))
        if not self.isEmpty():
            last = Rhythm.getEvents(self)[-1]
            if metricalEvent < last:
                raise Exception("MetricalEvent {} must be later in time than last event in list {}.".format(metricalEvent.getOnsetSec(), last.getOnsetSec()))
            if not metricalEvent.consistent(last):
                raise Exception("MetricalEvent {} not consistent with last event in list  {}".format(metricalEvent, last))
            if metricalEvent.getMetricalPosition() < last.getMetricalPosition():
                raise Exception("MetricalEvent {} must be metrically later than last event {}".format(metricalEvent, last))
        #print "ME append"
        #print metricalEvent.getBeatInfo()
        Rhythm.append(self, metricalEvent)
        return self

    def getBarSequence(self, start, end=None):
        """
            Retrieve event sequence starting at bar 'start' until
            bar number 'end' (including)
            Returns a MeterGrid
        """
        p = Rhythm()
        if end == None:
            end = start

        if end<start:
            raise Exception("'End' must greater than 'start'")

        for e in Rhythm.getEvents(self):
            if e.getBar() >= start and e.getBar() <= end:
                p.append(e)
        return p

    def getEventNumbersForBarSequence(self, start, end=None):
        """
            Retrieve ids for event sequence starting at bar 'start' until
            bar number 'end' (including)
            Returns a IntSpan
        """
        p = []
        if end == None:
            end = start

        if end<start:
            raise Exception("'End' must greater than 'start'")

        for i, e in enumerate(Rhythm.getEvents(self)):
            if e.getBar() >= start and e.getBar() <= end:
                p.append(i)
        return IntSpan(p)

    def get_signature_changes(self, include_first=False):
        ret = {}
        last_sig = None
        for i, e in enumerate(self.events):
            cur_sig = e.mp.getSignature()
            if last_sig == None:
                last_sig  = cur_sig
                if include_first:
                    ret[e.bar] = cur_sig
                continue
            if cur_sig != last_sig:
                ret[e.bar] = cur_sig
                last_sig = cur_sig
        return ret

    def toQuarterFormat(self):
        tmp = []
        #qpos = self.getQuarterPositionsFractional()
        div_pool = {}
        for i, e in enumerate(self.events):
            #print "-"*60
            #print "Transforming: {}".format(e)
            bi_old = e.getBeatInfo()
            mi_old = e.getMeterInfo()
            denom = mi_old.denominator
            num = mi_old.numerator
            div = bi_old.tatums
            qper = mi_old.getQuarterLength()
            qpos = e.mp.quarterPositionFractional()
            if qper != int(qper):
                raise RuntimeError("Aksak meters not supported")
            qper = Fraction(int(qper))
            bf = mi_old.getBeatFactor(music21Mode=True, as_fraction=True)
            #print "bi:{}, mi:{}, num:{}, denom:{}, bf:{}, div:{}, qpos:{}".format(bi_old, mi_old, num, denom, bf, div, qpos)
            if denom == 4:
                tmp.append(e.clone())
                continue
            new_sig = Fraction(num, denom)
            denom = new_sig.denominator
            num = new_sig.numerator
            sig_factor = 4./denom
            #print "New sig: {}, sig_factor:{}".format(new_sig, sig_factor)
            if sig_factor != int(sig_factor):
                raise RuntimeError("Invalid sig factor:{}".format(sig_factor))
            sig_factor = int(sig_factor)
            #print "Quarter period: {}, control:{}".format(qper, num*sig_factor)
            new_beat_dur = bi_old.beatDurationSec/bf
            new_beat = int(qpos)
            new_tatum = qpos - new_beat
            new_division = new_tatum.denominator
            #print "New beat: {}, new tatum:{}, new_division: {}".format(new_beat, new_tatum, new_division)
            if e.bar not in div_pool:
                div_pool[e.bar] = {}

            if new_beat+1 in div_pool[e.bar]:
                div_pool[e.bar][new_beat+1] = max(new_tatum.denominator, div_pool[e.bar][new_beat+1])
            else:
                div_pool[e.bar][new_beat+1] = new_tatum.denominator
            #print "div_pool", div_pool
            bi = BeatInfo(tatums=new_division, beatDurationSec=new_beat_dur)
            #print "New bi:{}".format(bi)

            mi = MeterInfo(numerator=num*sig_factor, denominator=denom*sig_factor)
            #print "New mi:{}".format(mi)
            mc = MetricalContext(bi, mi)
            mp = MetricalPosition(e.bar, new_beat+1, new_tatum.numerator+1, subtatum=0, metricalContext=mc)
            me = MetricalEvent(e.onsetSec, mp, e.durationSec, None)
            #print "ADDED", me
            tmp.append(me)
        #print "DIV POOL", div_pool
        mg = MeterGrid()
        for i, e  in enumerate(tmp):
            try:
                div = div_pool[e.bar][e.beat]
                if div != e.division:
                    #print "old", e
                    e.rescale(div)
                    #print "new", e
            except:
                pass
            mg.append(e)
        return mg

    def getBarBeatDict(self, events="index", as_string=False, quarter_format=False):
        ret = {}
        cur_bar = None
        cur_beat = None
        if quarter_format:
            mg = self.toQuarterFormat()
        else:
            mg = self.events
        for i, e in enumerate(mg):
            bar_change = False
            bar, beat = e.bar, e.beat
            if cur_bar != bar:
                cur_bar = bar
                ret[cur_bar] = {}
                bar_change = True

            if bar_change or cur_beat != beat:
                cur_beat = beat
                ret[cur_bar][cur_beat] = []

            if events == "raw":
                ev = (i, e) if not as_string else (i, str(e))
            elif events == "mp":
                ev = (i, e.mp) if not as_string else (i, str(e.mp))
            elif events == "index":
                ev = i if not as_string else str(i)
            else:
                raise TypeError("Invalid data format: {}.".format(events))
            ret[cur_bar][cur_beat].append(ev)
        return ret

    def getBarNumbers(self):
        """ Retrieve bar numbers as list"""
        start = Rhythm.getEvents(self)[0].getMetricalPosition().bar
        end = Rhythm.getEvents(self)[-1].getMetricalPosition().bar

        return list(range(start, end+1))

    def getEventsOfBeat(self, bar, beat):
        ret = []
        for e in Rhythm.getEvents(self):
            if e.getBar() == bar and e.getBeat() == beat:
                ret.append(e)
        return ret

    def getMeterInfosForBars(self):
        if len(self.events) == 0:
            return []
        bar = 0
        old_bar = self.events[0].bar
        meter_infos =[]
        mi = self.events[0].getMeterInfo()
        #meter_infos.append( (old_bar, mi))
        for ev in self.events:
            bar = ev.getMetricalPosition().bar
            if bar != old_bar:
                try:
                    diff_bar = bar-old_bar
                except:
                    diff_bar = 1
                for i in range(diff_bar):
                    meter_infos.append( (old_bar+i, mi))
                mi = ev.getMeterInfo()
            old_bar = bar
        meter_infos.append( (old_bar, mi))
        return meter_infos

    def getCumulativeBarLengths(self, quarters=True):
        """ Retrieve cumulative sums of bar length"""
        mis = self.getMeterInfosForBars()
        if len(mis) == 0:
            return None
        cum_sum = 0
        cum_sums = []
        for mi in mis:
            cum_sums.append(cum_sum)
            if quarters:
                bl = mi[1].getQuarterLength()
            else:
                bl = mi[1].getPeriod()
            cum_sum += bl
        return cum_sums

    def getFirstBarNumber(self):
        return Rhythm.getEvents(self)[0].getMetricalPosition().bar

    def getLastBarNumber(self):
        return Rhythm.getEvents(self)[-1].getMetricalPosition().bar

    def hasUpbeat(self):
        return Rhythm.getEvents(self)[0].getMetricalPosition().bar < 1

    def find_first_greater_than(self, metrical_position):
        for i, e in enumerate(self):
            if e.mp >= metrical_position:
                return i
        return -1

    def find_last_less_than(self, metrical_position):
        for i, e in enumerate(self):
            if e.mp >= metrical_position:
                return i-1
        return -1

    def getMetricalPositions(self):
        """ Retrieve MetrcialPositions of events"""
        p = [e.getMetricalPosition() for e in Rhythm.getEvents(self)]
        return p

    def getMetricalPositionsDecimal(self, debug=False):
        """ Retrieve MetrcialPositions of events"""
        p = [e.getMetricalPositionDecimal(debug) for e in Rhythm.getEvents(self)]
        return p

    def getQuarterPositionsDecimal(self):
        """ Retrieve MetricalPositions of events"""
        cbl = self.getCumulativeBarLengths()
        first = self.getFirstBarNumber()
        #print cbl, first
        p = []
        for ev in self.events:
            #print "="*60
            mp = ev.getMetricalPosition()
            qpos = cbl[mp.bar-first] + mp.quarterPositionDecimal()
            #print mp
            #print mp.bar-first, cbl[mp.bar-first], mp.quarterPositionDecimal(), qpos
            p.append(qpos)
        return p

    def getQuarterPositionsFractional(self):
        """ Retrieve quarter positions of events as Fraction"""
        cbl = self.getCumulativeBarLengths()
        first = self.getFirstBarNumber()
        #print cbl, first
        p = []
        for ev in self.events:
            #print "="*60
            mp = ev.getMetricalPosition()
            qpos = Fraction(cbl[mp.bar-first]) + mp.quarterPositionFractional()

            #print mp
            #print mp.bar-first, cbl[mp.bar-first], mp.quarterPositionDecimal(), qpos
            p.append(qpos)
        return p


    def getBeatPositionsFractional(self):
        """ Retrieve MetricalPositions of events as running beat numbers with
            rational sub beat positions
        """
        cbl = self.getCumulativeBarLengths(quarters=False)
        first = self.getFirstBarNumber()
        #print cbl, first
        positions = []
        for ev in self.events:
            #print "="*60
            mp = ev.getMetricalPosition()
            #print mp, mp.beatPositionFractional()
            #print mp.bar-first, cbl[mp.bar-first], mp.beatPositionFractional()
            bpos = Fraction(cbl[mp.bar-first], 1) + mp.beatPositionFractional()
            positions.append(bpos)
        return positions

    def getQuarterIOIsDecimal(self, pad=False):
        ret = diff(self.getQuarterPositionsDecimal())
        if pad:
            ret.append(None)
        return ret

    def getQuarterIOIsFractional(self, pad=False):
        ret =  diff(self.getQuarterPositionsFractional())
        if pad:
            ret.append(None)
        return ret

    def getMetricalIOIsDecimal(self, pad=False):
        ret =  diff(self.getMetricalPositionsDecimal())
        if pad:
            ret.append(None)
        return ret

    def getMCM(self, MCM_division=48):
        """ Retrieve Metrical Circle Map event positions with N=MCM_division"""
        p = [e.getMCM(MCM_division) for e in Rhythm.getEvents(self)]
        return p

    def syncopations(self):
        ret = []
        bpos = self.getBeatPositionsFractional()
        for i in range(len(bpos)):
            if self[i].tatum == 1:
                ret.append(0)
                continue
            if i == len(bpos)-1:
                ret.append(1)
                continue

            diff = bpos[i+1]-bpos[i]
            #print bpos[i], bpos[i+1], diff
            if diff.denominator == bpos[i].denominator and diff.numerator == 1:
                ret.append(0)
            else:
                ret.append(1)
        return ret

    def syncopicity(self):
        syncs = self.syncopations()
        return (sum(syncs)+0.)/len(syncs)

    def getEventBars(self):
        """ Retrieve bar number of events"""
        p = [e.getBar() for e in Rhythm.getEvents(self)]
        return p

    def getEventBeats(self):
        """ Retrieve beat number of events"""
        p = [e.getBeat() for e in Rhythm.getEvents(self)]
        return p

    def getEventTatums(self):
        """ Retrieve tatum positions of events"""
        p = [e.getTatum() for e in Rhythm.getEvents(self)]
        return p

    def getEventSubtatums(self):
        """ Retrieve subtatum positions of events"""
        p = [e.getSubtatum() for e in Rhythm.getEvents(self)]
        return p

    def getEventDivisions(self):
        """ Retrieve beat division of events"""
        p = [e.getDivision() for e in Rhythm.getEvents(self)]
        return p

    def getEventPeriods(self):
        """ Retrieve meter periods of events"""
        p = [e.getPeriod() for e in Rhythm.getEvents(self)]
        return p

    def getDurationTatums(self):
        """ Retrieve duration tatums of events """
        p = [e.getDurationTatum() for e in Rhythm.getEvents(self)]
        return p

    def getEventBeatDurations(self):
        """ Retrieve beat durations for events """
        p = [e.getBeatDuration() for e in Rhythm.getEvents(self)]
        return p

    def getEventSignatures(self):
        """ Retrieve signatures per event """
        p = [e.getSignature() for e in Rhythm.getEvents(self)]
        return p

    def getSignatures(self):
        """ Get set of all present signatures """
        mis = unique([e.getMeterInfo().getSignature() for e in Rhythm.getEvents(self)], lambda x: str(x))
        return mis

    def shiftbar(self, bar):
        """ Shift all bar numbers by constant amount """
        for e in Rhythm.getEvents(self):
            e.getMetricalPosition().addBar(bar)

    def leastCommonTatum(self):
        """ Calc least common multiple of all tatums """
        p = [e.getBeatInfo().getTatums() for e in Rhythm.getEvents(self)]
        return lcm_vec(p)

    def standardize(self, force = False):
        """ Standardize all tatum grids of all events to
            the least common multiple of all tatums
            ATTENTION: Tatum proportions get destroyed this way.
        """
        if self.isEmpty():
            raise RuntimeError("No events!")
        lcm = self.leastCommonTatum()
        for e in Rhythm.getEvents(self):
            factor = lcm
            if factor <= 0:
                raise Exception("Invalid rescaling factor: {}".format(factor))
            e.rescale(factor, force)
        return self

    def compress(self):
        """Inverse operation to standardize()"""
        if self.isEmpty():
            raise RuntimeError("No events!")
        events = Rhythm.getEvents(self)
        i = 0
        #print len(events)
        while i < (len(events)):
            #print "Outer while: {}".format(i)
            beat = events[i].getBeat()
            bar = events[i].getBar()
            chunk = []
            tatums = []
            while i < (len(events)) and events[i].getBeat() == beat and events[i].getBar() == bar:
                chunk.append(i)
                tatums.append(events[i].getTatum()-1)
                #print "Inner while: {}, beat:{}".format(i, events[i].getMetricalPosition())
                i += 1

            oldDiv = events[chunk[0]].getMetricalContext().getDivision()
            tatums.append(oldDiv)
            gcd = gcd_vec(tatums)
            #print "Tatums:{}, GCD: {}, OldDiv:{}".format(tatums,gcd, oldDiv)
            #print chunk
            if len(chunk) == 1 and events[chunk[0]].getTatum() == 1:
                gcd = oldDiv
            if gcd > 1:
                newDivision = oldDiv/gcd
                #print "New division: {}".format(newDivision)
                for j in chunk:
                    events[j].rescale(newDivision)
                    #print events[j]
            #print chunk
            #print tatums
        return self

    def getBeatChunksRaw(self, chunk_filter=BeatChunkFilter(), as_indices=False):
        """
            Returns a list of lists of events belonging to a common beat.

        """
        ev = Rhythm.getEvents(self)
        ret = []
        last_bar, last_beat = None, None
        chunk = []
        chunk_idz = []
        for i in range(len(ev)):
            e = ev[i]
            bar, beat= e.getBar(), e.getBeat()
            #print "-"*60
            #print "Event #{}: {}".format(i, e)
            if (bar == last_bar and beat == last_beat) or len(chunk)== 0:
                chunk_idz.append(i)
                #print "Appended index", i
                chunk.append(e)
                #print "Appended event", e
            else:
                if chunk_filter.apply(chunk):
                    if as_indices:
                        ret.extend(chunk_idz)
                    else:
                        ret.append([_ for _ in chunk])
                    #print "Appended chunk of length", len(chunk)
                else:
                    pass
                    #print "Defied chunk of length", len(chunk)
                chunk = [e]
                chunk_idz = [i]
            last_bar, last_beat = bar, beat

        #Add the last chunk if necessary
        if chunk_filter.apply(chunk):
            if as_indices:
                ret.extend(chunk_idz)
            else:
                ret.append([_ for _ in chunk])
            #print "Appended chunk of length", len(chunk)
        #print "# chunks", len(ret)
        #print "\n".join([",".join([str(e.getMetricalContext()) for e in _]) for _ in ret])
        return ret

    def getBeatChunks(self, div_filter=None, grid_pattern="complete"):
        """
            Returns a list of lists of events belonging to a common beat.

            *div_filter* can be used to filter only
            beats with a certain division.

            *complete* indicates if the length of the beat chunks
            should be equal to the division, i.e., returning only
            beats with fully occupied tatum grids.
        """
        bcf = []
        if div_filter is not None:
            df = BeatChunkFilterDivision(div_filter)
            bcf.append(df)
        if grid_pattern is not None and grid_pattern != "complete":
            df = BeatChunkFilterPattern(grid_pattern)
            bcf.append(df)
        if len(bcf) > 0:
            bcf = BeatChunkFilterCombi(bcf)
        else:
            bcf = BeatChunkFilter()
        return self.getBeatChunksRaw(chunk_filter=bcf)


    def _tatum_proportion_to_swing_ratio(self, tatum_proportion):
        if tatum_proportion == None:
            #print "None -> 1.0"
            return 1.0
        l = len(tatum_proportion)
        first = sum(tatum_proportion[0:(l-1)])
        second = tatum_proportion[l-1]
        #print "{} -> {}".format(tatum_proportion, first/second)
        return first/second

    def getSwingRatios(self, average=False, max_div=4, include_ternary=False):
        """
            Returns a list of all swing ratios for beats with
            first and last or tatum position occupied for beats
            with a maximal division max_div
        """
        swingRatios = []
        bcfp = BeatChunkFilterPattern(pattern="first_last")
        if include_ternary and max_div<3:
            max_div = 3
        if max_div < 2:
            max_div = 2
        bcfd = BeatChunkFilterDivision(divisions=list(range(2, max_div+1)))
        bcfc = BeatChunkFilterCombi([bcfp, bcfd])
        beatChunks = self.getBeatChunksRaw(chunk_filter=bcfc)
        #print "\n---".join([",".join([str(e.getMetricalPosition()) for e in _]) for _ in beatChunks])
        #print "Num beat chunks", len(beatChunks)
        for bc in beatChunks:
            #print bc[0].getBeatInfo()
            tp = bc[0].getBeatInfo().tatumProportion
            sr = self._tatum_proportion_to_swing_ratio(tp)
            swingRatios.append(sr)
            #print "Tatum proporz: {}, swing ratio: {}".format(tp,sr)
        if average:
            swingRatios = mean(swingRatios)
            #print "swing Ratios", swingRatios
        return swingRatios

    def getSwingRatios2(self, average=False, include_ternary=False):
        """
            Returns a list of all swing ratios for beats with binary
            division
        """
        swingRatios = []
        beatChunks = self.getBeatChunks(div_filter=2)
        if (include_ternary):
            beatChunks2 = self.getBeatChunks(div_filter=3, grid_pattern = [1, 0, 1])
            beatChunks.extend(beatChunks2)
        for bc in beatChunks:
            if len(bc) != 2 and len(bc) != 3:
                raise RuntimeError("Beat chunk of invalid length {} found.".format(len(bc)))
            tp = bc[0].getBeatInfo().tatumProportion
            sr = self._tatum_proportion_to_swing_ratio(tp)
            swingRatios.append(sr)
        if average:
            swingRatios = mean(swingRatios)
        return swingRatios

    def getSwingCandidates(self, max_div=4, only_full=False):
        #print "getSwingCandidates called"
        pattern = "full_swing" if only_full else "first_last"
        bcfp = BeatChunkFilterPattern(pattern=pattern)
        bcfd = BeatChunkFilterDivision(divisions=list(range(2, max_div+1)))
        bcfc = BeatChunkFilterCombi([bcfp, bcfd])
        chunks= self.getBeatChunksRaw(chunk_filter=bcfc, as_indices=True)
        #print "#candidates {} ({}%)".format(len(chunks), round((100.0*len(chunks))/len(self), 1))
        return chunks

    def getMeanTempo(self, bpm=False):
        #TODO: Fix weird way of calculation mean values,
        if self.isEmpty():
            raise RuntimeError("No events")
        beatdur = []
        for e in Rhythm.getEvents(self):
            bd = e.getMetricalPosition().getBeatInfo().getBeatDurationSec()
            if bpm:
                bd = 60/bd
            beatdur.append(bd)
        return mean(beatdur), sd(beatdur)

    def durationClassification(self, type="ioi", mode="rel"):
        durationClasses = []
        ev = Rhythm.getEvents(self)
        type = type[0:3].lower()
        if mode == None:
            mode = "rel"
        mode = mode[0:3].lower()
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

            if mode == "rel":
                ref_dur = ev[i].getBeatInfo().getBeatDurationSec()
            elif mode == "abs":
                ref_dur = .5
            else:
                raise ValueError("Invalid mode:{}".format(mode))

            #print "================================="
            #print "Onset: {0:.3f}, dur: {1:.3f}".format(ev[i].getOnsetSec(), dur)

            dur_class = classify_duration(dur, ref_dur)
            durationClasses.append(dur_class)

        #print durationClasses
        return durationClasses

    def getMetricalWeights(self, level = "beats"):
        """ Get list of metrical weights for evens"""
        return [e.getMetricalWeight() for e in Rhythm.getEvents(self)]

    def division_complexity(self):
        tot_sum = 0
        N = len(self)-1
        if N == 0:
            return 0.
        for i in range(N):
            div1 = self[i].getDivision()
            div2 = self[i+1].getDivision()
            #print "d1, d2", div1, div2
            if div1 != div2:
                if powTwoBit(lcm(div1, div2)):
                    tot_sum += .5
                else:
                    tot_sum += 1.0
                #print "Tot_sum", tot_sum
        #print "Tot_sum", tot_sum
        return tot_sum/N

    def compression_complexity(self):
        debug = False
        bin_rhythm = self.binary_rhythm(as_string=False, flat=False)
        tot_sum = 0.0
        #print bin_rhythm
        for b in bin_rhythm:
            n = len(b)
            if n > 1:
                if debug: print(n, b, sum(b), (n-sum(b))/(n-1))
                tot_sum += (n-sum(b))/(n-1)
        tot_sum = tot_sum/len(bin_rhythm)
        return tot_sum

    def binary_rhythm(self, as_string=True, flat=False, sep="."):
        debug = False
        ret = []
        buffer = []
        old_bar = None
        old_beat = None
        old_division = None
        for e in self:
            if debug: print("Processing: ", e.mp)
            if old_bar == None:
                buffer.append(e.tatum)
                if debug: print("Buffer: ", buffer)
            elif e.bar == old_bar and e.beat == old_beat:
                buffer.append(e.tatum)
                if debug: print("Buffer: ", buffer)
            else:
                bin_str = index_list_to_binary_str(buffer, old_division, offset=1, as_string=False)
                ret.append(bin_str)
                buffer = [e.tatum]
            old_bar = e.bar
            old_beat = e.beat
            old_division = e.division

        bin_str = index_list_to_binary_str(buffer, old_division, offset=1, as_string=False)
        ret.append(bin_str)
        if as_string:
            tmp = ["".join([str(_) for _ in v]) for v in ret]
            if flat:
                ret = sep.join([v for v in tmp])
            else:
                ret = tmp
        else:
            if flat:
                tmp = []
                for v in ret:
                    tmp.extend(v)
                ret = tmp
        return ret


    def metric_complexity(self, method="combined", weights= [0.5, 0.5]):
        K1 = 0.0
        K2 = 0.0
        #print "Method: ", method
        if method == "division" or method=="combined":
            K1 = self.division_complexity()
            #print "K1:", K1
        if method == "compression" or method=="combined":
            K2 = self.compression_complexity()
            #print "K2:", K2
        #print self
        if method == "division":
            weights = [1.0, 0.0]
        elif method == "compression":
            weights = [0.0, 1.0]
        elif method == "combined":
            pass
        else:
            raise ValueError("Invalid method for metric_complexity:{}".format(method))
        return scalar_prod([K1, K2], weights)

    def setNewDivision(self, max_ticks, destructive=False):
        if destructive:
            mel = self
        else:
            mel = self.clone()
        #print "Max_ticks:", max_ticks, len(mel)
        for i in range(len(mel)):
            div = mel[i].division
            if max_ticks % div == 0:
                continue
            numEvents = len(self.getEventsOfBeat(mel[i].bar, mel[i].beat))
            new_div = best_divider(div, max_ticks)
            #print "Div:{}, new_div:{}".format(div, new_div)
            if numEvents >= new_div:
                raise RuntimeError("Not requantizable")
            old_tatum = mel[i].tatum-1
            new_tatum = int(round(float(old_tatum)/div*new_div))+1
            #print "Old tatum:{}, new_ tatum:{}".format(old_tatum, new_tatum-1)
            #print "Before: ", mel[i]
            bi = mel[i].getBeatInfo()
            bi.tatums = new_div
            mp = mel[i].getMetricalPosition()
            mp.tatum = new_tatum
            #print "After: ", mel[i]
        return mel

    def requantize(self, max_div=12, tolerance = .1, destructive=False):
        if destructive:
            mel = self
        else:
            mel = self.clone()
        for i in range(len(mel)):
            tatum = mel[i].tatum-1
            div = mel[i].division
            #print "div: {}, tatum, {}".format(div, tatum)
            n, m = farey_proportion(tatum, div, max_div, tolerance)
            new_tatum = n
            #print "Old tatum:{}, new_ tatum:{}".format(tatum, new_tatum)

            #print "Before: ", mel[i]
            mel[i].mp.addTatum(new_tatum-tatum)
            if i > 0:
                if mel[i].mp == mel[i-1].mp:
                    print("Warning duplicate metrical position: {}".format(mel[i].mp))
                    mel[i].mp.addTatum(tatum-new_tatum)
            #print "After: ", mel[i]
        return mel


    @staticmethod
    def createIsoMeter(length, signature="4/4", tempo=120., div=1, start=0., as_beat_track=False):
        beatDur = 60./tempo
        bi = BeatInfo(div, beatDur)
        mi = MeterInfo.fromString(signature)
        onset = start
        deltaT = beatDur/div
        period = mi.getPeriod()
        mc = MetricalContext(bi, mi)
        bar = 0
        beat = 0
        tatum = 0
        mg = MeterGrid()
        for i in range(length):
            mp = MetricalPosition(bar+1, beat+1, tatum+1, 0, mc)
            me = MetricalEvent(onset, mp)
            mg.append(me)
            tatum += 1
            if tatum >= div:
                tatum = 0
                beat += 1
                if beat >= period:
                    beat = 0
                    bar += 1
            onset += deltaT
        if as_beat_track:
            mg[0].value = Signature.fromString(signature)
        return mg

    @staticmethod
    def fromString(binary_string, signature="4/4", tempo=120., div=1, start=0):
        beat_dur = 60./tempo
        bi = BeatInfo(div, beat_dur)
        mi = MeterInfo.fromString(signature)
        mc = MetricalContext(bi, mi)
        tatum_dur = beat_dur/div
        #print "beat dur:{}, tatum dur:{}, div: {}".format(beat_dur, tatum_dur, div)
        r = Rhythm.fromString(binary_string, tatum_dur, start=0.0)
        #print "r", len(r), len(binary_string)
        #print "="*60
        mg = MeterGrid()
        for ev in r:
            onset_in_bar_units = ev.onset/beat_dur/mi.period
            mp = MetricalPosition(1, 1, 1, 0, mc).fromDecimal(onset_in_bar_units+1, mc)
            #print "onset {} virt_onset :{} mp {}".format(ev.onset, onset_in_bar_units, mp)
            me = MetricalEvent(ev.onset + start, mp, tatum_dur, None)
            mg.append(me)
        return mg

    def projection(self, dim):
        """ Retrieve value dimensions"""
        dim = dim.replace("_", "-")
        if dim == "onset":
            return self.getOnsets()
        elif dim == "duration":
            return self.getDurations()
        elif dim == "meter":
            return self.getMetricalPositions()
        elif dim == "durtatum":
            return self.getDurationTatums()
        elif dim == "bars":
            return self.getEventBars()
        elif dim == "beatpos":
            return self.getEventBeats()
        elif dim == "tatums":
            return self.getEventTatums()
        elif dim == "divisions":
            return self.getEventDivisions()
        elif dim == "periods":
            return self.getEventPeriods()
        elif dim == "meter-decimal" or dim == "meter_decimal":
            return self.getMetricalPositionsDecimal()
        elif dim == "meter-ioi-decimal" or dim == "meter-ioi-dec":
            return self.getMetricalIOIsDecimal()
        else:
            raise ValueError("Invalid dimension: {}".format(dim))

    def splitMetricalPositions(self, include_subtatum=False):
        """Return a dict with list of elements of metrical positions"""
        ret = {"period" : self.getEventPeriods(),
               "division": self.getEventDivisions(),
               "bar": self.getEventBars(),
               "beat": self.getEventBeats(),
               "tatum": self.getEventTatums()
               }
        if include_subtatum:
            ret["subtatum"] = self.getEventSubtatums()
        return ret

    def to_dataframe(self, split_metrical_positions=True, ignore_values=True, quote_signatures=False):
        """Convert MeterGrid object into a handy pandas DataFrame"""
        if len(self) == 0:
            return DataFrame()

        #df = DataFrame({"onset":self.onsets, "durations": self.durations})
        df = Rhythm.to_dataframe(self, ignore_values)
        if split_metrical_positions:
            mps = self.splitMetricalPositions(include_subtatum=False)
            for k in ["period", "division", "bar", "beat", "tatum"]:
                df[k] = mps[k]
        else:
            df["metrical_position"] = [str(_) for _ in self.getMetricalPositions()]
        df["beat_duration"] = self.getEventBeatDurations()
        if quote_signatures:
            df["signature"] = ['"'+str(_)+'"' for _ in self.getEventSignatures()]
        else:
            df["signature"] = [str(_) for _ in self.getEventSignatures()]
        print("Quote sign", quote_signatures)
        print(df["signature"])
        print(df)
        return df


    def toString(self):
        """ Make a nice string"""
        slist = []
        for e in Rhythm.getEvents(self):
            slist.append(e.toString() )
        s = '\n'.join(slist)
        return(s)

    def __str__(self):  return self.toString()
    #def __repr__(self): return self.toString()

    metricalpositions = property(getMetricalPositions)
