""" Class implementation of EsAC Parser"""
import os
import re
import sys

from melospy.basic_representations.jm_util import (MiniStack, chomp, dict_from_keys_vals, gcd,
                                                   math_mod, prime_exponent, remove_runs, snippet)
from melospy.basic_representations.melody import *
from melospy.basic_representations.section_list import *
from melospy.basic_representations.solo import *

plus = '+'
minus = '-'
flat = 'b'
sharp = '#'
accidental = flat + sharp
octaver = plus + minus
us = "_"
dot = "."
caret = "^"
pause = "0"
prolong = us + dot
real_notes = "1234567"
pseudo_notes = "0^"
note_numbers = "01234567^"
note_token = "01234567^+-#b_."
note_end_token = "01234567^_.#b"
note_begin_token = "01234567^+-"
meta_token = "(){}<>'@|"

bar = "|"
phrase = "\'"
phrase_special = "@"
open_3 = '('
open_5 = '<'
open_7 = '{'
open_tuplet = open_3 + open_5 + open_7
close_3 = ')'
close_5 = '>'
close_7 = '}'
close_tuplet = close_3 + close_5 + close_7
tuplet = open_tuplet + close_tuplet

note_fu = accidental + us + bar + phrase + tuplet + octaver + note_numbers
note_fu_dummy = [note_fu for i in range(8)]
note_fu_dummy[0] = us + bar + phrase + tuplet + octaver + note_numbers
note_fu_dummy.append(us + bar + phrase + tuplet + octaver + note_numbers)
notes_dummy = [i for i in note_numbers]
notes_fu        = dict_from_keys_vals(notes_dummy, note_fu_dummy)
accidental_fu   = {sharp: us + bar + phrase + tuplet + octaver + note_numbers, flat: us + bar + phrase + tuplet + octaver + note_numbers}
octaver_fu      = {plus: plus + note_numbers, minus: minus + note_numbers}
prolong_fu      = {us: prolong + bar + phrase + close_tuplet + open_tuplet +  octaver + note_numbers , dot: dot + bar + phrase + close_tuplet  + open_tuplet +  octaver + note_numbers}
open_tuplet_fu  = {open_3: open_tuplet + octaver + note_numbers, open_5: open_tuplet + octaver + note_numbers, open_7: open_tuplet + octaver + note_numbers}
close_tuplet_fu = {close_3: tuplet + octaver + note_numbers + bar + phrase, close_5: tuplet + octaver + note_numbers + bar + phrase, close_7: tuplet + bar + phrase + octaver + note_numbers}
bar_fu          = { bar: open_tuplet + octaver + note_numbers + phrase }
phrase_fu       = { phrase: open_tuplet + octaver + note_numbers + phrase_special, phrase_special: open_tuplet + octaver + note_numbers}
follow_ups = {'0': notes_fu,
               '1': notes_fu,
               '2': notes_fu,
               '3': notes_fu,
               '4': notes_fu,
               '5': notes_fu,
               '6': notes_fu,
               '7': notes_fu,
               '^': notes_fu,
               '+': octaver_fu,
               '-': octaver_fu,
               '_': prolong_fu,
               '.': prolong_fu,
               '#': accidental_fu,
               'b': accidental_fu,
               '|': bar_fu,
               '\'':phrase_fu,
               '@': phrase_fu,
               '(': open_tuplet_fu,
               '<': open_tuplet_fu,
               '{': open_tuplet_fu,
               ')': close_tuplet_fu,
               '>': close_tuplet_fu,
               '}': close_tuplet_fu
               }
token_types = {'0': 'pause',
         '1': 'note',
         '2': 'note',
         '3': 'note',
         '4': 'note',
         '5': 'note',
         '6': 'note',
         '7': 'note',
         '^': 'caret',
         '+': 'plus',
         '-': 'minus',
         '_': 'us',
         '.': 'dot',
         '#': 'sharp',
         'b': 'flat',
         '|': 'bar',
         '\'':'phrase',
         '@': 'phrase-special',
         '(': 'open3',
         '<': 'open5',
         '{': 'open7',
         ')': 'close3',
         '>': 'close5',
         '}': 'close7'
         }
