""" Class for Solo Meta Data"""

from melospy.basic_representations.composition_info import *
from melospy.basic_representations.jm_util import get_NA_str
from melospy.basic_representations.meta_data import *
from melospy.basic_representations.record_info import *
from melospy.basic_representations.solo_info import *
from melospy.basic_representations.transcription_info import *


class SoloMetaData(MetaData):
    """ Class for solo meta data"""

    def __init__(self, soloInfo=None, recordInfo=None, transcriptionInfo=None, compositionInfo=None):
        self.setSoloInfo(soloInfo)
        self.setRecordInfo(recordInfo)
        self.setTranscriptionInfo(transcriptionInfo)
        self.setCompositionInfo(compositionInfo)

    def clone(self):
        return SoloMetaData(self.getSoloInfo().clone(), self.getRecordInfo().clone(), self.getTranscriptionInfo().clone(), self.getCompositionInfo().clone())

    def getInfoTypes(self):
        return ["SoloInfo", "RecordInfo", "TranscriptionInfo", "CompositionInfo"]

    def getSoloInfo(self):
        return self.__si

    def setSoloInfo(self, si):
        if si == None or isinstance(si, SoloInfo):
            self.__si = si
        else:
            raise TypeError("Expected SoloInfo object or None.")
        return self

    def getCompositionInfo(self):
        return self.__ci

    def setCompositionInfo(self, ci):
        if ci == None or isinstance(ci, CompositionInfo ):
            self.__ci = ci
        else:
            raise TypeError("Expected CompositionInfo object or None.")
        return self

    def getTranscriptionInfo(self):
        return self.__ti

    def setTranscriptionInfo(self, ti):
        if ti == None or isinstance(ti, TranscriptionInfo ):
            self.__ti = ti
        else:
            raise TypeError("Expected TranscriptionInfo object or None. Got {}".format(type(ti)))
        return self

    def getRecordInfo(self):
        return self.__ri

    def setRecordInfo(self, ri):
        if ri == None or isinstance(ri, RecordInfo):
            self.__ri = ri
        else:
            raise TypeError("Expected RecordInfo objector or None.")
        return self

    def identifier(self):
        return self.getField("filenamesv").rsplit('.', 1)[0].replace("_FINAL", '')

    def __eq__(self, other):
        if isinstance(other, type(None)):
            return False
        for v in self.__dict__:
            if self.__dict__[v] != other.__dict__[v]:
                return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    def __getitem__(self, i):
        return self.getField(i)

    def __str__(self):
        sep = "\n================================="
        return "\n".join([
          "\n" + sep, get_NA_str(self.__si),\
          "\n" + sep, get_NA_str(self.__ri),\
          "\n" + sep, get_NA_str(self.__ti),\
          "\n" + sep, get_NA_str(self.__ci)])

    soloinfo              = property(getSoloInfo, setSoloInfo)
    compinfo              = property(getCompositionInfo, setCompositionInfo)
    transinfo             = property(getTranscriptionInfo, setTranscriptionInfo)
    recordinfo            = property(getRecordInfo, setRecordInfo)
