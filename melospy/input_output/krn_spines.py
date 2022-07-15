""" Class for representing **kern spinges"""

import re
import sys

from melospy.basic_representations.annotated_beat_track import *
from melospy.basic_representations.chord import *
from melospy.basic_representations.jm_stats import mean, mode
from melospy.basic_representations.jm_util import (chomp, diff, lcm, lcm_vec, multiple_insert,
                                                   powTwoBit, print_vector)
from melospy.basic_representations.melody import *
from melospy.basic_representations.popsong_meta_data import *
from melospy.basic_representations.segmenter import *
from melospy.basic_representations.solo import *
from melospy.input_output.krn_params import *

START = 1
END = -1
SINGLETON = 100
IN_TIE = 2
NO_TIE = 0

IN_PHRASE = 0
IN_BAR = 0
UNDEFINED = -1
OUT_OF_PHRASE = -1

class KernBaseEvent(object):
    def __init__(self, value, qdur, bar=IN_BAR, signature="4/4", tempo=120, qpos=0):
        self.value = value
        self.qdur = qdur
        self.bar = bar
        self.signature = MeterInfo.fromString(signature)
        self.tempo = tempo
        self.qpos = 0
        self.phrase = UNDEFINED
        self.master_form = ""

    def __str__(self):
        return "v:{}|{}|{}|{}|{}|{}".format(str(self.value), self.qdur, self.bar, self.qpos, self.signature, self.tempo)

class KernNoteEvent(KernBaseEvent):
    def __init__(self, value, qdur, bar=IN_BAR, tie=NO_TIE, phrase=IN_PHRASE):
        KernBaseEvent.__init__(self, value, qdur, bar)
        self.tie = tie
        self.phrase = phrase

    def __str__(self):
        super_str = KernBaseEvent.__str__(self)
        return "({}|t:{}|p:{}|f:{})".format( super_str, self.tie, self.phrase, self.master_form)

class KernChordEvent(KernBaseEvent):
    def __init__(self, value, qdur, bar=IN_BAR):
        KernBaseEvent.__init__(self, value, qdur, bar)

    def __str__(self):
        super_str = KernBaseEvent.__str__(self)
        return "({})".format(super_str)


