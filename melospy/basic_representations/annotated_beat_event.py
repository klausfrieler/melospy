""" Class implementation of AnnotatedBeatEvent"""

from fractions import Fraction

from melospy.basic_representations.chord import *
from melospy.basic_representations.form_name import *
from melospy.basic_representations.jm_util import cloner
from melospy.basic_representations.metrical_event import *
from melospy.basic_representations.metrical_position import *
from melospy.basic_representations.rhythm_event import *


class AnnotatedBeatEvent(RhythmEvent):

    def __init__(self, onset=0, metrical_position=None, form_part="", chord="", bass_pitch=None, chorus_id=None):
        """ Initialize module """
        self.setMetricalPosition(metrical_position)

        RhythmEvent.__init__(self, onset, self.duration, chord)
        self.bass_pitch = bass_pitch
        self.setForm(form_part)
        self.setChord(chord)
        self.signature_change = ""
        self.chorus_id = chorus_id

    def clone(self):
        """ Provides a deep copy """
        #print self.onset, self.duration, self.metrical_position, self.form, self.chord, self.bass_pitch
        abe = AnnotatedBeatEvent(self.onset,
                                 cloner(self.metrical_position),
                                 cloner(self.form),
                                 cloner(self.chord),
                                 self.bass_pitch,
                                 self.chorus_id)
        abe.duration = self.duration
        abe.signature_change = self.signature_change
        return abe

    def setMetricalPosition(self, metrical_position):
        self.metrical_position =  metrical_position
        if metrical_position != None:
            self.duration = metrical_position.getBeatInfo().beatDurationSec
        else:
            self.duration = 0
    def addBar(self, bar):
        #print "ABEvent Add bar called"
        self.metrical_position.addBar(bar)

    def setChord(self, chord):
        if isinstance(chord, Chord) or chord == None or chord == "":
            self.chord = chord
        else:
            self.chord = Chord(chord)

    def setForm(self, form):
        if isinstance(form, FormName) or form == None or form == "":
            self.form = form
        else:
            self.form = FormName(form)

    def getFormString(self):
        if self.form == None or not self.form:
            return ""
        form = str(self.form)
        if self.form.hasWildcard():
            form = "*" + form
        return form

    def getMetricalPosition(self):
        return self.metrical_position

    def getSignature(self):
        return self.metrical_position.getSignature()

    def getBar(self):
        return self.metrical_position.getBar()

    def getBeat(self):
        return self.metrical_position.getBeat()

    def getTatum(self):
        return self.metrical_position.getTatum()

    def toMetricalEvent(self, value="chord"):
        try:
            me = MetricalEvent(self.onset, self.metrical_position, self.duration)
        except:
            return None
        if value == "chord":
            me.value = self.chord
        elif value == "chorus_id":
            me.value = self.chorus_id
        elif value == "form":
            me.value = self.form
        elif value == "bass_pitch":
            me.value = self.bass_pitch
        elif value == "formstring":
            me.value = self.getFormString()
        return me

    def toString(self, sep="|"):
        """ Make a nice string """
        if not isinstance(sep, str):
              sep = "|"
        re = RhythmEvent.toString(self)
        try:
            mp = "pos:" +self.metrical_position.toString()
        except:
            mp = "pos:NA"
        return sep.join([re, mp, str(self.chord), get_NA_str(self.bass_pitch, ""), str(self.form), get_NA_str(self.chorus_id, "")])


    def __str__(self):
        return self.toString()
    #def __repr__(self): return self.toString()
