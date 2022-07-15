""" Class implementation of TonyCSV reader"""
import csv
import os
import sys

from melospy.basic_representations.beatometer import *
from melospy.basic_representations.jm_stats import mean, mean_frac, sd
from melospy.basic_representations.jm_util import (chomp, dict_from_keys_vals, find_empty,
                                                   remove_empty, type_check)
from melospy.basic_representations.melody import *


class TonyCSVReader(object):
    """Class for reading TonyCSV file"""

    def __init__(self, filename, method="gaussification", min_ioi=None, pitch_unit="Hz", pitch_corr=True, params=None, debug=None):
        self.read(filename, method, min_ioi, pitch_unit, pitch_corr, params, debug)

    def getEventList(self):
        return self.__events

    def getMelody(self):
        return self.__melody

    def read(self, filename, method="gaussification", min_ioi=None, pitch_unit="Hz", pitch_corr=True, params=None, debug=None):
        """
        Read TonyCSV note tracks: 4 columns, no header, Englisch convention, comma separated
        * First column: Onset (sec)
        * Second column: Pitch (Hz)
        * Third column: Duration (sec)
        * *Fourth column: Intensity (AU, unused)
        """
        #print params
        with open(filename, 'r') as csvfile:
            csvreader = csv.reader(csvfile, delimiter=',', lineterminator="\n", quoting=csv.QUOTE_MINIMAL)
            self.__events = []
            header = ["onset", "pitch_hz", "duration", "intensity"]
            for r in csvreader:
                event = dict_from_keys_vals(header, r)
                self.__events.append(event)
            corr = 0.0
            if pitch_corr:
                corr = mean_frac([hz_to_midi(float(e["pitch_hz"])) for e in self.__events])
            nt = NoteTrack()
            for e in self.__events:
                onset = float(e["onset"])
                if pitch_unit == "Hz":
                    pitch = int(round(hz_to_midi(float(e["pitch_hz"]))-corr))
                else:
                    pitch = int(e["pitch_hz"])
                duration = float(e["duration"])
                nt.append(NoteEvent(pitch, onset, duration))

            if min_ioi != None:
                nt = nt.withoutShorties(threshold=min_ioi)

            if debug == None:
                debug = BeatometerDebugParams()
            bm = Beatometer(nt, debug=debug)
            if params != None:
                bm.setParams(params)

            mg = bm.annotate(method=method)
            self.__melody = nt.annotateMeter(mg)

        #self.__melody.compress()
        #print "-------------------------"
        #print self.__melody
        return self.__melody


    events  = property(getEventList)
    melody  = property(getMelody)
