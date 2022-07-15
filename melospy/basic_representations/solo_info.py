""" Class for songs"""

from melospy.basic_representations.jm_util import get_NA_str, get_YesNo_str
from melospy.basic_representations.key import *
from melospy.basic_representations.signature import *

std_instruments = {"ts":"Tenor saxophone", 
                   "ts-c":"C-melody Saxophone", 
                   "as": "Alto saxophone", 
                   "bs": "Baritone Saxophone", 
                   "bsx": "Bass saxophone", 
                   "cbsx": "Bass saxophone", 
                   "ss": "Sopran saxophone", 
                   "sss": "Sopranino saxophone", 
                   "cl": "Clarinet", 
                   "bcl": "Bass clarinet", 
                   "acl": "Alto clarinet", 
                   "tp": "Trumpet", 
                   "tpt": "Trumpet", 
                   "flgn": "Flugelhorn", 
                   "tb": "Trombone", 
                   "fl": "Flute", 
                   "cor": "Cornet", 
                   "ptp": "Pocket trumpet", 
                   "frhn": "French horn", 
                   "ob": "oboe", 
                   "voc": "Vocals", 
                   "vib": "Vibraphone", 
                   "g":"Guitar", 
                   "b":"double bass",
                   "corn": "Cornet", 
                   "p": "piano"}
styles = ["TRADITIONAL", "SWING",  "BEBOP", "COOL", "HARDBOP", "POSTBOP", "FREE", "FUSION", "OTHER", "MIX", ""]
rhythm_feels= ["TWOBEAT", "SWING", "BALLAD", "LATIN", "FUNK", ""]
tempo_classes = ["SLOW", "MEDIUM SLOW", "MEDIUM", "MEDIUM UP", "UP", ""]

