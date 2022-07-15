""" Class implementation of Lilypond writer"""
import codecs
import re

from melospy.basic_representations.config_param import *
from melospy.basic_representations.jm_util import *
from melospy.basic_representations.solo import *

instrument_clefs = {"ts":"treble_8",
                    "ts-c":"treble_8",
                    "as": "treble_8",
                    "bs": "bass",
                    "bsx": "bass",
                    "cbsx": "bass",
                    "ss": "treble",
                    "sss": "treble",
                    "cl": "treble",
                    "bcl": "bass",
                    "acl": "treble",
                    "tp": "treble",
                    "tpt": "treble",
                    "flgn": "treble",
                    "tb": "bass",
                    "fl": "treble",
                    "cor": "treble",
                    "ptp": "treble",
                    "frhn": "treble",
                    "ob": "treble",
                    "voc": "treble",
                    "vib": "treble",
                    "g":"treble_8",
                    "corn": "treble"}

lilypond_header = """\\version "{}"\n
#(ly:set-option 'point-and-click #f)\n
"""
title_header = """\\header {{
  title = "{}"
  composer = "{}"
  tagline = ##f
}}
"""
global_sect = """global =
{{
    \\override Staff.TimeSignature #'style = #'()
    \\time {}
    \\clef "{}"
    \\key {}
    \\override Rest #'direction = #'0
    \\override MultiMeasureRest #'staff-position = #0
}}
"""
transpose_sect ="""\\transpose c' {}
"""
overrides = r""" \\global
  		%\\override Score.MetronomeMark #'transparent = ##t
  		%\\override Score.MetronomeMark #'stencil = ##f

  		\\override HorizontalBracket #'direction = #UP
  		\\override HorizontalBracket #'bracket-flare = #'(0 . 0)

  		\\override TextSpanner #'dash-fraction = #1.0
  		\override TextSpanner #'bound-details #'left #'text = \markup{ \concat{\draw-line #'(0 . -1.0) \draw-line #'(1.0 . 0) }}
  		\\override TextSpanner #'bound-details #'right #'text = \markup{ \concat{ \draw-line #'(1.0 . 0) \draw-line #'(0 . -1.0) }}
"""
chord_sect = """\\chords {{
        {}
      }}
"""
main_sect = """\\score
{{
    {}
    \\new Staff
    <<
    {}
    {{
     {}
     {}
     {}
    }}
    >>
}}
"""

class LilypondObject(object):
    """Abstract base class"""
    def __init__(self):
        pass

class LilypondVoid(LilypondObject):
    """Class representing a empty object"""
    def __init__(self):
        self.tokens = [str(self)]
    def debug_str(self):
        return "(void)"
    def __str__(self):
        return ""

class LilypondString(LilypondObject):
    """Class representing a string object"""
    def __init__(self, s):
        self.value = s
    def debug_str(self):
        return self.value
    def __str__(self):
        return self.value

class LilypondPartial(LilypondObject):
    """Class representing a note event as Lilypond note tokens"""
    def __init__(self, base_dur, count=1):
        self.base_dur= base_dur
        self.count = count
        self.tokens = [LilypondString(str(self))]

    def debug_str(self):
        return "Unit: {}| Mult: {}".format(self.unit, self.multiple)

    def __str__(self):
        if self.count != 1:
            ret = "\\partial {}*{}".format(self.base_dur, self.count)
        else:
            ret = "\\partial {}".format(self.base_dur)
        return ret

class LilypondBarline(LilypondObject):
    """Class representing a barline"""
    types = {"double-start": ".|",
              "double-end": "|.",
              "single": "|",
              "double": "||",
              "dotted": ";",
              "dashed": "!" }
    def __init__(self, bar_type="single"):
        self.bar_type = bar_type
        self.tokens = [LilypondString(str(self))]

    def debug_str(self):
        return "barline: {}".format(self.bar_type)

    def getTokens(self):
        return str(self)

    def __str__(self):
        try:
            tmp = self.types[self.bar_type]
        except:
            raise "Invalid bar type: '{}'".format(self.bar_type)
        if self.bar_type != "single":
            return '\\bar "{}"\n'.format(tmp)
        return "|"

class LilypondTime(LilypondObject):
    """Class representing a note event as Lilypond note tokens"""
    def __init__(self, duration, num_dots=0, tie=False, qpos=None, tuplet_factor=1, tuplet_position=None, qper=None):
        self.duration = int(duration)
        if not powTwoBit(self.duration):
            raise ValueError("Duration must be power of 2, got {}".format(duration))
        self.num_dots = num_dots
        self.tie = "~" if tie else ""
        self.tuplet_factor = tuplet_factor
        self.qpos = qpos
        self.qioi = self._calc_quarter_ioi()
        self.tuplet_position = tuplet_position
        self.qper = qper

    def has_tie(self):
        return self.tie == "~"

    def _calc_quarter_ioi(self):
        qioi = Fraction(4, self.duration)
        tot_qioi = qioi
        for i in range(self.num_dots):
            tot_qioi += qioi/2
            qioi /= 2
        tf = 1 if self.tuplet_factor == None else self.tuplet_factor
        return tot_qioi/tf

    def debug_str(self):
        return "{}{}{}|qpos:{}|qioi:{}|tfac:{}|tpos:{}".format(self.duration, "."*self.num_dots, self.tie, self.qpos, self.qioi, self.tuplet_factor, self.tuplet_position)

    def __str__(self):
        return "{}{}{}".format(self.duration, "."*self.num_dots, self.tie)

