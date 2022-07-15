""" Class implementation of Rhythm """

from numpy import sign

from melospy.basic_representations.key import *
from melospy.basic_representations.meter_grid import *
from melospy.basic_representations.note_event import *
from melospy.basic_representations.rhythm import *

from .jm_util import cycle_list


class NoteTrack(Rhythm):

    def __init__(self, notetrack=None):
        """ Initialize module rhythm """
        if notetrack == None:
            Rhythm.__init__(self, notetrack)
        else:
            if isinstance(notetrack, NoteTrack):
                Rhythm.__init__(self, notetrack)
            else:
                raise Exception("Expected NoteTrack or 'None', got:{}".format(type(notetrack)))

    def clone(self):
        """ Provides deep copy """
        r = NoteTrack(None)
        for e in Rhythm.getEvents(self):
            r.append(e.clone())
        return r

    def append(self, noteEvent):
        """ Append a NoteEvent object"""
        if not isinstance(noteEvent, NoteEvent):
            raise Exception("NoteEvent,append: Non-valid value for NoteEvent!")
        Rhythm.append(self, noteEvent)
        return self

    def clear(self):
        """ Yeah, well. Deletes all events"""
        Rhythm.clear(self)
        self.__pitches = []

        return self

    def getPitches(self, as_integer=True):
        """ Retrieve pitches of NoteEvents"""
        pitches = []
        for e in Rhythm.getEvents(self):
            p = int(round(e.getPitch())) if as_integer else e.getPitch()
            pitches.append(p)
        return pitches

    def getLoudnessData(self, fields=[]):
        def loudness_mapper(loud, key):
            if loud == None:
                return None
            return loud.__dict__[key]

        if len(fields) == 0:
            ret = [_.loudness for _ in Rhythm.getEvents(self)]
            return ret
        ret = {}
        for f in fields:
            ret[f] = [loudness_mapper(_.loudness, f) for _ in Rhythm.getEvents(self)]

        return ret

    def getF0ModulationData(self, fields=[]):
        def f0mod_mapper(f0mod, key):
            if f0mod == None:
                return None
            #print f0mod.__dict__
            return f0mod.__dict__[key]

        if len(fields) == 0:
            ret = [_.modulation  for _ in Rhythm.getEvents(self)]
            return ret
        ret = {}
        for f in fields:
            ret[f] = [f0mod_mapper(_.modulation, f) for _ in Rhythm.getEvents(self)]

        return ret

    def annotateMeter(self, metergrid):
        """Annotate the notetrack with a given metergrid and returns
            a Melody object
        """
        type_check(metergrid, MeterGrid)
        if len(self.getEvents()) != len(metergrid):
            raise ValueError("Expected MeterGrid of len {}, got {} ".format(len(self), len(metergrid)))
        from .melody import Melody
        from .metrical_note_event import MetricalNoteEvent
        melody = Melody()

        for i in range(len(self.getEvents())):
            ne =self.getEvents()[i]
            me = metergrid.getEvents()[i]
            mne= MetricalNoteEvent.fuse(ne, me)
            melody.append(mne)

        return melody


    def transpose(self, dp):
        """ Transpose all NoteEvents by dp"""
        for e in Rhythm.getEvents(self):
            e.transpose(dp)
        return self

    def intervals(self):
        """ Retrieve pitch intervals"""
        ev =  Rhythm.getEvents(self)
        intervals = []
        for i in range(len(ev)-1):
            intervals.append(int(round(ev[i+1].getPitch()-ev[i].getPitch(), 10)))
        return intervals

    def parsons(self):
        ev =  Rhythm.getEvents(self)
        parsons = []
        for i in range(len(ev)-1):
            parsons.append(sign(round(ev[i+1].getPitch()-ev[i].getPitch(), 10)))
        return parsons

    def contour(self, type="huron", format="code"):
        ev =  self.getPitches()
        #print ev
        if type == "huron":
            contour = huron_contour(ev, format)
        elif type == "abesser":
            contour = abesser_contour(ev, format)
        else:
            raise ValueError("Invalid contour mode: {}".format(type))
        return contour

    def intervalClassification(self, numeric = True):
        ev =  Rhythm.getEvents(self)
        classes = []
        int_classes = {0: "o", 1: "S", 2:"S", 3:"T", 4:"T", 5:"L", 6:"L", 7:"L"}
        int_classes_num = {0: 0, 1: 1, 2:1, 3:2, 4:2, 5:3, 6:3, 7:3}
        for i in range(len(ev)-1):
            interval = int(round(ev[i+1].getPitch()-ev[i].getPitch(), 10))
            if not numeric:
                if abs(interval) >= 8:
                    ic = "J"
                else:
                    ic = int_classes[abs(interval)]
                if interval<0:
                    ic = "-" + ic
                if interval>0:
                    ic = "+" + ic
            else:
                if abs(interval) >= 8:
                    ic = 4
                else:
                    ic = int_classes_num[abs(interval)]
                if interval<0:
                    ic = -ic

            classes.append(ic)
        return classes

    def estimateKey(self, suggested_root=None):
        profile_major = [6.33, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88]
        profile_minor = [6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17]
        sharps_major = [1, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 1]
        sharps_minor = [0, 1, 0, 0, 1, 0, 1, 0, 1, 1, 0, 1]
        profile_major.extend(profile_major)
        profile_minor.extend(profile_minor)

        pitches = self.getPitches()
        #print "estimateKey: pitches", pitches

        pcvec = [int(round(p)) % 12 for p in pitches]
        #print "estimateKey: pc's", pcvec

        max_maj = (0, 0)
        max_min = (0, 0)
        for i in range(12):
            tmp_prof_maj = cycle_list(profile_major, 12-i)
            tmp_prof_min = cycle_list(profile_minor, 12-i)
            sum_maj = sum(tmp_prof_maj[_] for _ in pcvec )
            sum_min = sum(tmp_prof_min[_] for _ in pcvec )
            #print "Tonic: {} maj: {}, min:{}".format(NoteName.fromMIDIPitch(i, generic=True), sum_maj, sum_min)
            if sum_maj > max_maj[1]:
                max_maj = (i, sum_maj)

            if sum_min > max_min[1]:
                max_min = (i, sum_min)
        if max_maj[1] >= 0.9 * max_min[1]:
            tonic = NoteName.fromMIDIPitch(max_maj[0], useSharp=sharps_major[max_maj[0]], generic=True)
            ret = Key(tonic, "maj")
        else:
            tonic = NoteName.fromMIDIPitch(max_min[0], useSharp=sharps_minor[max_min[0]], generic=True)
            ret = Key(tonic, "min")
        #print "Ret: {}, max_maj:{}, max_min:{}".format(ret, max_maj, max_min)
        if suggested_root != None:
            sr = NoteName(suggested_root)
            tmp = Key(suggested_root, ret.getScaleType())
            if ret.rootName != sr.getBaseName():
                if str(ret.getScaleType()) == "maj":
                    if (ret.getRootPitchClass() - sr.getPitchClass()) % 12 == 3:
                        tmp = Key(sr.getBaseName(), "min")
                else:
                    if (ret.getRootPitchClass() - sr.getPitchClass()) % 12 == 9:
                        tmp = Key(sr.getBaseName(), "maj")
            ret = tmp

        return ret

    def projection(self, dim):
        """ Projections retrieve value dimensions"""
        if dim == 1 or dim =="onset":
            return self.getOnsets()
        elif dim == 2 or dim =="duration":
            return self.getDurations()
        elif dim == 3 or dim =="pitch":
            return self.getPitches()
        else:
            raise ValueError("Invalid dimension {}".format(dim))

    def to_dataframe(self, ignore_loudness=True, ignore_values=True):
        """Convert NoteTrack object into a handy pandas DataFrame"""
        if len(self) == 0:
            return DataFrame()

        #df = DataFrame({"onset":self.onsets, "durations": self.durations})
        df = Rhythm.to_dataframe(self, ignore_values)
        df["pitch"] = self.getPitches()
        if not ignore_loudness:
            l = self.getLoudnessData(["max", "median"])
            if any(l["max"]):
                df["loud_max"] = l["max"]
            if any(l["median"]):
                df["loud_median"] = l["median"]
        return df

    def toString(self):
        """ Make a nice string"""
        slist = []
        for e in Rhythm.getEvents(self):
            slist.append(e.toString() )
        s = '\n'.join(slist)
        return(s)


    def __str__(self):  return self.toString()
    #def __repr__(self): return self.toString()


    pitches     = property(getPitches)
    loudness    = property(getLoudnessData)
