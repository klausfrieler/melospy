""" Class implementation of Lilypond writer"""
import codecs
import re

from melospy.basic_representations.config_param import *
from melospy.basic_representations.jm_util import *
from melospy.basic_representations.solo import *
from melospy.input_output.lilypond_intermediate import *
from melospy.input_output.lilypond_renderer import *
from melospy.input_output.lilypond_writer_data import *
from melospy.input_output.lilypond_writer_params import *


class LilypondWriter2(object):
    """Class for writing Lilypond files """

    def __init__(self, melody=None, params=None, debug=False):
        self.lilypondVersion = "2.13.2"
        self.debug = debug

        if isinstance(params, dict):
            params = LilypondWriterParams.fromDict(params)

        self.params = params if params != None else LilypondWriterParams()

        self.setMelody(melody)
        if melody != None:
            self.parse_streams(melody)
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
            #print "self.key 1", self.key
        except:
            try:
                self.key = melody.getKeySections()[0].value
                #print "self.key 2", self.key
            except:
                self.key = Key("C")
                #print "self.key 3", self.key
        if not isinstance(self.key, Key):
            try:
                self.key = Key(self.key)
                #print "self.key 4", self.key
            except:
                #print "self.key 5", self.key
                self.key = Key("C")

        try:
            self.signature = melody.getMetadata().getField("signature")
        except:
            self.signature = ""
        #EsAC files may have signatures as list of space separated strings
        if not isinstance(self.signature, Signature):
            sigs = self.signature.split(" ")
            if len(sigs) > 1:
                self.signature = Signature.fromString(sigs[0])
        try:
            sig_check = melody.signature_check()
        except:
            sig_check = False

        #print "Signature check {}.".format("passed" if sig_check else "failed")
        if not sig_check  or self.signature == "":
            self.signature = melody[0].getMetricalContext().getSignature()
            if not self.signature or str(self.signature) == "1/4":
                self.signature = Signature(4, 4)

        try:
            self.tempo = round(float(melody.getMetadata().getField("avgtempo")))
            if self.tempo <=0:
                raise
        except:
            try:
                self.tempo= round(melody.getMeanTempo(bpm=True), 1)
            except:
                self.tempo = 120
        self.tempo = int(self.tempo)
        try:
            self.title = melody.getMetadata().getField("title")
        except:
            try:
                self.title = melody.getMetadata().getField("filename_sv")
            except:
                try:
                    self.title = melody.getMetadata().getField("filename")
                except:
                    self.title = "N.N"
        try:
            self.performer = melody.getMetadata().getField("performer")
        except:
            try:
                self.performer = melody.getMetadata().getField("artist")
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

        #print "self.upbeat: orig: {} corr:{}".format(self.params.getValue("upbeat"), self.upbeat)

    def setMelody(self, melody):
        self.melody = melody
        if melody != None:
            self.setMetadata(melody)

    def getLilypondHeader(self):
        return lilypond_header.format(self.lilypondVersion)

    def getLilypondTitle(self):
        title = str(self.title)
        title = re.sub('[ ]{2}', '', title)
        title = title.replace('\"', "")
        title = title.replace('\n', " - ")
        if self.title_addon != "":
            title = "{} ({})".format(title, self.title_addon)
        if self.solo_part != "" and self.solo_part != 1:
            title = "{} (Solo {})".format(title, self.solo_part)
        return str(title_header).format(title, self.performer)

    def getGlobalSection(self, signature, clef, key):
        return global_sect.format(str(signature), clef, key.getLilypondString())

    def getLilypondTransposition(self, transposition):
        if transposition == None:
            lily_pitch = "c'"
        else:
            lily_pitch = NoteName.fromMIDIPitch(60 + transposition, useSharp=False).getLilypondName()
        return transpose_sect.format(lily_pitch)

    def fixChordTies(self, lily_beat_stream):
        lbs = lily_beat_stream.flatten()

        lbs[0].set_tied(False)
        #if first bar is pick up and has no chord
        #set the first element to tied to prevent rendering
        #in case of incomplete bars
        if lbs[0].bar < 1:
            if lbs[0].pitch == -1:
                lbs[0].set_tied(True)

        for i in range(len(lbs)-1):
            ev = lbs[i]
            if ev.bar == 1 and ev.beat == 1 and ev.qpos == 0:
                ev.set_tied(False)
                continue
            if lbs[i+1].pitch != ev.pitch:
                lbs[i+1].set_tied(False)
            else:
                lbs[i+1].set_tied(True)

    def parse_streams(self, melody):
        self.lily_note_stream = None
        self.lily_chord_stream = None
        self.lily_note_stream = LilypondIntermediateStream(melody, 
                                                           debug= self.debug)
        try:
            check_parsing = self.params["check_parsing"]
        except:
            check_parsing  = True
        if check_parsing and not self.lily_note_stream.check_all():
            raise RuntimeError("Parsing of melody failed")

        try:
            bt = melody.beattrack
            if not isinstance(bt, AnnotatedBeatTrack):
                return
        except:
            return

        first_bar = melody[0].bar
        if first_bar > 1:
            first_bar = 1
        last_bar = self.lily_note_stream[-1].bar
        last_event = self.lily_note_stream[-1][-1][-1]
        if last_event.extends_bar():
            #print "added one to last_bar"
            last_bar += 1
        bef = len(bt)
        #print "first_bar, last_bar", first_bar, last_bar
        #print bt
        bt = bt.cut_overhead(first_bar, last_bar, patch=True)
        #print "Adapting beat track. Removed {} element(s).".format(bef-len(bt))
        #suspicious = melody.beattrack.detect_suspicious_chord_changes()
        #print "Detected {} suspicious chord changes".format(suspicious)
        self.lily_chord_stream = LilypondIntermediateStream(bt, debug=False)
        #print "BEFORE\n", self.lily_chord_stream
        self.fixChordTies(self.lily_chord_stream)
        #print "AFTER", self.lily_chord_stream

    def getLilypondChords(self, solo):
        #print "AFTER\n", lily_stream
        #return ""
        if self.lily_chord_stream == None:
            return ""

        bar_lines, signatures = self.get_bar_annotations(solo)
        event_renderer= LilypondChordRenderer()
        beat_renderer = LilypondBeatRenderer(event_renderer)
        bar_renderer  = LilypondChordBarRenderer(beat_renderer, signatures)
        stream_render = LilypondStreamRenderer(bar_renderer, line_breaks=8)

        s = stream_render.render(self.lily_chord_stream, debug=False)
        if len(self.lily_chord_stream) > 1:
            s += "|"

        chords = chord_sect.format(s)
        #print "chords:\n", chords
        return chords


    def getLilypondTempo(self, tempo):
        if tempo <= 0:
            return ""
        return " \\tempo 4 = {}".format(tempo)

    def getLilypondBarNumber(self, start_bar):
        return " \\set Score.currentBarNumber = #{}".format(start_bar)

    def getLilypondNotes(self, melody, debug=False):
        if self.lily_note_stream == None:
            return ""
       #print "Barlines", sorted(bar_lines)
        #if signatures:
        #    print "signatures ", ",".join([str(s) for s in signatures])
        #bar_lines = [""]*len(melody)
        try:
            spelling_context = melody.getSpellingContext()
        except:
            spelling_context = [False]*len(melody)

        #print "Spelling context", spelling_context
        try:
            bar_lines, signatures = self.get_bar_annotations(melody)
        except:
            bar_lines, signatures = {}, {}
        event_renderer= LilypondPitchRenderer(spelling_context)
        beat_renderer = LilypondBeatRenderer(event_renderer)
        bar_renderer  = LilypondBarRenderer(beat_renderer, bar_lines, signatures)
        stream_render = LilypondStreamRenderer(bar_renderer, line_breaks=1)
        s = stream_render.render(self.lily_note_stream)
        #s = lily_stream.render()
        #print melody[0]
        s += '\\bar  ".."'
        return s

    def get_bar_annotations(self, melody):
        barlines = {}
        signatures = {}
        bt = melody.beattrack
        if not isinstance(bt, AnnotatedBeatTrack):
            try:
                signatures = melody.get_signature_changes(include_first=True)
                #print "Found {} signature changes".format(len(signatures))
            except:
                pass
            return barlines, signatures

        last_form = bt[0].getFormString()
        last_chorus = bt[0].chorus_id
        last_chorus = None
        last_sig = bt[0].getSignature()
        for abe in bt:
            if abe.getFormString() != "" and abe.getFormString() != last_form:
                barlines[abe.getBar()]= "double"
            last_form = abe.getFormString()
            if abe.chorus_id != last_chorus:
                barlines[abe.getBar()]= "chorus"
            last_chorus = abe.chorus_id
            if abe.getSignature() != "" and abe.getSignature() != last_sig:
                signatures[abe.getBar()] = abe.getSignature()
        #print barlines
        return barlines, signatures

    def add_phrase_annotation(self, lily_stream):
        return lily_stream

    def add_idea_annotation(self, lily_stream):
        return lily_stream

    def write(self, filename, melody=None, with_title_section=True, debug=False):
        if melody == None:
            melody = self.melody
        else:
            self.setMetadata(melody)
            self.parse_streams(melody)

        if melody == None or len(melody) == 0:
            raise RuntimeError("No events to write, buddy")
        #header
        lilypond_header_section = self.getLilypondHeader()
        if debug:
            print("header_section")
            print(lilypond_header_section)
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
        #chord_section = ""
        if debug:
            print("chord_section")
            print(chord_section)
            print("="*60)
        #translate events to Lilypond
        #upbeat = str(self.getLilypondUpbeat(melody, self.params.getValue("upbeat")))
        lilypond_notes = self.getLilypondNotes(melody)

        if debug:
            print("lilypond_notes")
            print(lilypond_notes)
            print("="*60)
        #print "after chord"

        tempo_str = self.getLilypondTempo(self.tempo)
        start_bar = self.lily_note_stream[0].bar
        bar_number_set = self.getLilypondBarNumber(start_bar)

        main_section = main_sect.format(transpose_section,
                                     chord_section,
                                     transpose_section,
                                     overrides,
                                     tempo_str,
                                     bar_number_set,
                                     lilypond_notes
                                     )
        #print main_section
        with codecs.open(filename, 'w', 'utf-8') as textfile:
            textfile.write(lilypond_header_section)
            if with_title_section:
                textfile.write(title_section)
            textfile.write(global_section)
            textfile.write(main_section)

        return True