diatonic_to_chromatic = {'1': 0, '2':2, '3': 4, '4': 5, '5':7, '6': 9, '7': 11}
tuplet_factors= {'(': 3, '<': 5, '{': 7,')': 3, '>': 5, '}': 7}
tuplet_co_factors= {'(': 2, '<': 4, '{': 8,')': 2, '>': 4, '}': 8}

class TupletStack(object):
    """Very very basic tuplet stack"""
    elements = "()<>{}"
    def __init__(self):
        self.stack = []

    def empty(self):
        return len(self.stack)== 0

    def flush(self):
        self.stack = []
        return self

    def count(self):
        return len(self.stack)

    def pop(self):
        if self.empty():
            return None
        self.stack = self.stack[0:(self.count()-1)]
        return self

    def last(self):
        if not self.empty():
            return self.stack[-1]
        return None

    def is_open(self, element):
        return element in "(<{"

    def is_closed(self, element):
        return element in "}>)"

    def match(self, el1, el2):

        if el1 == "(" and el2 == ")":
            return True
        if el1 == "<" and el2 == ">":
            return True
        if el1 == "{" and el2 == "}":
            return True
        return False

    def push(self, element):
        #print "Push: {}, last: {}".format(element, self.last())
        if element not in self.elements:
            raise ValueError("Invalid element:{}. Expected one of :{}".format(element, self.elements))
        #print "Closed: {}".format(self.is_closed(element))
        if self.is_closed(element):
            if not self.match(self.last(), element):
                raise ValueError("Unbalanced parantheses:{}./. {}".format(element, self.last))
            self.pop()
        else:
            self.stack.append(element)
        return self

    def __str__(self):
        return "TupleStack: {} ({})".format(self.stack, self.count())


class EsacEvent(object):
    """Class for general Esac events"""
    def __init__(self, value):
        self.value = value
    def clone(self):
        return EsacEvent(self.value)
    def __str__(self):
        return str(self.value)

class EsacNoteEvent(EsacEvent):
    """Class for Esac note events"""

    def __init__(self, value, us_count, dot_count, tuplet_factor):
        self.value = value
        self.us_count = us_count
        self.dot_count = dot_count
        if dot_count>us_count:
            raise ValueError("Number of underscores ({}) exceeds numbers of dots ({})".format(us_count, dot_count))
        dur = 1
        for i in range(us_count):
            dur *= 2
        tmp_dur = dur // 2
        for i in range(dot_count):
            dur += tmp_dur
            tmp_dur /= 2

        self.duration = dur
        self.tuplet_factor = tuplet_factor
        self.tuplet_co_factor  = 1
        for i in range(prime_exponent(tuplet_factor, 3)):
            self.tuplet_co_factor *= 2
        for i in range(prime_exponent(tuplet_factor, 5)):
            self.tuplet_co_factor *= 4
        for i in range(prime_exponent(tuplet_factor, 7)):
            self.tuplet_co_factor *= 8

    def clone(self):
        return EsacNoteEvent(self.value, self.us_count, self. dot_count, self.tuplet_factor)

    def __str__(self):
        return "p:{}|d:{}|t:{}|c:{}".format(self.value, self.duration, self.tuplet_factor, self.tuplet_co_factor)

