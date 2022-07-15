""" Class implementations of Lilypond Intermediate Representation"""

import melospy.input_output.lilypond_helper as lh
from melospy.basic_representations.metrical_event import *
from melospy.basic_representations.metrical_note_event import *
from melospy.basic_representations.solo import *
from melospy.pattern_retrieval.intspan import IntSpan


class LilypondIntermediateEvent(object):
    def __init__(self, pitch=-1, qpos=None, qioi=None, qdur=None, backref=None, beat_container=None, f0_modulation=""):
        #pitch still as MIDI pitch
        self.pitch = pitch
        #qpos relative to position in beat (=tatum)
        self.set_qpos(qpos)
        #print "self.qpos", self.get_qpos()
        #true metrical IOI as quarter-based fraction
        self.qioi = qioi
        #true metrical duration as quarter-based fraction
        self.qdur = qdur
        if qdur == 0:
            raise ValueError("Duration zero found for {},{},{}, {}".format(qpos, qioi, qdur, backref))
        #for the last event in a melody IOI is not defined
        #patch it for the moment with duration or distance to next beat,
        #might be subject to change for better solution
        if self.qioi == None:
            self.qioi = max(self.qdur, 1-self.qpos)

        if self.qioi != None and self.qdur > self.qioi:
            raise ValueError("IOI {} smaller than duration {}".format(qioi, qdur))

        #end position of the event
        self.offset = self.qpos + self.qdur
        #offset-onset interval, what misses to next event?
        self.ooi = self.qioi - self.qdur

        #back reference to event index in melody, necessary to get context information
        self.backref= backref
        #part of total duration contained in the current beat
        #virtual duration = duration as appearing under tuplet factor
        self.virtual_dur = None
        #part of total duration overhanging from the current beat
        #indicator if it's a tied note or not (for rendering)
        self.__tied  = False
        #back ref to containing LilypondIntermediateBeat object
        self.beat_container = beat_container
        #textual annotation of f0 modulation
        self.f0_modulation = f0_modulation

    def set_tied(self, val):
        self.__tied = val

    def get_tied(self):
        return self.__tied

    def is_tied(self):
        if self.is_rest():
            return False
        if self.__tied == None:
            return False
        return self.__tied

    def get_qper(self):
        if self.beat_container is None or self.beat_container.bar_container is None:
            return None
        return self.beat_container.bar_container.qper

    def get_split_durations(self, tuplet_factor=1):
        #we need to handle a special case: A pure quarter on halb beat
        # not on the last beat and not followed by a tuplet beat
        # will not get split
        if self.qpos == Fraction(1, 2) and self.qdur == 1 and self.beat != self.get_qper():
            #print "SPECIAL", self
            next_beat = self.beat_container.get_succeeding_beat()
            if next_beat == None:
                #print "SPECIAL 6", self.beat != self.get_qper()
                return [{"diff_bar":0, "beat0":self.beat-1, "pos":self.qpos, "dur":1}]
            else:
                #print "SPECIAL 2"
                if next_beat.bar == self.bar:
                    if next_beat.qbeat > self.beat + 1:
                        #print "SPECIAL 3"
                        return [{"diff_bar":0, "beat0":self.beat-1, "pos":self.qpos, "dur":1}]
                    elif next_beat.qbeat == self.beat + 1 and next_beat.tuplet_factor == 1:
                        #print "SPECIAL 4"
                        return [{"diff_bar":0, "beat0":self.beat-1, "pos":self.qpos, "dur":1}]
        #max_dur = min(4, self.qper)
        #print "self.beat", self.beat
        if tuplet_factor != 1 and self.offset > 1 and self.qpos == Fraction(1, 2) and not self.beat == self.qper:
            #print "BRANCH"
            dur = 1 - self.qpos
            new_beat = (self.beat % self.qper) + 1
            #print "Old:{} new:{}".format(self.beat, new_beat)
            splits = lh.split_duration(dur, self.qpos, self.beat, self.qper, debug=False, only_durations=False)
            splits2 = lh.split_duration(self.qdur-dur, 0, new_beat, self.qper, debug=False, only_durations=False)
            splits.extend(splits2)
            #print "self", self
            #print "Splittin dur:{}, beat:{}, pos:{}, max_dur:{}".format(self.qdur, self.beat, self.qpos, self.qper)
            #print "\n--".join([str(_) for _ in splits])
        else:
            splits = lh.split_duration(self.qdur, self.qpos, self.beat, self.qper, debug=False, only_durations=False)
        #print "self", self
        #print "Splittin dur:{}, beat:{}, pos:{}, max_dur:{}".format(self.qdur, self.beat, self.qpos, self.qper)
        #print "\n--".join([str(_) for _ in splits])
        return splits


    def set_virtual_duration(self, tuplet_factor=1):
        """Calculates virtual in-duration and true overhang duration
            as well as virtual in-duration and overhang duraiton of ensuing rests
        """
        #are we are already done?
        self.virtual_dur = self.qdur * tuplet_factor
        return

    def is_rest(self):
        return self.pitch < 0

    def set_qpos(self, qpos):
        self.__qpos = qpos - int(qpos)

    def get_qpos(self):
        return self.__qpos

    def beat_span(self):
        """calculate the actual number of beats
            the event spans
        """
        end = self.qpos + self.qdur
        ret = int(end) - int(self.qpos)
        if int(end) != end:
            ret += 1
        return ret

    def get_preceding_event(self):
        i = self.beat_container.preceding_event_index(self.qpos)
        if i == None:
            prev_beat = self.beat_container.get_preceding_beat()
            if prev_beat == None or prev_beat.is_empty():
                return None
            else:
                return prev_beat.events[-1]
        return self.beat_container.events[i]

    def get_succeeding_event(self):
        i = self.beat_container.succeeding_event_index(self.qpos)
        if i == None:
            succ_beat = self.beat_container.get_succeeding_beat()
            if succ_beat == None or succ_beat.is_empty():
                return None
            else:
                return succ_beat.events[0]
        return self.beat_container.events[i]

    def has_atomic_duration(self, virtual=False):
        #print "has_atomic_duration", self
        #print "atonic", lh.render_atomic_duration(self.qdur)
        if virtual:
            dur = self.virtual_dur.numerator
        else:
            dur = self.qdur.numerator
        #print "dur", dur, lh.is_atomic_dur(dur)
        return lh.is_atomic_dur(dur)

    def is_overlong(self):
        qper = self.qper
        #print "beat0:{}, qper:{}, offset:{}, extend:{}".format(beat0, qper, offset, offset>qper )
        if qper is None or self.qdur > qper:
            return  True
        return False

    def extends_bar(self):
        #print self
        beat0 = self.beat - 1
        qper = self.qper
        offset =  beat0 + self.offset
        #print "beat0:{}, qper:{}, offset:{}, extend:{}".format(beat0, qper, offset, offset>qper )
        if offset > qper:
            return  True
        return False

    def is_multi_beat(self, virtual=False):
        #self.set_virtual_duration()
        #a multibeat event starts at a beat, spans more than a beat but not over the barline
        #and has an atomic duration
        # or has a length of exactly a quarter
        if self.is_overlong() or self.extends_bar():
            return False

        if not powTwoBit(self.qdur.denominator):
            return False

        if self.qpos == Fraction(1, 2) and self.qdur == 1:
            if self.beat_container.tuplet_factor != 1:
                return False
            return True

        if self.qpos == 0 and self.qdur >= 1 and self.has_atomic_duration(virtual=virtual):
            return True

        return False

    def split(self, tuplet_factor=1):
        #self.set_virtual_duration()

        splits = self.get_split_durations(tuplet_factor = tuplet_factor)
        #print "enter split", self
        #print "\n".join([str(_) for _ in splits])
        if len(splits) == 0:
            raise ValueError("Empty splits")

        total_dur = sum([_["dur"] for _ in splits])
        if total_dur > self.qdur:
            raise ValueError("Total split duration ({}) larger than event duration {}".format(tot_dur, self.qdur))

        cur_pos = self.qpos
        cur_beat_container = self.beat_container

        for i in range(len(splits)-1):
            cur_dur = splits[i]["dur"]
            cur_pos = splits[i]["pos"]
            #print "splits[i]", splits[i]
            cur_pos = splits[i]["pos"]
            ev = LilypondIntermediateEvent(self.pitch, 
                                           qpos=cur_pos, 
                                           qioi=cur_dur, 
                                           qdur=cur_dur, 
                                           backref=self.backref, 
                                           beat_container=cur_beat_container, 
                                           f0_modulation=self.f0_modulation)
            ev.set_tied(True)
            if i >= 0:
                cur_beat_container = None
            splits[i]["event"] = ev

        qioi = self.qioi - sum(_["dur"] for _ in splits[0:-1])
        if qioi <=0:
            raise RuntimeError("Negative IOI")

        ev = LilypondIntermediateEvent(self.pitch, 
                                       qpos=splits[-1]["pos"], 
                                       qioi=qioi, 
                                       qdur=splits[-1]["dur"], 
                                       backref=self.backref, 
                                       beat_container=cur_beat_container, 
                                       f0_modulation=self.f0_modulation)
        splits[-1]["event"] = ev

        #if len(splits) > 1:
        #    print "Split {} into".format(self)
        #    print "\n".join(["--" +str(_["event"]) for _ in splits])
        #    print "\n".join([str(_) for _ in splits])

        return splits

    def get_bar(self):
        if self.beat_container is None:
            return None
        return self.beat_container.bar_container.bar

    def get_beat(self):
        if self.beat_container is None:
            return None
        return self.beat_container.qbeat

    def get_metrical_position(self, as_string=False):
        try:
            bar = self.beat_container.bar_container.bar
        except:
            bar = None
        try:
            beat = self.beat_container.qbeat
        except:
            beat = None
        #print bar, beat
        if as_string:
            #try:
            #    return "({}, {})".format(self.beat_container.bar_container != None, self.beat_container != None)
            #except:
            #    return "NOT SET"
            return "{}.{}.{}".format(bar, beat, self.qpos)
        return bar, beat

    def render(self, renderer=None):
        if isinstance(self.pitch, Chord):
            return str(self.pitch)
        if renderer == None:
            flat = True
        if self.pitch >= 0:
            s = NoteName.fromMIDIPitch(self.pitch).getLilypondName(flat)
        else:
            s = "r"

        if self.is_multi_beat():
            cur_dur = self.qdur
        else:
            cur_dur = self.virtual_dur
        #print "Pitch:{}, Note name:{}".format(self.pitch, nn)
        try:
            dur_token_in = lh.render_atomic_duration(cur_dur)
        except:
            dur_token_in  = "X"
            #print "ERROR", cur_dur, self.backref
            #print "Non atomic duration:", self.virtual_dur, self
        s = s + dur_token_in
        if self.is_tied():
            s += "~"
        return s

    def debug_str(self):
        #return "pitch:{}|qpos:{}|qioi:{}|qdur={}|vdur:{},{}|rdur:{},{}|bref:{}".format(
        #self.pitch, self.qpos, self.qioi, self.qdur, self.virtual_dur, self.dur_over, self.rest_vdur_in, self.rest_dur_over, self.backref)
        if self.__tied == None:
            tie = "NA"
        elif self.is_tied():
            tie = "~"
        else:
            tie = ""
        f_str = "pitch:{}|pos:{}|qioi:{}|qdur={}|vdur:{}|bref:{}|{}|f0:{}"
        return f_str.format(str(self.pitch), 
                            self.get_metrical_position(as_string=True), 
                            self.qioi, self.qdur, 
                            self.virtual_dur, 
                            self.backref, 
                            tie, 
                            self.f0_modulation)

    def __str__(self):
        #return self.get_metrical_position(as_string=True)
        return self.debug_str()


    qpos = property(get_qpos, set_qpos)
    tied = property(get_tied, set_tied)
    bar  = property(get_bar)
    beat = property(get_beat)
    qper = property(get_qper)

