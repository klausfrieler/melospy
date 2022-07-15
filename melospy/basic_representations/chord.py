""" Class to represent chords, uses chord_types and note_names

.. moduleauthor:: Klaus Frieler <kgf@ommiversum.de>

"""
from melospy.basic_representations.chord_type import *
from melospy.basic_representations.key import *
from melospy.basic_representations.note_name import *
from melospy.basic_representations.scale import *


class Chord(object):
    """
        Class to represent chords.
    """

    def __init__(self, chordLabel=None):
        """ Initialize chord """
        self.__chordType = None
        self.__rootNote = None
        self.__bassNote = None
        if isinstance(chordLabel, Chord):
            chordLabel = chordLabel.getChordLabel()
        if chordLabel != None:
            try:
                self.setChordLabel(chordLabel)
            except ValueError:
                raise ValueError("Malformed chord label: " + chordLabel)
        else:
            self.__chordLabel = None

    def setChordLabel(self, chordLabel):
        """ Set chord label """
        #HACK: replace maj7 by j7
        chordLabel = chordLabel.replace("maj7", "j7")
        chordLabel = chordLabel.replace("7sus4", "sus7")
        chordLabel = chordLabel.replace("7#9", "79#")
        chordLabel = chordLabel.replace("7#5", "+7")
        # find chord bass note & remove it from chord label
        idx = chordLabel.find("/")
        l = len(chordLabel)
        if idx > -1 and idx + 1 < l:
            self.setBassNote(chordLabel[idx+1:l])
            chordLabel = chordLabel[:idx]
        else:
            self.__bassNote = None
        # find chord root note & remove
        # if second character is a b -> first two characters are root note name
        if len(chordLabel) == 1:
            # e.g. "C"
            self.__rootNote = NoteName(chordLabel)
            self.__chordType = ChordType("") # major chord without tensions
        elif len(chordLabel) > 1:
            if chordLabel.lower()[0] == "n":
                self.__rootNote = None
                self.__chordType = ChordType("nc")
            elif chordLabel[1] == "b":
                # e.g. "Abm7"
                self.__rootNote = NoteName(chordLabel[0:2])
                self.__chordType = ChordType(chordLabel[2:])
            elif chordLabel[1] == "#":
                if len(chordLabel) > 2:
                    if chordLabel[2] == "5":
                        # e.g. "G#5"
                        self.__rootNote = NoteName(chordLabel[0])
                        self.__chordType = ChordType(chordLabel[1:])
                    else:
                        # e.g. "G#m7
                        self.__rootNote = NoteName(chordLabel[0:2])
                        self.__chordType = ChordType(chordLabel[2:])
                else:
                    self.__rootNote = NoteName(chordLabel)
                    self.__chordType = ChordType("") # major chord without tensions
            else:
                # e.g. Cmaj7
                self.__rootNote = NoteName(chordLabel[0])
                self.__chordType = ChordType(chordLabel[1:])

        else:
            raise Exception("Remaining chord label is empty!")
        #print "setChordLabel", type(self.__rootNote), type(self.rootnote), type(self.getRootNote())
        #print "setChordLabel", self.__rootNote, self.rootnote, self.getRootNote()
        
    def getChordLabel(self):
        """ Return chord label """
        if self.__chordType != None:
            if self.__rootNote != None:
                chordLabel = self.__rootNote.getNoteName() + self.__chordType.getChordTypeLabel()
                if self.__bassNote != None:
                    chordLabel += "/" + self.__bassNote.getNoteName()
            else:
                chordLabel = self.__chordType.getChordTypeLabel()
        else:
            return ""
            #raise Exception("Cannot create chord label!")
        return chordLabel

    def getChordTypeLabel(self, reduced=False):
        return self.__chordType.getChordTypeLabel(reduced)

    def getLilypondTemplate(self):
        if self.__chordType == None or self.__rootNote == None:
            return "r{}"
            #raise ValueError("Could not create LilypondTemplate for chord: {}".format(self))
        chord_label = self.__rootNote.getLilypondName() + "{}"
        lily_label = self.__chordType.getLilypondLabel()
        bass_label = ""
        if self.__bassNote != None:
            bass_label = "/" + self.__bassNote.getLilypondName()
            #raise Exception("Cannot create chord label!")
        #print "Chord:{}, chord_label:{}, lily_label:{}, bass_label:{}".format(self, chord_label, lily_label, bass_label)
        tot_label = lily_label + bass_label
        if tot_label:
            chord_label += ":" + tot_label
        return chord_label

    def setChordType(self, val):
        """ set chord type """
        if isinstance(val, ChordType):
            self.__chordType = val
        else:
            self.__chordType = ChordType(val)

    def getChordType(self):
        """ get chord type """
        return self.__chordType

    def getRootNote(self):
        """ get root note """
        return self.__rootNote

    def setRootNote(self, val):
        """ set root note """
        if isinstance(val, NoteName):
            if not val.isGeneric():
                raise ValueError("Root note must be generic note name, got {}".format(val))
            self.__rootNote = val
        else:
            self.__rootNote = NoteName(val, generic = True)

    def getBassNote(self):
        """ get bass note """
        return self.__bassNote

    def setBassNote(self, val):
        """ set bass note """
        if isinstance(val, NoteName):
            if not val.isGeneric():
                raise ValueError("Bass note must be generic note name, got {}".format(val))
            self.__bassNote = val
        else:
            self.__bassNote = NoteName(val, generic = True)

    def getPitchClassSet(self, includeBass=False, rootRelative=True, withTensions=True):
        """
            Returns the chord content as a pitch class set, i.e. as asubset of the integers 0 to 11.
            Parameters:
              includeBass (default: False): adds the bass note to the PC set
              rootRelative (default: True): if True PC set is calculated with the root taken as 0, otherwise PC set with C=0 is returnd
              withTension (default: True): adds all tensions
        """
        triadPCContent  = { "maj":[0, 4, 7],"min":[0, 3, 7],"dim":[0, 3, 6],"aug":[0, 4, 8], "sus":[0, 5, 7], "nc":None}
        cht = self.getChordType()
        pcset = triadPCContent[cht.getTriadType()]

        if cht.getSeventh() != "N/A":
            pcset.append(10 + cht.getSeventh())

        if withTensions:
            if cht.getNinth() != "N/A":
                pcset.append(2 + cht.getNinth())
            if cht.getSecondNinth() is not None and cht.getSecondNinth() != "N/A":
                pcset.append(2 + cht.getSecondNinth())
            if cht.getEleventh() != "N/A":
                pcset.append(5 + cht.getEleventh())
            if cht.getThirteenth() != "N/A":
                pcset.append(9 + cht.getThirteenth())

        if includeBass:
            #print "Bass: ", self.getBassNote(), " root:", self.getRootNote()
            if self.getBassNote() != None:
                bassPC = (12+(self.getBassNote().getPitchClass()-self.getRootNote().getPitchClass())) % 12
                pcset.append(bassPC)

        if not rootRelative:
            pcset = [((pc + self.getRootNote().getPitchClass()) % 12) for pc in pcset]
        if pcset == None:
            return None
        return sorted(set(pcset))

    def getDiatonicPitchClass(self, pitch, extended=False, minmaj_map=True, filterNC=False):
        ret = ""
        if extended:
            mapping = ['1', '-', '2', '3', '3', '4', 'T', '5', '%', '6', '7', '7']
            #else:
            #    mapping = ['1', 'b2', '2', '3', '3', '4', 'T', '5', 'b6', '6', '7', '7']
        else:
            mapping = ['1', '2', '2', '3', '3', '4', 'T', '5', '6', '6', '7', '7']
        try:
            cpc = (pitch - self.getRootNote().getMIDIPitch()) % 12
            label = mapping[cpc]
            tt = self.chordtype.getTriadType()
            if minmaj_map:
                if cpc == 3 and tt != 'min' and tt != 'dim' and tt != 'sus':
                    label = "B"
                if cpc == 4 and tt != 'maj' and tt != 'aug':
                    label = ">"
                if cpc == 10 and self.chordtype.getSeventh() == 1:
                    label = "<"
                if cpc == 11 and self.chordtype.getSeventh() == 0:
                    label = "L"
            ret = label
        except:
            if not filterNC:
                ret = "X"

        return ret

    def getChromatic(self, pitch, filterNC):
        cdpcx = self.getDiatonicPitchClass(pitch, True, True, filterNC)
        try:
            _ = int(cdpcx)
            return "diatonic"
        except:
            return "chromatic"

    def getMostLikelyScale(self):
        c = Chord(self.getChordLabel())
        c.setRootNote(NoteName("C"))
        ret = None
        for s in theScaleManager.most_likely:
            #print c, s
            if Chord(s) == c:
                return theScaleManager.most_likely[s]
        return ret

    def matchScale(self, pcvec):
        ret = []
        #print roots, pcvec, len(pcvec)
        root = self.getRootNote().getPitchClass()
        for scale in self.__scales:
            if scale =='none':
                continue
            comp = theScaleManager.calcCompatibility(scale, root, pcvec, weighted = True)
            val = round(float(comp[0])/len(pcvec), 3)
            val = val*(1-0.25*abs(len(self.__scales[scale])-7))
            val = val*self.__scale_preferences[scale]
            if self.getMostLikelyScale() == scale:
                val *= 1.25
            #print root, scale, val, comp
            if len(ret) == 0:
                ret.append((NoteName(root).getBaseName(), scale, val))
            elif val > ret[-1][2]:
                ret = [(NoteName(root).getBaseName(), scale, val)]
            elif val == ret[-1][2]:
                ret.append((NoteName(root).getBaseName(), scale, val))
        #print ret
        return ret

    def onTheFlatSide(self):
        ct = self.chordtype.getTriadType()
        #print "ct", self, ct
        #print "="*60
        if ct in ["maj", "aug", "sus", "nc"]:
            tmp_ct = "maj"
        else:
            tmp_ct = "min"
        root_pc = self.getRootNote().getMIDIPitch() % 12
        if root_pc == 8 and tmp_ct == "min":
            return self.getRootNote().onTheFlatSide()
        root = self.getRootNote()

        if ct in ["maj", "aug", "sus"] and self.chordtype.getSeventh() == 0:
            root = NoteName.fromMIDIPitch((root_pc + 5) % 12, generic=True)
            if self.getRootNote() == NoteName("Db"):
                root = NoteName("Gb")
            if self.chordtype.getNinth() == -1 or self.chordtype.getThirteenth() == -1:
                tmp_ct = "min"

        if ct == "maj" and self.chordtype.getSeventh() == 1:
            if self.chordtype.getEleventh() == 1:
                root = NoteName.fromMIDIPitch((root_pc - 5) % 12, generic=True)

        if ct == "dim":
            if self.chordtype.getSeventh() <= 0:
                root = NoteName.fromMIDIPitch((root_pc - 2) % 12, generic=True)
                tmp_ct  = "min"
        if root.onTheFlatSide() != self.getRootNote().onTheFlatSide():
            root = root.getEnharmonic()
        #print "ct: {}, tmp_ct:{}, root_orig:{}, root:{}".format(ct, tmp_ct, self.rootnote, root)
        dummy_key = Key(root, tmp_ct)
        #print "Orig:{} -> {}".format(self, dummy_key)

        return dummy_key.onTheFlatSide()

    def isMinorParallel(self, other):
        ct1 = self.getChordType()
        ct2 = other.getChordType()

        tt1 = ct1.getTriadType()
        tt2 = ct2.getTriadType()
        sev1 = ct1.getSeventh()
        sev2 = ct2.getSeventh()
        #print "C1: {}, CT1: {}".format(self, ct1)
        #print "C2: {}, CT2: {}".format(other, ct2)
        ret = False

        if tt1 == "min" and tt2 == "maj":
            if sev1 == -1 or sev2 == 0 or sev2 == -1:
                return False

            root1 = self.getRootNote().getPitchClass()
            root2 = other.getRootNote().getPitchClass()
            diff = (root2 - root1) % 12
            if diff == 3:
                ret = True
        return ret
    def __eq__(self, other):
        if not isinstance(other, Chord):
            return False
        return self.getChordLabel() == other.getChordLabel()

    def __ne__(self, other):
        return not self.__eq__(other)

    #def __len__(self):
    #    pcset = self.getPitchClassSet(True)
    #    if pcset == None:
    #        return 0
    #    return len(pcset)

    def __str__(self):
        return self.getChordLabel()

    # define managed attributes
    chordtype   = property(getChordType, setChordType)
    rootnote    = property(getRootNote, setRootNote)
    bassnote    = property(getBassNote, setBassNote)
    label       = property(getChordLabel, setChordLabel)
