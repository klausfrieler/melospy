""" Class implementation of MCSV writer"""
import csv
import os
import sys

from melospy.basic_representations.jm_util import type_check

FANTASTIC_header_all = ["onset",
                    "onsetics",
                    "takt",
                    "beat",
                    "ticks",
                    "pitch",
                    "durs",
                    "durtic",
                    "dur16",
                    "LBDM1",
                    "LBDM2",
                    "refLBDM1",
                    "refLBDM2",
                    "temperley",
                    "simple0-0-0",
                    "simple0-0-1",
                    "simple0-0-2",
                    "simple0-0-3",
                    "simple0-0-4",
                    "simple0-1-0",
                    "simple0-1-1",
                    "simple0-1-2",
                    "simple0-1-3",
                    "simple0-1-4",
                    "simple0-2-0",
                    "simple0-2-1",
                    "simple0-2-2",
                    "simple0-2-3",
                    "simple0-2-4",
                    "simple0-3-0",
                    "simple0-3-1",
                    "simple0-3-2",
                    "simple0-3-3",
                    "simple0-3-4",
                    "simple0-4-0",
                    "simple0-4-1",
                    "simple0-4-2",
                    "simple0-4-3",
                    "simple0-4-4",
                    "simple1-0-0",
                    "simple1-0-1",
                    "simple1-0-2",
                    "simple1-0-3",
                    "simple1-0-4",
                    "simple1-1-0",
                    "simple1-1-1",
                    "simple1-1-2",
                    "simple1-1-3",
                    "simple1-1-4",
                    "simple1-2-0",
                    "simple1-2-1",
                    "simple1-2-2",
                    "simple1-2-3",
                    "simple1-2-4",
                    "simple1-3-0",
                    "simple1-3-1",
                    "simple1-3-2",
                    "simple1-3-3",
                    "simple1-3-4",
                    "simple1-4-0",
                    "simple1-4-1",
                    "simple1-4-2",
                    "simple1-4-3",
                    "simple1-4-4"]