class EsacParser(object):
    """Class for parsing EsAC code"""

    def __init__(self, code, unit, barlength, signatures, key, tempo):
        self.tempo = tempo
        self.unit = unit
        self.bar_lengths = barlength
        self.key = key
        self.signatures = signatures
        self.events = []
        self.has_upbeat = False
        self.beat_units = []
        self.meter_infos = []
        self.phrase_list = SectionList("PHRASE")
        self.set_meter_infos()
        self.parse(code)

    def getMelody(self):
        return self._melody

    def getEsacEvents(self):
        return self.events

    def set_meter_infos(self):
        if not self.signatures:
            return
        for i in range(len(self.signatures)):
            denom = self.signatures[i].denominator
            num   = self.signatures[i].numerator
            factor = self.unit/denom
            #[5, 7, 11, 13, 15, 17, 19, 21, 23, 25, 27, 29, 31]
            if denom >= 8 and num !=9 and num % 2 == 1:
                mi = MeterInfo(num, denom, num)
            else:
                mi = MeterInfo(num, denom, None)
            bu = num/mi.period*factor
            self.meter_infos.append(mi)
            self.beat_units.append(bu)
            #print "Num:{}, denom: {}, period:{}, bl:{}, unit:{}, factor:{}".format(num, denom, mi.period, bl, self.unit, factor,)

    def guess_meter_info_from_bar_length(self, length):
        if self.unit <= 4:
            if length == 1:
                raise ValueError("Numerator is 1")
            return (MeterInfo(length, self.unit), 1)
        beat_units = 1
        #print "Length: {}, cf: {}, unit:{}".format(length,beat_units, self.unit)
        while length % beat_units == 0 and self.unit/beat_units >= 4:
            beat_units *=  2
        beat_units  = beat_units // 2
        proporz = None
        num  = length // beat_units
        denom = self.unit // beat_units
        if denom >= 8 and num !=9 and num % 2 == 1:
            proporz = num
        #At this place we do not want 1/4 signature...even we admitted them in MeterInfo
        if num==1:
            raise ValueError("Numerator is 1")
        return (MeterInfo(num, denom, proporz), beat_units)

    def _is_note_end(self, token, last_token):
        #print "Token:{}, last_token:{}".format(token, last_token)

        if last_token not in note_end_token:
            return False
        if token in meta_token:
            return True
        elif token == plus:
            if last_token != plus:
                return True
        elif token == minus:
            if last_token != minus:
                return True
        elif token == caret or token == pause:
                return True
        elif token in note_numbers:
            if last_token not in "+-({<|\'@":
                return True
        return False

    def has_fixed_meter(self):
        return self.bar_lengths

    def append(self, esac_event):
        #print "Inserted: {}".format(esac_event)
        self.events.append(esac_event)

    def rescale_note_events(self):
        if len(self.events) == 0:
            return
        for e in self.events:
            try:
                e.duration = e.duration * self.max_tuplet_factor * e.tuplet_co_factor // e.tuplet_factor
            except:
                pass
        if self.has_fixed_meter():
            #print "Bar lengths before:{}".format(self.bar_lengths)
            #print "Beat units before:{}".format(self.beat_units)
            self.bar_lengths = [bl * self.max_tuplet_factor for bl in self.bar_lengths]
            self.beat_units  = [bl * self.max_tuplet_factor for bl in self.beat_units]
            #print "Bar lengths after:{}".format(self.bar_lengths)
            #print "Beat units after:{}".format(self.beat_units)
        else:
            pass
            #print "Free meter"

    def remove_events(self, removables):
        if len(self.events) == 0:
            return []
        self.events = [e for e in self.events if e.value not in removables]

    def replace_events(self, old, new):
        if len(self.events) == 0:
            return
        for e in self.events:
            if e.value == old:
                e.value = new

    def replace_events_at(self, old, new, pos):
        if len(self.events) == 0:
            return
        count = 0
        if not isinstance(pos, list):
            pos = [pos]
        for e in self.events:
            if e.value == old:
                if count in pos:
                    e.value = new
                count += 1

    def get_bar_lengths(self):
        bar_lengths = []
        bar_dur = 0
        for e in self.events:
            if e.value == 'bar':
                bar_lengths.append(bar_dur)
                bar_dur = 0
                continue
            try:
                dur = e.duration
                bar_dur += dur
            except:
                pass
        #last events has to be added, if it's a note event
        try:
            dur = self.events.duration
            bar_dur += dur
        except:
            pass
        bar_lengths.append(bar_dur)
        return bar_lengths

    def check_bar_lengths(self):
        self.has_upbeat = False
        bars = self.get_bar_lengths()
        errors = []
        fixables = []
        #error_msg = ""
        for i  in range(len(bars)):
            #print "CHECK:", bars[i], self.bar_lengths, bars[i] in self.bar_lengths
            if bars[i] not in self.bar_lengths:
                if i > 0 and i<(len(bars)-1):
                    forward = 0
                    backward = 0
                    if (bars[i] + bars[i+1]) in self.bar_lengths:
                        forward = 1
                        #print "First fixable found at", i
                    if (bars[i] + bars[i-1]) in self.bar_lengths:
                        backward = -1
                    if backward or forward:
                        fixables.append((i, backward+forward))
                    else:
                        errors.append((i, bars[i]))
                    #error_msg += "Invalid bar length {} in bar {}, expected {}\n".format(bars[i], i+1, self.bar_lengths)
                if i == 0:
                    tmp_bar = bars[0]+bars[-1]
                    if tmp_bar in self.bar_lengths or bars[i]<min(self.bar_lengths):
                        #print "Found upbeat"
                        self.has_upbeat = True
                    else:
                        errors.append((i, bars[i]))
                        #error_msg += "Invalid bar length {} in bar {}, expected {}\n".format(bars[i], i+1, self.bar_lengths)
                if i == len(bars)-1:
                    tmp_bar = bars[0]+bars[-1]
                    #print tmp_bar
                    if self.has_upbeat:
                        if tmp_bar not in self.bar_lengths:
                            errors.append((i, bars[i]))
                    else:
                        self.has_upbeat = True

        return errors, fixables

    def calculate_fixes(self, fixes):
        #pos = [f[0] for f in fixables]
        #dirs = [f[1] for f in fixables]
        if len(fixes) == 0:
            return ret

        ret = []
        remove = []
        i = 0
        zero_count = 0
        while i < len(fixes):
            dir = fixes[i][1]
            pos = fixes[i][0]
            #print "i: {}, fix:{}".format(i, fixes[i])
            if dir == 0:
                i += 1
                zero_count +=1
                continue
            if dir == 1:
                if i+1< len(fixes) and fixes[i+1][0] == pos + 1:
                    ret.append(pos)
                    #print "+1D Added ", pos, " at ", i
                    remove.append(i)
                    remove.append(i+1)
                    i += 1
                    #if i+2 < len(fixes) and fixes[i+2][1] == 0:
                    #    fixes[i+2] = (fixes[i+2][0], 1)
                else:
                    ret.append(pos)
                    #print "+1S Added ", pos, " at ", i
                    remove.append(i)
            elif dir  == -1:
                if i>0 and fixes[i-1][0] == pos-1:
                    ret.append(pos-1)
                    #print "-1D Added ", pos-1, " at ", i
                    remove.append(i)
                    remove.append(i-1)
                    #if i-2 >= 0 and fixes[i-2][1] == 0:
                    #    fixes[i-2] = (fixes[i-2][0], -1)
                else:
                    ret.append(pos-1)
                    #print "-1S Added ", pos-1, " at ", i
                    remove.append(i)
            i += 1
        new_fixes = [fixes[i] for i in range(len(fixes)) if i not in remove]
        #print "new fixes:", new_fixes
        #return ret
        if len(new_fixes)>0:
            if zero_count == len(new_fixes):
                new_fixes[0] = (new_fixes[0][0], +1)
                if len(new_fixes)>1:
                    if new_fixes[1][0] == new_fixes[0][0]+1:
                        new_fixes[1] = (new_fixes[1][0], -1)
                #print "Mod. new fixes:", new_fixes
            more = self.calculate_fixes(new_fixes)
            ret.extend(more)
        return ret

    def add_meter_info(self, b):
        (mi, bu) = self.guess_meter_info_from_bar_length(b)
        self.bar_lengths.append(b)
        self.meter_infos.append(mi)
        #adjust for some nasty peculiarities in the CWM signature notation
        bu = bu * mi.getNumerator()/ mi.getPeriod()
        self.beat_units.append(bu)
        #print "Lengths: {}, unit:{}, bu:{}, mi:{}".format(b, self.unit, bu, mi)

    def check_bars(self, code):
        #print "check_bars called"
        debug = False
        if self.has_fixed_meter():
            if debug: print("1st run")
            errors, fixables = self.check_bar_lengths()
            if debug:
                print("Bar lengths: ", self.get_bar_lengths())
                print("Errors: ", errors)
                print("Fixables: ", fixables)
            if len(fixables)>0:
                for i in range(len(fixables)):
                    bar_code = self.select_code_by_bar(code, fixables[i][0])
                    print("Invalid bar length {} in bar {}, expected {}".format(self.get_bar_lengths()[fixables[i][0]], fixables[i][0], self.bar_lengths))
                    print("-----> "+ bar_code)
                raise ValueError("Invalid bar length(s) found")

            #self.print_events()
            if errors:
                #self.replace_events_at('phrase-special', 'bar', errors)
                self.replace_events('phrase-special', 'bar')
                #code = code.replace(phrase_special, bar)
                if debug: print("2nd run")
                errors, fixables = self.check_bar_lengths()
                if debug:
                    print("Bar lengths: ", self.get_bar_lengths())
                    print("Errors: ", errors)
                    print("Fixables: ", fixables)
                if len(fixables) != 0:
                    pos = self.calculate_fixes(fixables)
                    #print pos
                    self.replace_events_at('bar', 'phrase-special', pos)
                if debug: print("3rd run")
                errors, fixables = self.check_bar_lengths()
                if debug:
                    print("Bar lengths: ", self.get_bar_lengths())
                    print("Errors: ", errors)
                    print("Fixables: ", fixables)

                #print errors
                if errors:
                    code = code.replace(phrase_special, bar)
                    #print code
                    for i in range(len(errors)):
                        bar_code = self.select_code_by_bar(code, errors[i][0])
                        print("Invalid bar length {} in bar {}, expected {}".format(errors[i][1], errors[i][0], self.bar_lengths))
                        print("-----> "+ bar_code)
                    raise ValueError("Invalid bar length(s) found")
        else:
            self.meter_infos = []
            self.beat_units = []
            self.bar_lengths = []
            #Due to ambiguity in the old EsAC code specification in the case of
            #FREE signature and
            #new lines starting with white space, it cannot be decided if the this
            #whitespace is a bar marker or not
            #we go for a possibly incorrect but simple solution:
            #ignoring this whitespace as beat marker...
            #self.replace_events('phrase-special', 'bar')
            barlens = self.get_bar_lengths()
            tmp = set(barlens)
            #print tmp, barlens, self.has_upbeat
            for b in tmp:
                try:
                    self.add_meter_info(b)
                except:
                    if b != barlens[0]:
                        print("BUMM: ", b)
                    else:
                        self.has_upbeat = True
                        tmp_b = barlens[0] + barlens[-1]
                        if tmp_b not in barlens:
                            self.add_meter_info(tmp_b)

            errors, fixables = self.check_bar_lengths()
            #print errors, fixables
            if errors:
                for i in range(len(errors)):
                    bar_code = self.select_code_by_bar(code, errors[i][0])
                    print("Invalid bar length {} in bar {}, expected {}".format(errors[i][1], errors[i][0], self.bar_lengths))
                    print("-----> "+ bar_code)
                raise ValueError("Invalid bar length(s) found")
            if len(fixables)>0:
                for i in range(len(fixables)):
                    bar_code = self.select_code_by_bar(code, fixables[i][0])
                    print("Invalid bar length {} in bar {}, expected {}".format(self.get_bar_lengths()[fixables[i][0]], fixables[i][0], self.bar_lengths))
                    print("-----> "+ bar_code)
                raise ValueError("Invalid bar length(s) found")

    def select_code_by_bar(self, code, index):
        return code.split("|")[index]

    def find_bar_length(self, bar_unit_length):
        #print self.bar_lengths, bar_unit_length
        for i in range(len(self.bar_lengths)):
            if self.bar_lengths[i] == bar_unit_length:
                return i
        return None

    def get_phrase_sections(self):
        return self.phrase_list

    def compute(self):
        if not self.meter_infos:
            raise RuntimeError("Cannot compute without Meter information")

        bar_offset = 0 if self.has_upbeat else 1
        beat_offset = 0
        bar_unit_lengths = self.get_bar_lengths()
        #compensate for possible of too short last bar, due to upbeat
        #and calculate beat offset for the upbeat bar
        #some complications for beat offsets in case of multiple or free meter needed...
        #print "Upbeat:", self.has_upbeat
        #print bar_unit_lengths
        #print ",".join([str(v) for v in self.meter_infos])
        bar_dur_init = 0
        if self.has_upbeat:
            tmp = bar_unit_lengths[0]+ bar_unit_lengths[-1]
            #print "first: {}, last: {}, sum: {}".format(bar_unit_lengths[0], bar_unit_lengths[-1], tmp)
            cur_sig = self.find_bar_length(tmp)
            if cur_sig == None:
                #if upbeat length and length of last bar do NOT match
                #assume upbeat meter is the the same as of first bar
                cur_sig = self.find_bar_length(bar_unit_lengths[1])
                cur_mi = self.meter_infos[cur_sig]

                #divisor = bar_unit_lengths[1]/cur_mi.getPeriod()
                #beat_offset = (bar_unit_lengths[1]-bar_unit_lengths[0])/divisor

                bar_dur_init = bar_unit_lengths[1]-bar_unit_lengths[0]
                #print "Upbeat MI: {}, divisor: {}, beat_offset: {}".format(cur_mi, divisor, beat_offset)
                bar_unit_lengths[-1] = bar_unit_lengths[-2]
                #print "Final bar (1): {}".format(bar_unit_lengths[-1],)
            else:
                cur_mi = self.meter_infos[cur_sig]
                #divisor = tmp/cur_mi.getPeriod()
                #beat_offset = bar_unit_lengths[-1]/divisor
                bar_dur_init = bar_unit_lengths[-1]
                #print "CurSig:{}, MI: {}, divisor: {}, beat_offset: {}".format(cur_sig, cur_mi, divisor, beat_offset)
                bar_unit_lengths[-1] = tmp
                #print "Final bar (2): {}".format(bar_unit_lengths[-1],)
        else:
            cur_sig = self.find_bar_length(bar_unit_lengths[0])
            #print "Init: ", cur_sig, bar_unit_lengths
            if cur_sig == None:
                raise RuntimeError("Incorrect first bar length.")

        #global key variables
        self.global_key = None
        minor = 0
        major = 0
        key_pc = self.key.getPitchClass()

        #running counter & stuff
        bar_count = 0
        bar_dur = bar_dur_init
        onsetSec = 0
        durationSec = 0
        #print self.bar_lengths

        cur_mi = self.meter_infos[cur_sig]
        cur_bl = self.beat_units[cur_sig]
        phrase_id = 1
        event_counter = 0
        #print "bar: {}, length: {}, cur_bar:{}, beat-length:{}, meter-info:{}".format(bar_count, bar_unit_lengths[0], cur_sig, cur_bl, str(cur_mi))
        for e in self.events:
            #print e
            if e.value == "bar" and e != self.events[-1]:
                bar_count += 1
                bar_dur = 0
                cur_sig = self.find_bar_length(bar_unit_lengths[bar_count])
                cur_mi = self.meter_infos[cur_sig]
                cur_bl = self.beat_units[cur_sig]
                #print "\n***bar: {}, cur_sig:{}, bl:{}, mi:{}".format(bar_count, cur_sig, cur_bl, str(cur_mi))
                continue

            if isinstance(e, EsacNoteEvent):
                dur = e.duration
                beat = bar_dur/cur_bl + 1
                tatum = (bar_dur % cur_bl)+1
                durationSec = float(dur)/cur_bl*self.tempo
                #print "Current beat length", cur_bl
                #print "\nEvent: {}, bar_dur: {}, beat: {}, tatum: {}".format(e, bar_dur, beat, tatum)
                #print "Onset: {}, duration: {}".format(onsetSec, durationSec)
                bi = BeatInfo(cur_bl, self.tempo)
                mc = MetricalContext(bi, cur_mi)

                #HOTFIX 19.10.2013
                #Beat offset became obsolete. now we initialize the total bar duration to
                #the correct value with better result, since tatum positions
                #are correct now too, which they weren't before...:-)
                #if bar_count != 0:
                #   beat_offset = 0

                mp = MetricalPosition(bar_count+bar_offset, beat, tatum, 0, mc)
                #print "Meter: ", mp
                if e.value == 'pause':
                    pass
                elif e.value == 'caret':
                    #print "************************CARET*******************"
                    #print durationSec
                    mne = self._melody[-1]
                    #print mne
                    mne.setDurationSec(mne.getDurationSec() + durationSec)
                    #mne.__setDurationTatum(mne.getDurationTatum() + dur)
                else:
                    mne = MetricalNoteEvent(onsetSec, e.value, mp, durationSec, dur)
                    self._melody.append(mne)
                    pc = int(e.value) % 12
                    diff = math_mod(pc - key_pc, 12)
                    if diff == 3 or diff == 8:
                        minor += 1
                    if diff ==  4 or diff ==  9:
                        major += 1
                    #print "Key-PC:{}, pc:{}, diff:{}, min:{}, maj:{}".format(key_pc, pc, diff, minor, major)
                    #print mne

                onsetSec += durationSec
                bar_dur += dur

            if e.value == "phrase" or e == self.events[-1]:
                phrase  = Section("PHRASE", phrase_id, event_counter, len(self._melody)-1)
                #print phrase
                self.phrase_list.append(phrase)
                event_counter =  len(self._melody)
                phrase_id += 1

            #except:
            #    pass
        scaleType = 'min' if minor>major else 'maj'
        self.global_key = Key(NoteName(key_pc), scaleType)
        #print __file__, key_pc, minor, major, NoteName(key_pc), Key(NoteName(key_pc)),self.global_key

    def tokenize(self, code):
        """ Tokenize code into possible tokens:
            Note complexes, tuple marker, bar separators, phrase marks
        """
        self.max_tuplet_factor = 1
        i = 0
        last = ""
        pitch = 0
        tuplet_factor = 1
        tf = []
        tuplet_stack = TupletStack()

        us_count    = 0
        dot_count   = 0
        bar_count   = 0
        phrase_count = 0
        event = None

        #print code
        tonic_pitch = self.key.getPitchClass()
        if tonic_pitch > 6:
            tonic_pitch += 48
        else:
            tonic_pitch +=60

        while i < len(code):
            ch = code[i]
            fu = None
            try:
                token_type = token_types[ch]
            except KeyError:
                raise ValueError("Invalid character at position {}: {}".format(i, snippet(code, i, 5)))

            if last:
                fu = follow_ups[last]
                if not ch in fu[last]:
                    #print "ch:{}, last: {}, FU: {}".format(ch, last, fu)
                    raise ValueError("Parse error at position {}: {}".format(i, snippet(code, i, 5)))

            if   token_type == 'plus':  pitch += 12
            elif token_type == 'minus': pitch -= 12
            elif token_type == 'sharp': pitch += 1
            elif token_type == 'flat':  pitch -= 1
            elif token_type == 'note':
                pitch += diatonic_to_chromatic[ch] + tonic_pitch
                #print "Ch: {}, d->c:{}, pitch:{}".format(ch, diatonic_to_chromatic[ch], pitch)
            elif token_type == 'caret':
                pitch = 'caret'
                if i == 0:
                    raise ValueError("Melody starts with caret {}: {}".format(i, snippet(code, i, 5)))
            elif token_type == 'pause': pitch = 'pause'
            elif token_type == 'us':  us_count +=1
            elif token_type == 'dot':
                dot_count +=1
                if dot_count>us_count:
                    raise ValueError("Misplaced dot at position {}: {} {}/{}".format(i, snippet(code, i, 5), us_count, dot_count))
            elif token_type == 'open3' or token_type == 'open5' or token_type == 'open7':
                tuplet_stack.push(ch)
                #print tuplet_stack
                tuplet_factor *= tuplet_factors[ch]
                #print "Tuplet factor: {}".format(tuplet_factor)
                event = EsacEvent(token_type)
            elif token_type == 'close3' or token_type == 'close5' or token_type == 'close7':
                try:
                    tuplet_stack.push(ch)
                    #print tuplet_stack
                except:
                    raise ValueError("Found extra closing tuplet sign at position {}: {}".format(i, snippet(code, i, 5)))
                tuplet_factor /= tuplet_factors[ch]
                #print "Tuplet factor: {}".format(tuplet_factor)
                event = EsacEvent(token_type)
            elif token_type == 'bar':
                bar_count += 1
                event = EsacEvent(token_type)
                if not tuplet_stack.empty():
                    raise ValueError("Tuplet stretching over bar line at position {}: {}".format(i, snippet(code, i, 5)))
            elif token_type == 'phrase':
                phrase_count +=1
                event = EsacEvent(token_type)
            elif token_type == 'phrase-special':
                event = EsacEvent(token_type)
            else:
                raise RuntimeError("Something impossible found at position {}: {}".format(i, snippet(code, i, 5)))

            #print

            if i != len(code)-1:
                is_note_end = self._is_note_end(code[i+1], code[i])
                #print "Next_token:{}, last_token:{}, note_end: {}".format(code[i+1], code[i], is_note_end)
            else:
                is_note_end = False

            #print "Pos:{}, char:{}, type:{}, value:{}, us:{}, dot:{}, end:{}".format(i, ch, token_type, pitch, us_count, dot_count, is_note_end)
            if is_note_end:
                self.append(EsacNoteEvent(pitch, us_count, dot_count, tuplet_factor))
                pitch       = 0
                us_count    = 0
                dot_count   = 0
                tf.append(tuplet_factor)
            if event:
                self.append(EsacEvent(token_type))

            event = None
            last = ch
            i +=1

        #last event not captured yet
        if last not in meta_token:
            self.append(EsacNoteEvent(pitch, us_count, dot_count, 1))
        self.max_tuplet_factor = lcm_vec(tf)

        #print "Max Tuplet factor: {}".format(self.max_tuplet_factor)
        #self.remove_events(['open3', 'open5', 'open7', 'close3', 'close5', 'close7'])

    def parse(self, code):
        """
        Parse EsAC code and fill Melody-object
        """
        self._melody = Melody()

        self.events = []
        self.tokenize(code)
        #self.print_events()
        self.rescale_note_events()
        #print "--------------------\nRescaled"
        #self.print_events()
        #print code
        self.check_bars(code)
        #print [str(mi) for mi in self.meter_infos]
        self.compute()
        self._melody.compress()
        #print self._melody
        key_section = SectionList()
        key_section.append(Section("KEY", self.global_key, 0, len(self._melody)-1))
        self.solo = Solo(self._melody, None, None, self.get_phrase_sections(), None, None, None, key_section)
        return True

    def print_events(self):
        print("\n".join([str(e) for e in self.events]))

    def __str__(self):
        return "\n".join([str(e) for e in self.events])

    melody  = property(getMelody)
