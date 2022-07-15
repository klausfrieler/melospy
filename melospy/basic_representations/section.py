""" Class implementation of Section """

from melospy.basic_representations.chord import *
from melospy.basic_representations.form_name import *
from melospy.basic_representations.idea import *
from melospy.basic_representations.key import *


class Section(object):
    """ class Section represents a section in Rhythm, NoteTrack, MeterGrid and mostly a Melody object.
        The Section value is basically a label and of mutable type depending on the type of the section. Section are marked with start and end indices in the corresponding list.
        The element at the end index is included.
    """

    types = {'KEY':Key, 'FORM':FormName, 'PHRASE':int, 'CHORUS':int, 'CHORD':Chord, 'BAR':int, 'IDEA': Idea}

    def __init__(self, sectionType, val, start, end):
        """ Initialize module """
        self.__startID  = 0
        self.__endID    = 0
        self.setEndID(end)
        self.setStartID(start)
        self.setType(sectionType)
        self.setValue(val)

    def clone(self):
        """ Returns a deep copy"""
        return Section(self.getType(), self.getValue(), self.getStartID(), self.getEndID())

    def setStartID(self, val):
        """ Set function for StartID """
        val = int(val)
        if val < 0:
            raise ValueError("IDs must be >=0!")
        if val > self.__endID:
            raise ValueError("startID ({}) must be less or equal than endID ({})!".format(val, self.__endID))
        self.__startID = val
        return self

    def getStartID(self):
        """ Get start ID """
        return self.__startID

    def setEndID(self, val):
        """ Set function for StartID """
        val = int(val)
        if val<0:
            raise ValueError("IDs must be >=0!")
        if val< self.__startID:
            raise ValueError("endID must be greater or equal than startID!")

        self.__endID = val
        return self

    def getEndID(self):
        """ Get end ID """
        return self.__endID

    def eventCount(self):
        return self.__endID - self.startID+1

    def shiftIDs(self, delta):
        """ Shift IDs by delta """
        if delta >= 0:
            self.endID   = self.endID   + delta
            self.startID = self.startID + delta
        else:
            self.startID = self.startID + delta
            self.endID   = self.endID   + delta

        return self

    def is_inside(self, find_id):
        if self.startID <= find_id and self.endID >= find_id:
            return True
        return False

    def snip(self, startID, endID):
        """ Snip by setting start and endIDs"""
        if startID < self.__startID:
            raise ValueError("new startID must be >={}!".format(self.__startID))
        if endID > self.__endID:
            raise ValueError("new endID must be <={}!".format(self.__endID))
        self.__startID = startID
        self.__endID = endID
        return self

    def setType(self, sectionType):
        """ Set type of section"""
        if not isinstance(sectionType, str):
            raise TypeError("Expected one of " + ", ".join(list(self.types.keys())))
        if str(sectionType).upper() in list(self.types.keys()):
            self.__type = sectionType.upper()
        else:
            raise ValueError("Invalid value {} for type.".format(str(sectionType)))
        return self

    def getType(self):
        """ Get type of section"""
        return self.__type


    def setValue(self, val):
        """ Set value of section"""
        if isinstance(val, self.types[self.__type]):
            self.__value = val
        else:
            raise TypeError("{}-Section: Value must be a {} object, got; {}".format(self.__type, self.types[self.__type], type(val)))
        return self

    def getValue(self):
        """ get value of section"""
        return self.__value

    def __eq__(self, other):
        if not isinstance(other, Section): return False
        return (self.__startID == other.__startID and self.__endID == other.__endID and self.__type == other.__type)

    def __ne__(self, other):
        return not self == other

    def __le__(self, other): return self.__startID <= other.__startID
    def __ge__(self, other): return self.__startID >= other.__startID
    def __lt__(self, other): return self.__startID< other.__startID
    def __gt__(self, other): return self.__startID> other.__startID

    def toString(self, sep = "|"):
        if not isinstance(sep, str):
            sep = "|"
        s = sep.join(["type:" + str(self.getType()), "val:" +str(self.getValue()), "s:" + "{}".format(self.getStartID()), "e:"+str(self.getEndID())])
        s = sep.join([str(self.getType()), str(self.getValue()), "%04d" % (self.getStartID()), "%04d" % (self.getEndID())])
        return(s)

    def __str__(self):  return self.toString()
    def __len__(self):  return self.__endID-self.__startID+1
    #def __repr__(self): return self.toString()

    startID     = property(getStartID, setStartID)
    endID       = property(getEndID, setEndID)
    type        = property(getType, setType)
    value       = property(getValue, setValue)