#actually only the first 15 columns are used by FANTASTIC
FANTASTIC_header = FANTASTIC_header_all[0:15]
class MCSVWriter(object):
    """Class for writing MCSV1 files, SIMILE or FANTASTIC style"""

    def __init__(self, melody, style="simile"):
        self.__preamble = ""
        self.setEventList(melody)
        self.setStyle(style)
        #print "Found style", style

    def setStyle(self, style = "simile"):
        if style not in ["simile", "FANTASTIC"]:
            raise ValueError("Expected MSCV 'simile' or 'FANTASTIC' style, got {}".format(style))
        self.style = style

    def setEventList(self, melody):
        #type_check(events, list)
        events = []
        mel = melody.clone().standardize(force=True)
        phrase_markers = [0] * len(mel)
        try:
            phrase_markers = list(mel.export("phrbd"))
            phrase_markers = phrase_markers[1:] + [1]
        except:
            #if we do not have phrase IDs set
            #one all encompassing phrase
            phrase_markers[len(phrase_markers)-1] = 1
        for i, e in enumerate(mel):
            row ={
                  'onset': e.getOnsetSec(),\
                  'period':e.getPeriod(),\
                  'division':e.getDivision(),\
                  'bar':e.getBar(),\
                  'beat':e.getBeat(),\
                  'tatum': e.getTatum(),\
                  'pitch': e.getPitch(),\
                  'duration':e.getDurationSec(),\
                  'durtatum':e.getDurationTatum(),\
                  'phrase':phrase_markers[i]
                  }
            events.append(row)

        ticks = events[0]['division']
        sig = melody.getEvents()[0].getMetricalContext().getMeterInfo()
        self.__preamble = self.level1Preamble(sig.getNumerator(), sig.getDenominator(), ticks)
        self.__events = events

    def getEventList(self):
        return self.__events

    def write(self, filename):
        if self.style == "simile":
            self.writeSimileStyle(filename)
        elif self.style  == "FANTASTIC":
            self.writeFANTASTICStyle(filename)
        else:
            raise RuntimeError("Something weird happend")

    def makeEntry(self, event, key, decimal=".", NA_string="-1"):
        if key in event:
            val = event[key]
            if isinstance(val, float):
                val = round(val, 4)
            if decimal == ".":
                return val
            else:
                return str(val).replace(".", decimal)
        else:
            return NA_string

    def level1Preamble(self, numerator, nominator, ticks):
        return "Signature: {}/{}, Ticks per Beat: {}\n".format(numerator, nominator, ticks)

    def writeSimileStyle(self, filename):
        if len(self.events) == 0:
            raise RuntimeError("No events to write, buddy")
        with open(filename, 'w') as csvfile:
            csvfile.write(self.__preamble)
            #csvfile.write("onset;onsetics;takt;beat;ticks;pitch;durs;durtic;dur16;phrase;chord;form\n")
            csvfile.write("onset;onsetics;takt;beat;ticks;pitch;durs;durtic;dur16;\n")
        with open(filename, 'a') as csvfile:
            csvwriter = csv.writer(csvfile, delimiter=';', lineterminator="\n", quotechar='|', quoting=csv.QUOTE_MINIMAL)
            for e in self.events:
                row = [
                    self.makeEntry(e, 'onset'),\
                    self.makeEntry(e, 'onsetic'),\
                    self.makeEntry(e, 'bar'),\
                    self.makeEntry(e, 'beat'),\
                    self.makeEntry(e, 'tatum')-1,\
                    int(round(self.makeEntry(e, 'pitch'))),\
                    self.makeEntry(e, 'duration'),\
                    self.makeEntry(e, 'durtic'),\
                    self.makeEntry(e, 'durtatum')
#                    self.makeEntry(e, 'phrase'),\
#                    self.makeEntry(e, 'chord'),\
#                    self.makeEntry(e, 'form')
                 ]
                csvwriter.writerow(row)
        return True

    def writeFANTASTICStyle(self, filename):
        if len(self.events) == 0:
            raise RuntimeError("No events to write, buddy")
        with open(filename, 'w') as csvfile:
            csvfile.write(self.__preamble)
            #csvfile.write("onset;onsetics;takt;beat;ticks;pitch;durs;durtic;dur16;phrase;chord;form\n")
            header = ";".join([_ for _ in FANTASTIC_header])
            csvfile.write(header + "\n")
        with open(filename, 'a') as csvfile:
            csvwriter = csv.writer(csvfile, delimiter=';', lineterminator="\n", quotechar='|', quoting=csv.QUOTE_MINIMAL)
            for e in self.events:
                seg_markers= [0] * (len(FANTASTIC_header)-9)
                #FANTASTIC uses only 'temperley' seg column which is No. 13
                seg_markers[4] = e["phrase"]
                row = [
                    self.makeEntry(e, 'onset', ","),\
                    self.makeEntry(e, 'onsetic'),\
                    self.makeEntry(e, 'bar'),\
                    self.makeEntry(e, 'beat'),\
                    self.makeEntry(e, 'tatum')-1,\
                    int(round(self.makeEntry(e, 'pitch'))),\
                    self.makeEntry(e, 'duration', ","),\
                    self.makeEntry(e, 'durtic', ","),\
                    self.makeEntry(e, 'durtatum', ",")
#                    self.makeEntry(e, 'phrase')
#                    self.makeEntry(e, 'chord'),\
#                    self.makeEntry(e, 'form')
                 ]
                row.extend(seg_markers)
                if len(row) != len(FANTASTIC_header):
                    raise ValueError("Length ({}) of MCSV1 row does not match len of header {}".format(len(row), len(FANTASTIC_header)))
                csvwriter.writerow(row)
        return True

    events  = property(getEventList, setEventList)
