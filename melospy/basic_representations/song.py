""" Class for songs"""

from melospy.basic_representations.esac_info import *
from melospy.basic_representations.melody import *
from melospy.basic_representations.meta_data import *


class Song(Melody):
    """ Class for songs"""

    def __init__(self, melody=None, metadata=None, phrases=None):
        self.setMelody(melody)
        self.setMetadata(metadata)
        self.setPhraseSections(phrases)

    def clone(self):
        """ Provides deep copy """
        mel = Melody.clone(self)
        song = Song(mel, try_clone(self.getMetadata()), try_clone(self.getPhraseSections()))
        return song

    def getMelodyEvents(self):
        return Rhythm.getEvents(self)

    def setMelody(self, melody):
        if isinstance(melody, Melody) or melody == None:
            Melody.__init__(self, melody)
        else:
            raise TypeError("Expected Melody object or 'None'!")

    def _checkSectionIntegrity(self, sect):
        if sect == None:
            #be nice to your user
            return True
        if sect.getStartID() == 0 and sect.getEndID() == (len(self)-1):
            return True
        return False

    def getPhraseSections(self):
        return self.__phrases

    def setPhraseSections(self, val):
        #self.__phrases = None
        #self.__phraseIDs = None
        if val == None or (isinstance(val, SectionList) and val.getType() == 'PHRASE'):
            if self._checkSectionIntegrity(val):
                self.__phrases   = try_clone(val)
                self._setPhraseIDs(self.__phrases)
            else:
                raise ValueError("Phrase list does not match melody events")
        else:
            raise TypeError("Expected 'SectionList<'PHRASES>' object!")
        return self
    def getSection(self, section_type):
        if section_type == "PHRASE":
            return self.getPhraseSections()
        return None
    def getPhraseIDs(self):
        return self.__phraseIDs

    def _setPhraseIDs(self, val):
        if val:
            self.__phraseIDs = val.getValues(eventBased=True)
            if len(self.__phraseIDs) != len(self):
                startID = self.__phrases()[0].getStartID()
                endID   = self.__phrases()[-1].getEndID()
                raise RuntimeError("Expected {} phrase ids, got {}. (Start: {}, end:{})".format(len(self.__melody), len(phraseIDs), startID, endID))
        else:
            self.__phraseIDs = None


    def getMetadata(self):
        return self.__metadata

    def setMetadata(self, val):
        if isinstance(val, MetaData) or isinstance(val, EsacInfo) or val == None:
            self.__metadata = val
        else:
            raise TypeError("Expected MetaData, EsacInfo or None! Got {}".format(type(val)))

    def getPopSongInfo(self):
        return self.__metadata.getPopSongInfo()

    def get_main_id(self):
        main_id = "NA"
        try:
            smd = self.__metadata
        except:
            return main_id
        try:
            main_id = smd.getField("filename")
        except:
            pass
        return main_id

    def __str__(self):
        linesep = "=============================="
        s = "\n".join([str(self.__metadata), linesep, Melody.__str__(self)])
        return s

    metadata   = property(getMetadata, setMetadata)
