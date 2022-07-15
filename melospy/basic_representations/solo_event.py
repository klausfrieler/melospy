""" Class implementation of SoloEvent """

from melospy.basic_representations.metrical_note_event import *

modulations = ["fall-off", "vibrato", "bend", "straight", "slide", ""]
modulations_short = ["fal", "vib", "ben", "str", "sli", ""]

class SoloEvent(MetricalNoteEvent):


    def __init__(self, mne, modulations=""):
        """ Initialize module """
        mne = mne.clone()
        MetricalNoteEvent.__init__(self, mne.onset, mne.pitch, mne.getMetricalPosition(), mne.duration, mne.getDurationTatum())
        self.setF0Modulation(modulations)

    def clone(self):
        mne = MetricalNoteEvent.clone(self)
        se = SoloEvent(mne=mne, modulations=self.modulation)
        return se

#    def findModulation(self, value):
#        try:
#            idx = modulations_short.index(str(value).lower()[0:3])
#        except:
#            return None
#        return modulations[idx]

#    def setModulation(self, value):
#        """ Set function for modulation"""
#        val = self.findModulation(value)
#        if val != None:
#            self.__modulation = val
#        else:
#            raise Exception("Invalid modulation: {}".format(value))

#    def getModulation(self):
#        """ Get function for modulation"""
#        return self.__modulation

    def toString(self, sep="|"):
        """ Make a nice string """
        if not isinstance(sep, str):
              sep = "|"
        ne = MetricalNoteEvent.toString(self)
        return sep.join([ne, "mod:" + str(self.getModulation())])

    def __str__(self):
        return self.toString()

#    modulation = property(getModulation, setModulation)