class LilypondIntermediateBeat(object):

    """Class representing events under a beat (quarter-based)"""
    def __init__(self, qbeat, bar, division=1, bar_container=None):
        self.qbeat = qbeat
        self.bar = bar
        self.division = division
        val, tf = lh.analyse_frac_duration(Fraction(1, division))
        #print "div:{}, val:{} tf:{}".format(division,val, tf )
        self.tuplet_factor = tf
        self.events = []
        #barck ref to containign LilypondIntermedietBar object
        self.bar_container = bar_container
        self.dur = 1

    def append(self, event):
        event.beat_container = self
        self.events.append(event)
        #self.set_virtual_durations()

    def is_empty(self):
        return len(self.events) == 0

    def first_ref(self):
        if len(self) > 0:
            for e in self.events:
                if e.backref >= 0:
                    return e.backref
        return None

    def last_ref(self):
        if len(self) > 0:
            for e in reversed(self.events):
                if e.backref >= 0:
                    return e.backref
        return None

    def get_duration(self):
        if len(self.events) == 0:
            return None
        duration = self.events[-1].offset
        return duration

    def set_virtual_durations(self):
        for e in self.events:
            e.set_virtual_duration(self.tuplet_factor)

    def preceding_event_index(self, qpos):
        if qpos == 0:
            return None
        for i, e in enumerate(self.events):
           #print i, e.qpos , qpos
            if e.qpos == qpos:
                return i-1
        return None

    def succeeding_event_index(self, qpos):
        for i, e in enumerate(self.events):
            if e.qpos > qpos:
                return i
        return None

    def get_preceding_beat(self):
        i = self.bar_container.preceding_beat_index(self.qbeat)
        if i == None:
            try:
                prev_bar = self.bar_container.get_preceding_bar()
            except:
                #print "get_preceding_beat EXIT 2"
                return None
            if prev_bar == None or prev_bar.is_empty():
                #print "get_preceding_beat EXIT 3"
                return None
            else:
                #print "get_preceding_beat EXIT 4"
                return prev_bar.events[-1]
        #print "get_preceding_beat EXIT 5"
        return self.bar_container.events[i]

    def get_succeeding_beat(self):
        try:
            i = self.bar_container.succeeding_beat_index(self.qbeat)
        except:
            return None
        if i == None:
            try:
                succ_bar = self.get_succeeding_bar()
            except:
                return None
            if succ_bar == None or succ_bar.is_empty():
                return None
            else:
                return succ_bar.events[0]
        return self.bar_container.events[i]

    def get_bar_number(self):
        return self.bar_container.bar

    def split(self):
        if len(self.events) == 0:
            raise RuntimeError("Attempt to split empty beat event")
        last = self.events[-1]
        splits = last.split(self.tuplet_factor)
        self.events[-1] = splits[0]["event"]
        return splits

    def is_multi_beat(self):
        if len(self) == 1:
            if self.events[0].is_multi_beat():
                return True
        return False

    def is_hanging_multi_beat(self):
        if len(self) == 1:
            first = self.events[0]
            if first.extends_bar():
                return False
            if first.is_multi_beat() and first.offset != int(first.offset):
                return True
        return False

    def beat_span(self):
        if len(self) == 0:
            return None
        return self.events[-1].beat_span()

    def occupied_beats(self, max_val):
        lower = self.qbeat
        upper = min(max_val, self.qbeat + self.beat_span()-1)
        #if self[-1].qpos == Fraction(1,2) and self[-1].qdur == 1:
        #    upper -= 1
        return list(range(lower,  upper + 1))

    def handle_non_atomics(self):
        """
            Split non atomic events, e.g. events with duration
            not of form 2^n or 2^n-1.
        """
        #print "enter event.handle_non_atomics\n", self
        inserts = []
        offset = 0
        for i, e in enumerate(self.events):
            if e.virtual_dur == None:
                raise RuntimeError("handle_non_atomics called before set_virtual_duration")
            cur_dur = e.virtual_dur

            if e.has_atomic_duration(virtual=True):
                continue

            elements = list(lh.split_non_atomic_dur(cur_dur.numerator, e.qpos.numerator))
            #print "Split {} into {}, denom = {}".format(cur_dur, elements, cur_dur.denominator)
            tmp = []
            qpos = e.qpos

            for dur in elements:
                qdur = Fraction(dur, cur_dur.denominator)/self.tuplet_factor
                #print "dur:{} cur_dur.denominator:{} self.tuplet_factor:{} qdur:{}".format(dur, cur_dur.denominator, self.tuplet_factor, qdur)
                le = LilypondIntermediateEvent(e.pitch, qpos=qpos, qioi=qdur, qdur=qdur, backref=e.backref, beat_container=self, f0_modulation=e.f0_modulation)
                le.set_tied(True)
                qpos += qdur
                tmp.append(le)
                #print "added event {} at {}".format(le, i)
            #last element should be untied
            tmp[-1].f0_modulation = e.f0_modulation
            tmp[-1].set_tied(False)
            inserts.append((i+offset, tmp))
            offset += len(elements)-1
            #print "new offset", offset
        #if len(inserts)>0:
            #print "{} inserts due to non-atomic".format(len(inserts))
            #print self
            #inserts[-1]
        for ins in inserts:
            self.events.pop(ins[0])
            self.events[ins[0]:ins[0]] = ins[1]

        #self.set_virtual_durations()
        #print "After handling non.atomic\n",self
        return len(inserts)

    def insert_simple_event(self, event):
        #print "beat.insert_simple_event", event
        idx = 0
        #print "="*60
        #print "BEFORE INSERT\n", self
        for i in range(len(self.events)):
            if self.events[i].qpos == event.qpos:
                raise RuntimeError("Attempt to insert event {} at non-empty position ({})".format(event, self.events[i].qpos))
            idx = len(self)
            #print "Testing idx: {} for {} <-> {}".format(i, event.qpos, self.events[i].qpos)
            if self.events[i].qpos > event.qpos:
                if event.offset > self.events[i].qpos:
                    raise RuntimeError("Offset of insert event {} exceeds onset ({})".format(event.offset, self.events[i].qpos))
                #print "Found idx: {} for {} <-> {}".format(i, event.offset, self.events[i].qpos)
                #print "Found idx: {} for {} <-> {}".format(i, event.qpos, self.events[i].qpos)
                idx = i
                break

        event.beat_container = self
        #print "inserting at", idx
        self.events.insert(idx, event)
        #print "="*60
        #print "AFTER INSERT\n", self

    def prepend_event(self, event):
        if self.is_empty():
            self.append(ev)
            return
        #if event.qdur != event.qioi:
        #    raise ValueError("IOI of prepend event {} not equal to duration {}".format(event.qioi, event.qdur))
        if self.events[0].qpos == 0:
            #print "old", self.events[0]
            #print "new", event
            raise RuntimeError("Attempt to prepend event at non-empty position (#{})".format(event))
        if event.qpos >= self.events[0].qpos:
            raise ValueError("Prepended event qpos {} lies behind first event qpos={}".format(event.qpos, self.events[0].qpos))
        if self.events[0].qpos != event.qdur:
            raise ValueError("Prepended event too long {}>{}".format(event.qdur, self.events[0].qpos))
        event.beat_container = self
        self.events.insert(0, event)
        #print "inserted event at beginning", str(event)
        #self.set_virtual_durations()

    def get_bar(self):
        return self.bar_container.bar

    def is_direct_prec(self, beat):
        if beat == None:
            return False
        if beat.get_bar() != self.get_bar():
            return False
        if  self.qbeat - beat.qbeat == 1:
            return True
        return False

    def insert_initial_rest(self):
        #print "insert_initial_rest called for m. {}/{}".format(self.get_bar(), self.qbeat)
        if len(self.events) == 0:
            return
        #print "First element", self.events[0]
        if self.events[0].qpos == 0:
            return
        prev_beat = self.get_preceding_beat()
        #if prev_beat != None and (prev_beat[-1].get_tied() or prev_beat[-1].is_multi_beat()):
        #print "prev_beat", prev_beat
        if prev_beat != None:
            prev_offset = prev_beat[-1].offset + prev_beat[-1].get_beat()-1
            #if prev_beat.bar != self.bar:
            #    prev_offset =  prev_offset % prev_beat.bar_container.qper
            onset = self.events[0].get_beat() - 1 + self.events[0].qpos
            #print "prev_offset: {} current onset:{}".format(prev_offset, onset)
            if prev_offset == onset:
                #print "bailing out", onset, prev_offset
                return
        qdur = self.events[0].qpos
        event = LilypondIntermediateEvent(-1, qpos=0, qioi=qdur, qdur=qdur, backref=-1, beat_container=self)
        self.events.insert(0, event)
        #print "inserted rest at beginning", str(event)
            #self.set_virtual_durations()

    def insert_end_rest(self):
        if len(self.events) == 0:
            return
        last = self.events[-1]
        if last.offset < 1:
            qdur = 1-(last.qpos+last.qdur)
            event = LilypondIntermediateEvent(-1, qpos=last.offset, qioi=qdur, qdur=qdur, backref=-1, beat_container = self)
            #print "inserted rest at end", str(event)
            self.events.append(event)

    def insert_rests(self):
        #if we do not start on beat border (qpos == 0), insert a rest
        self.insert_initial_rest()
        #if we do not extend to end of beat, insert also a rest
        self.insert_end_rest()
        #we have to set virtual durations of inserted rests
        #self.set_virtual_durations()
        #print "after insert_rest (beat)", self
    def patch_tuplet_factor(self):
        if self.tuplet_factor != 1:
            if self.tuplet_factor == Fraction(3, 2) and self.division == 6:
                if len(self) <= 3:
                    upper = sum(e.qpos>= Fraction(1, 2) for e in self)
                    lower = sum(e.qpos< Fraction(1, 2) for e in self)
                    if upper == 0 or lower == 0:
                        return self.tuplet_factor
                return "6/4"
        return self.tuplet_factor

    def render(self, renderer=None):
        ret = []
        for e in self.events:
             s = e.render(renderer)
             ret.append(s)
        s = " ".join(ret)
        if self.tuplet_factor != 1 and len(self) > 1:
            s = "\\tuplet {} {{".format(self.patch_tuplet_factor()) + s + "}"
        return s

    def debug_str(self):
        head = "  qbeat:{}|tf:{}|div:{}|n:{}\n".format(self.qbeat, self.tuplet_factor, self.division, len(self.events))
        event_s = "\n".join(["  --"+str(ev) for ev in self.events])
        return head + event_s

    def get_total_duration(self):
        return sum(e.qdur for e in self.events)

    def backref_check(self):
        mismatch = 0
        for e in self.events:
            try:
                if e.beat_container != self:
                    mismatch += 1
            except:
                mismatch += 1
        return mismatch

    def get_total_duration(self):
        tot_dur = 0
        for e in self.events:
            tot_dur += e.qdur
        return tot_dur

    def duration_check(self, warning=False):
        tot_dur = self.get_total_duration()
        if tot_dur != self.dur and warning:
            print("Inconsistent duration {} <-> {} found in m. {}/{}".format(tot_dur, self.qper, self.bar, self.beat))
            print("Event: {} - {}".format(self.events[0].events[0].backref, self.events[-1].events[-1].backref))
            return False
        return True

    def monotony_check(self):
        negs = [e for e in diff([e.bar for e in self.events]) if e<0]
        if len(negs)>0:
            return False
        return True

    def __str__(self):
        return self.debug_str()
    def __len__(self):
        return len(self.events)
    def __iter__(self):
        return iter(self.events)
    def __getitem__(self, i):
        return self.events[i]

