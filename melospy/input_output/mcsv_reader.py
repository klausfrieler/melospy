""" Class implementation of MCSV reader"""
import csv
import os
import sys

from melospy.basic_representations.jm_stats import mean, sd
from melospy.basic_representations.jm_util import (chomp, dict_from_keys_vals, find_empty,
                                                   remove_empty, type_check)
from melospy.basic_representations.popsong_meta_data import *
from melospy.basic_representations.section_list import *
from melospy.basic_representations.solo import *
from melospy.input_output.mcsv_params import MCSVReaderParams


class MCSVReader(object):
    """Class for reading MCSV file of level  0 or 1"""

    def __init__(self, filename, params=None, csv_format=None):
        self.params = params
        #print params, type(params)
        self.read(filename, csv_format)

    def getLevel(self):
        return self.__level

    def setLevel(self, level = 1):
        if level is not None and level < 1  or level >2:
            raise ValueError("Expected MSCV level of 1 or 2, got {}".format(level))
        self.__level = level

    def getEventList(self):
        return self.__events

    def getMelody(self):
        return self.__melody

    def parseLevel1Preamble(self, preamble):
        fields = preamble.split(",")
        tmp = [chomp(s) for s in fields[0].split(":")]
        signature = None
        ticks = None
        if tmp[0].lower() == "signature":
            signature = tmp[1]
        else:
            raise RuntimeError("MCSV Leve1 1 Preamble malformed: {}".format(preamble))
        tmp = [chomp(s) for s in fields[1].split(":")]
        if tmp[0].lower() == "ticks per beat":
            ticks = tmp[1]
        else:
            raise RuntimeError("MCSV Leve1 1 Preamble malformed: {}".format(preamble))
        #print signature, ticks
        return signature, ticks


    def read(self, filename, csv_format="mcsv1"):
        """
        Read MCSV level 1 or 2 file (mcsv1 or mcsv2)
        """
        if csv_format == "mcsv1":
            return self.read_mcsv1(filename)
        elif csv_format == "mcsv2":
            return self.read_mcsv2(filename)
        raise ValueError("Invalid MCSV format: {}".format(csv_format))

    def read_mcsv1(self, filename):
        """
        Read MCSV level 1 file. The Level is actually automatically identified.
        Fields are read as specified in the header and Melody object is filled.
        Decimal commas are translated to decimal points.
        """
        psi = PopSongInfo(filename=os.path.basename(filename))

        with open(filename, 'r') as csvfile:
            csvreader = csv.reader(csvfile, delimiter=';', lineterminator="\n", quotechar='|', quoting=csv.QUOTE_MINIMAL)
            #for f in csvreader:
            #    print f
            preamble = next(csvreader)
            #print preamble
            sig, ticks = self.parseLevel1Preamble(preamble[0])
            ticks = int(ticks)
            psi.signature = Signature.fromString(sig)
            mi = MeterInfo.fromString(sig)
            mi.setPeriod(int(str(sig).partition("/")[0]))
            self.__metricalContext = MetricalContext(BeatInfo(), mi)
            #print self.__metricalContext
            header = next(csvreader)
            #print header
            nulls = find_empty(header)
            must_remove_end = False
            if len(nulls) > 0:
                if nulls[0] != len(header)-1:
                    raise RuntimeError("Header line malformed:{}", header)
                else:
                    header = remove_empty(header)
                    must_remove_end = True
                    #print "Must remove end"
            if "takt" in header:
                self.setLevel(1)
            else:
                self.setLevel(2)
            #print "Level: {}".format(self.level)
            #print "===================================================="
            self.__events = []
            for r in csvreader:
                if must_remove_end:
                    r = remove_empty(r)
                #any comma must be a decimal point, actually
                r = [ f.replace(",", ".") for f in r]
                event = dict_from_keys_vals(header, r)
                #print event["pitch"]
                self.__events.append(event)

            #print len(self.__events)
            #print self.__events
            tf = self._guessOnsetScaleFactor()
            mean_dur, sd_dur = self._analyseBeatDurations(int(mi.getNumerator()), ticks)
            #print "Mean dur : {}, sd_dur: {}, tf: {}".format(mean_dur, sd_dur, tf)
            psi.setAvgTempoBPM(round(60/mean_dur, 1), withTempoClass=True)
            self.__melody = Song()
            phrase_markers = []
            for e in self.__events:
                bi = BeatInfo(ticks, mean_dur)
                mc = MetricalContext(bi, mi)
                mp = MetricalPosition(int(e['takt']), 
                                      int(e['beat']), 
                                      int(e['ticks'])+1, 0, mc)
                me = MetricalNoteEvent(float(e['onset'])*tf, float(e['pitch']), mp, float(e['durs'])*tf)
                #print me
                #print "----------------------"
                self.__melody.append(me)

                try:
                    phrase_markers.append(int(e['temperley']))
                except:
                    pass
            if self.params != None:
                if self.params.getValue("requantize", False):
                    max_div = self.params.getValue("max_div", 6)
                    tolerance = self.params.getValue("toleranve", .1)
                    if max_div <= ticks:
                        self.__melody.requantize(max_div=max_div, tolerance=tolerance, destructive=True)
        self.__melody.compress()
        #print "-------------------------"
        #print self.__melody
        if len(phrase_markers) > 0:
            #print phrase_markers
            starts = []
            for i in range(len(phrase_markers)):
                if phrase_markers[i]  == 1:
                    starts.append(i)
            phrases = SectionList("PHRASE")
            for i in range(len(starts)):
                if i == 0:
                    start = 0
                else:
                    start = starts[i-1] + 1
                phrases.append(Section("PHRASE", i, start, starts[i]))
            #print "phrases", phrases
            #print len(self.__melody)
            self.__melody.setPhraseSections(phrases)

        #print "psi", psi
        psi.key = self.__melody.estimateKey()
        md = PopSongMetaData(psi)
        self.__melody.setMetadata(md)
        return True

    def read_mcsv2(self, filename):
        """
        Read MCSV level 2 file (using pandas)
        """
        from pandas import DataFrame
        import pandas as pd
        df = pd.read_csv(filename, decimal=".", sep=";")
        #print df.info()
        try:
            mean_dur = mean(df["beat_duration"])
        except:
            mean_dur = 120
            #print mean_dur, sd_dur
        self.__melody = Solo()
        #psi.signature = Signature.fromString(sig)
        is_solo = False
        for index, row in df.iterrows():
            bi = BeatInfo(row["division"], row["beat_duration"])
            signature = row["signature"].replace('"', "").replace("'", "")
            mi = MeterInfo.fromString(signature)
            mc = MetricalContext(bi, mi)
            mp = MetricalPosition(int(row["bar"]), int(row["beat"]), int(row["tatum"]), 0, mc)
            if "loud_max" in row:
                loudness = Loudness(maximum=row["loud_max"], median = row["loud_median"])
            else:
                loudness = None
            me = MetricalNoteEvent(float(row["onset"]), float(row["pitch"]), mp, float(row["duration"]), loudness=loudness)

            #print me
            #print "----------------------"
            self.__melody.append(me)
        try:
            chordSection = SectionList.fromEventList(df["chord"], "CHORD")
            self.__melody.setChordSections(chordSection)
            is_solo = True
        except:
            pass
        try:
            chorusSection = SectionList.fromEventList(df["chorus_id"], "CHORUS")
            self.__melody.setChorusSections(chorusSection )
            is_solo = True
        except:
            pass
        try:
            phraseSection = SectionList.fromEventList(df["phrase_id"], "PHRASE")
            self.__melody.setPhraseSections(phraseSection )
        except:
            pass
        try:
            keySection = SectionList.fromEventList(df["key"], "KEY")
            self.__melody.setKeySections(keySection)
        except:
            pass
        try:
            formSection = SectionList.fromEventList(df["form"], "FORM")
            self.__melody.setFormSections(formSection)
            is_solo = True
        except:
            pass
        if is_solo:
            metadata = SoloMetaData(soloInfo=SoloInfo(), recordInfo=RecordInfo(), transcriptionInfo=TranscriptionInfo(), compositionInfo=CompositionInfo())
        else:
            try:
                sig = ";".join(list(set(df["signature"])))
            except:
                sig = "4/4"
            metadata = PopSongMetaData(
                popSongInfo = PopSongInfo(filename=filename, 
                                          mainSignature=sig))

        metadata.setField("avgtempo", round(60/mean_dur, 1))
        col_names = set(df.columns.values.tolist())
        std_cols = ["onset", "duration", "period", "division", "bar", "beat", "tatum", "beat_duration", "signature", "pitch", "loud_max", "loud_median", "phrase_id", "phrase_begin", "chorus_id", "chord", "form", "key"]
        #print si

        remaining_cols = col_names.difference(std_cols)
        for col in remaining_cols:
            val = list(set(df[col]))[0]
            #print "Column: {}, val: {}".format(col, val)
            try:
                metadata.setField(col, val)
            except:
                pass
        #print metadata
        #print self.__melody

    def _guessOnsetScaleFactor(self):
        """
        Old MCSV files use sometimes miliseconds as unit for onsets/durations,
        we'll try to find out here the simple way using the last IOI
        """

        if len(self.__events)<2:
            return 1.

        last_ioi = float(self.__events[-1]['onset'])-float(self.__events[-2]['onset'])

        if last_ioi > 1:
            return .001
        return 1.0

    def _analyseBeatDurations(self, period, ticks_per_beat):
        beat_durs = []
        for i in range(len(self.__events)-1):
            beat_durs.append(self._guessBeatDuration(period, ticks_per_beat, i, i+1))
        avg = mean(beat_durs)
        std = sd(beat_durs)
        #print(beat_durs)
        if not float_equal(std, 0, 3):
            print("Warning: File not quantized sd={}".format(round(std, 4)))
        return avg, std

    def _guessBeatDuration(self, period, ticks_per_beat, ev1=0, ev2=1):
        if len(self.__events) < 2:
            return None
        onset1 = float(self.__events[ev1]['onset'])
        takt1  = float(self.__events[ev1]['takt'])
        beat1  = float(self.__events[ev1]['beat'])-1
        ticks1 = float(self.__events[ev1]['ticks'])
        onset2 = float(self.__events[ev2]['onset'])
        takt2  = float(self.__events[ev2]['takt'])
        beat2  = float(self.__events[ev2]['beat'])-1
        ticks2 = float(self.__events[ev2]['ticks'])

        dec1 = takt1 +  beat1/period + ticks1/ticks_per_beat/period
        dec2 = takt2 +  beat2/period + ticks2/ticks_per_beat/period
        diff = dec2-dec1
        ioi = onset2-onset1
        beat_duration = (ioi/diff)/period
        #print "Period: {}, Ticks/Beat:{}".format(period, ticks_per_beat)
        #print "Event1: {} - {}/{}/{}".format(onset1, takt1, beat1, ticks1)
        ##print "Event2: {} - {}/{}/{}".format(onset2, takt2, beat2, ticks2)
        #print "Dec1: {}, dec2: {}, diff: {}, ioi:{}".format(dec1, dec2, diff, ioi)
        #print "Beat duration: {}".format(beat_duration)
        return beat_duration

    level   = property(getLevel, setLevel)
    events  = property(getEventList)
    melody  = property(getMelody)