class LilypondToken(LilypondTime):
    """Class representing a note event as Lilypond note tokens"""
    def __init__(self, pitch="?", duration=4, num_dots=0, backref=None, textspan="", tie=False, qpos=None, tuplet_factor=None, tuplet_position=None, qper=None):
        LilypondTime.__init__(self, duration, num_dots, tie, qpos, tuplet_factor, tuplet_position, qper)
        self.pitch = pitch
        self.textspan = textspan
        self.backref = backref

    def debug_str(self):
        tmp = LilypondTime.debug_str(self)
        return "{}{}|bref:{}|mark:'{}'".format(self.pitch, tmp, self.backref, self.textspan)

    def __str__(self):
        tmp = LilypondTime.__str__(self)
        token = "{}{}{}".format(self.pitch, tmp, self.textspan)
        if self.tuplet_position  == "begin":
            return "\n\\tuplet {} {{{}".format(self.tuplet_factor, token)
        elif self.tuplet_position  == "end":
            return "{}}}".format(token)
        return token



class LilypondTokenChunk(LilypondObject):
    """Class representing a single note event with ties or a rest
    """

    def __init__(self, tokens=None):
        if tokens != None and not isinstance(tokens, list):
            tokens= [tokens]
        self.tokens = tokens if tokens != None else []

    def append(self, token):
        if not isinstance(token, LilypondObject):
            raise TypeError("Expected LilypondObject, got {}".format(type(token)))
        self.tokens.append(token)
        return self

    def insertToken(self, i, token):
        if not isinstance(token, LilypondObject):
            raise TypeError("Expected LilypondObject, got {}".format(type(token)))
        self.tokens.insert(i, token)
        return self

    def getQuarterIOI(self):
        qioi = 0
        for token in self.tokens:
            try:
                qioi += token.qioi
            except:
                pass
        return qioi

    def getStartQuarterPosition(self):
        for token in self.tokens:
            try:
                qpos = token.qpos
                return qpos
            except:
                pass
    def insertSingleBarlines(self):
        barline = LilypondBarline("single")
        tmp = []
        for token in self.tokens:
            try:
                if token.qpos == 0:
                    tmp.append(barline)
                    #print "insert barline before"
                    #print "token", token.debug_str()
            except:
                pass
            tmp.append(token)
        self.tokens = tmp

    def as_rest(self):
        for tok in self.tokens:
            tok.tie = ""
            tok.pitch ="r"

    def untie_last(self):
        if len(self.tokens) > 0:
            self.tokens[-1].tie = ""

    def __getitem__(self, i):
        return self.tokens[i]

    def __len__(self):
        return len(self.tokens)

    def type_str(self):
        ret = "\n".join([str(type(_)) for _ in self.tokens])
        return ret

    def debug_str(self):
        ret = "\n".join([_.debug_str() for _ in self.tokens])
        return ret

    def __str__(self):
        ret = " ".join([str(_) for _ in self.tokens])
        return ret

