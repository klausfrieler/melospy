""" Class implementation of Melody """

import numpy as np

from melospy.basic_representations.accents import *
from melospy.basic_representations.meter_grid import *
from melospy.basic_representations.metrical_note_event import *
from melospy.basic_representations.note_track import *
from melospy.basic_representations.timeseries import *


class Melody(NoteTrack, MeterGrid):

    def __init__(self, melody=None):
        """ Initialize module melody"""
        #print type(melody)
        if melody == None or isinstance(melody, Rhythm) or isinstance(melody, MetricalNoteEvent):
            Rhythm.__init__(self, melody)
        else:
            raise TypeError("Expected 'Rhythm' object, 'MetricalNoteEvent' or 'None' !")

    def clone(self):
        """ Provides deep copy """
        r = Melody(None)
        for e in Rhythm.getEvents(self):
            r.append(e.clone())
        return r

    def append(self, mne):
        """ Append a MetricalNoteEvent object"""
        if not isinstance(mne, MetricalNoteEvent):
            raise TypeError("Expected 'MetricalNoteEvent' got {}".format(type(mne)))
        Rhythm.append(self, mne)
        return self

    def extend(self, mnes):
        """ Append a MetricalNoteEvent object"""
        for mne in mnes:
            if not isinstance(mne, MetricalNoteEvent):
                raise TypeError("Expected 'MetricalNoteEvent' got {}".format(type(mne)))
            Rhythm.append(self, mne)
        return self

    def concat(self, melody):
        """Concatenates a copy of 'melody' to current melody.
        If onset times and metrical poisitions of  the added melody do not fit
        a Exception is thrown, so caller has to make sure they fit
        """
        for mne in Rhythm.getEvents(melody):
            self.append(mne)
        return self

    def annotateModulation(self, modulation_annotation):
        """Takes a list of modulations and returns solo object with
            added modulation annotation.
            If list is empty or None, all modulation will be set to
            empty string
        """
        #from melospy.basic_representations.solo import Solo
        #from melospy.basic_representations.solo_event import SoloEvent
        #s = Solo()
        moduls = []
        if modulation_annotation != None:
            moduls = [(self.findEvent(re.onset), re.value) for re in modulation_annotation]

        #for i, e in enumerate(Rhythm.getEvents(self)):
        #    se = SoloEvent(e.clone(), "")
        #    s.append(se)
        for mods in moduls:
            idx = mods[0]
            val = mods[1]
            if idx != None:
                self[idx].setF0Modulation(val)
        return self

    def addLoudnessData(self, loudness_data):
        #print "addLoudnessData called"
        if len(self) != len(loudness_data):
            raise ValueError("Loudness data does not fit. Expected {} elements, got {}".format(len(self), len(loudness_data)))
        for i, e in enumerate(self):
            l = Loudness.fromStruct(loudness_data[i])
            e.setLoudness(l)
        return self

    def addLoudnessDataByNoteId(self, loudness_data, note_ids):
        #print "addLoudnessData called"
        if len(self) != len(loudness_data):
            raise ValueError("Loudness data does not match events. Expected {} elements, got {}".format(len(self), len(loudness_data)))
        if len(note_ids) != len(loudness_data):
            raise ValueError("Loudness data does not match note ids. Expected {} elements, got {}".format(len(note_ids), len(loudness_data)))
        if len(note_ids) != len(self):
            raise ValueError("Note ids do not match events. Expected {} elements, got {}".format(len(self), len(note_ids)))
        if min(note_ids) < 0 or max(note_ids)>= len(self):
            raise ValueError("Note ids do not match events. Min ID {}, max ID: {}".format(min(note_ids), max(note_ids)))

        for ni in note_ids:
            l = Loudness.fromStruct(loudness_data[ni])
            self[ni].setLoudness(l)

        #for i, e in enumerate(self):
        #    l = Loudness.fromStruct(loudness_data[i])
        #    e.setLoudness(l)
        return self

    def addLoudnessDataWithOnsets(self, loudness_data, onsets):
        #print "addLoudnessDataWithOnsets called"
        if len(self) != len(loudness_data):
            raise ValueError("Loudness data does not match events. Expected {} elements, got {}".format(len(self), len(loudness_data)))
        if len(onsets) != len(loudness_data):
            raise ValueError("Loudness data does not match onset data. Expected {} elements, got {}".format(len(onset), len(loudness_data)))
        print("Loudness data {} vs. {}".format(len(onsets), len(loudness_data)))

        i = 0
        for j in range(len(onsets)):
            #print "Onsets[{}]:{}, self.onset[{}]: {}".format(j, onsets[j], i, self[i].onset)
            while onsets[j] != self[i].onset:
                #print "--- Onsets[{}]:{}, self.onset[{}]: {}".format(j, onsets[j], i, self[i].onset)
                i += 1
                #print "......Skip ", i
            #print "--- Onsets[{}]:{}, self.onset[{}]: {}".format(j, onsets[j], i, self[i].onset)
            l = Loudness.fromStruct(loudness_data[j])
            self[i].setLoudness(l)

        return self

    def addLoudnessDataByNoteId(self, loudness_data, note_ids):
        #print "addLoudnessData called"
        if len(self) != len(loudness_data):
            raise ValueError("Loudness data does not match events. Expected {} elements, got {}".format(len(self), len(loudness_data)))
        if len(note_ids) != len(loudness_data):
            raise ValueError("Loudness data does not match note ids. Expected {} elements, got {}".format(len(note_ids), len(loudness_data)))
        if len(note_ids) != len(self):
            raise ValueError("Note ids do not match events. Expected {} elements, got {}".format(len(self), len(note_ids)))
        if min(note_ids) < 0 or max(note_ids)>= len(self):
            raise ValueError("Note ids do not match events. Min ID {}, max ID: {}".format(min(note_ids), max(note_ids)))

        for ni in note_ids:
            l = Loudness.fromStruct(loudness_data[ni])
            self[ni].setLoudness(l)

        #for i, e in enumerate(self):
        #    l = Loudness.fromStruct(loudness_data[i])
        #    e.setLoudness(l)
        return self

    def addLoudnessAndModulationByNoteId(self, loudness_data, f0mod_data, note_ids, keep_original_annotations=True):
        #print "addLoudnessAndModulationByNoteId called"
        if len(self) != len(loudness_data):
            raise ValueError("Loudness data does not match events. Expected {} elements, got {}".format(len(self), len(loudness_data)))
        if len(note_ids) != len(loudness_data):
            raise ValueError("Loudness data does not match note ids. Expected {} elements, got {}".format(len(note_ids), len(loudness_data)))
        if len(self) != len(f0mod_data):
            raise ValueError("F0 modulation data does not match events. Expected {} elements, got {}".format(len(self), len(loudness_data)))
        if len(note_ids) != len(f0mod_data):
            raise ValueError("F0 modulation data does not match note ids. Expected {} elements, got {}".format(len(note_ids), len(loudness_data)))
        if len(note_ids) != len(self):
            raise ValueError("Note ids do not match events. Expected {} elements, got {}".format(len(self), len(note_ids)))
        if min(note_ids) < 0 or max(note_ids)>= len(self):
            raise ValueError("Note ids do not match events. Min ID {}, max ID: {}".format(min(note_ids), max(note_ids)))

        for ni in note_ids:
            l = Loudness.fromStruct(loudness_data[ni])
            f = F0Modulation.fromStruct(f0mod_data[ni])
            if keep_original_annotations:
                annotated = self[ni].getAnnotatedF0Modulation()
                f.set_modulation(annotated)
            self[ni].setLoudness(l)
            self[ni].setF0Modulation(f)

        #for i, e in enumerate(self):
        #    l = Loudness.fromStruct(loudness_data[i])
        #    e.setLoudness(l)
        return self

    def getLoudnessField(self, field, default="NA"):
        ret = [e.getLoudnessField(field, default) for e in self]
        return ret

    def getF0ModulationField(self, field, default=None):
        ret = [e.getF0ModulationField(field, default) for e in self]
        return ret

    def getModulations(self, short_form=False):
        moduls = []
        for e in Rhythm.getEvents(self):
            try:
                val = e.getAnnotatedF0Modulation()
            except:
                val = ""
            if short_form:
                val = val.lower()[0:3]
            moduls.append(val)
        return moduls

    def getF0Modulations(self):
        moduls = []
        for e in Rhythm.getEvents(self):
            try:
                val = e.getF0Modulation()
            except:
                val = F0Modulations()
            moduls.append(val)
        return moduls

    def getSegments(self, segmentType):
        #print "getSegments Melody"
        ret = []
        if segmentType != "bars":
            return []
        for i in self.getBarNumbers():
            #print type(Melody(self.getBarSequence(i,i)))
            ret.append(Melody(self.getBarSequence(i, i)))
        #print len(ret)
        #print ret[0]
        return ret

    def getTotalMetricalDuration(self):
        mp_first = self.events[0].getMetricalPosition().toDecimal()
        mp_last = self.events[-1].getMetricalPosition().toDecimal()
        mdd = self.events[-1].estimateMetricalDurationDecimal()
        #print "First: {}, Last: {}, Dur:{}".format(mp_first, mp_last, mdd)
        return mp_last-mp_first + mdd

    def getGradientContour(self, mode="strict"):
        ts = TimeSeries(self)
        #print ts
        gl = ts.gradientList(format="with-index")
        #print gl
        return gl

    def getSpellingContext(self):
        try:
            key = self.getMetadata().getField("key")
            if not isinstance(key, Key):
                key = Key(key)
        except:
            key = Key("C")

        scale_pcs = key.getPitchClasses()
        key_flat = key.onTheFlatSide()

        #print "Key:{}, PCS:{}, key flat:{}".format(key, scale_pcs, key_flat)

        return [key_flat]*len(self)


    def simpleExport(self, what, optParam=None):

        #print "Melody.simpleExport called with {} (optParam:{})".format(what, optParam)
        try:
            val = np.array(self.projection(what))
            #print "{} found in projections".format(what)
            return val
        except:
            pass
        #print "{} not found in projections".format(what)
        if what == "parsons":
            #print "'{}' found in other exports".format(what)
            return np.array(self.parsons())
        elif what == "interval":
            #print "'{}' found in other exports".format(what)
            return np.array(diff(self.getPitches()))
        elif what == "fuzzyinterval" or what == "fuzzyint" or what == "fuzzy-interval" :
            #print "'{}' found in other exports".format(what)
            return np.array(self.intervalClassification())
        elif what == "durclass":
            #print "'{}' found in other melody exports, optParam:{}".format(what, optParam)
            return np.array(self.durationClassification(type="dur", mode=optParam))
        elif what == "ioiclass":
            #print "'{}' found in other melody exports, optParam:{}".format(what, optParam)
            return np.array(self.durationClassification(type="ioi", mode=optParam))
        elif what == "ioi":
            #print "'{}' found in other exports".format(what)
            return np.array(self.getIOIs())
        elif what == "dur_ratio":
            #print "'{}' found in other exports".format(what)
            classify = False
            if optParam is not None and optParam.lower()[0:5] == "class":
                classify = True
            return np.array(self.getDurationRatios(classify=classify))
        elif what == "dur_ratio_class":
            #print "'{}' found in other exports".format(what)
            return np.array(self.getDurationRatios(classify=True))
        elif what == "ioi_ratio":
            #print "'{}' found in other exports".format(what)
            classify = False
            if optParam is not None and optParam.lower()[0:5] == "class":
                classify = True
            return np.array(self.getIOIRatios(classify=classify))
        elif what == "ioi_ratio_class":
            #print "'{}' found in other exports".format(what)
            return np.array(self.getIOIRatios(classify=True))
        elif what == "metricalweights" or what == "weights" or what == "mw":
            #print "{} found in other exports".format(what)
            return np.array(self.getMetricalWeights())
        elif what == "pitchclass" or what == "pc":
            #print "{} found in other exports".format(what)
            return np.array([v % 12 for v in self.getPitches()])
        elif what == "huroncontour" or what == "huron-contour":
            #print "'{}' found in other exports".format(what)
            #print self.huronContour(format= "num")
            c = self.contour(type="huron", format=optParam)
            #print "Type: {}".format(type(c))
            return c
        elif what == "abessercontour" or what == "abesser-contour":
            #print "'{}' found in other exports".format(what)
            #print self.huronContour(format= "num")
            c = self.contour(type="abesser", format=optParam)
            #print "Type: {}".format(type(c))
            return c
        elif what == "gradient-contour":
            #print "'{}' found in other exports".format(what)
            return np.array(self.getGradientContour(mode=optParam))
        elif what == "swing-ratios":
            #print "'{}' found in other exports".format(what)
            max_div = 2
            if optParam is not None:
                if isinstance(optParam, int):
                    max_div = max(2, optParam)
                if isinstance(optParam, str) and optParam.lower() == "include-ternary":
                    max_div = 3
                #print "include_ternary", include_ternary
            #print "max_div", max_div
            return np.array(self.getSwingRatios(max_div=max_div))
        elif what == "total-duration":
            #print "'{}' found in other exports".format(what)
            return np.array(self.totalDuration())
        elif what == "total-metrical-duration":
            #print "'{}' found in other exports".format(what)
            return np.array(self.getTotalMetricalDuration())
        elif what == "syncopations":
            #print "'{}' found in other exports".format(what)
            return np.array(self.syncopations())
        elif what == "syncopicity":
            #print "'{}' found in other exports".format(what)
            return np.array(self.syncopicity())
        elif what == "loudness":
            #print "'{}' found in other exports".format(what)
            return np.array(self.getLoudnessField(field=optParam))
        elif what == "modulation":
            #print "-"*60
            #print "{} found in other exports with optParam {}".format(what, optParam)
            short_form = False
            ret = []
            if isinstance(optParam, str):
                if optParam.lower() ==  "annotated_short":
                    short_form = True
                    ret = np.array(self.getModulations(short_form))
                else:
                    #mf = self.getF0ModulationField(field=optParam.lower())
                    ret = np.array(self.getF0ModulationField(field=optParam.lower(), default=np.nan))
                    #if optParam == "range_cents":
                    #    print ", ".join([str(type(e)) for e in ret])
            return ret
        elif what == "norm_onsets":
            #print "'{}' found in other exports".format(what)
            #print(self.getNormalizedOnsets())
            return np.array(self.getNormalizedOnsets())
        elif what == "metric_complexity":
            #print "'{}' found in other exports".format(what)
            if optParam == None:
                optParam = "combined"
            return np.array(self.metric_complexity(method=optParam))
        elif what == 'accent':
            #print "{} found in other exports with param '{}'".format(what, optParam)
            #to do
            accent_type = ""
            params = None
            if isinstance(optParam, str):
                accent_type = optParam
            if isinstance(optParam, dict):
                accent_type = optParam["type"]
                params = optParam
            af = AccentFactory()
            #print "accent_type", accent_type, params
            a = af.create(accent_type)
            if params != None:
                a.setParams(params)
            return np.array(a.calculate(self))
        elif what == "mcm":
            #print "'{}' found in other exports (N={})".format(what, optParam)
            if optParam == None or optParam == "":
                optParam = 48

            optParam = int(optParam)
            mcm = self.getMCM(optParam)
            if optParam in mcm:
                for i in range(len(mcm)):
                    if optParam == mcm[i]:
                        #print "WARNING: MCM: Found {} for {} at {}: {}".format(mcm[i], self.getMetricalPositionsDecimal(debug = True)[i], self.getMetricalPositions()[i], str(self.getMetricalPositions()[i].getMetricalContext()))
                        mcm[i] = 0
                        #sys.exit(0)
                #raise ValueError("Found invalid position = {}", optParam)
            return np.array(mcm)
        else:
            raise ValueError("Melody: Invalid export specified: " +str(what))

    def export(self, what, segmentType=None, optParam=None):
        #print "Melody.export: {}, {}".format(what, segmentType)
        if segmentType != None:
            try:
                segments = self.getSegments(segmentType)
            except:
                raise ValueError("Segmentation <{}> for export not available.".format(segmentType))
            if len(segments) == 0:
                raise ValueError("Segmentation <{}> for export not available.".format(segmentType))
            ret = []
            for seg in segments:
                ret.append(seg.simpleExport(what, optParam))
        else:
            ret = self.simpleExport(what, optParam)

        return ret

    def projection(self, dim):
        """ Retrieve value dimensions"""
        try:
            pr = NoteTrack.projection(self, dim)
            #print "Melody.projection {} found in NoteTrack class", dim
        except:
            pass
        try:
            pr = MeterGrid.projection(self, dim)
            #print "Melody.projection {} found in MeterGrid class", dim
            return pr
        except:
            pass
        if dim == 1 or dim == "onset":
            return self.getOnsets()
        elif dim == 2 or dim == "duration":
            return self.getDurations()
        elif dim == 3 or dim == "meter":
            return self.getMetricalPositions()
        elif dim == 4 or dim == "durtatum":
            return self.getDurationTatums()
        elif dim == 5 or dim =="pitch":
            return self.getPitches()
        elif dim == 6 or dim =="offset":
            return self.getOffsets()
        else:
            raise ValueError("Invalid dimension specified: " +str(dim))

    def toQuarterFormat(self):
        mg = MeterGrid(self).toQuarterFormat()
        ret = Melody()
        for i, e in enumerate(self):
            mne = MetricalNoteEvent(onsetSec=e.onset, pitch=e.pitch, metricalPosition=mg[i].mp, durationSec=e.duration, durationTatum=mg[i].durtatum, loudness=e.loudness)
            ret.append(mne)
        return ret

    def to_dataframe(self, split_metrical_positions=True, ignore_loudness=True, ignore_f0mod=True, ignore_values=True, quote_signatures=False):
        """Convert Melody object into a handy pandas DataFrame"""
        if len(self) == 0:
            return DataFrame()

        df = MeterGrid.to_dataframe(self, split_metrical_positions, ignore_values, quote_signatures)
        df["pitch"] = self.getPitches()

        if not ignore_loudness:
            l = self.getLoudnessData(["max", "median"])
            if any(l["max"]):
                df["loud_max"] = l["max"]
            if any(l["median"]):
                df["loud_median"] = l["median"]
        if not ignore_f0mod:
            l = self.getF0ModulationData(["annotated", "range_cents", "freq_hz", "median_dev"])
            if any(l["annotated"]):
                df["annotated"] = l["annotated"]
            if any(l["range_cents"]):
                df["range_cents"] = l["range_cents"]
            if any(l["freq_hz"]):
                df["freq_hz"] = l["freq_hz"]
            if any(l["median_dev"]):
                df["median_dev"] = l["median_dev"]

        return df

    def toString(self):
        """ Make a nice string"""
        slist = [str(e) for e in Rhythm.getEvents(self)]
        s = '\n'.join(slist)
        return(s)

    def __str__(self):  return self.toString()
    #def __repr__(self): return self.toString()
