""" Class implementation of Lilypond Renderer"""

import melospy.basic_representations.jm_util as jm_util
import melospy.input_output.lilypond_helper as lh
from melospy.input_output.lilypond_intermediate import *


class LilypondPitchRenderer(object):
    def __init__(self,  spelling_context):
        self.spelling_context = spelling_context
        self.in_tie = False
        self.add_modulation = True

    def render_modulation(self, lily_event, s):
        if not self.add_modulation:
            if lily_event.is_tied():
                s += "~"
            return s
        if lily_event.is_tied():
            s += "~"
            if lily_event.f0_modulation == "vibrato":
                if not self.in_tie:
                    s += r"^\markup{\left-align \small vib}"
                    #print "Event:{} -> Result:{}".format(lily_event, s)
            self.in_tie = True
        else:
            if lily_event.f0_modulation == "bend":
                s += r"\bendAfter #+4 "
            elif lily_event.f0_modulation == "fall-off":
                s += r"\bendAfter #-4 "
            elif lily_event.f0_modulation == "slide":
                s += r"\glissando "
            elif lily_event.f0_modulation == "vibrato":
                if not self.in_tie:
                    s += r"^\markup{\left-align \small vib}"
                    #print "Event:{} -> Result:{}".format(lily_event, s)
            self.in_tie = False
        return s

    def render_modulation2(self, lily_event, s):
        if not self.add_modulation:
            if lily_event.is_tied():
                s += "~"
            return s
        tmp_s = s
        if lily_event.is_tied():
            s += "~"
            if lily_event.f0_modulation == "vibrato":
                if not self.in_tie:
                    s = r"\override Glissando.style = #'trill " + s
                s += r"\glissando "
                print("Event:{} -> Result:{}".format(lily_event, s))
            self.in_tie = True
        else:
            if lily_event.f0_modulation == "bend":
                s += r"\bendAfter #-4"
            elif lily_event.f0_modulation == "fall-off":
                s += r"\bendAfter #-2"
            elif lily_event.f0_modulation == "slide":
                s += r"\glissando"
            elif lily_event.f0_modulation == "vibrato":
                if self.in_tie:
                    s += r" \override Glissando.style = #'line"
                else:
                    s = r"\override Glissando.style = #'trill " + s
                    s += r"\glissando \hideNotes " + tmp_s
                    s += r" \unHideNotes \override Glissando.style = #'line"
                    print("Event:{} -> Result:{}".format(lily_event, s))
            self.in_tie = False
        return s

    def render(self, lily_event, force_multi_beat=False):
        if lily_event.pitch >= 0:
            backref = lily_event.backref
            flat = self.spelling_context[backref]
            s = NoteName.fromMIDIPitch(lily_event.pitch).getLilypondName(flat)
        else:
            s = "r"

        if force_multi_beat or lily_event.is_multi_beat():
            #print "multibeat"
            cur_dur = lily_event.qdur
        else:
            #print "no multibeat"
            cur_dur = lily_event.virtual_dur

        try:
            dur_token_in = lh.render_atomic_duration(cur_dur)
        except:
            dur_token_in  = "X"
            #print "ERROR", cur_dur, self.backref
            #print "Non atomic duration:", self.virtual_dur, self
        s = s + dur_token_in
        s = self.render_modulation(lily_event, s)
            #if lily_event.f0_modulation:
            #    print "Event:{} -> Result:{}".format(lily_event, s)
        return s


class LilypondChordRenderer(object):
    def __init__(self,  params=None):
        self.params = params

    def render(self, lily_event):
        if lily_event.pitch:
            if lily_event.get_tied():
                s = "s{}"
            else:
                if lily_event.pitch == -1:
                    s = "r{}"
                else:
                    s = str(lily_event.pitch.getLilypondTemplate())
        else:
            s = "r{}"

        try:
            dur_token_in = lh.render_atomic_duration(lily_event.qdur)
        except:
            dur_token_in  = "X"
            #print "Non atomic duration:", self.virtual_dur, self
        s = s.format(dur_token_in)
        return s


