""" Class for Transcription Info"""
from melospy.basic_representations.jm_util import get_NA_str
from melospy.basic_representations.sloppy_date import *

#from enum import *

SOURCE_TYPES          = ("SCAN", "ESAC", "PLAY", "S2S")
TRANSCRIPTION_STATUS  = {"PREFINAL", "FINAL", "DRAFT", "ASSIGNED", "CUT"}

class TranscriptionInfo(object):
    """ Class for transcription info, part of solo meta data"""

    def __init__(self, source="", sourceType="", transcriber="", coder="", dateOfCoding="", status="", fileNameTrack="", fileNameSolo="", fileNameSV="", soloStartSec=-1, soloEndSec=-1, soloTime =""):
        self.setSource(source)
        self.setSourceType(sourceType)
        self.setTranscriber(transcriber)
        self.setCoder(coder)
        self.setStatus(status)
        self.setFileNameSV(fileNameSV)
        self.setFileNameTrack(fileNameTrack)
        self.setDateOfCoding(dateOfCoding)
        self.setFileNameSolo(fileNameSolo)
        self.setSoloStartSec(soloStartSec)
        self.setSoloEndSec(soloEndSec)
        self.setSoloTime(soloTime)

    def clone(self):
        ret = TranscriptionInfo()
        ret.__dict__ = {k:self.__dict__[k] for k in self.__dict__}
        return ret

    def getSource(self):
        return self.__source

    def setSource(self, source):
        self.__source = source
        return self

    def getSourceType(self):
        return self.__sourcetype

    def setSourceType(self, sourceType):
        #if sourceType and not sourceType in SOURCE_TYPES:
        #    raise ValueError("Source type must be one of  {}".format(",".join(SOURCE_TYPES)))
        #else:
        self.__sourcetype = sourceType
        return self

    def getTranscriber(self):
        return self.__transcriber

    def setTranscriber(self, transcriber):
        self.__transcriber = transcriber
        return self

    def getCoder(self):
        return self.__coder

    def setCoder(self, coder):
        self.__coder = str(coder)
        return self

    def getStatus(self):
        return self.__status

    def setStatus(self, val):
        if val and not val in TRANSCRIPTION_STATUS:
            types = ",".join(TRANSCRIPTION_STATUS)
            raise ValueError("Status must be one of {}. Found: {}".format(types, val))
        else:
            self.__status = val
        return self

    def getFileNameSV(self):
        return self.__filenamesv

    def setFileNameSV(self, filename):
        self.__filenamesv = filename
        return self

    def getFileNameTrack(self):
        return self.__filenametrack

    def setFileNameTrack(self, filename):
        self.__filenametrack = filename
        return self

    def getFileNameSolo(self):
        return self.__filenamesolo

    def setFileNameSolo(self, filename):
        self.__filenamesolo= filename
        return self

    def getDateOfCoding(self):
        return self.__dateofcoding

    def setDateOfCoding(self, val):
        self.__dateofcoding = SloppyDate.fromString(val)
        return self

    def getSoloStartSec(self):
        return self.__solostart

    def setSoloStartSec(self, val):
        self.__solostart = val
        return self

    def getSoloEndSec(self):
        return self.__soloend

    def setSoloEndSec(self, val):
        self.__soloend = val
        return self

    def getSoloTime(self):
        return self.__solotime

    def setSoloTime(self, val):
        self.__solotime= val
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
          "Transcription Info",
          "="*40,
          "Source:          " + get_NA_str(self.__source),
          "Source Type:     " + get_NA_str(self.__sourcetype),
          "Transcriber:     " + get_NA_str(self.__transcriber),
          "Coder:           " + get_NA_str(self.__coder),
          "Status:          " + get_NA_str(self.__status),
          "SV File :        " + get_NA_str(self.__filenamesv),
          "File Track:      " + get_NA_str(self.__filenametrack),
          "File Solo:       " + get_NA_str(self.__filenamesolo),
          "Date of Coding:  " + get_NA_str(self.__dateofcoding),
          "Solo Time:       " + get_NA_str(self.__solotime),
          "Solo Start (s):  " + get_NA_str(self.__solostart),
          "Solo End (s):    " + get_NA_str(self.__soloend)])

    source              = property(getSource, setSource)
    sourcetype          = property(getSourceType, setSourceType)
    transcriber         = property(getTranscriber, setTranscriber)
    coder               = property(getCoder, setCoder)
    status              = property(getStatus, setStatus)
    dateofcoding        = property(getDateOfCoding, setDateOfCoding)
    filenametrack       = property(getFileNameTrack, setFileNameTrack)
    filenamesolo        = property(getFileNameSolo, setFileNameSolo)
    filenamesv          = property(getFileNameSV, setFileNameSV)
    solostart           = property(getSoloStartSec, setSoloStartSec)
    soloend             = property(getSoloEndSec, setSoloEndSec)
    solotime            = property(getSoloTime, setSoloTime)