class LilypondStream(object):
    """Class representing a Lilypond Stream,
        a list of LilyTokenChunks
    """
    def __init__(self, chunks=None):
        if chunks != None and not isinstance(chunks, list):
            chunks = [chunks]
        self.chunks = chunks if chunks != None else []

    def append(self, chunk):
        #print type(chunk)
        if not isinstance(chunk, LilypondObject):
            #print "ALARM"
            raise TypeError("Expected LilypondObject got {} ('{}')".format(type(chunk)), chunk)
        self.chunks.append(chunk)
        return self

    def extend(self, chunks):
        if isinstance(chunks, list) or isinstance(chunks, LilypondStream):
            for chunk in chunks:
                self.append(chunk)
        elif isinstance(chunks, LilypondTokenChunk):
            self.chunks.extend(chunks)
        return self

    def flatten(self):
        ret = []
        for chunk in self.chunks:
            ret.extend(chunk.tokens)
        return ret

    def getStartQuarterPosition(self):
        return self.chunks[0].getStartQuarterPosition()

    def __getitem__(self, i):
        return self.chunks[i]

    def _set_tuplet_positions(self, debug=False):
        last_tf = 1
        tuplet_dur = 0
        for i, chunk in enumerate(self.chunks):
            if not isinstance(chunk, LilypondTokenChunk):
                continue
            for j, token in enumerate(chunk):
                if not isinstance(token, LilypondToken):
                    continue

                tf = token.tuplet_factor
                if debug:
                    print("Last_tf:{}, cur_tf:{}, tuplet_dur:{}, event:{}".format(last_tf, tf, tuplet_dur, token.debug_str()))
                if tf == 1:
                    if tuplet_dur == 0:
                        last_tf = tf
                        continue

                if last_tf == 1:
                    if tf != 1:
                        token.tuplet_position = "begin"
                        tuplet_dur += token.qioi
                        last_tf = tf
                        if debug:
                            print("Found tuplet BEGIN: {}".format(token.debug_str()))
                else:
                    #if tf != 1 and last_tf != tf:
                    #
                    #    if tf.denominator % last_tf.denominator == 0 or last_tf.denominator % tf.denominator == 0:
                    #        print "UGLY FIX", tf, last_tf, tf/last_tf
                    #        tf = last_tf
                    #    else:
                    #        raise RuntimeError("Nested Tuplets not allowed. Found {} expected {}".format(tf, last_tf))
                    tuplet_dur += token.qioi
                    if debug:
                        print("tuplet_dur={}, qioi= {}, 4*tuplet_dur={}, int(4*tuplet_dur)={}".format(tuplet_dur, token.qioi, 4*tuplet_dur, int(4*tuplet_dur)))
                    if 4  *tuplet_dur == int(4 * tuplet_dur) or tuplet_dur % tf.denominator == 0:
                        token.tuplet_position = "end"
                        tuplet_dur = 0
                        if debug:
                            print("Found tuplet END:{}".format(token.debug_str()))
                        last_tf = 1
                    #else:
                    #    last_tf = tf
        return self

    def getQuarterIOI(self):
        qioi = 0
        for chunk in self.chunks:
            qioi += chunk.getQuarterIOI()
        return qioi

    def insertTokenChunk(self, i, chunk):
        self.chunks.insert(i, chunk)

    def insertSingleBarlines(self):
        for chunk in self.chunks:
            chunk.insertSingleBarlines()

    def insertBarline(self, barline, qper):
        qpos = self.getStartQuarterPosition()
        qioi = self.getQuarterIOI()
        if qpos + qioi <= qper:
            #print "insert", qpos, qioi, qper
            #print self.debug_str()
            self.chunks[0].insertToken(0, barline)

            return
        for chunk in self.chunks:
            for i, token in enumerate(chunk):
                #print "chunk", chunk.debug_str()
                try:
                    if token.qpos == 0:
                        chunk.insertToken(i, barline)
                        return
                except:
                    pass
        raise RuntimeError("Could not insert bar line!")

    def check_tuplect_factors(self):
        flat = self.flatten()
        beat_marker = -1
        last = 0
        tfs = []
        for i in range(len(flat)-1):
            rest = flat[i].qpos - int(flat[i].qpos)
            if rest > last:
                pass

    def sanity_check(self):
        flat = self.flatten()
        bad = []
        for i in range(len(flat)-1):
            try:
                tmp = flat[i].qpos + flat[i].qioi
                qper = flat[i].qper
                if tmp % qper != flat[i+1].qpos:
                    print("Check: {} {} {}".format(tmp,  int(tmp) % qper, tmp % qper))
                    print("Error:\n 1. {}\n 2. {}".format(flat[i].debug_str(), flat[i+1].debug_str()))
                    bad.append(i)
            except:
                pass
        return bad

    def debug_str(self, sep="\n"):
        flat = self.flatten()
        ret = sep.join([_.debug_str() for _ in flat])
        return ret

    def __str__(self):
        flat = self.flatten()
        ret = " ".join([str(_) for _ in flat])
        return ret