class LilypondBeatRenderer(object):
    def __init__(self, event_renderer):
        self.event_renderer = event_renderer

    def sextuplet_check(self, lily_beat):
        if lily_beat.tuplet_factor != Fraction(3, 2) :
            return None
        if lily_beat.division % 2 != 0:
            return None
        if lily_beat.division == len(lily_beat):
            return None

        lower_dur = sum(e.qdur for e in lily_beat if e.qpos < Fraction(1, 2))
        upper_dur = sum(e.qdur for e in lily_beat if e.qpos >= Fraction(1, 2) )
        last_dur_overhang = (lily_beat[-1].offset-1)
        #print "last_dur_overhang", last_dur_overhang
        upper_dur -= last_dur_overhang
        #print "lower:{}, upper: {}".format(lower_dur, upper_dur)
        return lower_dur, upper_dur

    def render_half_sextuplet(self, events, num, denom):
        ret = []
        if len(events) == 0:
            return ""

        force_multi_beat = False
        if len(events) == 1:
            force_multi_beat  = True

        for e in events:
             s = self.event_renderer.render(e, force_multi_beat =force_multi_beat )
             ret.append(s)
        s = " ".join(ret)
        if len(ret) > 1:
            s = "\\tuplet {}/{} {{".format(int(num), int(denom)) + s + "}"
        return s

    def render_splitable_sextuplet(self, lily_beat):
        lower_part = [e for e in lily_beat if e.qpos < Fraction(1, 2)]
        upper_part = [e for e in lily_beat if e.qpos >= Fraction(1, 2)]
        tf_num = lily_beat.division/2
        tf_denom = jm_util.closest_power_of_two(lily_beat.division)/2
        s_lower = self.render_half_sextuplet(lower_part, tf_num, tf_denom)
        s_upper= self.render_half_sextuplet(upper_part, tf_num, tf_denom)
        s = s_lower  + " " +  s_upper
        #print "Splitable sextuplet result", s
        return s

    def pretty_tuplet_factor(self, lily_beat):
        tf = lily_beat.tuplet_factor
        factor = jm_util.closest_power_of_two(lily_beat.division)/tf.denominator
        pretty_tf = "{}/{}".format(int(tf.numerator*factor), int(tf.denominator*factor))
        #print "ORig:{} pretty:{}".format(tf, pretty_tf)
        return pretty_tf

    def render(self, lily_beat):
        ret = []
        sext_prop = self.sextuplet_check(lily_beat)

        if sext_prop == 1 or sext_prop == 0:
            #print "Found splittable sextuplet", sext_prop
            return self.render_splitable_sextuplet(lily_beat)

        for e in lily_beat.events:
             s = self.event_renderer.render(e)
             ret.append(s)
        s = " ".join(ret)
        if lily_beat.tuplet_factor != 1 and len(lily_beat) > 1:
            s = "\\tuplet {} {{".format(self.pretty_tuplet_factor(lily_beat)) + s + "}"
        return s

class LilypondBarRenderer(object):
    bar_types = {"double-start": ".|",
                 "double-end": "|.",
                 "single": "|",
                 "double": "||",
                 "double-bold": "..",
                 "dotted": ";",
                 "dashed": "!",
                 "chorus": "||"
                 }

    def __init__(self, beat_renderer, bar_lines, signatures, chord_list=[]):
        self.beat_renderer = beat_renderer
        self.bar_lines = bar_lines
        self.signatures = signatures
        self.chord_list = chord_list

    def render(self, lily_bar, bar_count=0):
        ret = []

        for e in lily_bar.events:
             s = self.beat_renderer.render(e)
             ret.append(s)

        metric = True
        if lily_bar.qper == 1:
            metric = False

        if metric:
            barline = self.bar_types["single"]
        else:
            barline = ""
            if bar_count % 4 == 0:
                barline = self.bar_types["dashed"]
        #print "Rendering bar ", lily_bar.bar
        chorus = False
        if lily_bar.bar in self.bar_lines:
            bt = self.bar_lines[lily_bar.bar]
            try:
                barline = self.bar_types[bt]
                if bt == "chorus":
                    chorus = True
                #print "Found barline {} for m. {}".format(barline, lily_bar.bar)
                #print lily_bar
            except:
                raise ValueError("Found invalid barline type: {} for m. {}".format(bt, lily_bar.bar))

        if lily_bar.bar in self.signatures:
            ret.insert(0, "\\time {}".format(self.signatures[lily_bar.bar]))

        if barline and barline != "|":
            barline  = r'\bar "{}"'.format(barline)
        if chorus:
            barline += r" \mark \default"
            #print "Chorus found", barline
        ret.insert(0, barline)
        s = " ".join(ret)
        return s

class LilypondChordBarRenderer(object):
    bar_types = {"double-start": ".|",
                 "double-end": "|.",
                 "single": "|",
                 "double": "||",
                 "double-bold": "..",
                 "dotted": ";",
                 "dashed": "!",
                 "chorus": "||"
                 }

    def __init__(self, beat_renderer, signatures):
        self.beat_renderer = beat_renderer
        self.signatures = signatures

    def render(self, lily_bar, bar_count=0):
        ret = []

        for e in lily_bar.events:
             s = self.beat_renderer.render(e)
             ret.append(s)

        metric = True
        if lily_bar.qper == 1:
            metric = False

        if metric:
            barline = self.bar_types["single"]
        else:
            barline = ""

        if lily_bar.bar in self.signatures:
            ret.insert(0, "\\time {}".format(self.signatures[lily_bar.bar]))

        if barline and barline != "|":
            barline  = '\\bar "{}"'.format(barline)

        ret.insert(0, barline)
        s = " ".join(ret)
        return s

class LilypondStreamRenderer(object):
    def __init__(self, bar_renderer, line_breaks=1, left_pad=6):
        self.bar_renderer = bar_renderer
        self.line_breaks  = line_breaks
        self.left_pad     = " "*left_pad

    def render(self, lily_stream, debug=False):
        #if debug:
        #    print "LilypondStreamRenderer.render", lily_stream
        ret = []
        bars = self.line_breaks
        try:
            offset = lily_stream.events[0].bar-1
        except:
            offset = 0
        #print "offset", offset
        for i, e in enumerate(lily_stream.events):
            s = self.bar_renderer.render(e, i)
            if bars and (i + offset) % bars == 0:
                s = "\n" + self.left_pad  + s
            ret.append(s)
        s  = " ".join(ret)
        return s