class LilypondIntermediateBar(object):

    """Class for collecting events in a bar"""
    def __init__(self, bar, signature="4/4", stream=None):
        self.bar = bar
        self.events = []
        #signture object, best for indication meter changes
        if isinstance(signature, Signature):
            self.signature = signature
        elif isinstance(signature, str):
            self.signature = Signature.fromString(signature)
        #length of bar in quarter units
        self.qper = int(self.signature.getQuarterLength())
        self.stream = stream

    def append(self, event):
        event.bar_container = self
        self.events.append(event)
        #self.set_virtual_durations()

    def first_ref(self):
        if len(self) > 0:
            for e in self.events:
                fr = e.first_ref()
                if fr != None :
                    return fr
        return None

    def last_ref(self):
        if len(self) > 0:
            for e in reversed(self.events):
                lr = e.last_ref()
                if lr != None :
                    return lr
        return None

    def set_virtual_durations(self):
        for e in self.events:
            e.set_virtual_durations()

    def has_followup_beat(self, i):
        if i == len(self)-1:
            return False
        d = self.events[i+1].qbeat - self.events[i].qbeat
        if d == 1:
            return True
        return False

    def preceding_beat_index(self, beat):
        if beat == 1:
            return None
        for i, e in enumerate(self.events):
            if e.qbeat == beat:
                return i-1
        return None

    def succeeding_beat_index(self, qbeat):
        for i, e in enumerate(self.events):
            if e.qbeat > qbeat:
                return i
        return None

    def get_preceding_bar(self):
        return self.stream.get_preceding_bar(self.bar)

    def get_succeeding_bar(self):
        return self.stream.get_succeeding_bar(self.bar)

    def get_beat_index(self, beat):
        for i, e in enumerate(self.events):
            if e.qbeat == beat:
                return i
        return -1

    def get_multi_beats(self):
        mb = []
        for i, e in enumerate(self.events):
            if e.is_multi_beat():
                mb.append(e.qbeat)
        return mb


    def insert_simple_event(self, beat, event):
        i = self.get_beat_index(beat)
        #print "bar.insert_simple_event", beat, event, i
        #print "beat:", self
        if i >= 0:
            self.events[i].insert_simple_event(event)
            #self.events[i].prepend_event(event)
            return
        division = event.qdur.denominator
        if event.qdur > 1:
            division = 1
        mb = LilypondIntermediateBeat(qbeat=beat, bar=self.bar, division=division, bar_container=self)
        mb.append(event)
        self.insert_beat_event(beat, mb)

    def remove_beat(self, beat):
        i = self.get_beat_index(beat)
        #print "bar.insert_simple_event", beat, event, i
        #print "beat:", self
        if i < 0:
            return
        self.events.pop(i)

    def insert_beat_event(self, beat, event):
        if beat < 1 or beat > self.qper:
            raise ValueError("Invalid beat {} for event {}".format(beat, event))
        if event.qbeat != beat:
            raise ValueError("Beat of event {} does not match {}".format(event.qbeat, beat))
        i = self.get_beat_index(beat)
        if i >= 0:
            raise ValueError("Beat of event {} already set {}".format(beat))
        i = self.succeeding_beat_index(beat)
        if i == None:
            i = len(self)
        event.bar_container = self
        self.events.insert(i, event)

    def insert_event(self, beat, event):
        if isinstance(event, LilypondIntermediateBeat):
            self.insert_beat_event(beat, event)
        elif isinstance(event, LilypondIntermediateEvent):
            self.insert_simple_event(beat, event)
        else:
            raise ValueError("Event type '{}' not allowed".format(type(event)))
        #self.set_virtual_durations()

    def expand_overhang(self, debug=False):
        inserts = []
        for i, e in enumerate(self.events):
            splits = e.split()
            #print "split at {}, len={}".format(i, len(s))
            if len(splits) == 1:
                continue
            inserts.append(splits[1:])
        #print "Got {} insert chains".format(len(inserts))
        #print "Got {} inserts".format(sum(len(_) for _ in inserts))
        overhangs = []
        for ins in inserts:
            for ev in ins:
                #print ev["diff_bar"], ev["event"]
                if ev["diff_bar"] > 0:
                    overhangs.append(ev)
                else:
                    beat = ev["beat0"]+1
                    self.insert_event(beat, ev["event"])
        #print "Got {} overhang events".format(len(overhangs))
        return overhangs

    def handle_non_atomics(self):
        for e in self.events:
            e.handle_non_atomics()

    def fill_up_beats(self):
        hmb = []
        #mb = [b + 1 for b in self.get_multi_beats()]

        for e in self.events:
            e.insert_rests()
            if e.is_hanging_multi_beat():
                end_beat = e.qbeat + e.beat_span()-1
                if self.get_beat_index(end_beat)<0:
                    #print "found hanging multibeat\n", e
                    hmb.append((end_beat, e.events[0]))
        for mb in hmb:
            end_beat = mb[0]
            e = mb[1]
            qpos = 1 - (e.offset-int(e.offset))
            qdur = 1 - qpos
            mb = LilypondIntermediateBeat(qbeat=end_beat, bar=self.bar, division=qdur.denominator, bar_container=self)
            me = LilypondIntermediateEvent(pitch=-1, qpos=qpos, qioi=qdur, qdur=qdur, backref=-1)
            mb.append(me)
            self.insert_event(end_beat, mb)
            #print "fill_up_beat inserted", mb
        return len(hmb)

    def post_process(self, debug=False):
        #print "-->Bar post_process called"
        if debug:
            print("Post processing m. {}".format(self.bar))
            print(" -- Filling up beats.")

        self.fill_up_beats()
        if debug:
            print(" -- Setting virtual durations")
        self.set_virtual_durations()
        if debug:
            print(" -- Handlling non atomics...")
        self.handle_non_atomics()
        if debug:
            print(" -- Inserting rests...")
        self.insert_rests()
        #print "Done."
        #print self
        #print "="*60

    def is_empty(self):
        return len(self.events) == 0

    def insert_rests(self):
        beats = []
        specials = []
        for e in self.events:
            beats.extend(e.occupied_beats(self.qper))
            if e[-1].qpos == Fraction(1, 2) and e[-1].qdur == 1:
                specials.append(e.qbeat+1)

        beats = IntSpan(beats)
        full_beats = IntSpan(list(range(1, self.qper+1)))
        diff_beats = full_beats.difference(beats)
        patches = diff_beats.as_start_duration_patches()
        #print "Beats: {}, diff_beats: {}, patches: {}, specials: {}".format(beats, diff_beats, patches, specials)
        for p in patches:
            dur = p[1]
            rest = LilypondIntermediateEvent(pitch=-1, qpos=0, qioi=dur, qdur=dur, backref=-1)
            self.insert_simple_event(p[0], rest)
            if dur > 4:
                splits = rest.get_split_durations()
                self.remove_beat(p[0])
                for s in splits:
                    rest = LilypondIntermediateEvent(pitch=-1, qpos=s["pos"], qioi=s["dur"], qdur=s["dur"], backref=-1)
                    self.insert_simple_event(s["beat0"]+1, rest)

            #print "inserted rest of dur {} at {}".format(dur, p[0])
        for s in specials:
            if s not in diff_beats:
                dur = Fraction(1, 2)
                rest = LilypondIntermediateEvent(pitch=-1, qpos=dur, qioi=dur, qdur=dur, backref=-1)
                try:
                    self.insert_simple_event(s, rest)
                   #print "inserted special rest of dur {} at {}".format(dur, s)
                except:
                    pass
        return len(patches) + len(specials)

    def render(self, flat=True):
        ret = []
        #self.insert_rests()
        for e in self.events:
             s = e.render(flat)
             ret.append(s)
        s = " ".join(ret) + " | "
        return s

    def debug_str(self):
        head = "bar:{}|sig:{}|qper:{}\n".format(self.bar, self.signature, self.qper)
        event_s = "\n".join([str(ev) for ev in self.events])
        return head+event_s

    def get_total_duration(self):
        return sum(e.get_total_duration() for e in self.events)

    def duration_check(self, warning=False):
        tot_dur = self.get_total_duration()
        if tot_dur != self.qper and warning:
            print("Inconsistent duration {} <-> {} found in m. {}".format(tot_dur, self.qper, self.bar))
            print("Event: {} - {}".format(self.events[0].events[0].backref, self.events[-1].events[-1].backref))
            return False
        return True

    def backref_check(self):
        mismatch = 0
        for e in self.events:
            try:
                if e.bar_container != self:
                    mismatch += 1
            except:
                mismatch += 1
        return mismatch

    def monotony_check(self):
        for e in self:
            if not e.monotony_check():
                print("Inconsistent onsets found at m. {}/{}: {}".format(e.get_bar(), e.qbeat, e))
                return False
        negs = [e for e in diff([e.qbeat for e in self.events]) if e < 0]
        if len(negs) > 0:
            return False
        return True

    def __len__(self):
        return len(self.events)
    def __str__(self):
        return self.debug_str()
    def __iter__(self):
        return iter(self.events)
    def __getitem__(self, i):
        return self.events[i]

