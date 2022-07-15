""" Class for note names """
import re

from melospy.basic_representations.jm_util import type_check


class NoteName(object):
    """ Class for note names """

    allNoteLetter           = ('A', 'B', 'C', 'D', 'E', 'F', 'G')
    allNoteNamesSharp       = ('C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B')
    allNoteNamesFlat        = ('C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B')
    allNoteLetterPitchClass = ( 9, 11, 0, 2, 4, 5, 7 )
    allNoteAccidentalPitchClassShift    = ( -1, 0, 1)
    allNoteAccidentals                  = ('b', '', '#')
    allNoteNamesLilySharp       = ('c', 'cis', 'd', 'dis', 'e', 'f', 'fis', 'g', 'gis', 'a', 'ais', 'b')
    allNoteNamesLilyFlat        = ('c', 'des', 'd', 'es', 'e', 'f', 'ges', 'g', 'aes', 'a', 'bes', 'b')

    def __init__(self, noteNameLabel, generic=False):
        """ Initialize note name. Constructur must receive a label, no empty constructors allowed"""
        if isinstance(noteNameLabel, str):
            self.setNoteLabel(noteNameLabel, generic)
        elif isinstance(noteNameLabel, (int, float)):
            if generic:
                raise TypeError("MIDI pitch not allowed for generic NoteNames")
            self.__init__(NoteName.fromMIDIPitch(noteNameLabel).getNoteName(), False)
        else:
            raise TypeError("NoteName constructor takes only basetring or integer")

    def setNoteLabel(self, val, generic=False):
        """ Fill a NoteName object via note name string.
            Valid note names are of the form::

                notename ::= <noteletter>[accidental][octave]

            with::

                noteletter ::= ['A'-'G''a'-'g']
                accidental ::= 'b'|'#'
                octave     ::= '-'['0'-'9']

            A NoteName object has three attributes::

                __noteLabel: string
                __noteLetter: string
                __noteAccidental: string
                __octave: int

            *__noteLetter* and *__noteAccidental* can only be set via *setNoteLabel()*.
            *__octave* can be modified independently.

            A generic note name does not have an octave specifier.
        """
        if not isinstance(val, str):
            raise ValueError("Note name must be a string!")

        p = re.compile("(^[A-Ga-g]{1})([b#]?)(-?[0-9]?$)")
        m = p.match(val)
        if not m:
            raise ValueError("Malformed note name: '" + val + "'")


        self.__noteLetter = m.group(1).upper()
        self.__noteAccidental = m.group(2)
        if len(m.group(3)) > 0:
            self.__octave = int(m.group(3))
            self.__octave += 1
            if self.__octave < 0:
                raise ValueError("Octave must not be smaller than -1: " + val)
        else:
            self.__octave   = None

        if generic and self.__octave != None:
            raise ValueError("Generic NoteName must not have octave specifier.")

        return self

    def getPitchClass(self, circle_of_fifths=False):
        """ Get pitch class that corresponds to note name """
        pc = (self.allNoteLetterPitchClass[self.allNoteLetter.index(self.__noteLetter) ] + \
                 self.allNoteAccidentalPitchClassShift[ self.allNoteAccidentals.index(self.__noteAccidental) ] + 12 ) % 12

        if circle_of_fifths:
            pc = (pc * 7) % 12
        return pc

    def getMIDIPitch(self):
        """ Get corresponding pitch class (C4 = 60).
            For the lowest octave getMIDIPItch and getPitchClass
            yield the same values
        """
        val = NoteName.getPitchClass(self)
        if self.__octave != None:
            val += int(self.__octave)*12
        return val

    @staticmethod
    def fromMIDIPitch(val, useSharp=True, generic=False):
        """ Set a Notename by providing a MIDI pitch
            between 0 and 127 (C4 = 60)."""

        if val < 0 or val > 127:
            raise ValueError("MIDIPitch must be a numeric value between 0 and 127, got:{}".format(val))
        #TODO: if we got a float, do something more clever

        val = int(round(val))
        pc = val  % 12
        if useSharp:
            note = NoteName.allNoteNamesSharp[pc]
        else:
            note = NoteName.allNoteNamesFlat[pc]

        if generic:
            ret = NoteName(str(note), generic=True)
        else:
            octave = val // 12 -1
            ret = NoteName(str(note) + str(octave))

        return ret

    @staticmethod
    def fromAccidentals(num_acc, use_sharp=True):
        if use_sharp:
            pc = (num_acc*7) % 12
            note = NoteName.allNoteNamesSharp[pc]
        else:
            pc = (num_acc * 5) % 12
            note = NoteName.allNoteNamesFlat[pc]
        ret = NoteName(str(note), generic=True)
        return ret

    def getNoteName(self):
        """ Get full note name """
        if self.__noteLetter == None:
            return 'N/A'
        if self.__noteAccidental != None:
            basename = self.__noteLetter + str(self.__noteAccidental)

        if self.__octave != None:
            basename += str(self.__octave-1)
        return basename

    def getBaseName(self):
        if self.__noteLetter == None:
            return 'N/A'
        if self.__noteAccidental != None:
            basename = self.__noteLetter + str(self.__noteAccidental)
        return basename

    def getNoteAccidental(self):
        """ Get note accidental """
        return self.__noteAccidental

    def getNoteLetter(self):
        """ Get note name letter """
        return self.__noteLetter

    def setOctave(self, val):
        """Add a octave value to a note name, the American way. Middle c = C4 and so on.
              Octave must be an integer value between -1 and 9
        """
        try:
            #val =  int(val)
            if val == None or val >= -1 and val <= 9:
                self.__octave = val
            else:
                raise ValueError
        except:
            raise ValueError("Expected octave between -1 and 9 or None, got {}".format(val))

        return self

    def getLilypondName(self, flat=None):
        if self.isGeneric():
            name = self.__noteLetter.lower()
            if self.__noteAccidental == "b":
                if name != "e":
                    name += "es"
                else:
                    name = "es"
            if self.__noteAccidental == "#":
                name += "is"
            return name

        pc = self.getPitchClass()
        if flat == None:
            flat = self.onTheFlatSide()
        if flat:
            name = self.allNoteNamesLilyFlat[pc]
        else:
            name = self.allNoteNamesLilySharp[pc]
        octave = 0
        if self.__octave != None:
            octave = self.__octave - 4
        octave_str  = ""
        if octave < 0:
            octave_str = ","*abs(octave)
        elif octave > 0:
            octave_str = "'"*octave

        return name + octave_str

    def isGeneric(self):
        return self.__octave == None

    def onTheFlatSide(self):
        nl = self.getBaseName()
        if nl == "F":
            return True
        if nl.find("b") >= 0:
            return True
        if nl in self.allNoteNamesSharp:
            return False
        return True

    def getOctave(self):
        return self.__octave

    def getEnharmonic(self):
        midi = self.getMIDIPitch()
        useSharp = False
        if self.onTheFlatSide():
            useSharp = True
        nn = NoteName.fromMIDIPitch(midi, useSharp, self.isGeneric())
        #print "Orig: {}, Enharmonic: {}".format(self, nn)
        return nn

    def __str__(self): return self.getNoteName()

    def __eq__(self, other):
        if not isinstance(other, NoteName): return False
        return str(self) == str(other)

    def __ne__(self, other):
        return not self.__eq__(other)

    noteAccidental  = property(getNoteAccidental)
    noteLetter      = property(getNoteLetter)
    octave          = property(getOctave, setOctave)

#class NoteName
