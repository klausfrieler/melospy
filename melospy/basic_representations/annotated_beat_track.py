""" Class implementation of AnnotatedBeatTrack """

import melospy.basic_representations.jm_util as jm_util
from melospy.basic_representations.accents import *
from melospy.basic_representations.annotated_beat_event import *
from melospy.basic_representations.meter_grid import MeterGrid
from melospy.basic_representations.note_track import NoteTrack
from melospy.basic_representations.rhythm import *


class AnnotatedBeatTrack(Rhythm):

    def __init__(self, anno_beat_track=None):
        """ Initialize module rhythm """
        if anno_beat_track == None or isinstance(anno_beat_track, AnnotatedBeatTrack):
            Rhythm.__init__(self, anno_beat_track)
        else:
            raise Exception("Expected AnnotatedBeatTrack or 'None', got:{}".format(type(notetrack)))

    def clone(self):
        """ Provides deep copy """
        abt = AnnotatedBeatTrack(None)
        for e in Rhythm.getEvents(self):
            abt.append(e.clone())
        return abt

    def append(self, ABEvent):
        """ Append a AnnotatedBeatEvent object"""
        if not isinstance(ABEvent, AnnotatedBeatEvent):
            raise Exception("AnnotatedBeatEvent.append: Invalid value for AnnotatedBeatEvent!")
        Rhythm.append(self, ABEvent)
        return self

    def clear(self):
        """ Yeah, well. Deletes all events"""
        Rhythm.clear(self)
        return self

    def shiftbar(self, bar):
        """ Shift all bar numbers by constant amount """
        #print "Annotated Beat Track shiftbar called"

        for ABEvent in Rhythm.getEvents(self):
            ABEvent.addBar(bar)

    def slice(self, start, end, to_full_bar=True):
        """slice Beat track between start and end"""
        if self.events is None or len(self) == 0:
            return None
        left = find_last_lt(self.getOnsets(), start, allowEqual = True)
        right = find_first_gt(self.getOnsets(), end, allowEqual = True)
        #print "left, right", left, right
        #print self.__beattrack[left]
        if to_full_bar:
            #print "Adjusting to full bar. Before : ({}, {})".format(left, right)
            new_left = self.findNextFullBar(left, forward=False)
            new_right = self.findNextFullBar(right, forward=True)
            #print "After: ({}, {})".format(new_left, new_right)
            #print_vector(self.__beattrack[right:])
            if new_left >= 0:
                left = new_left
            if new_right >= 0:
                right = new_right
        #print self.__beattrack[self.__beattrack._get_form_start()]
        #print self.__beattrack.getForm()
        bt = Rhythm.slice(self, left, right)
        if self[left].chord == "":
            last_chord = self.find_last_value_before(left, value_type="chord")
            bt[0].chord = last_chord
            #print "Adjusted first chord to {}".format(last_chord)
        if self[left].form == "":
            if to_full_bar:
                last_form = self.find_last_value_before(left, value_type="form")
            else:
                last_form = FormName("I1")
            bt[0].form = last_form
            #print "Adjusted first form to {}".format(last_form)

        #print bt.getForm()
        #print "Form start", self.__beattrack._get_form_start()
        #print left, right
        #bt.calcSignatureChanges(in_form=False)
        return bt

    def cut_overhead(self, first_bar, last_bar=None, patch=True):
        """Remove some overhead at the beginning till first_bar"""
        ret = AnnotatedBeatTrack()
        if len(self) == 0:
            return ret
        last_chord = ""
        last_form = None
        #print "first_bar, last_bar (1)", first_bar, last_bar
        if last_bar == None:
            last_bar = self[-1].getBar()
        #print "first_bar, last_bar (2)", first_bar, last_bar
        for e in self:
            #print "Form:'{}', chord:'{}'".format(e.form, e.chord)
            #print "e:", e
            if e.getBar() >= first_bar and e.getBar() <= last_bar:
                ev = e.clone()
                ret.append(ev)
            else:
                if e.form:
                    last_form = e.form
                    #print "last_form", last_form
                if e.chord:
                    last_chord = e.chord
                    #print "last_chord", last_chord
        #print "cut_overhead: len(ret)", len(ret)
        if patch and ret and not ret[0].form:
            #print "Patch form", last_form
            ret[0].setForm(last_form)
        if patch and ret and not ret[0].chord:
            #print "Patch chord", last_chord
            ret[0].setChord(last_chord)
        #print "first", ret[0]

        return ret

    def detect_suspicious_chord_changes(self):
        mg = self.toMeterGrid()
        accent_obj= MetricalAccents(positions=["primary", "secondary"])
        accents = accent_obj.calculate(mg)
        #bps = mg.getBeatPositionsFractional()
        #print ", ".join([str(round(_, 1)) for _ in bps])
        positions = []
        if len(mg)<=2:
            return 0
        for i in range(1, len(mg)):
            if accents[i] == 0:
                if accents[i-1] == 0:
                    positions.append(i)
        #print "positions:"
        #print "\n".join(str(mg[_]) for _ in positions)
        return len(positions)

    def _get_form_start(self):
        if len(self) == 0:
            return None
        for i in range(len(self)):
            fp = self[i].form
            if  fp is not None and fp and (str(fp) == "A1" or self[i].form.hasWildcard()):
                return i
        return None

    def set_form_start(self, bar, with_intro=False):
        i = self.find_bar_begin(bar)
        if i < 0:
            raise ValueError("Could not set form start for bar {}".format(bar))
        self[i].form = FormName("A1")
        if with_intro and i != 0:
            self[0].form = FormName("I1")

    def normalizeForm(self):
        if len(self) == 0:
            return
        if self[0].form != None and self[0].form:
            return

        for i in range(len(self)):
            fp = self[i].form
            #pri*t "i, fp", i, str(fp)
            if  fp != None and fp:
                if str(fp) == "I1":
                    self[i].form = self[0].form
                    self[0].form = fp
                elif str(fp) == "A1":
                    self[0].form = FormName("I1")
                else:
                    raise RuntimeError("Impossible error during normalizing form {}:{}".format(i, str(fp)))
                return
        raise RuntimeError("Impossible error during normalizing form {}:{}".format(i, str(fp)))
        return

    def setChorusIDs(self):
        if len(self) == 0:
            return self
        chorus_id = 0
        for i in range(len(self)):
            fp = self[i].form
            if  fp != None:
                if str(fp) == "A1":
                    chorus_id += 1

                elif fp and fp.hasWildcard() and chorus_id == 0:
                    chorus_id = 1
            self[i].chorus_id = chorus_id
        return self

    def calcSignatureChanges(self, in_form=True):
        last_sig = None
        form_start = self._get_form_start()
        if form_start == None and in_form:
            raise ValueError("Could not find start of form.")
        for i, ev in enumerate(self):
            if ev.metrical_position == None:
                continue
            if in_form and i < form_start:
                continue
            sig = str(ev.getSignature())
            #print "i, sig", i, sig, ev
            if sig != last_sig:
                if ev.getBeat() != 1:
                    raise ValueError("Found signature change not on first beat {}:{}".format(i, ev))
                ev.signature_change = sig
                last_sig = sig
        return self

    def findBeat(self, bar, beat):
        for abe in self:
            if abe.getBar() == bar and abe.getBeat() == beat:
                return abe
        return None

    def find_beat(self, bar, beat):
        for i, abe in enumerate(self):
            if abe.getBar() == bar and abe.getBeat() == beat:
                return i
        return -1

    def find_bar_begin(self, bar_no):
        return self.find_beat(bar_no, 1)

    def findNextFullBar(self, idx, forward=True):
        try:
            ev = self[idx]
        except:
            return -1
        #print "Testing idx {} with {}".format(idx, ev)
        if ev.getBeat() == 1 and not forward:
            return idx
        if forward:
            cur_bar = ev.getBar()+1
            search_range = list(range(idx, len(self), +1))
        else:
            cur_bar = ev.getBar()
            search_range = list(range(idx, -1, -1))
        for i in search_range:
            abe = self[i]
            #print "Testing {} with bar {} and beat {}".format(i, abe.getBar(), abe.getBeat())
            if abe.getBar() == cur_bar and abe.getBeat() == 1:
                #print "Found beginning of bar: {}".format(abe)
                return i
        #print "No full bar found"
        return -1

    def find_last_value_before(self, idx, value_type="chord"):
        last_value = ""
        for i, e in enumerate(self.events):
            if i == idx:
                break
            ev = e.toMetricalEvent(value=value_type)
            if ev.value != "":
                last_value = ev.value
        return last_value

    def _init_beat_enumerator(self, form_start, start_sig, bar_offset=None, beat_offset=None):
        if len(start_sig.split("a"))>1:
            period = 4
            form_start = 2 * form_start
        else:
            period = MeterInfo.fromString(start_sig).period
        bar  = -form_start // period +1
        beat = -form_start % period
        if bar_offset is not None and beat_offset is not None:
            be = jm_util.BeatEnumerator(period, bar_offset, beat_offset-1)
        else:
            be = jm_util.BeatEnumerator(period, bar, beat)

        #print "period: {}, bar:{}, bar_offset:{}, beat:{}, beat_offset: {}, beat_enum:{}".format(period, bar, bar_offset, beat, beat_offset, be)
        return be

    def metricalPositionsFromSignatures(self, sig_list, form_start=0, bar_offset=None, beat_offset=None):
        #print sig_list
        #print "="*60
        #print "metricalPositionsFromSignatures"
        max_i = 0
        if len(self) != len(sig_list):
            raise ValueError("Expected signature list of length {}, got {}".format(len(self), len(sig_list)))
        ret = AnnotatedBeatTrack()

        #if sig_list[0] == "":
        #    raise ValueError("Beat track misses first signature")
        ensure_first_element(sig_list)
        simplify_list(sig_list)

        form_start = self._get_form_start()
        #print "Form start: {}".format(form_start)
        if form_start == None:
            raise ValueError("Could not find start of form")
        beat_enum = self._init_beat_enumerator(form_start, sig_list[0], bar_offset, beat_offset)
        beat_interpolate = False
        last_dur = 0
        ev = Rhythm.getEvents(self)
        #last_chord = None
        for i, e in enumerate(ev):
            sig = sig_list[i]
            if i < max_i:
                print("-"*60)
                print("i:{}, sig:{}, beat_enum:{}, e:".format(i, sig, beat_enum, e))
            if i == form_start:
                if len(sig) == 0:
                    sig = sig_list[0]
                    if len(sig) == 0:
                         raise ValueError("Could not find signature")
            beat_dur = e.durationSec
            if i <(len(self)-1):
                beat_dur = ev[i+1].onset - ev[i].onset
                last_dur = beat_dur
            else:
                beat_dur = last_dur
            if i < max_i:
                print("e:{}".format(e))
                print("i: {}, beat_dur:{}".format(i, beat_dur))
            #check for signature change
            if len(sig) > 0:
                if i > 0 and beat_enum.beat_count != 0 :
                    raise ValueError("Found signature change not a beginning of a bar")
                if len(sig.split("a"))>1:
                    #special case 2/2a2 for half time tapping
                    beat_interpolate = True
                    sig = Signature(4, 4)
                else:
                    beat_interpolate = False

                #bi = BeatInfo(1, beat_dur)
                #print "sig change bi", bi
                mi = MeterInfo.fromString(sig)

                if i > 0:
                    beat_enum.__init__(mi.period, beat_enum.bar_count, 0)
            if beat_interpolate:
                beat_dur = e.durationSec/2

            bi = BeatInfo(1, beat_dur)
            mc = MetricalContext(bi, mi)
            mp = MetricalPosition(beat_enum.bar_count, beat_enum.beat_count + 1, 1, 0, mc)
            #if i<5:
            #    print "Onset:{} beatdur:{}, orig:{}, bi:{}, mp:{}".format(e.onset, beat_dur, e.durationSec, beat_interpolate, mp)

            abe = AnnotatedBeatEvent(e.onset, mp, e.form, e.chord, e.bass_pitch, e.chorus_id)
            abe.duration = beat_dur
            if i < max_i:
                print("inserted event", abe.metrical_position, abe.chord, abe.metrical_position.mc)
            ret.append(abe)
            beat_enum.inc()
            #print "First inc", be
            if beat_interpolate:
                mp = MetricalPosition(beat_enum.bar_count, beat_enum.beat_count+1, 1, 0, mc)
                #print "Interpolate onset:{} beatdur:{}, new_onset:{}".format(e.onset, beat_dur, e.onset+beat_dur)
                abe = AnnotatedBeatEvent(e.onset+beat_dur, mp, None, None, e.bass_pitch, e.chorus_id)
                abe.duration = beat_dur
                #print "inserted interpolated event", abe.metrical_position, abe.chord
                ret.append(abe)
                beat_enum.inc()
                #print "Second inc", be
        #for abe in ret:
        #    print abe.metrical_position.mc
        return ret

    def getBassPitches(self):
        """ Retrieve bass pitches of AnnotatedBeatEvents"""
        pitches = []
        for e in Rhythm.getEvents(self):
            pitches.append(e.bass_pitch)
        return pitches

    def getChordList(self, as_string=False):
        """ Retrieve chords of AnnotatedBeatEvents as flat list"""
        chords = []
        for e in Rhythm.getEvents(self):
            if not as_string:
                chords.append(e.chord)
            else:
                chord_str = str(e.chord) if e.chord != None else ''
                chords.append(chord_str )
        return chords

    def getChords(self, as_string=False, remove_repeats=True):
        """ Retrieve chord change points of AnnotatedBeatEvents as Rhythm"""
        chords = Rhythm()
        last_chord = None
        for e in Rhythm.getEvents(self):
            val = None
            if e.chord is not None:
                #print "Testing ", last_chord, e.chord
                val = str(e.chord) if as_string else e.chord
                if remove_repeats and e.chord == last_chord:
                    val = None
                    #print "Found dublett", last_chord, e.chord
                if val is not None:
                    chords.append(RhythmEvent(e.onset, e.duration, val))
                    #print "Added ", val
                    last_chord = e.chord
        return chords

    def getFormList(self, as_string=False):
        """ Retrieve form parts of AnnotatedBeatEvents"""
        form_parts = []
        for e in Rhythm.getEvents(self):
            if not as_string:
                form_parts.append(e.form)
            else:
                form_str = e.form.full_label() if e.form else ''
                form_parts.append(form_str)
        return form_parts

    def getForm(self, as_string=False):
        """ Retrieve form change points of AnnotatedBeatEvents as Rhythm"""
        forms = Rhythm()
        for e in Rhythm.getEvents(self):
            #print e, e.chord
            if e.form:
                val = str(e.form) if as_string else e.form
                forms.append(RhythmEvent(e.onset, e.duration, val))
        return forms

    def getSignatureList(self, as_string=False, simplify=False):
        """ Retrieve signatures of AnnotatedBeatEvents"""
        signatures = []
        for e in Rhythm.getEvents(self):
            if not as_string:
                signatures.append(e.getMetricalPosition().getSignature())
            else:
                signatures.append(str(e.getMetricalPosition().getSignature()))
        if simplify:
            signatures = jm_util.simplify_list(signatures)
        return signatures

    def getMeterInfoList(self, as_string=False, simplify=False):
        """ Retrieve MeterInfo of AnnotatedBeatEvents"""
        mis = []
        for e in Rhythm.getEvents(self):
            if not as_string:
                mis.append(e.getMetricalPosition().getMeterInfo())
            else:
                mis.append(str(e.getMetricalPosition().getMeterInfo()))
        if simplify:
            mis = jm_util.simplify_list(mis)
        return mis

    def getChorusIDs(self):
        return [_.chorus_id for _ in self]

    def getSignatureChanges(self, compact=False):
        ret = []
        for i, ev in enumerate(self):
            if compact:
                if ev.signature_change:
                    ret.append((i, ev.signature_change))
            else:
                ret.append(ev.signature_change)

        return ret

    def toMeterGrid(self, value="chord"):
        mg = MeterGrid()
        for e in self.events:
            try:
                ev = e.toMetricalEvent(value=value)
                #print "value {}  {}.".format(ev.value, type(ev.value))
                if ev.value:
                    mg.append(ev)
                    #print len(mg)
            except:
                return None
        return mg

    def getBarBeatDict(self, value="chord", events="index", as_string=False):
        mg = self.toMeterGrid(value=value)
        if mg == None:
            return {}
        return mg.getBarBeatDict(events=events, as_string=as_string)

    def get_chord_changes_by_form(self):
        #sig_list[40] = 3
        #print "Annotated BeatTrack get_chord_changes_by_form called"
        form_list = self.getFormList(as_string=True)
        sig_list = simplify_list([_.period for _ in self.getMeterInfoList(simplify=False)])
        chord_list = self.getChordList(as_string=True)
        form_cur = ""
        sig_cur = ""
        sig_changes = []
        form_starts = []
        for i in range(len(sig_list)):
            if sig_list[i] and sig_list[i] != sig_cur:
                sig_changes.append(i)
                sig_cur = sig_list[i]
            if (form_list[i] and form_list[i] != form_cur) or form_list[i] == "A1":
                form_starts.append(i)
                form_cur = form_list[i]
                sig_list[i] = sig_cur

        form_starts.append(len(chord_list))
        segments = sorted(set(form_starts).union(sig_changes))
        #print sig_list, len(sig_list), len(form_list), sig_changes, form_starts, segments
        #print form_list
        seq = []
        for i in range(len(form_starts)-1):
            cur_cs = ChordSequence()
            start = form_starts[i]
            end  = form_starts[i+1]
            #print "start, end", start, end
            loc_sig_changes = [start]
            for j in range(len(sig_changes)):
                if start <= sig_changes[j] and sig_changes[j]<end:
                    loc_sig_changes.append(sig_changes[j])
            loc_sig_changes.append(end)
            loc_sig_changes = sorted(set(loc_sig_changes))
            #print "loc_sig_changes", loc_sig_changes, i
            for j in range(len(loc_sig_changes)-1):
                strlist = chord_list[loc_sig_changes[j]: loc_sig_changes[j+1]]
                #print "j={}, len strlist={}".format(j, len(strlist))
                #print strlist, sig_list[loc_sig_changes[j]]
                cs = ChordSequence.fromStringList(strlist, sig_list[loc_sig_changes[j]], fill_up=True)
                if cs:
                    cur_cs.extend(cs)
                #print "length now:", len(strlist),  cur_cs.length_in_bars()

            seq.append((form_list[start], cur_cs))
            #print "inserted ", form_list[start],  cur_cs.length_in_bars()
        ret = []
        copy = False
        #print "len(seq)", len(seq), seq
        for el in seq:
            if copy and el[0] == "A1":
                break
            if el[0] == "A1" or el[0][0] == "*":
                copy = True
            if copy:
                #ret.append("{}: {}".format(el[0], str(el[1])))
                ret.append(el)
        #print "\n".join([str(_) for _ in zip(form_list, chord_list)])
        if len(ret) == 1:
            s_ret = ["{}: {}".format(ret[0][0], str(ret[0][1].simplify()))]
        else:
            s_ret = ["{}: {}".format(el[0], str(el[1])) for el in ret]
        #print "s_ret", s_ret
        if len(s_ret) > 0:
            s_ret = "\n".join(s_ret)
        else:
            s_ret = ""
        s_ret = s_ret.replace("*", "")
        #print "ret", s_ret
        return s_ret

    def addBassData(self, bass_pitches, quick_fix=False):
        if bass_pitches == None or len(bass_pitches) ==  0:
            return self
        offset = 2 if quick_fix else 0

        if len(bass_pitches) < len(self)-offset:
            raise ValueError("Expected bass data of len {}, got {}".format(len(self), len(bass_pitches)))
        is_notetrack = isinstance(bass_pitches, NoteTrack)
        #print "is_notetrack", is_notetrack
        for i in range(len(self)-offset):
            if is_notetrack:
                bp = bass_pitches[i].pitch
                #print "bp", bp
            else:
                bp = bass_pitches[i]
            self[i].bass_pitch = bp
        return self

    def splitMetricalPositions(self, include_tatums=False):
        ev = Rhythm.getEvents(self)
        periods = []
        divisions = []
        bars = []
        beats = []
        for abe in ev:
            #print "abe", abe.metrical_position.beat, type(abe.metrical_position.beat)
            periods.append(abe.metrical_position.period)
            divisions.append(abe.metrical_position.division)
            bars.append(abe.metrical_position.bar)
            beats.append(abe.metrical_position.beat)
        ret = {"period":periods, "division": divisions, "bar": bars, "beat":beats}
        if include_tatums:
            ret["tatum"] = [1]*len(self)
        return ret

    def fill_up(self):
        """Inserts events for missing beats"""
        def get_new_items(n, abe):
            new_items = []
            for j in range(n):
                new_item = abe.clone()
                new_item.chord = None
                mp = new_item.metrical_position
                mp.beat = mp.beat + j + 1
                new_item.metrical_position = mp
                new_item.onset = new_item.onset + (j+1)*new_item.metrical_position.getBeatInfo().beatDurationSec
                #print new_item.metrical_position.getBeatInfo().beatDurationSec
                new_items.append(new_item)
                #print "Appended new item {}".format(new_item)
            return new_items

        if len(self) == 0:
            return
        positions = []
        items = []
        for i in range(len(self)-1):
            cur = self[i]
            post = self[i+1]
            if cur.getTatum() !=  1:
                raise RuntimeError("Detected sub beat position in beat track for {}".format(cur))
            if post.getBar()-cur.getBar() > 1:
                raise RuntimeError("Detected missing bar between {} and {}".format(cur, post))
            if cur.getBar() == post.getBar():
                beat_diff = post.getBeat()- cur.getBeat()-1
            else:
                beat_diff = cur.metrical_position.period - cur.getBeat()
            if beat_diff > 0:
                #print "Cur: {}, post: {}".format(cur.metrical_position, post.metrical_position)
                #print "Beat diff", beat_diff, i
                positions.append(i)
                new_items = get_new_items(beat_diff, cur)
                items.append(new_items)
                #print "New items: ", len(new_items)
        last = self[-1]
        beat_diff = cur.metrical_position.period - last.getBeat()
        if beat_diff > 0:
            positions.append(len(self)-1)
            new_items = get_new_items(beat_diff, last)
            items.append(new_items)

        new_events = multiple_insert(Rhythm.getEvents(self), positions, items)
        #print "\n".join([str(e.metrical_position) for e in new_events])
        self.setEvents(new_events)
        return self

    def setSingleForm(self):
        if len(self) == 0:
            return
        ev = Rhythm.getEvents(self)
        ev[0].setForm("A1")

    def to_dataframe(self, split_metrical_positions=True, exclude_empty=True, include_tatums=False, quote_signatures=False):
        """Convert Annotated Beattrack object into a handy pandas DataFrame"""

        if len(self) == 0:
            return DataFrame()

        df = Rhythm.to_dataframe(self, ignore_values=True)
        if split_metrical_positions:
            mps = self.splitMetricalPositions(include_tatums=include_tatums)
            for k in ["period", "division", "bar", "beat"]:
                df[k] = mps[k]
            if include_tatums:
                df["tatum"] = mps["tatum"]
        else:
            df["metrical_position"] = [str(_) for _ in self.getMetricalPositions()]

        tmp = self.getSignatureList()
        if quote_signatures:
            tmp = ["'" + str(_) + "'" for _ in tmp]
        if not exclude_empty or (exclude_empty and tmp and any(tmp)):
            four_four = "'4/4'" if quote_signatures else "4/4"
            df["signature"] = jm_util.fill_up_vector(tmp, four_four)
        tmp = self.getChordList()
        if not exclude_empty or (exclude_empty and tmp and any(tmp)):
            df["chord"] = jm_util.fill_up_vector(tmp, "NC")
        tmp = self.getFormList()
        if not exclude_empty or (exclude_empty and tmp and any(tmp)):
            df["form"] = jm_util.fill_up_vector(tmp, "I")
        tmp = self.getChorusIDs()
        if not exclude_empty or (exclude_empty and tmp and any(tmp)):
            df["chorus_id"] = tmp
        tmp = self.getBassPitches()
        if not exclude_empty or (exclude_empty and tmp and any(tmp)):
            df["bass"] = tmp
        return df

    def toString(self):
        """ Make a nice string"""
        slist = []
        for e in Rhythm.getEvents(self):
            slist.append(e.toString() )
        s = '\n'.join(slist)
        return(s)


    def __str__(self):
        return self.toString()
    #def __repr__(self): return self.toString()


    bass_pitches     = property(getBassPitches)