class KernSpine(object):
    def __init__(self, id=None, debug=False):
        self.data = []
        self.meter = []
        self.keys = []
        self.clef = None
        self.staff = None
        self.tempos_bpm = []
        self.spine_type = None
        self.markers = {"bars":[], "phrase":[], "master_form":[], "form":[], "tie":[]}
        self.debug = debug
        self.cur_bar = None
        self.cur_meter = None
        self.cur_tempo = 120
        self.id = id
        self.bar_qstarts = []
        self.bar_before_meter = False
        self.bar_offset = 0
        self.phrases = None
        self.cur_line = -1

    def append(self, item):
        item = chomp(item)
        if item[0:2] == "!!":
            self.debug_msg("comment found: {}".format(item))
            return
        if len(item) == 0:
            self.data.append(item)
            return
        if item[0] == "*":
            self._parse_metadata(item)
        elif item[0] == "=":
            #self.debug_msg("bar marker {}".format(item))
            self._add_bar_marker(item)
            #self.debug_msg("after marker {}".format(item))
        else:
            self._parse_token(item)
        return self

    def find_next_non_rest(self, idx):
        for i in range(idx, len(self.data)):
            if self.data[i].value != -1:
                return i
        return idx

    def post_process(self):
        phrases = self.markers["phrase"]
        if len(phrases):
            for i in range(len(phrases)):
                self.data[phrases[i][0]].phrase = phrases[i][1]
        ties = self.markers["tie"]
        if len(ties):
            for i in range(len(ties)):
                self.data[ties[i][0]].tie = ties[i][1]

        master_form = self.markers["master_form"]
        if len(master_form):
            for i in range(len(master_form)):
                idx, val = master_form[i]
                idx = self.find_next_non_rest(idx)
                self.data[idx].master_form = val

        self._set_quarter_positions()
        #self.debug_msg(self.markers["master_form"])
        #self.debug_msg(self.markers["form"])
        #form = self._guess_form()
        #print "Guessed form:"
        #print_vector(form, " | ")

    def convert_to_melody(self, start_onset=0):
        if self.spine_type != "notes":
            raise RuntimeError("Cannot convert {} spine to Melody".format(self.spine_type))
        if len(self.data) == 0:
            return Melody()
        d = self.data
        #print self
        mps = self._calc_metrical_positions()
        timing = self._calc_onsets_and_durations()
        mel = Melody()
        self._handle_ties_and_rests()

        self.phrases  = self._get_phrase_sections()
        self.choruses = self._get_chorus_sections()
        for i in range(len(d)):
            if d[i].value >= 0 and not d[i].tie:
                if mps[i].tatum <= 0:
                    self.debug_msg("Error at {} value: {}".format(i, mps[i]))
                mne = MetricalNoteEvent(onsetSec=timing[i][0], durationSec=timing[i][1], metricalPosition=mps[i], pitch=d[i].value)
                mel.append(mne)
        #print mel
        #print "Len after", len(mel)
        return mel


    def _find_first_form_start_in_solos(self):
        cur_bar = -1
        for i, ev in enumerate(self.data):
            if ev.master_form[0:4].lower() == "solo":
                cur_bar = ev.bar
                break
        if cur_bar < 0:
            print("No form start found")
            return cur_bar
        for fm in self.markers["form"]:
            if fm[0] >= cur_bar:
                return fm[0]
        return -1

    def convert_to_annotated_beat_track(self, start_onset=0):
        if self.spine_type != "chords":
            raise RuntimeError("Cannot convert {} spine to ABT".format(self.spine_type))
        if len(self.data) == 0:
            return AnnotatedBeatTrack()
        d = self.data
        #print self.markers["master_form"]
        #print self.markers["form"]
        first_form_bar_no = self._find_first_form_start_in_solos()
        #print "first_form_bar_no =", first_form_bar_no
        #print "\n".join([str(e) for e in d])
        #sys.exit(-1)
        #if self.spine_type == "chords":
        #    for ev in d:
        #        print "Bar: {} Nom: {}, qpos: {}".format(ev.bar, ev.bar*4-4, ev.qpos)
        mps = self._calc_metrical_positions()
        timing = self._calc_onsets_and_durations()
        #print "timing"
        #print "\n".join(["t:{} d:{}".format(round(t[0],2), round(t[1], 2)) for t in timing])
        abt = AnnotatedBeatTrack()
        for i in range(len(d)):
            abe = AnnotatedBeatEvent(timing[i][0], mps[i], chord=d[i].value)
            abt.append(abe)

        abt.fill_up()
        abt.set_form_start(first_form_bar_no, with_intro=True)
        #print abt
        abt.calcSignatureChanges()
        #print_vector(abt.getSignatureChanges(compact=True))
        return abt

    def debug_msg(self, s):
        if self.debug:
            print("Spine #{}: {}".format(self.id, s))

    def get_avg_tempo(self, bpm=False):
        if bpm:
            avg_tempo = mean([tempo[1] for tempo in self.tempos_bpm])
            if avg_tempo is None:
                avg_tempo = 120
        else:
            avg_tempo = mean([60./tempo[1] for tempo in self.tempos_bpm])
            if avg_tempo is None:
                avg_tempo = .5
        return avg_tempo

    def get_main_key(self):
        if len(self.keys) == 0:
            return Key("C")
        return self.keys[0]

    def get_main_meter(self):
        if len(self.meter) > 0:
            sig = self.meter[0][1].getSignature()
        else:
            sig =  Signature.fromString("4/4")
        return sig

    def _key_from_accidentals(self, accidentals):
        sharps = re.compile("[a-g][#]")
        flats  = re.compile("[a-g][-]")
        num_sharps = len(sharps.findall(accidentals))
        num_flats  = len(flats.findall(accidentals))
        if num_sharps > 0:
            if num_flats > 0:
                print("Inconsistent accidentals found: {}".format(accidentals))
                key = Key("C")
            else:
                key = Key.fromAccidentals(num_sharps, useSharp=True)
        else:
            key = Key.fromAccidentals(num_flats, useSharp=False)

        return key


    def _parse_key(self, item):
        try:
            key = Key(item[1:].replace("-", "b").replace(":", ""))
            self.debug_msg("Found new key {}".format(key))
        except:
            return False
        self.keys.append(key)
        return True

    def _parse_metadata(self, item):
        ignore = ["**kern", "**notes", "==", "*-"]
        if item[0:2] == "*M":
            if item[2] == "M":
                self.cur_tempo = int(item[3:])
                self.tempos_bpm.append((len(self.data), self.cur_tempo))
                self.debug_msg("Found new tempo {}".format(self.cur_tempo))
            else:
                self.cur_meter = MeterInfo.fromString(item[2:])
                self.meter.append((len(self.data), self.cur_meter))
                ##if len(self.bar_qstarts) == 0:
                #    if not self.cur_bar:
                #       raise RuntimeError("Bar number/Meter deadlock")
                    #bar_qpos = (self.cur_bar-1) *self.cur_meter.getQuarterLength(as_fraction=True)
                    #self.bar_qstarts.append((self.cur_bar, bar_qpos))
                    #print "Fixed bars", self.bar_qstarts
                self.debug_msg("Cur_meter: {}".format(self.cur_meter))
        elif item[0:5] == "*clef":
            self.clef = item[3:]
        elif item[0:6] == "*staff":
            self.staff = int(item[6:])
        elif item[0:5] == "*solo":
            self.debug_msg("Ignored solos")
        elif item[0:5] == "*head":
            self.debug_msg("Ignored head")
        elif item[0:7] == "*bridge":
            self.debug_msg("Ignored bridge")
        elif item[0:6] == "*intro":
            self.debug_msg("Ignored intro")
        elif item[0:3] == "*k[":
            key = self._key_from_accidentals(item[3:(len(item)-1)])
            self.keys.append(key)
        elif item[0:2] == "*>":
            self._add_master_form_marker(item[2:])
        elif item in ignore:
            self.debug_msg("Ignored: {}".format(item))
        else:
            if not self._parse_key(item):
                self.data.append(item)

    def _add_bar_marker(self, item):
        #print "bar item", item
        try:
            last_bar_no = self.markers["bars"][-1][1]
        except:
            last_bar_no = None
        try:
            bar_no = int(re.findall("[0-9]+", item)[0])
        except:
            bar_no = last_bar_no + 1
        self.markers["bars"].append((len(self.data), bar_no))
        self.cur_bar = bar_no
        if item.find("|") >= 0 or item.find("-") >= 0:
            self._add_form_marker(bar_no, item)
        #print "last_bar, cur_bar", last_bar_no , bar_no
        if last_bar_no is not None and last_bar_no + 1 != bar_no:
            raise RuntimeError("Detected non-consecutive bar number {} after {} in line {}".format(last_bar_no, bar_no, self.cur_line))
        #self.debug_msg("_add_bar_marker '{}', cur_bar={}".format(item, bar_no))
        if len(self.bar_qstarts):
            bar_qpos = self.bar_qstarts[-1][1] + self.cur_meter.getQuarterLength(as_fraction=True)
            #self.debug_msg("Bar no: {} New bar_qpos: {}, ".format(bar_no, bar_qpos))
            self.bar_qstarts.append((bar_no, bar_qpos))
        else:
            if self.cur_meter and len(self.data):
                if self.bar_before_meter:
                    bar_qpos = (bar_no-2) *self.cur_meter.getQuarterLength(as_fraction=True)
                    self.bar_qstarts.append((bar_no-1, bar_qpos))
                    self.bar_offset = bar_qpos
                    #self.debug_msg("Extra branch: bar_no: {}, qpos: {}, data_count:{}, bar_offset:{}".format(bar_no-1, bar_qpos, len(self.data), self.bar_offset))

                bar_qpos = (bar_no-1) *self.cur_meter.getQuarterLength(as_fraction=True)
                self.bar_qstarts.append((bar_no, bar_qpos))
                #self.debug_msg("Normal branch: bar_no: {}, qpos: {}".format(bar_no, bar_qpos))
            else:
                self.bar_before_meter = True
                #self.debug_msg("Found bar before meter definition, sucker")
        #print "Cur bar", bar_no

    def _add_marker(self, item, mtype="phrase"):
        markers = {"phrase": "{}", "tie":"[]"}
        o_item = item
        open_sym = markers[mtype][0]
        close_sym =  markers[mtype][1]
        has_open_sym = False
        if item[0] == open_sym:
            has_open_sym = True
            self.markers[mtype].append((len(self.data), START))
            item = item[1:]
        if item[-1] == close_sym:
            marker = SINGLETON if has_open_sym else END
            if has_open_sym:
                self.debug_msg("Found singleton '{}' of type {}".format(o_item, mtype))
            self.markers[mtype].append((len(self.data), marker))
            item = item[0:-1]
        return item

    def _add_phrase_marker(self, item):
        item = self._add_marker(item, mtype="phrase")
        return item

    def _add_tie_marker(self, item):
        item = self._add_marker(item, mtype="tie")
        if "_" in item:
            self.markers["tie"].append((len(self.data), IN_TIE))
        item = item.replace("_", "")
        return item

    def _add_master_form_marker(self, item):
        self.markers["master_form"].append((len(self.data), item))
        #if self.spine_type == "chords":
            #print "added master form", len(self.data), item

    def _add_form_marker(self, bar, item):
        if bar % 4 == 2:
            bar -= 1
        self.markers["form"].append((bar, item))

    def _parse_chord(self, item):
        duration = re.compile(r"[0-9\.]+")
        dur = duration.findall(item)[0]
        qdur =  self._make_quarter_dur(dur)
        #print "Bar: {}: Dur: {} -> qdur {}".format(self.cur_bar, dur, qdur)
        #item = re.sub(duration, "", item)
        item = item.replace(dur, "")
        #if item == "NC":
        #    print "In2: ", item
        item = item.replace(":", "")
        item = item.replace("-", "b")
        item = item.replace("4+", "11#")
        item = item.replace("5+", "13b")
        item = item.replace("+", "#")
        #item = item.replace("maj", "maj7")
        item = item.replace("dom", "7")
        item = item.replace("h7", "m7b5")
        item = item.replace("h", "m7b5")
        #print "Out", item
        item = KernChordEvent(Chord(item), qdur, bar=self.cur_bar)
        #print "Out2", item
        #print "-"*60
        item.tempo = self.cur_tempo
        return item

    def _make_quarter_dur(self, item):
        duration = re.compile("[0-9]+")
        dur = int(duration.findall(item)[0])
        qdur = Fraction(4, dur)
        dots = re.compile(r"[\.]")
        num_dots = len(dots.findall(item))
        orig_dur = qdur
        for i in range(num_dots):
            qdur += Fraction(orig_dur, 2**(i+1))
        return qdur

    def _kern_pitch_to_midi_pitch(self, item):
        pitch = re.compile("[a-gA-Gr]")
        acc = re.compile("[#-]")
        kern_pitch  = pitch.findall(item)
        accidentals = acc.findall(item)
        if kern_pitch[0] == "r":
            return -1
        note_map = {"c":0, "d":2, "e":4, "f":5, "g":7, "a":9, "b":11}

        if kern_pitch[0].lower() == kern_pitch[0]:
            octaves = len(kern_pitch)-1
        else:
            octaves = -len(kern_pitch)

        n_acc = len(accidentals)
        offset = 0
        if n_acc > 0:
            if accidentals[0] == "#":
                offset = n_acc
            else:
                offset = -n_acc
        pitch = note_map[kern_pitch[0].lower()]+ offset + 60 + 12*octaves
        return pitch

    def _parse_note(self, item):
        note = re.compile(r"[0-9\.]+[a-gA-Gr]+[#-]*")
        if len(re.sub(note, "", item)) > 0:
            raise RuntimeError("Invalid note token: '{}' in m. {}".format(item, self.cur_bar))
        #print "In: {}, p:{}, dur:{}, acc:{}".format(item, p, dur, acc, pitch)
        pitch = self._kern_pitch_to_midi_pitch(item)
        #print "In: {}, p:{}, acc:{}. out:{}".format(item, p, acc, pitch)
        qdur =  self._make_quarter_dur(item)
        item = KernNoteEvent(pitch, qdur, bar=self.cur_bar)
        item.signature = self.cur_meter
        item.tempo = self.cur_tempo
        return item

    def _parse_token(self, item):
        if item == ".":
            return
        if item[0:2] == "! ":
            return
        print(item)
        item = item.replace("??", "")
        item = item.replace("yy", "")
        print(item)
        #print("-"*60)
        #print("Before", item)

        #item = re.sub(";", "", item)
        #item = re.sub("'", "", item)
        item = re.sub("[;'/\\\JL()kK&]", "", item)
        print("Sub", item)
        item = self._add_phrase_marker(item)
        #print "Phrase", item
        item = self._add_tie_marker(item)
        #print "Tie", item
        if ":" in item or "NC" in item:
            try:
                item = self._parse_chord(item)
            except:
                raise RuntimeError("Invalid chord label '{}' in m.{}, line {}".format(item, self.cur_bar, self.cur_line))
            if self.spine_type is None:
                self.spine_type = "chords"
            elif self.spine_type == "notes":
                raise ValueError("Found chord in notes spine in m.{}, line {} ".format(self.cur_bar, self.cur_line))
        else:
            item = re.sub("[n]", "", item)
            try:
                item = self._parse_note(item)
            except:
                raise RuntimeError("Invalid note '{}' in m.{}, line {}".format(item, self.cur_bar, self.cur_line))
            if not self.spine_type:
                self.spine_type = "notes"
            elif self.spine_type == "chords":
                raise ValueError("Found note in chord spine in m.{}, line {}".format(self.cur_bar, self.cur_line))
        if item:
            if self.cur_bar is None and len(self.data) == 0:
                #print self.cur_bar
                raise ValueError("Found note {} before first bar in line {}".format(item, self.cur_line))

            self.data.append(item)


    def _set_quarter_positions(self):
        if len(self.data) == 0:
            return
        qpos = self.bar_offset
        #print self.data[0], type(self.data[0])
        #self.debug_msg("First element: {}".format(self.data[0]))
        self.data[0].qpos = qpos
        qpos = qpos + self.data[0].qdur
        for i in range(1, len(self.data)):
            self.data[i].qpos = qpos
            qpos += self.data[i].qdur

    def _get_beat_and_tatum(self, kern_event, log=False):
        log = True
        bar_offset = self.bar_qstarts[0][0]
        bar_qstart = self.bar_qstarts[kern_event.bar - bar_offset][1]
        period = kern_event.signature.period
        beat_factor = kern_event.signature.getBeatFactor(as_fraction = True)
        qperiod = period * beat_factor
        self.debug_msg("Event: {}".format(kern_event))
        qlen = int(kern_event.signature.getQuarterLength())
        print("Period: {}, BF: {} QPeriod: {}, QuartLength: {}".format(period, beat_factor, qperiod, qlen))
        if bar_qstart % qlen != 0:
            print("WARNING: Found bar start {} at invalid 4/4 position".format(bar_qstart))
            #raise 
            #log = True
        qpos_in_bar = kern_event.qpos - bar_qstart

        #bar_qlength = kern_event.signature.getQuart_erLength(as_fraction=True)
        beat_factor = kern_event.signature.getBeatFactor(as_fraction = True)
        beat0 = int(qpos_in_bar * beat_factor)
        tatum0 = qpos_in_bar * beat_factor - beat0
        if log:
            self.debug_msg("Event: {}".format(kern_event))
            self.debug_msg("bar: {}, qpos: {}".format(kern_event.bar, kern_event.qpos))
            self.debug_msg("Bar_offset:{}, bar_qstart:{}, qpos_in_bar:{}".format(bar_offset, bar_qstart, qpos_in_bar))
            self.debug_msg("BF: {}, beat0: {} tatum0: {}".format(beat_factor, beat0, tatum0))
            self.debug_msg("-"*40)

        if beat0 >= 4 or beat0 < 0 or tatum0 < 0:
            self.debug_msg("Event: {}".format(kern_event))
            self.debug_msg("bar: {}, qpos: {}".format(kern_event.bar, kern_event.qpos))
            self.debug_msg("Bar_offset:{}, bar_qstart:{}, qpos_in_bar:{}".format(bar_offset, bar_qstart, qpos_in_bar))
            self.debug_msg("BF: {}, beat0: {} tatum0: {}".format(beat_factor, beat0, tatum0))
            self.debug_msg("-"*40)
            raise RuntimeError("Spine #{}: Metrical error in m.{}".format(self.id, kern_event.bar))
        return (kern_event.bar, beat0, tatum0)

    def _beat_fractions_to_tatums(self, beat_fractions):
        if len(beat_fractions) == 0:
            return []
        division = lcm_vec([e[1].denominator for e in beat_fractions])
        tatums = [bf[1].numerator * division / bf[1].denominator +1 for bf in beat_fractions]
        invalid = sum(int(t<=0) for t in tatums)
        if invalid > 0:
            self.debug_msg("Invalid tatums found")
            self.debug_msg("Beat fractions: {}".format(beat_fractions))
            self.debug_msg("Tatums: {}".format(tatums))
            self.debug_msg("Division: {}".format(division))
            raise RuntimeError("Invalid tatum")
        return (division, tatums)

    def _calc_onsets_and_durations(self):
        d = self.data
        l = len(self.data)
        ret = [None] * l
        #cur_tempo = d[0].tempo
        for i in range(l):
            quarter_duration = 60./d[i].tempo
            onset = d[i].qpos * quarter_duration
            dur = d[i].qdur * quarter_duration
            ret[i] = (onset, dur)
        return ret

    def _calc_metrical_positions(self):
        event_stack = {}
        #self.debug = True
        for i in range(len(self.data)):
            #if self.id == 1 :
            #    print self.data[i]
            bar, beat0, tatum0 = self._get_beat_and_tatum(self.data[i], log=False)
            #if self.id == 1 and bar == 10:
            #    self._get_beat_and_tatum(self.data[i], log=True)

            if bar in event_stack:
                if beat0 + 1 in event_stack[bar]:
                    event_stack[bar][beat0 + 1].append((i, tatum0))
                else:
                    event_stack[bar][beat0 + 1] = [(i, tatum0)]
            else:
                    event_stack[bar] = {}
                    event_stack[bar][beat0 + 1] =  [(i, tatum0)]
        metrical_positions = [None] * len(self.data)
        for bar in event_stack:
            print("bar", bar)
            for beat in event_stack[bar]:
                print("beat", beat)
                events = event_stack[bar][beat]
                division, tatums = self._beat_fractions_to_tatums(events)

                for i in range(len(events)):
                    idx = events[i][0]
                    d = self.data[idx]
                    bi = BeatInfo(division, 60./d.tempo)
                    mi = d.signature
                    mc = MetricalContext(bi, mi)
                    print(mc)
                    mp = MetricalPosition(bar, beat, tatums[i], 0, mc)
                    metrical_positions[idx] = mp
        #print "\n".join([str(mp) for mp in metrical_positions])
        return metrical_positions

    def _patch_bar_gaps(self, action="patch"):
        gaps = []
        for i in range(len(self.data)-1):
            #print self.data[i+1]
            bar1 = self.data[i].bar
            bar2 = self.data[i+1].bar
            if bar2 >= bar1 + 2 :
                #print "Found bar gap of length {} at pos {}, bar:{}".format(i, bar2-bar1-1, self.data[i].bar)
                gaps.append((i, bar2-bar1-1))

        if action == "patch":
            positions = []
            items = []
            for i in range(len(gaps)):
                new_items = []
                pos = gaps[i][0]
                n_items = gaps[i][1]
                for j in range(n_items):
                    bar_dur = int(self.data[pos].signature.getQuarterLength())
                    item = KernChordEvent(Chord("NC"), bar_dur, bar=self.data[pos].bar+1+j)
                    item.tempo = self.data[pos].tempo

                    #print "New item", item
                    new_items.append(item)
                if len(new_items):
                    positions.append(pos)
                    items.append(new_items)
                    #print "Inserted {} items at pos {}".format(len(new_items), pos)
            self.data = multiple_insert(self.data, positions, items)
        else:
            return gaps

    def _get_num_ties_and_rests(self):
        num_ties = sum(1 for e in self.data if e.tie)
        num_rests = sum(1 for e in self.data if e.value<0)
        return num_ties, num_rests

    def _handle_ties_and_rests(self):
        d = self.data
        in_tie = False
        tie_idx = -1
        tie_qdur = Fraction(0)

        for i in range(len(d)):
            if d[i].value < 0 and d[i].phrase != IN_PHRASE:
                raise RuntimeError("Found phrase begin/end at rest in m.{}".format(d[i].bar))
            if d[i].tie == END and d[i].phrase == END:
                for j in range(1, len(d)-i-1):
                    if d[i+j].value > 0:
                        d[i+j].phrase = START
                        break
                #print "Phrase on tie end", d[i]
            if d[i].tie == START:
                tie_idx = i
                in_tie = True
                tie_qdur += d[i].qdur
            elif d[i].tie == NO_TIE:
                pass
            elif d[i].tie == IN_TIE:
                if not in_tie:
                    raise RuntimeError("Illegal tie continuation in m.{}".format(d[i].bar))
                if d[i].phrase == END:
                    raise RuntimeError("Phrase  end in-midth of tie in m.{}".format(d[i].bar))
                tie_qdur += d[i].qdur
            else:
                if not in_tie:
                    raise RuntimeError("Illegal tie end in m.{} {}".format(d[i].bar, i))
                d[tie_idx].qdur += tie_qdur
                d[tie_idx].tie = NO_TIE
                if d[i].phrase == START or d[i].phrase == SINGLETON:
                    raise RuntimeError("Phrase start on tie end in m.{}".format(d[i].bar))
                if d[i].phrase == END:
                     if d[tie_idx].phrase == START or d[i].phrase == SINGLETON:
                         raise RuntimeError("One note phrase found in m.{}".format(d[i].bar))
                     d[tie_idx].phrase = END
                in_tie = False
                tie_qdur = Fraction(0)
                #print "New at {}: {}".format(tie_idx, d[tie_idx])
                    #print "Found tie chain of length {}".format(i-tie_idx)
        #print "Found {} ties and {} rests = {} silent events".format(num_ties, num_rests, num_ties+num_rests)
        clean_data = []
        #self._check_phrase_consistency("Before")
        #print  "\n".join(["p: {}, v:{}, t:{}".format(e.phrase, e.value, e.tie) for e in d])

        for i in range(len(d)):
            if d[i].value >= 0 and d[i].tie == NO_TIE:
                clean_data.append(d[i])
            else:
                if d[i].master_form:
                    print("Lost master form!")
        self.data = clean_data
        self._check_phrase_consistency("")

    def _check_phrase_consistency(self, msg="DEBUG"):
        phrase_state = 1000
        errors =[]
        for i, ev in enumerate(self.data):
            if ev.phrase == SINGLETON:
                #self.debug_msg("{}: Found singleton {} in bar {}: {}".format(msg, i, ev.bar, ev))
                continue
            if ev.phrase == START:
                if phrase_state == START:
                    self.debug_msg("{}: Found double phrase start at {} in m.{}: {}".format(msg, i, ev.bar, ev))
                    errors.append(i)
                else:
                    phrase_state = START
            elif ev.phrase == END:
                if phrase_state == END:
                    self.debug_msg("{}: Found double phrase end at {} in m.{}: {}".format(msg, i, ev.bar, ev))
                    errors.append(i)
                else:
                    phrase_state = END
            else:
                if phrase_state == END and ev.value >= 0:
                    self.debug_msg("{}: Found pitch outside phrase at {} in m.{}: {}".format(msg, i, ev.bar, ev))
                    errors.append(i)
        if msg and not errors:
            self.debug_msg("{}: Phrase check O.K.".format(msg))
        return errors

    def _get_chorus_sections(self):
        d = self.data
        choruses = SectionList(sectionType="CHORUS")
        start = -1
        running_no = 1
        in_chorus = False
        for i, ev in enumerate(d):
            if ev.master_form[0:4].lower() == "solo":
                if in_chorus:
                    sect = Section(sectionType="CHORUS", val= running_no, start=start, end=i)
                    choruses.append(sect)
                    #print "Added section", sect
                    running_no += 1
                    start = i+1
                else:
                    start = i
                    in_chorus = True
            elif ev.master_form and in_chorus:
                print("WARNING: Found non-solo section '{}' at {}".format(ev.master_form, i))
                in_chorus = False
                break
        if in_chorus:
            sect = Section(sectionType="CHORUS", val= running_no, start=start, end=i)
            choruses.append(sect)
        return choruses

    def _get_phrase_sections(self):
        d = self.data
        phrases = SectionList(sectionType="PHRASE")
        start = -1
        running_no = 1
        nt, nr = self._get_num_ties_and_rests()
        if nt + nr > 0:
            raise RuntimeError("_get_phrase_sections before ties & rests handled")
        for i, ev in enumerate(d):
            #print "i: {} p:{}".format(i, ev.phrase)
            if ev.phrase == START or ev.phrase == SINGLETON:
                start = i
            if ev.phrase == END or ev.phrase == SINGLETON:
                sect = Section(sectionType="PHRASE", val= running_no, start=start, end=i)
                phrases.append(sect)
                #print "Added section", sect
                running_no += 1
        return phrases

    def _guess_form(self):
        fmarks = self.markers["form"]
        form_starts = [e[0] for e in fmarks]
        ret = [(1, FormName("A1"))]
        if len(form_starts) == 0:
            return ret
        if len(form_starts) == 1:
            return ret
        #print_vector(form_starts, ", ")
        form_lengths = diff(form_starts)
        print_vector(form_lengths, ", ")
        mean_length = mean(form_lengths)
        #print "Mean_length", mean_length
        total_length = sum(form_lengths)
        #print "Sum_length", total_length
        mode_length = mode(form_lengths)
        #print "Mode_length", mode_length

        if mean_length != int(mean_length):
            #print "Irregular form length found: {}".format(form_lengths)
            return ret
        try:
            if len(mode_length)>1:
                #print "Irregular form length found: {}".format(form_lengths)
                return ret
        except:
            pass
        if mean_length == 8 or mean_length == 4:
            #assume AABA
            if mode_length % 8 == 0:
                form = [FormName("A1"), FormName("A2"), FormName("B1"), FormName("A3")]
                ret = [(e[0], form[i % 4]) for i, e in enumerate(fmarks)]
            elif mode_length % 12 == 0:
                ret = [(e[0], FormName("A1")) for e in fmarks]
            else:
                pass
                #print "Irregular form length found: {}".format(form_lengths)
        else:
            #should be a blues o
            if mode_length % 12 == 0:
                ret = [(e[0], FormName("A1")) for e in fmarks]
            elif mode_length % 8 == 0:
                form = [FormName("A1"), FormName("A2"), FormName("B1"), FormName("A3")]
                ret = [(e[0], form[i % 4]) for i, e in enumerate(fmarks)]
            else:
                pass
                #print "Irregular form length found: {}".format(form_lengths)

        #print_vector(ret)
        return ret

    def __getitem__(self, i):
        spine = KernSpine()
        spine.data= self.data[i]
        return spine

    def __str__(self):
        return "\n".join(["{}|{}".format(i, str(d)) for i, d in enumerate(self.data)])