class SoloInfo(object):
    """ Class for solo info, part of solo meta data"""

    def __init__(self, melid=None, performer="", title="", title_addon="", solo_part=1, instrument="", averageTempoBPM=-1, tempo_class="", style="", rhythm_feel="", mainSignature="", hasMeterChanges="No", key="", chord_changes="", chorus_count=0):
        self.setMelid(melid)
        self.setPerformer(performer)
        self.setTitle(title)
        self.setTitleAddOn(title_addon)
        self.setSoloPart(solo_part)
        self.setFullTitle(title, solo_part, title_addon)
        self.setInstrument(instrument)
        self.setAvgTempoBPM(averageTempoBPM)
        self.setTempoClass(tempo_class)
        self.setStyle(style)
        self.setRhythmFeel(rhythm_feel)
        self.setSignature(mainSignature)
        self.setMeterChanges(hasMeterChanges)
        self.setKey(key)
        self.setChordChanges(chord_changes)
        self.setChorusCount(chorus_count)
        self.basefilename = None

    def clone(self):
        ret = SoloInfo()
        ret.__dict__ = {k:self.__dict__[k] for k in self.__dict__}
        return ret

    def getMelid(self):
        return self.__melid

    def setMelid(self, melid):
        self.__melid = melid
        return self

    def getPerformer(self):
        return self.__performer

    def setPerformer(self, performer):
        self.__performer = performer
        return self

    def getTitle(self):
        return self.__title

    def setTitle(self, title):
        self.__title = title
        return self

    def getTitleAddOn(self):
        return self.__titleaddon

    def setTitleAddOn(self, addon):
        self.__titleaddon = addon
        return self

    def getSoloPart(self):
        return self.__solopart

    def setSoloPart(self, solo_part):
        self.__solopart = solo_part
        return self
    def getFullTitle(self):
        return self.__fulltitle

    def setFullTitle(self, title, solo_part, title_addon):
        #print "setFullTitle called", title, solo_part, title_addon
        self.__fulltitle = ""
        if len(str(solo_part)) == 0:
            self.__fulltitle = title
        else:
            self.__fulltitle = "{}-{}".format(title, solo_part)
        if len(title_addon) > 0:
            self.__fulltitle  = "{}_{}".format(self.__fulltitle,  title_addon)
        #print "Set full title", self.__fulltitle
        return self

    def getInstrument(self):
        return self.__instrument

    def setInstrument(self, instrument):

        if len(instrument)>0 and instrument not in list(std_instruments.keys()) and instrument not in list(std_instruments.values()):
            raise ValueError("Unknown instrument: {}".format(instrument))

        self.__instrument = instrument
        return self

    def getAvgTempoBPM(self):
        return self.__avgtempo

    def setAvgTempoBPM(self, avgtempo, withTempoClass=False):
        if avgtempo != None:
            self.__avgtempo = float(avgtempo)
            if withTempoClass:
                self.setTempoClass(self.classify_tempo(avgtempo))
        else:
            self.__avgtempo  = None
        return self

    def getStyle(self):
        return self.__style

    def setStyle(self, val):
        val = val.upper()
        val = val.replace("-", "")
        if val not in styles:
            raise ValueError("Unknown style: {}".format(val))
        self.__style = val
        return self

    def getRhythmFeel(self):
        return self.__rhythmfeel

    def setRhythmFeel(self, val):
        val = val.upper()
        val = val.replace("-", "")
        val = val.replace(";", "/")

        feels = val.split("/")
        for f in feels:
            feel = f.split(":")
            if len(feel)>1:
                feel = feel[1]
            else:
                feel = feel[0]
            if feel not in rhythm_feels:
                raise ValueError("Unknown feel: {}".format(feel))

        self.__rhythmfeel = val
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

    def hasMeterChanges(self):
        return self.__meterchanges

    def setMeterChanges(self, val):
        self.__meterchanges = val
        return self

        return self.__meterchanges

    def getChordChanges(self):
        return self.__chordchanges

    def setChordChanges(self, val):
        self.__chordchanges = val
        return self

    def getChorusCount(self):
        return self.__choruscount

    def setChorusCount(self, val):
        self.__choruscount= val
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
        return "\n".join([
          "Solo Info",
          "="*40,
          "Melid:           " + get_NA_str(self.__melid),
          "Performer:       " + get_NA_str(self.__performer),
          "Title:           " + get_NA_str(self.__title),
          "Title AddOn:     " + get_NA_str(self.__titleaddon),
          "Solo Part:       " + get_NA_str(self.__solopart),
          "Instrument:      " + get_NA_str(self.__instrument),
          "Avg. Tempo:      " + get_NA_str(self.__avgtempo),
          "Tempo Class:     " + get_NA_str(self.__tempoclass.lower().capitalize()),
          "Style:           " + get_NA_str(self.__style.lower().capitalize()),
          "Feel:            " + get_NA_str(self.__rhythmfeel.lower().capitalize()),
          "Key:             " + get_NA_str(self.__key),
          "Signature:       " + get_NA_str(self.__signature),
          "Meter Changes:   " + get_YesNo_str(self.__meterchanges),
          "No. Choruses:    " + get_NA_str(self.__choruscount),
          "Chord Changes: \n" + get_NA_str(self.__chordchanges)
          ])

    melid               = property(getMelid, setMelid)
    performer           = property(getPerformer, setPerformer)
    title               = property(getTitle, setTitle)
    titleaddon          = property(getTitleAddOn, setTitleAddOn)
    solopart            = property(getSoloPart, setSoloPart)
    instrument          = property(getInstrument, setInstrument)
    avgtempo            = property(getAvgTempoBPM, setAvgTempoBPM)
    style               = property(getStyle, setStyle)
    rhythmfeel          = property(getRhythmFeel, setRhythmFeel)
    tempoclass          = property(getTempoClass, setTempoClass)
    signature           = property(getSignature, setSignature)
    meterchanges        = property(hasMeterChanges, setMeterChanges)
    key                 = property(getKey, setKey)
    chordchanges        = property(getChordChanges, setChordChanges)
    choruscount         = property(getChorusCount, setChorusCount)
    fulltitle           = property(getFullTitle, setFullTitle)
