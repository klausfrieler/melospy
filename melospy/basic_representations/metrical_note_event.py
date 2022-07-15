""" Class implementation of MetricalNoteEvent """

from fractions import Fraction

from melospy.basic_representations.metrical_event import *
from melospy.basic_representations.note_event import *


class MetricalNoteEvent(NoteEvent, MetricalEvent):

    def __init__(self, onsetSec, pitch, metricalPosition, durationSec=0, durationTatum=None, loudness=None, modulation=""):
        """ Initialize module """
        #Since both super classes derive from the same super class, use one only super class constructir and do the rest manually, to avoid convfusion and double calls
        MetricalEvent.__init__(self, onsetSec, metricalPosition, durationSec, durationTatum)
        self.setPitch(pitch)
        self.setLoudness(loudness)
        self.setF0Modulation(modulation)

    def clone(self):
        """ Provides a deep copy """
        mne = MetricalNoteEvent(self.getOnsetSec(), self.getPitch(), self.getMetricalPosition().clone(), self.getDurationSec(), self.getDurationTatum(), self.loudness)
        return mne

    def estimateMetricalDurationDecimal(self):
        """ Retrieve duration as fractional of bar """
        bar_dur=self.getMetricalContext().estimateBarLengthSeconds()
        meter_dur_dec = self.duration/bar_dur
        #print "Duration:{}, MC:{}, Bar length:{}, MDD:{} ".format(self.duration, self.getMetricalContext(), bar_dur, meter_dur_dec )
        return meter_dur_dec

    def estimateBeatDurationDecimal(self):
        beat_dur=self.getMetricalContext().getBeatInfo().getBeatDurationSec()
        #print "estimateBeatDurationDecimal - dur:{}, beat_dur: {}".format(self.duration, beat_dur)
        return self.duration/beat_dur

    def estimateBeatDurationFractional(self, max_denom=16):
        bdur = self.estimateBeatDurationDecimal()
        ret  = Fraction.from_float(bdur).limit_denominator(max_denom)
        if ret < Fraction(1, max_denom):
            ret = Fraction(1, max_denom)
            #print "estimateBeatDurationFractional - bdur:{}, ret:{}".format(bdur, ret)
        return ret

    def estimateQuarterDuration(self, max_denom=16):
        beat_factor = self.getMeterInfo().getBeatFactor(as_fraction=True)
        #print "estimateQuarterDuration - beat_factor", beat_factor
        bdur = self.estimateBeatDurationFractional(max_denom)*beat_factor
        return bdur

    def getLilypondPitch(self, flat=None):
        nn = self.getLilypondName()
        return nn

    @staticmethod
    def fuse(ne, me, priority = 1):
        """ Constructs a MetricaNoteEvent object directly from a NoteEvent and a MetricalEvent, if possible
            if 'priority'  is 1, the RhythmEvent values of the NoteEvent will be used,
            if 'priority'  is 2, the RhythmEvent values of the MetricalEvent will be used
            if 'priority'  is something else, priority one is used
        """
        if priority == 2:
            mne = MetricalNoteEvent(me.getOnsetSec(), ne.getPitch(), me.getMetricalPosition().clone(), me.getDurationSec(), me.getDurationTatum())
        else:
            mne = MetricalNoteEvent(ne.getOnsetSec(), ne.getPitch(), me.getMetricalPosition().clone(), ne.getDurationSec(), me.getDurationTatum())
        return mne

    def toString(self, sep="|"):
        """ Make a nice string """
        if not isinstance(sep, str):
              sep = "|"
        ne = MetricalEvent.toString(self)
        return sep.join([ne, "p:" + str(self.getPitch()), "vol:" + str(self.getLoudnessField("median")), "mod:" + self.getAnnotatedF0Modulation()])

    def toMSCV(self):
        """ Make a nice string """
        ne = MetricalEvent.toCMSV(self, sep=";")
        return sep.join([ne, str(self.getPitch())])

    def __str__(self):
        return self.toString()
    #def __repr__(self): return self.toString()
