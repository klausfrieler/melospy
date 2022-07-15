""" Classes to represent chords sequences

.. moduleauthor:: Klaus Frieler <kgf@ommiversum.de>

"""
import re
from fractions import Fraction

from melospy.basic_representations.chord import *
from melospy.basic_representations.meter_info import *

chords_seq_delims = {"beats": ' ', 'bars': '|'}

class ChordSequenceElement(object):

    def __init__(self, chord, bar_length=4, beat_position=1, length=4):
        self.setChord(chord)
        self.bar_length = bar_length
        self.length = length
        if beat_position > self.bar_length:
            raise ValueError("Beat position {} exceeds bar length {}".format(beat_position, bar_length))
        self.beat_pos = beat_position

    def setChord(self, chord):
        if isinstance(chord, str):
            chord = Chord(chord)
        if not isinstance(chord, Chord):
            raise ValueError("Invalid chord specification of type {}".format(type(chord)))
        self.chord = chord


    def length_in_bars(self):
        return Fraction(self.length, self.bar_length)

    def end_beat(self):
        eb = ((self.beat_pos-1) + self.length) % self.bar_length
        return eb

    def to_chord_vector(self):
        if int(self.length) != self.length:
            return []
        return [self.chord for _ in range(self.length)]

    def split(self):
        bp = self.beat_pos-1
        length = self.length
        bar_length = self.bar_length

        if (length + bp)<=bar_length:
            return [self]

        first_len = bar_length-bp
        first = ChordSequenceElement(self.chord, bar_length, self.beat_pos, first_len)
        ret = [first]
        num_bars = (length-bp) // self.bar_length

        for i in range(num_bars):
            cse = ChordSequenceElement(self.chord, bar_length, 1, bar_length)
            ret.append(cse)

        rest_len = length - first_len - num_bars*bar_length
        if rest_len>0:
            last = ChordSequenceElement(self.chord, bar_length, 1, rest_len)
            ret.append(last)

        return (ret)

    def fuse(self, ch_seq_elem, fill_up=False):
        if self.chord != ch_seq_elem.chord:
            raise ValueError("Expected chord {}, got {}".format(self.chord, ch_seq_elem.chord))

        should_start = self.end_beat()+1
        gap = ch_seq_elem.beat_pos-should_start
        if gap !=  0:
            if not fill_up:
                raise ValueError("Cannot fuse, gap of {} beats".format(gap))
            else:
                ch_seq_elem.beat_pos = should_start

        ret = ChordSequenceElement(self.chord, self.bar_length, self.beat_pos, self.length + ch_seq_elem.length)
        return ret

    def rest_beats(self):
        return (self.bar_length-(self.beat_pos-1))

    def toString(self, right_open=False):
        #print "self.bar_length, self.beat_pos, self.length", self.bar_length, self.beat_pos, self.length
        rest_beats = self.rest_beats()
        bp = self.beat_pos-1
        #print str(self.chord), rest_beats , "."*(rest_beats -1)
        #print "restbeats", rest_beats


        rest_length = self.length-rest_beats
        #print "rest_length:", rest_length
        if rest_length<=0:
            first_bar = str(self.chord) + chords_seq_delims["beats"]*(self.length-1)
            s = [first_bar]
            #print "s1=", s
        else:
            first_bar = str(self.chord) + chords_seq_delims["beats"]*(rest_beats-1)
            s = [first_bar]
            #print "s2=",s
            rest_bars = int(rest_length/self.bar_length)
            rest_beats = rest_length - rest_bars*self.bar_length
            #print "rest_length, rest_bars, rest_beats", rest_length, rest_bars, rest_beats
            s.extend([str(self.chord) + chords_seq_delims["beats"]*(self.bar_length-1)]*rest_bars)
            #print s
            if rest_beats > 0:
                #print rest_beats, int(rest_beats)
                rest_bar = str(self.chord) + chords_seq_delims["beats"]*(int(rest_beats)-1)
                #print "rest_bar", rest_bar
                s.append(rest_bar)
        if not right_open and (self.length + bp) % self.bar_length == 0:
            s.append("")
        if bp == 0:
            s.insert(0, "")
        #print "s=",s
        s = chords_seq_delims["bars"].join(s)
        return s

    def __str__(self):
        return self.toString()

    def __repr__(self):
        s = "Chord: {}, barlength: {}, beat_pos:{}, length: {}, ".format(str(self.chord), self.bar_length, self.beat_pos, self.length)
        return s


