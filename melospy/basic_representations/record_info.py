""" Class for record info"""

import re

from melospy.basic_representations.jm_util import get_NA_str
from melospy.basic_representations.sloppy_date import *


class RecordInfo(object):
    """ Class for record info, part of solo meta data"""

    def __init__(self, artist="", recordTitle="",
                 label="", recordBib="", trackNumber="",
                 lineup="", releaseDate="", recordingDate="",
                 musicBrainzID=""):
        self.__recordingyear = ""
        self.setArtist(artist)
        self.setRecordTitle(recordTitle)
        self.setLabel(label)
        self.setRecordBib(recordBib)
        self.setTrackNumber(trackNumber)
        self.setLineUp(lineup)
        self.setReleaseDate(releaseDate)
        self.setRecordingDate(recordingDate)
        #self.setRecordingYear(recordingDate)
        self.setMusicBrainzID(musicBrainzID)

    def clone(self):
        ret = RecordInfo()
        ret.__dict__ = {k:self.__dict__[k] for k in self.__dict__}
        return ret

    def getArtist(self):
        return self.__artist

    def setArtist(self, artist):
        self.__artist = artist
        return self

    def getRecordTitle(self):
        return self.__recordtitle

    def setRecordTitle(self, recordTitle):
        self.__recordtitle = recordTitle
        return self

    def getLabel(self):
        return self.__label

    def setLabel(self, label):
        self.__label = label
        return self

    def getRecordBib(self):
        return self.__recordbib

    def setRecordBib(self, recordBib):
        self.__recordbib = str(recordBib)
        return self

    def getTrackNumber(self):
        return self.__tracknumber

    def setTrackNumber(self, val):
        self.__tracknumber = val
        return self

    def getLineUp(self):
        return self.__lineup

    def setLineUp(self, lineup):
        self.__lineup = lineup
        return self

    def parseLineup(self, lineup=None, player_based=True):
        if lineup == None:
            lineup = self.__lineup
        lineup = lineup.split("+")[0]
        players = lineup.split(";")
        ret = {}
        for p in players:
            m = re.match(r"(.*)\((.*)\)", p)
            player = m.group(1).lstrip().rstrip()
            instruments = m.group(2).split(",")
            instruments = [_.lstrip().rstrip() for _ in instruments]
            if player_based:
                ret[player] = instruments
            else:
                for i in instruments:
                    if i in ret:
                        ret[i].append(player)
                    else:
                        ret[i] = [player]
        return ret

    def getReleaseDate(self):
        return self.__releasedate

    def setReleaseDate(self, val):
        if val == "?":
            self.__releasedate
        else:
            self.__releasedate = SloppyDate.fromString(val)
        return self

    def getRecordingDate(self):
        return self.__recordingdate

    def getRecordingYear(self):
        return self.__recordingyear

    def setRecordingYear(self, val):
        m = re.match(".*((19|20){1}[0-9]{2}).*", val)
        if m != None:
            self.__recordingyear = m.group(1)
        else:
            self.__recordingyear = val
        #self.__recordingdate = SloppyDate.fromString(val)
        return self

    def setRecordingDate(self, val):
        self.__recordingdate = val
        self.setRecordingYear(val)
        #self.__recordingdate = SloppyDate.fromString(val)
        return self

    def getMusicBrainzID(self):
        return self.__musicbrainzid

    def setMusicBrainzID(self, mbid):
        self.__musicbrainzid = mbid
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
          "Record Info",
          "="*40,
          "Artist:          " + get_NA_str(self.__artist),
          "Record title:    " + get_NA_str(self.__recordtitle),
          "Label:           " + get_NA_str(self.__label),
          "RecordBIB:       " + get_NA_str(self.__recordbib),
          "Track No:        " + get_NA_str(self.__tracknumber),
          "Line up:         " + get_NA_str(self.__lineup),
          "Released:        " + get_NA_str(self.__releasedate),
          "Recorded:        " + get_NA_str(self.__recordingdate),
          "MusicBrainzID:   " + get_NA_str(self.__musicbrainzid)])

    artist              = property(getArtist, setArtist)
    recordtitle         = property(getRecordTitle, setRecordTitle)
    label               = property(getLabel, setLabel)
    recordbib           = property(getRecordBib, setRecordBib)
    tracknumber         = property(getTrackNumber, setTrackNumber)
    lineup              = property(getLineUp, setLineUp)
    releasedate         = property(getReleaseDate, setReleaseDate)
    recordingdate       = property(getRecordingDate, setRecordingDate)
    recordingyear       = property(getRecordingYear, setRecordingYear)
    musicbrainzid       = property(getMusicBrainzID, setMusicBrainzID)
