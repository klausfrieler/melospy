""" Class PopSongInfo"""

from melospy.basic_representations.jm_util import get_NA_str, get_YesNo_str
from melospy.basic_representations.key import *
from melospy.basic_representations.signature import *

#styles = ["TRADITIONAL", "SWING",  "BEBOP", "COOL", "HARDBOP", "POSTBOP", "FREE", "FUSION", "OTHER", "MIX", ""]
#rhythm_feels= ["TWOBEAT", "SWING", "BALLAD", "LATIN", "FUNK", ""]
tempo_classes = ["SLOW", "MEDIUM SLOW", "MEDIUM", "MEDIUM UP", "UP", ""]

class PopSongInfo(object):
    """ Class for pop song info"""

    def __init__(self, artist="", title="", avgTempoBPM=-1, tempo_class="", mainSignature="", key="", filename="", chord_changes="", year="", country="", style=""):
        self.setArtist(artist)
        self.setTitle(title)
        if len(tempo_class) == 0:
            withTempoClass = True
        else:
            withTempoClass = False
        self.setAvgTempoBPM(avgTempoBPM, withTempoClass)
        if avgTempoBPM == -1. and not withTempoClass:
            self.setTempoClass(tempo_class)
        self.__tempoclass = ""
        self.setStyle(style)
        #self.setRhythmFeel(rhythm_feel)
        self.setSignature(mainSignature)
        #self.setMeterChanges(hasMeterChanges)
        self.setKey(key)
        self.setFilename(filename)
        self.setChordChanges(chord_changes)
        self.setYear(year)
        self.setCountry(country)
        #self.setChorusCount(chorus_count)
    def clone(self):
        ret = PopSongInfo()
        ret.__dict__ = {k:self.__dict__[k] for k in self.__dict__}
        return ret

    def getStyle(self):
        return self.__style

    def setStyle(self, style):
        self.__style = style
        return self

    def getArtist(self):
        return self.__artist

    def setArtist(self, artist):
        self.__artist= artist
        return self

    def getYear(self):
        return self.__year

    def setYear(self, year):
        self.__year = year
        return self

    def getCountry(self):
        return self.__country

    def setCountry(self, country):
        self.__country = country
        return self

    def getArtist(self):
        return self.__artist

    def setArtist(self, artist):
        self.__artist= artist
        return self

    def getTitle(self):
        return self.__title

    def setTitle(self, title):
        self.__title = title
        return self

    def getAvgTempoBPM(self):
        return self.__avgtempo

    def setAvgTempoBPM(self, avgTempo, withTempoClass=False):
        if avgTempo != None:
            self.__avgtempo = float(avgTempo)
            if withTempoClass and avgTempo > 0 :
                #print "avgtempo {} TC: {}".format(avgTempo, self.classify_tempo(avgTempo))
                self.setTempoClass(self.classify_tempo(avgTempo))
        else:
            self.__avgtempo  = None
        return self

    def getStyle(self):
        return self.__style

    def setStyle(self, val):
        val = val.upper()
        val = val.replace("-", "")
        #if val not in styles:
        #    raise ValueError("Unknown style: {}".format(val))
        self.__style = val
        return self

    def getFilename(self):
        return self.__filename

    def setFilename(self, filename):
        self.__filename = filename
        return self

    def getRhythmFeel(self):
        return self.__feel

    def setRhythmFeel(self, val):
        self.__feel = val
        return self

    def getTempoClass(self):
        return self.__tempoclass

    def setTempoClass(self, val):
        val = val.upper()
        val = val.replace("-", " ")
        if val not in tempo_classes:
            if val.upper() == "BALLAD":
                val = "SLOW"
            else:
                raise ValueError("Unknown tempo class: {}".format(val))
        self.__tempoclass = val
        return self

    def classify_tempo(self, tempo_bpm):
        if tempo_bpm < 80:
            return "SLOW"
        if tempo_bpm < 110:
            return "MEDIUM SLOW"
        if tempo_bpm < 140:
            return "MEDIUM"
        if tempo_bpm < 180:
            return "MEDIUM UP"
        return "UP"

    def getSignature(self):
        return self.__signature

    def setSignature(self, sig):
        if isinstance(sig, Signature) or sig == None or sig=="":
            self.__signature = sig
        elif isinstance(sig, str):
            self.__signature = Signature.fromString(sig)
        else:
            raise TypeError("Expected Signature object or string or None. Got {}".format(type(sig)))
        return self


    def getKey(self):
        return self.__key

    def setKey(self, key):
        if isinstance(key, Key) or key == None or key=="":
            self.__key = key
        elif isinstance(key, str):
            if key == "":
                self.__key = ""
            else:
                try:
                    self.__key = Key.fromString(key)
                except:
                    raise ValueError("Expected Key object or key string. Got: '{}' (type: {})".format(key, type(key)))
        else:
            raise TypeError("Expected Key object or key string. Got: {}".format(type(key)))
        return self

    def getChordChanges(self):
        return self.__chordchanges

    def setChordChanges(self, val):
        self.__chordchanges = val
        return self

    def __eq__(self, other):
        if isinstance(other, type(None)):
            return False
        for v in self.__dict__:
            if self.__dict__[v] != other.__dict__[v]:
                return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        ret = "\n".join([
          "PopSong Info",
          "="*40,
          "Artist:          " + get_NA_str(self.__artist),
          "Title:           " + get_NA_str(self.__title),
          "Avg. Tempo:      " + get_NA_str(round(self.__avgtempo,1)),
          "Tempo Class:     " + get_NA_str(self.__tempoclass.lower().capitalize()),
          "Style:           " + get_NA_str(self.__style.lower().capitalize()),
          #"Feel:            " + get_NA_str(self.__feel.lower().capitalize()),
          "Key:             " + get_NA_str(self.__key),
          "Chord Changes:   " + get_NA_str(self.__chordchanges),
          "Signature:       " + get_NA_str(self.__signature),
          "Filename:        " + get_NA_str(self.__filename),
          "Year:            " + get_NA_str(self.__year),
          "Country:         " + get_NA_str(self.__country)
          ])
        return str(ret.encode("utf-8"))
    
    artist              = property(getArtist, setArtist)
    title               = property(getTitle, setTitle)
    avgtempo            = property(getAvgTempoBPM, setAvgTempoBPM)
    style               = property(getStyle, setStyle)
    #rhythmfeel          = property(getRhythmFeel, setRhythmFeel)
    tempoclass          = property(getTempoClass, setTempoClass)
    signature           = property(getSignature, setSignature)
    key                 = property(getKey, setKey)
    filename            = property(getFilename, setFilename)
    chordchanges        = property(getChordChanges, setChordChanges)
    year                 = property(getYear, setYear)
    country             = property(getCountry, setCountry)
