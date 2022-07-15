""" Class for Form"""

import re

from melospy.basic_representations.chord_sequence import *
from melospy.basic_representations.jm_util import get_NA_str


class FormName(object):
    """Simple class for FormNames. Formnames are of Typ <letter>[']*<posint>"""

    def __init__(self, formName):
       self.setLabel(formName)

    def clone(self):
        label = self.__label if not self._wildcard else "*" + self.__label
        return FormName(label)

    def getLetter(self):
        return self.__letter

    def getModifier(self):
        return self.__modifier

    def getNumber(self):
        return self.__number

    def getLabel(self):
        return self.__label

    def hasWildcard(self):
        return self._wildcard

    def setLabel(self, label):
        if not isinstance(label, str):
            raise TypeError("Expected  string")

        self._wildcard = False
        if label == "I":
            self.__label = label
            self.__letter = "I"
            self.__modifier = None
            self.__number = 1
            return self
        if label[0] == "*":
            self._wildcard = True
            label = label[1:]
        p = re.compile("(^[A-I]{1})([']*)([1-9]{1}[0-9]*$)")
        m = p.match(label)
        if not m:
            raise ValueError("Form label syntax error: '" + label + "'")

        self.__label = label
        self.__letter = m.group(1)

        if len(m.group(2)) > 0:
            self.__modifier = m.group(2)
        else:
            self.__modifier = ""

        self.__number = int(m.group(3))

        return self

    def getModifierCount(self):
        return len(self.__modifier)

    def full_label(self):
        return "*"*self._wildcard + self.__label

    def __str__(self):
        return self.__label

    def __eq__(self, other):
        if not isinstance(other, FormName): return False
        return self.__label  == other.__label and self._wildcard == other._wildcard

    def __ne__(self, other):
        return not self.__eq__(other)

    def __gt__(self, other):
        if ord(self.__letter)>ord(other.__letter):
            return True
        if ord(self.__letter)<ord(other.__letter):
            return False
        if self.getModifierCount()>other.getModifierCount():
            return True
        if self.getModifierCount()<other.getModifierCount():
            return False
        if self.__number>other.__number:
            return True
        return False

    def __ge__(self, other):
        if self == other or self>other:
            return True
        return False

    def __lt__(self, other):
        return other > self

    def __le__(self, other):
        return self == other or other > self

    letter    = property(getLetter)
    modifier  = property(getModifier)
    number    = property(getNumber)
    label     = property(getLabel, setLabel)


class FormPart(FormName):

    def __init__(self, formName, length, chords=None):
        FormName.__init__(self, formName)
        self.setLength(length)
        self.setChords(chords)

    def clone(self):
        label = self.getLabel() if not self._wildcard else "*" + self.getLabel()
        return FormPart(label, self.getLength(), self.chords)

    def setLength(self, val):
        if not isinstance(val, int):
            raise TypeError("Expected integer")
        if val<1:
            raise ValueError("Length must be positive")
        self.__length = val
        return self

    def getLength(self):
        return self.__length

    def getChords(self):
        return self.__chords

    def setChords(self, chord_sequence):
        if chord_sequence == None:
            self.__chords = chord_sequence
            return
        if isinstance(chord_sequence, list):
            chord_sequence = ChordSequence(chord_sequence)
        if not isinstance(chord_sequence, ChordSequence) :
            raise ValueError("Expected ChordSequence or list of chords, got {}".format(type(chord_sequence)))
        seq_len = chord_sequence.length_in_bars()
        if self.__length != seq_len:
            raise ValueError("Expect chord sequence of length {}, got {}".format(self.__length, seq_len))
        self.__chords = chord_sequence

    def __eq__(self, other):
        if not isinstance(other, FormPart): return False
        return FormName.__eq__(self,  other) and self.__length == other.__length

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return "("+ self.getLabel() + "," + str(self.getLength()) + ")"

    length  = property(getLength, setLength)
    chords = property(getChords, setChords)