class ChordSequence(object):

    def __init__(self, chord_list=[]):
        self.chords= []
        if chord_list:
            for c in chord_list:
                if not isinstance(c, ChordSequenceElement):
                    c = ChordSequenceElement(c)
                self.append(c)

    @staticmethod
    def fromStringList(strlist, bar_length, fill_up=False):
        if len(strlist) == 1 and not len(strlist[0]):
            return None
        cse = ChordSequence()
        try:
            last = Chord(strlist[0])
        except:
            return None
        length = 0
        beat_pos = 0
        last_beat_pos = 0

        for s in strlist:
            #print "Counter:{}, bp: {}, s:{}".format(length, beat_pos, s)
            if s != "":
                c = Chord(s)
            if c != last:
                #print "Adding, length:{}, bp: {}, s:{}".format(length, last_beat_pos+1, last)
                ce = ChordSequenceElement(last, bar_length, last_beat_pos+1, length)
                cse.append(ce)
                last = c
                last_beat_pos = beat_pos
                length = 0
            length += 1
            beat_pos = (beat_pos + 1) % bar_length
        #print "Adding, length:{}, bp: {}, s:{}".format(length, last_beat_pos+1, last)

        if fill_up:
            if (last_beat_pos+length) % bar_length != 0:
                length = length + bar_length - ((last_beat_pos+length) % bar_length)

        ce = ChordSequenceElement(last, bar_length, last_beat_pos+1, length)
        cse.append(ce)
        return cse

    @staticmethod
    def fromString(s, bar_sep=chords_seq_delims["bars"], beat_sep=chords_seq_delims["beats"]):
        #print "s1= ",s
        s = s.strip(bar_sep)
        #print "s2= ",s
        elems = s.split(bar_sep)
        cs = ChordSequence()
        #print "Elements: ", elems
        for el in elems:
            if beat_sep == " ":
                c = re.compile(r"([A-G]{1}[a-z0-9b#-+]*(/[A-Z]?[b#]?)?(\s)*)")
            else:
                c = re.compile(r"([A-G]{1}[a-z0-9b#-+]*(/[A-Z]?[b#]?)?([.])*)")
            subs = c.findall(el)
            bp = 0
            length = 0
            bar_length = 0
            tmp = []
            #print "*"*60
            #print subs
            for se in subs:
                se = se[0]
                length = sum(1 for _ in se if _ == beat_sep) +1
                label = se.strip(beat_sep)
                #print "Checking: '{}' '{}' l:{}, bp:{}".format(se, label, length,bp)
                tmp.append((label, bp+1, length))
                bp = bp + length
                bar_length += length
            for _ in tmp:
                cse = ChordSequenceElement(_[0], bar_length, _[1], _[2])
                #print "Adding :{}".format(repr(cse))
                cs.append(cse)
        return cs

    def append(self, chord_seq_element):
        if not isinstance(chord_seq_element, ChordSequenceElement):
            raise ValueError("Expected 'ChordSequenceElement' got {}".format(type(chord_seq_element)))
        if len(self)>0:
            should_start = self.chords[-1].end_beat()+1
            gap = chord_seq_element.beat_pos - should_start
            if gap !=  0:
                raise ValueError("Gap of {} beats to last chord in sequence".format(gap))
        self.chords.append(chord_seq_element)
        #print "Added: {}".format(repr(chord_seq_element))
        return self

    def extend(self, chord_sequence):
        for c in chord_sequence:
            self.append(c)
        return self

    def normalize(self):
        tmp = []
        for c in self:
            if len(tmp) == 0:
                tmp.append(c.split()[0])
                tmp.extend(c.split()[1:])
            else:
                tmp.extend(c.split())
        self.chords = tmp
        return self

    def get_bar(self, bar_idx):
        count = 0
        for i, c in enumerate(self):
            count += c.length_in_bars()
            if count >= (bar_idx-1):
                return c

    def unique_chords(self):
        unique_ch = set(str(_.chord) for _ in self)
        ret = [Chord(_) for _ in unique_ch]
        return ret

    def count_unique_chords(self):
        unique_ch = set(str(_.chord) for _ in self)
        return len(unique_ch)

    def simplify(self):
        unique =  self.unique_chords()
        ret = self
        if len(unique) == 1:
            ret =  ChordSequence([list(unique)[0]])
        return ret

    def __len__(self):
        return len(self.chords)

    def __iter__(self):
        return iter(self.chords)

    def __getitem__(self, i):
        return self.chords[i]

    def to_chord_vector(self, per_beat=False):
        if per_beat:
            ret = []
            ret = ret.extend(i.to_chord_vector() for _ in self)
        else:
            ret = [i.chord for i in self]
        return ret

    def length_in_bars(self, format="float"):
        s = sum(el.length_in_bars() for el in self)
        if format == "float":
            s = float(s)
        if format == "int":
            s = int(s)
        return s

    def length_in_beats(self, format="float"):
        s = sum(el.length for el in self)
        if format == "float":
            s = float(s)
        if format == "int":
            s = int(s)
        return s

    def __str__(self):
        s = "".join([_.toString(right_open=True) for _ in self])
        if len(s) == 0:
            return ""
        return chords_seq_delims["bars"] + s + chords_seq_delims["bars"]*2

    def __repr__(self):
        s = "\n".join([repr(_) for _ in self])
        return s

class ChordProgression(object):

    def __init__(self):
        self.parts = []

    def add(self, form, chord_sequence):
        self.parts.append((form, chord_sequence))
        return self

    def get_form(self):
        ret = [_[0] for _ in self.parts]
        return ret

    def __str__(self):
        s = "\n".join(["{}: {}".format(_[0], _[1]) for _ in self.parts])
        return s
