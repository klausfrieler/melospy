import sys

from melospy.basic_representations.note_name import *
from melospy.basic_representations.scale import *

""" Class for keys """


class Key(object):
    """ Class for keys """

    def __init__(self, rootName=None, scaleType='maj'):
        self.setRootName(rootName)
        if scaleType == None or scaleType == "":
            scaleType = None
        self.setScaleType(scaleType)

        if self.__rootName != None:
            self.__rootName.setOctave(None)

    @staticmethod
    def fromString(key):
        if len(key) == 0 or key[0] == "?":
            return Key(scaleType="")
        if key.lower() == "free":
            return Key(scaleType="")
        key = str(key).replace(" ", "-").replace(":", "-")
        key = key.replace("--", "-").replace("--", "-")
        return Key(key.partition("-")[0], key.partition("-")[2])

    @staticmethod
    def fromAccidentals(num_acc, useSharp=True):
        note = NoteName.fromAccidentals(num_acc, useSharp)
        return Key(note)

    def clone(self):
        return Key(self.__rootName, self.__scaleType)

    def getRootName(self):
        return self.__rootName

    def getScaleType(self):
        return self.__scaleType

    def setScaleType(self, val):
        """ Set ScaleType from label as defined in the ScaleManager """
        if isinstance(val, Scale)  or val == None:
            self.__scaleType = val
        else:
            try:
                self.__scaleType = theScaleManager(val)
            except Exception:
                raise ValueError("Invalid argument: '{}'".format(val))
        return self

    def setRootName(self,  val):
        if val == None:
            self.__rootName = None
            return self

        if isinstance(val, NoteName):
            self.__rootName = val
            return self

        try:
            self.__rootName = NoteName(val)
        except Exception:
            raise ValueError("Invalid Note label: '{}' ({})".format(val, type(val)))
        return self

    def getChordByScaleStep(self, scalestep="I"):
        from melospy.basic_representations.chord import Chord
        if self.empty():
            return None
        c = None
        if scalestep == "I":
            chord_name = str(self.rootName) + str(self.scaleType)
            c = Chord(chord_name)
        else:
            #TODO implement other scale steps
            pass
        return c

    def getPitchClasses(self):
        return set(self.__scaleType.getPitchClasses(self.__rootName.getPitchClass()))

    def getMIDIKeyEvent(self):
        if self.empty():
            return 0, 0
        st = self.__scaleType
        if st == None:
            st = self.__scaleType = theScaleManager("maj")
        c_o_f, maj_ind = st.getMIDIModifier()
        #print "c_o_f, maj_ind ", c_o_f, maj_ind, st
        pc_root = self.getRootPitchClass(circle_of_fifths=True)

        pc_root = pc_root + c_o_f
        while (pc_root < -7):
            pc_root += 12
        while (pc_root > 6):
            pc_root -= 12
        return pc_root, maj_ind

    def getRootPitchClass(self, circle_of_fifths=False):
        return self.rootName.getPitchClass(circle_of_fifths)

    def getLilypondString(self):
        st = self.__scaleType
        #print "st", st, type(st), str(st) in ["min", "maj"]
        if str(st) in ["min", "maj"]:
            equiv = self
        else:
            equiv = self.getMajorEquivalent()
        #print equiv
        ret = "{} \\{}or".format(equiv.getRootName().getLilypondName(), equiv.getScaleType())
        return ret

    def getMajorEquivalent(self):
        pc_root, maj_ind = self.getMIDIKeyEvent()
        use_sharp = True
        pc = self.getRootPitchClass()
        #print "pc_root, pc, flatside", pc_root, pc, self.__rootName.onTheFlatSide()
        if pc == 0:
            if pc_root < 0:
                use_sharp = False
        else:
            if self.__rootName.onTheFlatSide():
                use_sharp = False
        #print "use_sharp ", use_sharp
        new_note = NoteName.fromMIDIPitch((pc_root*7) % 12 +60, use_sharp, generic=True)
        #print "new_note", new_note, type(new_note)
        if new_note == NoteName("A#"):
            new_note = NoteName("Bb")
        equiv = Key(new_note, ["maj", "min"][maj_ind])
        return equiv

    def onTheFlatSide(self):
        equiv = self.getMajorEquivalent()
        return equiv.rootName.onTheFlatSide()

    def empty(self):
        return self.__rootName == None

    def __eq__(self, other):
        if not isinstance(other, Key):
            return False
        if other.empty() and not self.empty():
            return False
        return self.__rootName == other.__rootName and self.__scaleType == other.__scaleType

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        if self.__rootName == None:
            return ""
        baseName = str(self.getRootName())

        if isinstance(self.__scaleType, Scale) and len(str(self.__scaleType))>0:
              baseName = baseName + "-" + str(self.getScaleType())
        return str(baseName)

    rootName  = property(getRootName, setRootName)
    scaleType = property(getScaleType, setScaleType)