class FormDefinition(object):

    """ Essentially a list of FormName/FormPart objects with some consistency checking"""

    def __init__(self, form = None):
        self.__form = []

        if form == None:
            return

        if not isinstance(form, list):
            raise TypeError("Expected list of FormNames, FormParts or tuples")

        for f in form:
            if isinstance(f, FormName):
                self.append(f)
            elif isinstance(f, tuple) and len(f) == 2:
                self.append(FormPart(f[0], f[1]))
            else:
                raise TypeError("Expected list of FormNames, FormParts or Tuples")

    @staticmethod
    def parseFormPart(part):
        #Old Python 2.7.5. version
        #try:
        #    l = re.compile("([A-I]{1})([']*){1}([1-9]?[0-9]*)?")
        #    n = l.match(part)
        #    label       = n.group(1)
        #    modifier    = n.group(2)
        #    bars        = n.group(3)
        #    return label, modifier, bars
        #except Exception, e:
        #    pass

        #New Python 2.7.3. compatible version, necessary due to bug in regexp
        try:
            l = re.compile("([A-I']*){1}")
            n = l.match(part)
            label    = n.group(1)[0]
            modifier = n.group(1)[1:]
            bars = part[len(n.group(1)):]
            return label, modifier, bars
        except Exception as e:
            pass
        return "", "", ""

    @staticmethod
    def fromString(formdef):
        counters = {}
        parts = []
        p = re.compile("([A-I]{1}[']*[1-9]*[0-9]*)?")
        m = p.match(formdef)
        org = formdef
        while m and len(formdef)>0:
            m = p.match(formdef)
            part = m.group(0)
            formdef = formdef[len(m.group(0)):]
            #print "Found: ", m.group(0)
            #print "Rest: ", formdef
            label, modifier, bars = FormDefinition.parseFormPart(part)
            if len(bars) == 0:
                bars = "8"
            if label in counters:
                counters[label] += 1
            else:
                counters[label] = 1
            fp = FormPart(label + modifier + str(counters[label]), int(bars))
            #print "token: ", str(fp)
            parts.append(fp)
        fd = FormDefinition(parts)
        #print "Got: {}, parsed:{} ".format(org, fd)
        return fd

    def append(self, fn):
        if isinstance(fn, str):
            fn = FormName(fn)

        if not isinstance(fn, (FormName, FormPart)):
            raise TypeError("Expected FormName or FormPart")

        if self.isEmpty():
            if fn.getLabel() != "A1" and fn.getLetter() != "I" and not fn.hasWildcard():
                raise ValueError("First form part must be 'A1' or 'I1' or start with wildcard '*'")
            else:
                self.__form.append(fn)
                return self

        #print "="*40
        #print "FORM:", ",".join([str(k) for k in self.__form])
        #print "ADD: ", fn
        last_of_same = self.last(letter = fn.getLetter())
        last = self.last()
        #print "Last: ", last
        #print "Last of samei: ", last_of_same
        if fn != None and last_of_same != None and not isinstance(last_of_same, type(fn)):
            raise TypeError("FormNames and FormParts cannot be mixed in FormDefinition")

        #if current or previous FormPart has wildcard, it can be inserted
        #except if last FormPart had a wildcard but current has the same letter
        if  (last and last.hasWildcard() and fn.getLetter() != last.getLetter())\
             or fn.hasWildcard():
            self.__form.append(fn)
            return self

        if last_of_same == None:
            #letter not found
            #special case 'I': can be inserted anywhere (however numbering and modifier rules apply as well
            if fn.getLetter() == "I" or fn.hasWildcard():
                self.__form.append(fn)
                return self

            max = self.maxLetter()
            if max == '-':
                #quasi empy
                self.__form.append(fn)
            elif fn.getNumber() == 1 and ord(fn.getLetter()) == ord(max)+1 and fn.getModifierCount() == 0:
                self.__form.append(fn)
            else:
                raise ValueError("Form part letters must be consecutively named. Offender: " + str(fn))
        else:
            if fn.getNumber() == last_of_same.getNumber()+1 and (fn.getModifierCount()-last_of_same.getModifierCount())<=1:
                self.__form.append(fn)
            else:
                raise ValueError("Form part numbers and modifiers must be consecutively named. Offender: {}, last: {} ".format(str(fn), str(last_of_same)))
        return self

    def isEmpty(self):
        return len(self.__form) == 0

    def last(self, letter = None):
        """Retrieves the last form element in the list with the given 'letter',
           if 'letter' is not None, otherwise just the last element.
           Returns "None" if list is empty or no element with the given letter is found.
        """
        #if not isinstance(letter, basestring):
        #    raise TypeError("Expected letter as string")
        if self.isEmpty(): return None
        if letter == None:
            return self.__form[-1]
        for f in reversed(self.__form):
            if f.getLetter() == letter[0]:
                return f
        return None

    def maxLetter(self, ignoreExtra = True):
        """ Find the 'largest' letter in the form list"""
        if self.isEmpty():
            return None
        #an 'A' must be in the list, if it's not empty
        min = ord('-')
        for f in self.__form:
            if ignoreExtra and f.getLetter() == 'I':
                continue
            if ord(f.getLetter())>min:
                min = ord(f.getLetter())

        return chr(min)

    def getLength(self):
        if self.isEmpty() or not isinstance(self.__form[0], FormPart):
            return 0
        sum = 0
        for f in self.__form:
          sum += f.getLength()
        return sum

    def getShortForm(self, withLengths = False):
        if withLengths:
            short = "".join([e.letter + e.modifier + str(e.getLength()) for e in self.__form])
        else:
            short = "".join([e.letter + e.modifier for e in self.__form])
        return short

    def setList(self, form):
        pass

    def getList(self):
        return self.__form

    def clear(self):
        self.__form = []

    def __getitem__(self, i):
        return self.__form[i]

    def __str__(self):
        base = ", ".join([str(e) for e in self.__form])
        return base

    form  = property(getList, setList)