class LilypondWriter(object):
    """Class for writing Lilypond files """

    def __init__(self, melody=None, params=None):
        self.lilypondVersion = "2.13.2"

        if isinstance(params, dict):
            params = LilypondWriterParams.fromDict(params)

        self.params = params if params != None else LilypondWriterParams()

        self.setMelody(melody)
        #print self.params

    def _get_clef(self, melody, def_clef):
        if def_clef != None and def_clef.lower() != "auto":
            #print "def_clef", def_clef
            return def_clef
        clef = "treble"
        try:
            instrument = melody.getMetadata().getField("instrument")
            clef = instrument_clefs[instrument]
            #print "\ninstrument:{}, clef:{}".format(instrument, clef)
        except:
            pass
        return clef

    def setMetadata(self, melody):
        #print "setMetadata: called", type(melody)
        #print "melody.getMetadata()", melody.getMetadata().getField("key")
        try:
            self.key = melody.getMetadata().getField("key")
        except:
            try:
                self.key = melody.getKeySections()[0].value
            except:
                self.key = Key("C")
        if not isinstance(self.key, Key):
            try:
                self.key = Key(self.key)
            except:
                self.key = Key("C")

        self.signature = melody.getMetadata().getField("signature")
        #print "self.signature", self.signature
        try:
            self.signature = melody.getMetadata().getField("signature")
        except:
            try:
                self.signature = melody[0].getMetricalContext().getSignature()
            except:
                self.signature = Signature(4, 4)

        try:
            self.tempo = round(float(melody.getMetadata().getField("avgtempo")))
        except:
            try:
                self.tempo= round(melody.getMeanTempo(bpm=True), 1)
            except:
                self.tempo = 120
        self.tempo = int(self.tempo)
        try:
            self.title = melody.getMetadata().getField("title")
        except:
            self.title = "N.N"
        try:
            self.performer = melody.getMetadata().getField("performer")
        except:
            self.performer = "N.N"
        try:
            self.title_addon = melody.getMetadata().getField("titleaddon")
        except:
            self.title_addon = ""
        try:
            self.solo_part = melody.getMetadata().getField("solopart")
        except:
            self.solo_part = ""

        self.upbeat = self._can_haz_upbeat(self.params.getValue("upbeat"), melody[0])
        #print "self.upbeat: orig: {} corr:{}".format(self.params.getValue("upbeat"), self.upbeat)

    def setMelody(self, melody):
        self.melody = melody
        if melody != None:
            self.setMetadata(melody)

    def getLilypondHeader(self):
        return lilypond_header.format(self.lilypondVersion)

    def getLilypondTitle(self):
        title = self.title
        title = re.sub('[ ]{2}', '', title)
        title = title.replace('\"', "")
        title = title.replace('\n', " - ")
        if self.title_addon != "":
            title = "{} ({})".format(title, self.title_addon)
        if self.solo_part != "" and self.solo_part != 1:
            title = "{} (Solo {})".format(title, self.solo_part)
        return title_header.format(title, self.performer)

    def getGlobalSection(self, signature, clef, key):
        return global_sect.format(str(signature), clef, key.getLilypondString())

    def getLilypondChords(self, solo):
        return ""

    def _get_partial_duration(self, qpos, qper):
        dur = qper - qpos
        denom = dur.denominator
        #print "_get_partial_duration", dur, denom, closest_power_of_two(denom)
        if denom != closest_power_of_two(denom):
            raise ValueError("No tuplets allowed for partial")
        return 4*denom, dur.numerator

    def _get_start_rest(self, melody):
        start_bar = melody[0].getBar()
        bar_offset = 0
        if start_bar > 0:
            bar_offset = start_bar-1
        #print "start_bar, bar_offset", start_bar, bar_offset
        qpos = melody[0].getQuarterPositionFractional()
        if qpos == 0 and bar_offset == 0:
            return LilypondVoid()
        qper = int(melody[0].getQuarterPeriod())

        ret = self._get_rest_chunk(0, qpos+bar_offset*qper, qper)
        ls = LilypondStream()
        ls.append(ret)
        return ls

    def _can_haz_upbeat(self, upbeat, start_event):
        """Even if upbeat representation is configured, this might not be
            feasible if solo starts with a pause after beginning of form.
            In this case return False.
            Assumes that first bar of the form is annotated with barnumber 1
        """

        #print "start_bar, bar_offset", start_bar, bar_offset
        if start_event.getQuarterPositionFractional() != 0 and start_event.getBar() > 0:
            return False
        return upbeat

    def _haz_upbeat(self, start_event):
        """
            Checks if actual upbeat is present
        """
        if self.upbeat:
            if start_event.getQuarterPositionFractional() != 0 and start_event.getBar() <= 0:
                return True
        return False

    def _needs_initial_rest(self, start_event):
        if start_event.getQuarterPositionFractional() != 0 and start_event.getBar() > 0:
                return True
        return False

    def getLilypondUpbeat(self, melody, debug=False):
        has_upbeat = self._haz_upbeat(melody[0])
        needs_start_rest = self._needs_initial_rest(melody[0])
        if debug:
            print("First event:\n {}\nhas_upbeat: {}".format(melody[0], has_upbeat))
        if not has_upbeat and not needs_start_rest:
            return LilypondStream(LilypondTokenChunk(LilypondVoid()))
        qpos = melody[0].getQuarterPositionFractional()
        qper = int(melody[0].getQuarterPeriod())

        if qpos >= qper :
            raise RuntimeError("Invalid quarter position {} for period {} of first event {}".format(qpos, qper, melody[0]))

        if self.upbeat:
            try:
                base_dur, count = self._get_partial_duration(qpos, qper)
                ret = LilypondStream(LilypondTokenChunk(LilypondPartial(base_dur, count).tokens))
            except:
                ret = self._get_start_rest(melody)
        else:
            ret = self._get_start_rest(melody)
        return ret

    def getLilypondTransposition(self, transposition):
        if transposition == None:
            lily_pitch = "c'"
        else:
            lily_pitch = NoteName.fromMIDIPitch(60 + transposition).getLilypondName()
        return transpose_sect.format(lily_pitch)

    def getLilypondTempo(self, tempo):
        return " \\tempo 4 = {}".format(tempo)

    def _chorus_hook(self, event_id, chorus_info):
        return None
        if chorus_info == None:
            return None
        try:
            tmp = chorus_info[event_id]
        except:
            return None

        if tmp["value"] < 0:
            return None

        val = None
        if tmp["marker"] == "start-list":
            val = LilypondBarline("double-start")
        elif tmp["marker"] == "end-list":
            val = LilypondBarline("double-end")
        elif tmp["marker"] == "end":
            val = LilypondBarline("double")
        return val

    def getLastChunk(self, melody, chord_context, debug=False):
        lily_stream = LilypondStream()
        has_upbeat = self._haz_upbeat(melody[0])
        if debug:
            print("has_upbeat:{} ".format(has_upbeat))

        last_note = melody[-1]
        qper = int(last_note.getQuarterPeriod())
        qpos = last_note.getQuarterPositionFractional()
        if debug:
            print("last_note:{}", last_note)
        virtual_pos = melody[0].getQuarterPositionFractional() if has_upbeat else int(last_note.getQuarterPeriod())

        max_ioi = min(virtual_pos, int(qper))
        qioi = max_ioi- qpos
        if qioi <= 0:
            qioi += qper
        if debug:
            print("qioi:{}, max_ioi:{}, virtual_pos:{}".format(qioi, max_ioi, virtual_pos))
        ls = self._get_token_stream(last_note, qioi, backref=len(melody), chord_context=chord_context, debug=False)
        lily_stream.extend(ls)
        if debug:
            print("ls", ls.debug_str())
        return ls

    def getLilypondNotes(self, melody, annotations=None, debug=False):
        qIOI = melody.getQuarterIOIsFractional()
        lily_stream = LilypondStream()
        chords = melody.getChordEvents()
        if chords == None:
            chords = [None]*len(melody)

        #print melody[0]
        upbeat_chunk = self.getLilypondUpbeat(melody, debug=False)
        lily_stream.extend(upbeat_chunk)
        #print "len:", len(melody)
        if debug:
            print("upbeat_chunk:'{}' ".format(upbeat_chunk))
        for i, qioi in enumerate(qIOI):
            if debug:
                print("="*60)
                print("{}|{}".format(i, melody[i]))
                #pass
            ls = self._get_token_stream(melody[i], qioi, backref=i, chord_context=chords[i], debug=False)
            lily_stream.extend(ls)

        ls = self.getLastChunk(melody, chord_context=chords[-1], debug=False)
        lily_stream.extend(ls)
        #if debug:
        #    for lc in lily_stream:
        #        print lc.debug_str()
        lily_stream._set_tuplet_positions()
        num_errors = lily_stream.sanity_check()
        if debug:
            print("Num timing errors:", len(num_errors))
        if debug:
            for i, lc in enumerate(lily_stream):
                print("{}".format(lc.debug_str()))
                #print "{}".format(type(lc))
        return lily_stream

    def add_measure_check(self, lily_stream):
        lily_stream.insertSingleBarlines()
        return lily_stream

    def add_chorus_annotation(self, lily_stream, melody):
        try:
            chorus_info = melody.chorus.flatten(start_value=1)
        except:
            return lily_stream

        return lily_stream

    def add_phrase_annotation(self, lily_stream):
        return lily_stream

    def add_idea_annotation(self, lily_stream):
        return lily_stream

    def write(self, filename, melody=None, debug=False):
        if melody == None:
            melody = self.melody

        if melody == None or len(melody) == 0:
            raise RuntimeError("No events to write, buddy")

        self.setMetadata(melody)
        #header
        lilypond_header_section = self.getLilypondHeader()
        if debug:
            print("header_section")
            print(header_section)
            print("="*60)

        title_section = self.getLilypondTitle()
        if debug:
            print("title_section")
            print(title_section)
            print("="*60)

        #global section
        clef = self._get_clef(melody, self.params.getValue("clef"))
        global_section = self.getGlobalSection(self.signature, clef, self.key)
        if debug:
            print("global_section")
            print(global_section)
            print("="*60)

        #transposition
        transpose_section = self.getLilypondTransposition(self.params.getValue("transpose"))
        if debug:
            print("transpose_section")
            print(transpose_section)
            print("="*60)

        #prepare chords
        chord_section = self.getLilypondChords(melody)
        if debug:
            print("chord_section")
            print(chord_section)
            print("="*60)


        #translate events to Lilypond
        #upbeat = str(self.getLilypondUpbeat(melody, self.params.getValue("upbeat")))
        lilypond_notes = self.getLilypondNotes(melody)

        if self.params.getValue("measure_check"):
            lilypond_notes = self.add_measure_check(lilypond_notes)

        if debug:
            print("lilypond_notes")
            print(lilypond_notes)
            print("="*60)

        tempo_str = self.getLilypondTempo(self.tempo)
        main_section = main_sect.format(transpose_section,
                                     chord_section,
                                     overrides,
                                     tempo_str,
                                     lilypond_notes
                                     )
        #print main_section
        with codecs.open(filename, 'w', 'utf-8') as textfile:
            textfile.write(lilypond_header_section)
            textfile.write(title_section)
            textfile.write(global_section)
            textfile.write(main_section)

        return True



    def _get_rest_chunk(self, qpos, qioi, qper, backref=None, textspan="", debug=False):
        #print "Rest: qpos={}, qioi={}, qper={}".format(qpos, qioi, qper)

        durations = self._calc_chunk_durations(qioi, qpos, qper, debug=debug)
        if len(durations) == 0:
            raise RuntimeError("No durations found for rest!")
        lc = LilypondTokenChunk()
        if len(durations) >= 2:
            #print "Swap test", durations[0], durations[1]
            if durations[0].duration < durations[1].duration and durations[0].duration > 4:
                durations[0], durations[1] = durations[1], durations[0]
                durations[0].qpos = durations[1].qpos
                durations[1].qpos = durations[0].qpos + durations[0].qioi

                #print "SWAPPED!"

        for dur in durations:
            if debug:
                print("dur:", dur.debug_str())
            lt = LilypondToken("r", dur.duration, dur.num_dots, backref=backref, textspan=textspan, tie=False, tuplet_factor=dur.tuplet_factor, qpos=dur.qpos, qper=qper)
            if debug:
                print(lt.debug_str())
            lc.append(lt)
        return lc

    def _get_token_chunk(self, metrical_note_event, qioi, backref, textspan="", chord_context=None):
        flat = self.key.onTheFlatSide()

        if chord_context != None and str(chord_context) != "NC":
            flat = chord_context.onTheFlatSide()
            #print "Chord:{}, flat:{}".format(chord_context, flat)
        pitch = metrical_note_event.getLilypondName(flat=flat)
        #print "chord_context:{}, flat={}, pitch:{}".format(chord_context, flat, pitch)
        qpos = metrical_note_event.getQuarterPositionFractional()
        qper = int(metrical_note_event.getQuarterPeriod())
        #if backref == 232:
        #    print "MNE {}".format(metrical_note_event)
        #    print "Note: qpos={}, qioi={}, qper={}".format(qpos, qioi, qper)

        if int(qper) != qper:
            raise RuntimeError("Asymmetric beats not implemented yet")
        qper = int(qper)

        durations = self._calc_chunk_durations(qioi, qpos, qper, debug=False)
        if len(durations) == 0:
            raise RuntimeError("No durations found for event: {}".format(metrical_note_event))

        lc = LilypondTokenChunk()
        for dur in durations:
            lt = LilypondToken(pitch, dur.duration, dur.num_dots, backref, textspan=textspan, tie=True, tuplet_factor=dur.tuplet_factor, qpos=dur.qpos, qper=qper)
            lc.append(lt)
        lc.untie_last()
        return lc

    def _get_token_stream(self, metrical_note_event, qioi, backref, textspan="", chord_context=None, debug=False):
        ls = LilypondStream()
        qpos = metrical_note_event.getQuarterPositionFractional()
        qper = int(metrical_note_event.getQuarterPeriod())
        qdur = metrical_note_event.estimateQuarterDuration()
        #print "_get_token_stream qioi:{}, qdur:{}, mp:{}".format(qioi, qdur, metrical_note_event.mp)
        if float(qioi-qdur) > 1:
            opt_dur = self._find_optimal_duration(qdur, qpos)
            #print "_find_optimal_duration qdur:{}, qioi:{}, opt_dur:{}, qdur/qioi:{}".format(qdur, qioi, opt_dur, float(qdur/qioi))
        else:
            opt_dur = qioi

        rest_dur = qioi - opt_dur
        if debug:
            print("-"*60)
            print("qpos={}, qioi={}, qdur={}, opt_dur={}, rest={}".format(qpos, qioi, qdur, opt_dur, rest_dur))
        lc = self._get_token_chunk(metrical_note_event, opt_dur, backref, textspan, chord_context)
        ls.append(lc)
        if rest_dur > 0:
            qpos = (qpos + opt_dur) % qper
            rests = self._get_rest_chunk(qpos, rest_dur, qper, backref=backref)
            ls.append(rests)
            #print "rests: {}".format(rests.debug_str())
        if debug:
            print("ls:\n{}".format(ls.debug_str()))

        return ls

    def _calc_dots(self, int_val):
        int_val = int(int_val)
        closest_pot = log(int_val+1, 2)
        num_dots = None
        rest = None
        if int_val > 0 and closest_pot == int(closest_pot):
            num_dots = int(closest_pot)-1
            rest = 2**int(log(int_val, 2))
        return rest, num_dots

    def _split_duration(self, int_val, max_period=None):
        ret = []
        #print "Val: {}, Period =  {}".format(int_val, max_period)

        if int_val != int(int_val):
            raise ValueError("Expect integer value got {}".format(int_val))

        if max_period != None:
            div = int(int_val/max_period)
            #print "Div: {}, Rest =  {}".format(int_val, div, int_val % max_period)
            int_val = int_val % max_period
            if div > 0:
                parts = self._split_duration(max_period)[0]
                ret = [parts] *div
                #print "Parts: {}, ret = {}".format(parts, ret)
        num_dots = self._calc_dots(int(int_val))
        #print "Num dots: {}, rest:{}".format(num_dots, int_val)

        if num_dots[0] != None:
            ret.append(num_dots)
            return ret

        while int_val > 0:
            closest_pot = int(log(int_val, 2))
            ret.append((2**closest_pot, 0))
            int_val = int_val-2**closest_pot
            num_dots = self._calc_dots(int_val)
            if num_dots[0] != None:
                ret.append(num_dots)
                break

        return ret

    def _partition_ioi(self, qioi, qpos, qper, debug=False):
        if debug:
            print("="*60)
            print("Enter _partition_ioi: qIOI={}, qpos={}, period={}".format(qioi, qpos, qper))
        ret = {}
        if int(qpos) != qpos:
            beat_offset = self._distance_next_beat(qpos)
            if debug: print("beat_offset={}".format(beat_offset))

            if qioi > beat_offset:
                ret["beat_offset"] =  {"qioi": beat_offset, "qpos": qpos}
                qioi -= beat_offset
                qpos += beat_offset
                qpos %= qper
                if debug: print("beat_offset: qpos={}, qioi={}".format(qpos, qioi))

        if qpos > 0 and qpos + qioi > qper:
            bar_offset = self._distance_next_bar(qpos, qper)
            if debug: print("bar_offset={}".format(bar_offset))
            if qioi > bar_offset:
                ret["bar_offset"] =  {"qioi": bar_offset, "qpos": qpos}
                qioi -= bar_offset
                qpos += bar_offset
                qpos %= qper
                if debug: print("bar_offset: qIOI={}, qpos={}".format(qioi, qpos))

        full_bars = int(int(qioi)/qper)
        if full_bars > 0:
            ret["full_bars"] =  {"qioi": full_bars, "qpos": qpos}
            qioi -= full_bars * qper
            qpos += full_bars * qper
            qpos %= qper
            if debug: print("full_bars: qIOI={}, qpos={}".format(qioi, qpos))

        val, tf  = self._analyse_frac_duration(qioi)
        if tf != 1 and val > 1:
            tmp = int(qioi)
            ret["tuplet_overhead"] =  {"qioi": tmp, "qpos": qpos}
            qioi -= tmp
            qpos += tmp
            qpos %= qper
            if debug: print("tuplet_overhead: qIOI={}, qpos={}".format(qioi, qpos))

        ret["main"] =  {"qioi": qioi, "qpos":qpos}
        return ret

    def _check_tuplet_factor(self, val, tf, qpos, qioi):
        #print "Val:{}, tf:{}, qpos:{}, qioi:{}".format(val, tf, qpos, qioi)
        good = True
        if tf.numerator == 1 and not powTwoBit(qpos.denominator):
            good = False
        if tf.numerator == 3 and (qpos.denominator % 9) == 0:
            good = False
        if good:
            #if qpos == int(qpos) or qioi.numerator == 1 or tmp.denominator % tf.numerator == 0:
            #print "Nothing to do"
            return val, tf

        aux_val, aux_tf  = self._analyse_frac_duration(Fraction(1, qpos.denominator))
        #print "Aux: {}, Aux_Tuplet: {}".format(aux_val, aux_tf)
        if tf != aux_tf:
            val = val * aux_tf /tf
            #if aux_tf>1:
            #    val *= 2
            tf = aux_tf
            #print "new val:{}, tf:{}".format(val, tf)
        return val, tf

    def _calc_chunk_durations(self, qioi, qpos, qper=4, debug=False):
        if debug:
            print("-"*60)
            print("Enter _calc_chunk_durations: qpos={}, qioi={}, period={}".format(qpos, qioi, qper))
        pioi = self._partition_ioi(qioi, qpos, qper)
        #print pioi
        ret = []
        if "beat_offset" in pioi:
            #print "-"*60
            val, tf  = self._analyse_frac_duration(pioi["beat_offset"]["qioi"])
            if debug: print("Beat offset: Val: {}, Tuplet: {}".format(val, tf))

            durations = self._split_duration(val.numerator)
            qoff = 0
            for d in durations:
                tmp = LilypondTime(duration=int(Fraction(val.denominator*4, d[0])),
                                   num_dots=d[1], tie=True, tuplet_factor=tf,
                                   qpos=pioi["beat_offset"]["qpos"] + qoff)
                if debug: print("Beat_offset added {} -> {}".format(d, tmp))
                qoff += tmp.qioi
                ret.append(tmp)

        if "bar_offset" in pioi:
            durations = self._split_duration(pioi["bar_offset"]["qioi"])
            qoff = 0
            for d in durations:
                tmp = LilypondTime(duration=int(Fraction(4, d[0])),
                                   num_dots=d[1], tie=True, tuplet_factor=1,
                                   qpos=pioi["bar_offset"]["qpos"] + qoff)
                if debug: print("Bar_offset added {} -> {}".format(d, tmp))
                #print "tmp.qioi", tmp.qioi
                qoff += tmp.qioi
                ret.append(tmp)

        if "full_bars" in pioi:
            durations = self._split_duration(pioi["full_bars"]["qioi"]*qper, min(qper, 4))
            for d in durations:
                tmp = LilypondTime(duration=int(Fraction(4, d[0])),
                                   num_dots=d[1], tie=True, tuplet_factor=1,
                                   qpos=pioi["full_bars"]["qpos"])
                if debug: print("Full bars added {} -> {}".format(d, tmp))
                ret.append(tmp)
        if "tuplet_overhead" in pioi:
            #print "-"*60
            durations = self._split_duration(pioi["tuplet_overhead"]["qioi"])
            qoff = 0
            for d in durations:
                tmp = LilypondTime(duration=int(Fraction(4, d[0])),
                                   num_dots=d[1], tie=True, tuplet_factor=1,
                                   qpos=pioi["tuplet_overhead"]["qpos"] + qoff)
                if debug: print("Tuplet_overhead added {} -> {}".format(d, tmp))
                qoff += tmp.qioi
                ret.append(tmp)

        if "main" in pioi:
            val, tf  = self._analyse_frac_duration(pioi["main"]["qioi"])
            #print "Main Raw: {} Val: {}, Tuplet: {}".format((pioi["main"]), val, tf)
            val, tf = self._check_tuplet_factor(val, tf, pioi["main"]["qpos"], pioi["main"]["qioi"])
            durations = self._split_duration(val.numerator, 4)
            qoff = 0
            for d in durations:
                #print "d", d, val.denominator*4, d[0], Fraction(val.denominator*4, d[0])
                tmp = LilypondTime(duration=int(Fraction(val.denominator*4, d[0])),
                                   num_dots=d[1], tie=True, tuplet_factor=tf,
                                   qpos=pioi["main"]["qpos"] + qoff)
                if debug: print("Main added {} -> {}".format(d, tmp))
                qoff += tmp.qioi
                ret.append(tmp)

        if debug:
            print("Exit _calc_chunk_durations")
            print("-"*60)
        return ret

    def _distance_next_beat(self, qpos):
        return (1-(qpos-int(qpos))) % 1

    def _distance_next_bar(self, qpos, qper):
        if qpos>= qper:
            raise RuntimeError("Invalid quarter position {} for period {}".format(qpos, qper))
        return int(qper) - qpos

    def _analyse_frac_duration(self, frac):
        #print "_analyse_frac_duration, frac=", frac
        num = frac.numerator
        denom = frac.denominator
        tuplet_factor = Fraction(1)
        closest_pot = closest_power_of_two(denom)
        val = Fraction(num, closest_pot)

        if closest_pot != denom:
            tuplet_factor = Fraction(denom, closest_pot)
        return val, tuplet_factor

    def _find_optimal_duration(self, qdur, qpos=None):
        rest = qdur - int(qdur)
        #print "qpos={}, qdur={}, rest={}, int={} ".format(qpos, qdur, rest, int(qdur))
        if rest >= Fraction(5, 6):
            return int(qdur) + 1
        if qpos != None:
            beat_offset = self._distance_next_beat(qpos)
            #print "beat_offset:{}, rest:{}".format(beat_offset, rest)
            if beat_offset > 0 :
                if rest > beat_offset:
                    tmp = self._find_optimal_duration(qdur-beat_offset, qpos+beat_offset)
                    #print "Rest: {}, beat_offset: {}, new_qdur: {}, tmp: {}".format(rest, beat_offset, qdur-beat_offset, tmp)
                    return beat_offset + tmp
                else:
                    return beat_offset + int(qdur)

        #denominators = [2,3,4,5,6,7,8,12,16,24,32]
        denominators = [2, 4]
        if qpos != None:
            if qpos.denominator > 2 and qpos.denominator % 2 == 1 :
                denominators = [qpos.denominator]

        min_diff = 1000
        min_denom = 0
        min_num = 0
        for denom in denominators:
            for num in range(1, denom):
                diff = abs(float(Fraction(num, denom)-rest))
                if diff < min_diff:
                    min_denom = denom
                    min_num = num
                    min_diff = diff

        #print "num:{}, denom:{}".format(min_num, min_denom)
        return int(qdur) + Fraction(min_num, min_denom)
