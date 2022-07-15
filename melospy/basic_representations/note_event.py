""" Class implementation of NoteEvent """

import melospy.basic_representations.jm_util as jm_util
from melospy.basic_representations.f0_modulation import *
from melospy.basic_representations.loudness import *
from melospy.basic_representations.note_name import *
from melospy.basic_representations.rhythm_event import *

modulations = ["fall-off", "vibrato", "bend", "straight", "slide", ""]
modulations_short = ["fal", "vib", "ben", "str", "sli", ""]

class NoteEvent(RhythmEvent):

    def __init__(self, pitch, onsetSec, durationSec=0, loudness=None, modulation=""):
        """ Initialize module """
        RhythmEvent.__init__(self, onsetSec, durationSec)
        self.setPitch(pitch)
        self.setLoudness(loudness)
        self.setF0Modulation(modulation)

    def clone(self):
        """ Returns a deep copy"""
        return NoteEvent(self.getPitch(), self.getOnsetSec(), self.getDurationSec(), self.getLoudness(), self.getF0Modulation())

    def setPitch(self, val):
        """ Set function for pitch """
        if val >=0  and  val <= 127:
            self.__pitch = val
        else:
            raise ValueError("Invalid pitch value: {}".format(val))
        return self

    def getPitch(self):
        """ Get function for pitch """
        return self.__pitch

    def setLoudness(self, val):
        """ Set function for loudness"""
        if val == None:
            self.__loudness = None
        else:
            self.__loudness = Loudness.fromStruct(val)
        return self

    def getLoudness(self):
        """ Get function for loudness"""
        return self.__loudness

    def getLoudnessField(self, field, default="NA"):
        """ Get function for loudness components"""
        if self.__loudness == None:
            return default

        val = jm_util.get_safe_value_from_dict(dictionary=self.__loudness.__dict__, key=field, default=default)
        if val == None:
            val = default
        return val

    def getF0ModulationField(self, field, default="NA"):
        """ Get function for F0modulation components"""
        if self.__modulation == None:
            return default

        val = jm_util.get_safe_value_from_dict(dictionary=self.__modulation.__dict__, key=field, default=default)
        #print "Field: {}, val: {}".format(field, val)
        if val == None:
            val = default
        return val

    def getAnnotatedF0Modulation(self):
        return self.getF0ModulationField("annotated", default="")

    def setF0Modulation(self, value):
        if value == None:
            self.__modulation = None
        else:
            self.__modulation= F0Modulation.fromStruct(value)

    def getF0Modulation(self):
        """ Get function for modulation"""
        return self.__modulation

    def transpose(self, dp):
        """ Transpose pitch by dp """
        self.setPitch(self.getPitch() + dp)
        return self

    def getLilypondName(self, flat=None):
        nn = NoteName.fromMIDIPitch(self.__pitch).getLilypondName(flat)
        return nn

    def toString(self, sep="|"):
        if not isinstance(sep, str):
            sep = "|"
        res = RhythmEvent.toString(self)
        s = sep.join([res, "p:" + str(self.getPitch()), "vol:" + str(self.getLoudnessField("median")), "mod:"+ self.getAnnotatedF0Modulation()])
        return(s)

    def __eq__(self, other):
        if not isinstance(other, NoteEvent): return False
        return RhythmEvent.__eq__(self, other) and self.getPitch() == other.getPitch()

    def __ne__(self, other):
        return  not self.__eq__(other)

    def __str__(self): return self.toString()
    #def __repr__(self): return self.toString()

    pitch    = property(getPitch, setPitch)
    loudness = property(getLoudness, setLoudness)
    modulation = property(getF0Modulation, setF0Modulation)