class LilypondIntermediateStream(object):
    """Class for an intermediate representation between Melody and LilypondWriter"""
    max_expand_recursion = 5

    def __init__(self, melody=None, params=None, debug=False):
        self.params = params
        self.setMelody(melody)
        self.events = self.parse(debug=False)
        if debug:
            print("\n"+"-"*60)
            print("BEFORE POST_PROCESS\n", self)
            print("-"*60)
        self.post_process()
        self.set_virtual_durations()
        #self.set_virtual_durations()
        #print "="*60
        if debug:
            print("AFTER POST_PROCESS\n", self)

    def append(self, lily_bar):
        self.events.append(lily_bar)

    def setMelody(self, melody):
        self.melody = melody

    def set_virtual_durations(self):
        for e in self.events:
            e.set_virtual_durations()

    def has_followup_bar(self, i):
        if i == len(self)-1:
            return False
        d = self.events[i+1].bar- self.events[i].bar
        if d == 1:
            return True
        return False

    def preceding_bar_index(self, bar):
        for i, e in enumerate(self.events):
            if e.bar >= bar:
                if i == 0:
                    return None
                return i-1
        if len(self) >0 :
            return len(self)-1
        return None

    def succeeding_bar_index(self, bar):
        for i, e in enumerate(self.events):
            if e.bar > bar:
                return i
        return None

    def get_preceding_bar(self, bar):
        i = self.preceding_bar_index(bar)
        if i == None:
            return None
        return self.events[i]

    def get_succeeding_bar(self, bar):
        i = self.succeeding_bar_index(bar)
        if i == None:
            return None
        return self.events[i]

    def get_bar_index(self, bar):
        for i, e in enumerate(self.events):
            if e.bar == bar:
                return i
        return -1

    def insert_event(self, bar, event, signature="4/4"):
        i = self.get_bar_index(bar)
        #print "stream.insert_event", event
        #print self
        if i >= 0:
            #print "Found Bar for event:", i
            self.events[i].insert_event(1, event)
            return

        mb = LilypondIntermediateBeat(qbeat=1, bar=bar, division=event.qdur.denominator)
        mb.append(event)
        #print "mb", mb
        mib = LilypondIntermediateBar(bar=bar, signature=signature, stream=self)
        mib.append(mb)
        self.insert_bar(bar, mib)

    def insert_beat(self, bar, event, signature="4/4"):
        i = self.get_bar_index(beat)
        if i >= 0:
            self.events[i].insert_beat_event(1, event)
        mb = LilypondIntermediateBar(bar=bar, signature=signature, stream=self)
        mb.append(event)
        self.insert_bar(bar, mb)

    def insert_bar(self, bar, event):
        if event.bar != bar:
            raise ValueError("Bar of event {} does not match {}".format(event.bar, bar))
        i = self.get_bar_index(bar)
        if i >= 0:
            raise ValueError("Bar of event {} already set {}".format(bar))
        i = self.succeeding_bar_index(bar)
        if i == None:
            i = len(self)
        event.stream = self
        self.events.insert(i, event)

    def remove_bar(self, bar):
        i = self.get_bar_index(bar)
        #print "bar.insert_simple_event", beat, event, i
        #print "beat:", self
        if i < 0:
            return
        self.events.pop(i)

    def remove_beat(self, bar, beat):
        i = self.get_bar_index(bar)
        #print "bar.insert_simple_event", beat, event, i
        #print "beat:", self
        if i < 0:
            return
        self.events[i].remove_beat(beat)

    def insert(self, bar, event, signature="4/4"):
        if isinstance(event, LilypondIntermediateBar):
            self.insert_bar(bar, event, signature)
        elif isinstance(event, LilypondIntermediateBeat):
            self.insert_beat(bar, event, signature)
        elif isinstance(event, LilypondIntermediateEvent):
            self.insert_event(bar, event, signature)
        else:
            raise ValueError("Event type '{}' not allowed".format(type(event)))
        #self.set_virtual_durations()

    def post_process(self):
        #print "Stream post_process called"
        self.expand_overhang()
        #self.set_virtual_durations()
        #print "AFTER EXPAND\n", self
        for e in self.events:
            e.post_process()
            #print "AFTER SINGLE POST PROCESSES", self
        self.insert_rests()
        #return n_inserts

    def insert_event2(self, bar, beat, event):
        i = self.get_bar_index(bar)
        if i >= 0:
            #print "Found bar", i
            self.events[i].insert_event(beat, event)
            return
        i = self.preceding_bar_index(bar)
        #print "predceding bar idx", i
        if i == None:
            signature = "4/4"
        else:
            signature = self.events[i].signature
        mb = LilypondIntermediateBeat(qbeat=beat, bar=bar, division=event.qdur.denominator)
        mb.append(event)
        #print "mb", mb
        mib = LilypondIntermediateBar(bar=bar, signature=signature, stream=self)
        mib.append(mb)
        self.insert_bar(bar, mib)


    def expand_overhang(self):
        inserts = []

        for i, e in enumerate(self.events):
            overhangs = e.expand_overhang()
            for ov in overhangs:
                ov["bar"] = ov["diff_bar"] + e.bar
            inserts.extend(overhangs)

        for ins in inserts:
            #print "="*60
            #print "Found overhang for m.{}/{} ".format(ins["bar"], ins["beat0"])
            #print "EVENT: {}".format(ins["event"])
            self.insert_event2(ins["bar"], ins["beat0"]+1, ins["event"])
            #print "Self", self
        #print "AFTER EXPAND\n",self
        #print "*"*60

    def insert_rests(self):
        #n_inserts = 0
        #print "stream.insert_rests called"
        bars = self.get_bar_numbers()
        if len(bars) == 0:
            return
        m = min(bars)
        if m > 1:
            m = 1
        else:
            m = bars[0]

        all_bars =IntSpan(list(range(m, bars[-1]+1)))
        #print "all_bars", all_bars
        diff_bars = all_bars.difference(IntSpan(bars))
        #print "diff_bars", diff_bars
        prec_bar = self.events[0]
        bar_idz = {e.bar: i for i, e in enumerate(self.events)}
        for b in all_bars:
            if b in diff_bars:
                qper = prec_bar.qper
                rest_event = LilypondIntermediateEvent(pitch=-1, qpos=0, qioi=qper, qdur=qper, backref=-1)
                self.insert_event(b, rest_event, prec_bar.signature)
                if qper > 4:
                    splits = rest_event.get_split_durations()
                    self.remove_bar(b)
                    for s in splits:
                        rest = LilypondIntermediateEvent(pitch=-1, qpos=s["pos"], qioi=s["dur"], qdur=s["dur"], backref=-1)
                        self.insert_event2(b, s["beat0"]+1, rest)
                #print "inserted full bar rest of dur {} in bar {}".format(qper, b)
            else:
                prec_bar = self.events[bar_idz[b]]

    def parse(self, melody=None, debug=False):

        lily_stream = []
        if melody == None:
            melody = self.melody
        if melody == None:
            return lily_stream
        if isinstance(melody, Melody):
            melody = melody.toQuarterFormat()
            pass
        elif isinstance(melody, AnnotatedBeatTrack):
            melody = melody.toMeterGrid(value="chord")
            bbd = melody.getBarBeatDict(events="index", as_string=False)
        else:
            raise ValueError("Got invalid object type {} for parsing".format(type(melody)))
        bbd = melody.getBarBeatDict(events="index", as_string=False)
        #print bbd
        qiois = melody.getQuarterIOIsFractional(pad=True)
        events = melody.getEvents()
        #print_vector( events[0:10])
        for bar in sorted(bbd.keys()):
            #signature will be taken from first element in bar
            idx = bbd[bar][list(bbd[bar].keys())[0]][0]
            sig = events[idx].getSignature()
            lily_bar = LilypondIntermediateBar(bar, sig, stream=self)
            for beat in sorted(bbd[bar].keys()):
                idx = bbd[bar][beat]
                lily_beat = LilypondIntermediateBeat(beat, bar, events[idx[0]].division)
                for i in idx:
                    lily_event = self.get_event(events[i], i, qiois[i], debug=debug)
                    lily_beat.append(lily_event)
                #lib.set_virtual_durations()
                lily_bar.append(lily_beat)
            lily_stream.append(lily_bar)
        return lily_stream

    def get_event(self, event, backref, qioi, debug=False):
        if isinstance(event, MetricalNoteEvent):
            return self.get_metrical_note_event(event, backref, qioi, debug)
        if isinstance(event, MetricalEvent):
            return self.get_chord_event(event, qioi, debug)

    def get_chord_event(self, metrical_event, qioi, debug=False):
        #print "get_chord_event event:{}, qioi:{}".format(metrical_event, qioi)
        if qioi == None:
            qioi = int(metrical_event.getQuarterPeriod()) -  metrical_event.getQuarterPositionFractional()
        lie = LilypondIntermediateEvent(pitch=metrical_event.value, qpos=0, qioi=qioi, qdur=qioi, backref=-1)
        return lie

    def get_metrical_note_event(self, metrical_note_event, backref, qioi, debug=False):
        qpos = metrical_note_event.getQuarterPositionFractional()
        qdur = metrical_note_event.estimateQuarterDuration()
        #print "metrical_note_event.estimateQuarterDuration()", qdur
        #print "_get_token_stream qioi:{}, qdur:{}, mp:{}".format(qioi, qdur, metrical_note_event.mp)
        if qioi == None or (qdur > 0 and float(qioi-qdur) > 1):
            opt_dur = lh.find_optimal_duration(qpos, qdur, zero_sub=Fraction(1, qpos.denominator))
        else:
            opt_dur = qioi
        if debug:
            print("-"*60)
            print("qpos={}, qioi={}, qdur={}, opt_dur={}".format(qpos, qioi, qdur, opt_dur))
        try:
            f0_mod = metrical_note_event.getAnnotatedF0Modulation()
        except:
            f0_mod = ""
            pass
        lie = LilypondIntermediateEvent(pitch=metrical_note_event.pitch, qpos=qpos, qioi=qioi, qdur=opt_dur, backref=backref, f0_modulation=f0_mod)

        return lie


    def get_bar_numbers(self):
        bars = [e.bar for e in self.events]
        return bars

    def render(self, renderer=None):
        ret = []
        for e in self.events:
             s = e.render(renderer)
             ret.append(s)
        s = "\n".join(ret)
        return s

    def duration_check(self, warning=False):
        ret = True
        for e in self:
            ret = ret and e.duration_check(warning=warning)
        if warning:
            msg = "passed." if ret else "failed."
            print("Duration check " + msg)
        return ret

    def backref_check(self):
        mismatch = 0
        for e in self.events:
            mismatch += e.backref_check()
            if e.stream != self:
                mismatch += 1
        if mismatch > 0:
            print("Stream mismatch", mismatch)
        return mismatch

    def pitch_check(self):
        mismatch = 0
        events = self.flatten()
        for e in events:
            if e.pitch < 0 and e.backref >= 0:
                mismatch += 1
        if mismatch > 0:
            print("Pitch mismatch", mismatch)
        return mismatch

    def tie_check(self):
        num_none = 0
        num_dangling_ties = 0
        events = self.flatten()
        for i in range(len(events)-1):
            if events[i].get_tied() == None:
                num_none += 1
            if events[i].get_tied():
               if events[i].pitch !=  events[i].pitch:
                   num_dangling_ties += 1
        if num_none >0:
            print("Number of undefined ties", num_none)
        if num_dangling_ties >0:
            print("Number of dangling ties", num_dangling_ties)
        return num_none == 0 and num_dangling_ties == 0

    def barnumber_check(self):
        sd = sum( (i - 1) for i in diff([_.bar for _ in self]))
        if sd > 0:
            print("Found bar line gap")
            return False
        return True

    def monotony_check(self):
        for e in self.events:
            if not e.monotony_check():
                print("Inconsistent beats found in m. {}: {}".format(e.bar(), e))
                return False

        errors = [e for e in diff([e.bar for e in self.events]) if e < 0 or e > 1]
        if len(errors)>0:
            print("Inconsistent bar number found: ", ",".join([e.bar for e in self]))
            return False
        #print "Monotony check passed"
        return True

    def check_all(self):
        ret = self.duration_check()
        ret = ret and self.backref_check() == 0
        ret = ret and self.tie_check()
        ret = ret and self.pitch_check() == 0
        ret = ret and self.monotony_check()
        return ret

    def flatten(self):
        events = [ ev  for bar in self.events for beat in bar for ev in beat]
        return events

    def debug_str(self):
        s = "\n".join([str(_) for _ in self.events])
        return s

    def __str__(self):
        return self.debug_str()
    def __len__(self):
        return len(self.events)
    def __iter__(self):
        return iter(self.events)
    def __getitem__(self, i):
        return self.events[i]
