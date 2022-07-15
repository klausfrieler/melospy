""" Class implementation of SV project file reader"""
import bz2
import os
import sys
from xml.dom import minidom

from melospy.basic_representations.annotated_beat_track import *
from melospy.basic_representations.chord import *
from melospy.basic_representations.chord_sequence import *
from melospy.basic_representations.jm_stats import mean, sd
from melospy.basic_representations.jm_util import type_check
from melospy.basic_representations.metrical_annotator import *
from melospy.basic_representations.note_track import *
from melospy.basic_representations.rhythm import *
from melospy.basic_representations.section_list import *
from melospy.basic_representations.signature import *
from melospy.basic_representations.solo import *
from melospy.input_output.sv_params import SVReaderParams


class SVModel(object):
    """ Class to represent a model, which is a node type in the SV project files
        that holds meta data information for layers.
        Particulary, the id of the dataset, the type and sample rate have to be
        extracted. A SVModel is fed into a SVDataset
        object which does the actually extracting and parsing of annotation data.
    """
    def __init__(self, model):
        """ Initialize module """
        self.__model      = model
        self.__sampleRate = int(self.__model.getAttribute("sampleRate"))
        self.__maintype   = self.__model.getAttribute("type")
        self.__subtype    = self.__model.getAttribute("subtype")
        self.__dataid     = self.__model.getAttribute("dataset")

    def getSampleRate(self):
        return(self.__sampleRate)

    def getMainType(self):
        if len(self.__maintype) == 0:
            return "NA"
        return(self.__maintype)

    def getSubtype(self):
        if len(self.__subtype) == 0:
            return "NA"
        return(self.__subtype)

    def getDataId(self):
        return(self.__dataid)

    def getDataType(self):
        if self.__maintype == "sparse":
            if len(self.__subtype)==0:
                return("beats")
            if self.__subtype=="note":
                return("notes")
            if self.__subtype=="region":
                return("phrases")
            if self.__subtype=="text":
                return("modulation")
            return("NA")
        else:
            return("wave")

    sampleRate            = property(getSampleRate)
    maintype              = property(getMainType)
    subtype               = property(getSubtype)
    dataid                = property(getDataId)

class SVDataSet(object):
    """
        Class to represent a data set, which is a node type in the
        SV project files that holds the data for annoation layers.
        A SVModel containing necesary meta dat is fed into a SVDataset
        object.
        After construction a SVDataset Model a call to parse() passing
        a xmldoc object, provides pre-parsed raw data as a list of lists.
    """

    def __init__(self, model):
        """ Initialize module """
        self.__id         = model.getDataId()
        self.__data       = None
        self.__type       = model.getDataType()
        self.__sampleRate = model.getSampleRate()
        self.__raw        = None

    def parse(self, xmldoc):
        """ Parse xmldoc for data set according to data id"""
        data = xmldoc.getElementsByTagName("dataset")
        for i in range(data.length):
            if data[i].getAttribute("id") == self.__id:
                self.__data = data[i]
                break
        if self.__data == None:
            raise Expection("Invalid data set id")
        if self.__type == "beats":
            return self.parseBeats()
        elif  self.__type == "notes":
            return self.parseNotes()
        elif self.__type == "phrases":
            return self.parsePhrases()
        elif self.__type == "modulation":
            return self.parseModulation()
        else:
            return None

    def parseBeats(self):
        if self.__data == None:
            raise Exception("parseBeats: No data")
        self.__raw = []
        for e in self.__data.childNodes:
            if e.nodeType == e.ELEMENT_NODE:
                time = float(e.getAttribute("frame"))/self.__sampleRate
                label = str(e.getAttribute("label"))
                self.__raw.append([time,  label])
        #print raw[1:10]
        return self.__raw

    def parseNotes(self):
        if self.__data == None:
            raise Exception("parseNotes: No data")
        self.__raw = []
        for e in self.__data.childNodes:
            if e.nodeType == e.ELEMENT_NODE:
                time = float(e.getAttribute("frame"))/self.__sampleRate
                duration = float(e.getAttribute("duration"))/self.__sampleRate
                pitch = float(e.getAttribute("value"))
                label = str(e.getAttribute("label"))
                self.__raw.append([time, duration, pitch, label])
        #print raw[1:10]
        return self.__raw

    def parsePhrases(self):
        if self.__data == None:
            raise RuntimeError("No data")
        self.__raw = []
        valid_ideas = 0
        i = Idea()
        for e in self.__data.childNodes:
            if e.nodeType == e.ELEMENT_NODE:
                time = float(e.getAttribute("frame"))/self.__sampleRate
                duration = float(e.getAttribute("duration"))/self.__sampleRate
                label = str(e.getAttribute("label"))
                if i.parseLabel(label):
                    valid_ideas += 1
                self.__raw.append([time, duration, label])
        #print "Valid ideas:{}/{}".format(valid_ideas, len(self.__raw))
        if valid_ideas:
            self.__type = "IFA"
        return self.__raw

    def parseModulation(self):
        if self.__data == None:
            raise RuntimeError("No data")
        self.__raw = []
        for e in self.__data.childNodes:
            if e.nodeType == e.ELEMENT_NODE:
                time = float(e.getAttribute("frame"))/self.__sampleRate
                value  = e.getAttribute("label")
                self.__raw.append([time, value])
        return self.__raw

    def getId(self):
        return self.__id

    def getDimensions(self):
        if self.__raw == None:
            return None
        return len(self.__raw[0])

    def getType(self):
        return self.__type

    def getSampleRate(self):
        return self.__sampleRate

    def getRaw(self):
        return self.__raw

    id          = property(getId)
    type        = property(getType)
    sampleRate  = property(getSampleRate)
    raw         = property(getRaw)

class SVParserBase(object):
    """ base class for annonation layer parser"""
    def __init__(self, events):
        """ Initialize module """
        self.setEvents(events)

    def getEvents(self):
        """ getter for event list """
        return self.__events

    def setEvents(self, events):
        """ setter for event list """
        if not isinstance(events, list):
            raise TypeError("Expected list of events")
        self.__events = events
        return self

    def isEmpty(self):
        return len(self.__events) == 0

    def clear(self):
        self._events = None

    events   =  property(getEvents, setEvents)

class SVParsePhrases(SVParserBase):
    """ class for parsing a phrases annonation layer."""
    def __init__(self, events, nt):
        """ Initialize module """
        SVParserBase.__init__(self, events)
        if not isinstance(nt, NoteTrack):
            raise TypeError("Expected 'NoteTrack' object")
        self.__notetrack = nt

    def getPhraseSection(self):
        if self.isEmpty():
            raise RuntimeError("No events")
        sl = SectionList("PHRASE")
        phrase = 1
        for e in self.getEvents():
            if not isinstance(e, list):
                continue
            onset = float(e[0])
            dur   = float(e[1])
            #print "{},{}".format(onset, dur)
            start, end = self.__notetrack.getIDsFromRegion(onset, onset + dur, tolerance = 0.05)
            #print "{},{}".format(start, end)
            if start == None:
                #print "Oops, no events found"
                continue
            sl.append(Section("PHRASE", phrase, start, end))
            phrase += 1
        return sl

class SVParseIdeas(SVParserBase):
    """ class for parsing IFA annonation layer."""
    def __init__(self, events, nt):
        """ Initialize module """
        SVParserBase.__init__(self, events)
        if not isinstance(nt, NoteTrack):
            raise TypeError("Expected 'NoteTrack' object")
        self.__notetrack = nt

    def getIFASections(self):
        if self.isEmpty():
            raise RuntimeError("No events")
        sl = SectionList("IDEA")
        void_buffer = False
        for e in self.getEvents():
            if not isinstance(e, list):
                continue
            onset = float(e[0])
            dur   = float(e[1])
            #print "{},{}".format(onset, dur)
            start, end = self.__notetrack.getIDsFromRegion(onset, onset + dur, tolerance=0.00)
            #print "{},{}:'{}'".format(start, end, e[2])
            if start == None:
                #print "Oops, no events found"
                if str(e[2]) == "void":
                    void_buffer = True
                continue
            tmp_idea = e[2]
            if void_buffer:
                #print "Added void buffer"
                tmp_idea = "void->" + tmp_idea
                void_buffer = False
            idea = Idea(tmp_idea)
            try:
                sl.append(Section("IDEA", idea, start, end))
            except Exception as e:
                print("IFA Error at {}".format(s_to_hms(onset)))
                raise(e)
        return sl


class SVParseChordForm(SVParserBase):
    """ class for parsing a phrases annonation layer."""
    def __init__(self, events, nt):
        """ Initialize module """
        SVParserBase.__init__(self, events)
        if not isinstance(nt, NoteTrack):
            raise TypeError("Expected 'NoteTrack' object")
        self.__notetrack = nt

    def _possibleTypes(self, cfs):
        types = []
        test = None
        try:
            #print "TEST SIG:", cfs
            test = Signature.fromString(cfs.split("a")[0])
            types.append('signature')
        except:
            pass
        try:
            test  = Chord(cfs)
            types.append('chord')
        except:
            pass
        try:
            test = FormName(cfs)
            types.append('form')
        except:
            pass
        return types

    def _parseChordFormSignature(self, cfs, results=None, expand_a2=True):
        """
        ChordFormSignature should be:
            <Form>-<Chord>-<Signature>
            <Form>-<Signature>-<Chord>
            <Form>-<Chord>
            <Form>-<Signature>
            <Chord>-<Signature>
            <Form>
            <Chord>
            <Signature>
        input:
            cfs: ChordFormSignature string
            results: dictionary with 'form', 'chord', 'signature' keys or None
        """
        if not results:
            results = {'form': None, 'chord': None, 'signature': None}
        elements = cfs.split("-")
        elements = [chomp(e) for e in elements]

        form    = None
        chord   = None
        sig     = None
        beat_interpolate = None
        nFound  = 0
        #print "\nEnter cfs parse\n=================="
        #print "CFS: {}, elements: {}, len: {}".format(cfs, elements, len(elements))
        if len(elements) == 1:
            pos_types = self._possibleTypes(elements[0])#
            if len(pos_types) == 0:
                raise ValueError("Invalid CFS-Syntax: " + elements[0])
            if 'chord' in pos_types:
                chord = Chord(elements[0])
                #print "try Chord: {}".format(chord)
            elif 'form' in pos_types:
                form = FormName(elements[0])
                #if form is not None:
                #    print "try Form: {}".format(form)
            else:
                if expand_a2:
                    sig = Signature.fromString(elements[0].split("a")[0])
                    if len(elements[0].split("a"))>1:
                        beat_interpolate = int(elements[0].split("a")[1])
                else:
                    sig = elements[0]
        else:
            #print "looop"
            for i in range(len(elements)):
                pos_types = self._possibleTypes(elements[i])#
                #print "pos_type", elements[i], pos_types
                if len(pos_types) == 0:
                    raise ValueError("Invalid CFS-Syntax: {}. Could not determine type of: '{}'".format(cfs, elements[i]))
                if not form and 'form' in pos_types:
                    form = FormName(elements[i])
                    #if form is not None:
                    #    print "try Form: {}, orig:{}".format(form, elements[i])
                        #print "try Form: {}".format(form)
                if not chord and 'chord' in pos_types:
                    chord = Chord(elements[i])
                        #print "try Chord: {}".format(type(chord))
                if not sig and 'signature' in pos_types:
                    #print "try Signature: {}, beat:{}".format(sig, beat_interpolate)
                    if expand_a2:
                        sig = Signature.fromString(elements[i].split("a")[0])
                        if len(elements[i].split("a"))>1:
                            beat_interpolate = int(elements[i].split("a")[1])
                    else:
                        sig = elements[i]
        if form:
            results['form'] = form
            nFound += 1
        if chord != None:
            results['chord'] = chord
            #print "Chords: {}".format(results['chord'])
            nFound += 1
        if sig:
            results['signature'] = sig
            if beat_interpolate and expand_a2:
                if sig.getNumerator() % beat_interpolate != 0:
                    raise ValueError("Invalid beat interpolation:  {}".format(beat_interpolate))
                results['beat_interpolate'] = beat_interpolate
                sig.setNumerator(sig.getNumerator() * beat_interpolate)
                sig.setDenominator(sig.getDenominator() * beat_interpolate)
                #print "Beat interpolation: {}".format(results['beat_interpolate'])
            #print "Signature: {}".format(results['signature'])
            nFound +=1

        #print nFound, elements, len(elements)
        if nFound != len(elements):
            if nFound == 3:
                print("Warning: Found ambiguous BCF string: {}. Using Chord".format(cfs))
                results["form"] = None
            else:
                raise ValueError("Invalid BCF-Syntax:  " + cfs)
        return results

    def parseBeatChordFormString(self, bcf, diagnostic=False, expand_a2=True):
        """BeatFormChord string syntax is:
            <bar>.<beat>:<Form>-<Chord>-<Signature>
        """
        #if not isinstance(bcf, basestring):
        #    raise TypeError("Expected string")
        results = {'beat': None, 'form': None, 'chord': None, 'signature': None, 'beat_interpolate': None}
        bcf = bcf.rstrip().lstrip()
        #print "BCF: {}".format(bcf)
        if len(bcf) == 0:
            return results
        #parse first part, if present
        elements = bcf.split(":")
        cfs = ""
        if len(elements) == 2:
            results['beat'] = elements[0]
            cfs = chomp(elements[1])
        elif len(elements) == 1:
            if bcf.find(".") == -1:
                cfs = elements[0]
                #print len(elements)
            else:
                results['beat'] = elements[0]
                return results
        else:
            raise ValueError("Invalid BCF-Syntax: " + bcf)
        if len(cfs) > 0:
            self._parseChordFormSignature(cfs, results, expand_a2)

        return results

    def rhythmToSectionList(self, rhythm, nt, sectType = None):
        """
            Transforms a consecutive list of starting points
            of sections (a 'Rhythm' object) to a SectionList
            object
        """
        if not isinstance(rhythm, Rhythm):
            raise TypeError("Expected 'Rhythm' object")
        if not isinstance(nt, NoteTrack):
            raise TypeError("Expected 'NoteTrackObject' object")
        if rhythm.isEmpty():
            if sectType != None:
                msg = sectType
            else:
                msg = "Rhythm"
            raise ValueError("Empty '{}' object".format(msg))

        if sectType == None:
            try:
                tmp = type(rhythm[0].getValue())
                if tmp == Chord:
                    sectType = 'CHORD'
                elif tmp == FormName or tmp == FormPart:
                    sectType = 'FORM'
                elif tmp == Key:
                    sectType = 'KEY'
                else:
                    sectType = 'PHRASE'
            except:
                raise ValueError("Expected value 'CHORD', 'FORM', or 'PHRASE for Rhythm item 0, got".format(tmp))
        try:
            sl = SectionList(sectType)
        except Exception as e:
            raise e

        for i in range(len(rhythm)):
            onset = rhythm[i].getOnsetSec()
            if i <(len(rhythm)-1):
                dur = rhythm[i+1].getOnsetSec()-onset
            else:
                dur = 10000
            #print "\n{}: Onset: {}, offset:{}".format(sectType, onset, onset+dur)
            start, end = nt.getIDsFromRegion(onset, onset + dur)

            #print "{}: start: {}, end:{} val:{}\n".format(sectType, start, end, str(rhythm[i].getValue()))
            if start == None:
                #print "OOOPS, no elements found for {}".format(onset)
                continue
            #if sectType == "FORM":
            #    print "Form: i={}, val={}, start:{}, end:{}".format(i, rhythm[i].getValue(), start, end)
            #if sectType == "CHORD":
            #    print "Chord i:{}, val:{}, start: {}, end:{} ".format(i, rhythm[i].getValue(), start, end)
            #sl.append(Section(sectType, rhythm[i].getValue(), start, end))
            try:
                sl.append(Section(sectType, rhythm[i].getValue(), start, end))
                pass
            except Exception as e:
                msg = "Error during section appending at onset {} : {}".format(rhythm[i].onsetSec, e.args[0])
                raise ValueError(msg)
        return sl

    def _get_chord_changes_by_form(self, form_list, sig_list, chord_list):
        #sig_list[40] = 3
        #print "_get_chord_changes_by_form"
        #print sig_list
        #print chord_list
        #print form_list
        form_cur = ""
        sig_cur = ""
        sig_changes = []
        form_starts = []
        if not sig_list[0]:
            for i in range(len(sig_list)):
                if sig_list[i]:
                    first = sig_list[i]
                    break
            sig_list[0] = first
        for i in range(len(sig_list)):
            if sig_list[i] and sig_list[i] != sig_cur:
                sig_changes.append(i)
                sig_cur = sig_list[i]
            if (form_list[i] and form_list[i] != form_cur) or form_list[i] == "A1":
                form_starts.append(i)
                form_cur = form_list[i]
                sig_list[i] = sig_cur

        form_starts.append(len(chord_list))
        segments = sorted(set(form_starts).union(sig_changes))
        #print sig_list, len(sig_list), len(form_list), sig_changes, form_starts, segments
        #print form_list
        seq = []
        for i in range(len(form_starts)-1):
            cur_cs = ChordSequence()
            start = form_starts[i]
            end  = form_starts[i+1]
            #print "start, end", start, end
            loc_sig_changes = [start]
            for j in range(len(sig_changes)):
                if start <= sig_changes[j] and sig_changes[j]<end:
                    loc_sig_changes.append(sig_changes[j])
            loc_sig_changes.append(end)
            loc_sig_changes = sorted(set(loc_sig_changes))
            #print "loc_sig_changes", loc_sig_changes, i
            for j in range(len(loc_sig_changes)-1):
                strlist = chord_list[loc_sig_changes[j]: loc_sig_changes[j+1]]
                #print "j=, len strlist=",j, len(strlist)
                #print "HERE", strlist, sig_list[loc_sig_changes[j]]
                cs = ChordSequence.fromStringList(strlist, sig_list[loc_sig_changes[j]], fill_up=True)
                if cs:
                    cur_cs.extend(cs)
                #print "length now:", len(strlist),  cur_cs.length_in_bars()

            seq.append((form_list[start], cur_cs))
            #print "inserted ", form_list[start],  cur_cs.length_in_bars()
        ret = []
        copy = False
        for el in seq:
            if copy and el[0] == "A1":
                break
            if el[0] == "A1" or el[0][0] == "*":
                copy = True
            if copy:
                #ret.append("{}: {}".format(el[0], str(el[1])))
                ret.append(el)
        #print "\n".join([str(_) for _ in zip(form_list, chord_list)])
        if len(ret) == 1:
           s_ret =["{}: {}".format(ret[0][0], str(ret[0][1].simplify()))]
        else:
            s_ret = ["{}: {}".format(el[0], str(el[1])) for el in ret]
        #print s_ret
        if len(s_ret) > 0:
            s_ret = "\n".join(s_ret)
        else:
            s_ret = ""
        #print ret
        s_ret = s_ret.replace("*", "")
        return s_ret

    def parse(self, diagnostic=None):
        """Main worker horse. Parse the raw data and give some meaning to it.
            Returns:
                AnnotatedBeatTrack object
                FORM section list
                CHORD section list
                chord changes string

        """
        if diagnostic == None:
            try:
                diagnostic = self.params.getValue("diagnostic")
            except:
                diagnostic = False
        if self.isEmpty():
            raise RuntimeError("No events")
        beats = AnnotatedBeatTrack()
        sf = SectionList("FORM")
        sc = SectionList("CHORD")
        sig_list = []
        #raw parsing
        evl = self.getEvents()
        for i in range(len(evl)):
            e = evl[i]
            if not isinstance(e, list):
                break
            onset = float(e[0])
            if i < (len(evl)-1):
                dur   = evl[i+1][0]-onset
            else:
                pass
                #dur = 10000
            #out of try
            #vals = self.parseBeatChordFormString(str(e[1]), expand_a2=False)
            try:
                vals = self.parseBeatChordFormString(str(e[1]), expand_a2=False)
            except Exception as error:
                if diagnostic:
                    print("Error at {}: {}".format(s_to_hms(onset), error.args[0]))
                else:
                    raise(error)
            #print onset, type(vals["form"])
            abe = AnnotatedBeatEvent(onset, None, vals["form"], vals["chord"])
            #if vals["form"] is not None:
            #    print vals["form"].hasWildcard()
            abe.duration = dur
            beats.append(abe)
            sig = str(vals["signature"]) if vals["signature"] else ""
            sig_list.append(sig)

        beats = beats.metricalPositionsFromSignatures(sig_list)
        #print beats
        beats.calcSignatureChanges()
        beats.normalizeForm()
        beats.setChorusIDs()
        #print beats
        #print beats.getSignatureChanges()
        if diagnostic:
            print("Assembling chord list...")
        #out of try
        #sc = self.rhythmToSectionList(beats.getChords(), self.__notetrack, "CHORD")
        #print sc
        try:
            sc = self.rhythmToSectionList(beats.getChords(), self.__notetrack, "CHORD")
        except Exception as e:
            if not diagnostic:
                raise Exception(e.args)
            else:
                print("Error in chord list: {}".format(e.args[0]))

        #form list
        if diagnostic:
            print("Assembling form list...")
        #out of try
        #print "After norming", beats.getForm()
        sf = self.rhythmToSectionList(beats.getForm(), self.__notetrack, "FORM")

        chord_changes = beats.get_chord_changes_by_form()
        #print beats
        return beats, sf, sc, chord_changes


class SVParseNotes(SVParserBase):
    """ Class for parsing a notes annonation layer."""
    def __init__(self, events):
        """ Initialize module """
        SVParserBase.__init__(self, events)
        self.note_track = None

    def getNoteTrack(self, duration_threshold=0.0):
        """Parses the event list and returns 'NoteTrack' object"""
        if self.isEmpty():
              raise RuntimeError("No events")

        if self.note_track is not None:
            return self.note_track

        self.note_track = NoteTrack()
        last_onset = None
        stack_count = 0
        for e in self.getEvents():
            onset = float(e[0])
            dur   = float(e[1])
            pitch = float(e[2])
            if last_onset is None:
                tmp_onset = onset
            else:
                tmp_onset = last_onset

            if dur >= duration_threshold:
                self.note_track.append(NoteEvent(pitch, tmp_onset, dur))
                last_onset = None
                stack_count = 0
            else:
                if last_onset is None:
                    last_onset = onset
                else:
                    stack_count += 1
                #print "Filtered duration {}, run #{}".format(dur, stack_count)
              #print nt.last().toString()
        return self.note_track

class SVParseTonyNotesLayer(SVParserBase):
    """ Class for parsing a notes annotation layer (Tony type)
        with annotation.
        Line format:
        0.720000000,328.417,1.978666666,0.787402,1
        <onset (s)>,<pitch (Hz)>,<duration (s)>,<intensity <a.u>, <label>
    """
    def __init__(self, events):
        """ Initialize module """
        SVParserBase.__init__(self, events)

    def getNoteTrack(self, transform_pitch=True):
        """Parses the event list and return 'NoteTrack' object"""
        if self.isEmpty():
            raise RuntimeError("No events")
        nt = NoteTrack()
        for e in self.getEvents():
              onset = float(e[0])
              dur   = float(e[1])
              pitch = float(e[2])
              if float_equal(pitch, 0):
                  continue
              if transform_pitch:
                  pitch = hz_to_midi(pitch)
              label = str(e[3])
              ne = NoteEvent(pitch, onset, dur)
              ne.setValue(label)
              nt.append(ne)
              #print ne
        return nt

class SVParseModulation(SVParserBase):
    """ Class for parsing a modulation (text) layer."""
    modulation = ["fall-off", "vibrato", "bend", "straight", "slide", ""]
    def __init__(self, events, nt):
        """ Initialize module """
        SVParserBase.__init__(self, events)
        self.modulations_short = [v[0:3] for v in self.modulation]
        self.nt = nt

    def _checkModulation(self, value):
        if str(value).lower()[0:3] in self.modulations_short:
            return True
        return False

    def getModulation(self):
        """Parses the event list and return 'Rhythm' object or None"""
        if self.isEmpty():
            #return None
            raise RuntimeError("No events")
        r = Rhythm()
        for e in self.getEvents():
            onset = float(e[0])
            value = ""
            if self._checkModulation(e[1]):
                value = str(e[1])
            #print value
            #else:
            #    print "WARNING: Invalid modulation {} at {}".format(onset, e[1])
            r.append(RhythmEvent(onset, 0, value))
        return r

class SVReader(object):
    """ class for readings SV-project files (which are bzip2'ed XML-files)."""
    def __init__(self, filename, params=None):
        """ Initialize module """

        self.__filename     = filename
        self.__lines        = None
        self.__notetrack    = None
        self.__beattrack    = None
        self.__sectPhrases  = None
        self.__sectForm     = None
        self.__sectChords   = None
        self.__diagnostics  = None
        self.__solo         = None
        self.__melody       = None
        self.__modulations  = None
        self.chord_changes  = None
        if params == None:
            params = SVReaderParams()
        self.params         = params

    def getFilename(self):
        """ Yeah, well, get the Filename """
        return(self.__filename)

    def getBasename(self):
        """ Yeah, well, get the basename """
        return(os.path.basename(self.__filename))

    def setFilename(self, filename):
        """ Yeah, well, set the filename """
        self.__filename = filename

    def setLines(self, lines):
        """ Set content of the file as a list of lines"""
        self.__lines = lines

    def getLines(self):
        """ Set content of the file as a list of lines"""
        return(self.__lines)

    def getLineCount(self):
        """ Returns numer of lines"""
        if self.__lines == None:
            return 0
        return(len(self.__lines))

    def getLine(self, idx):
        """ Returns lines No. idx"""
        len = self.getLineCount()
        if len == 0:
            #raise Exception("Lines are empty!")
            return(None)
        if abs(idx)>(len-1):
            #raise Exception("Given index to high!")
            return(None)
        return(self.__lines[idx].rstrip())

    def getNoteTrack(self):
        return self.__notetrack

    def getModulations(self):
        return self.__modulations

    def getBeatTrack(self):
        return self.__beattrack

    def getPhraseSections(self):
        return self.__sectPhrases

    def getFormSections(self):
        return self.__sectForm

    def getChordsSections(self):
        return self.__sectChords

    def getIFASections(self):
        return self.__sectIFA

    def getMelody(self):
        return self.__melody

    def getSolo(self):
        return self.__solo

    def getDiagnostics(self):
        return self.__diagnostics

    def unzip(self):
        """ Bunzip2 the file """
        bz2Reader = bz2.BZ2File(self.getFilename())
        self.setLines(bz2Reader.readlines())
        return True

    def isEmpty(self):
        return self.getLineCount()==0

    def XMLparse(self):
        """Parses the unzipped SV/XML file and return the a minidom object for further parsing"""
        if self.isEmpty():
            raise RuntimeError("Empty object, nothing to parse, buddy")

        #Note: If default encoding is utf-8, the encoding to UTF-8 doesn't work
        #on  accented e's. No idea, why
        #The problem is due to Music21, which sets the defaultencoding to utf-8
        #We reset the encoding for the time being in music21_adapter
        #but in future version with full music21 support we might need another solution.
        docString = '\n'.join(_.decode("UTF-8") for _ in self.__lines)
        #docString = '\n'.join(str(_) for _ in self.__lines)
        #print(type(docString))
        _illegal_xml_chars_RE = re.compile('[\x00-\x08\x0b\x0c\x0e-\x1F\\uD800-\\uDFFF\\uFFFE\\uFFFF]')
        docString  = _illegal_xml_chars_RE.sub("?", docString)

        xmldoc = minidom.parseString(docString)
        #print(xmldoc)
        return xmldoc

    def extractLayer(self, layer):
        """
            Parses the data sets and model and returns layer
            of type 'layer'
        """
        layer = layer.lower()
        if layer != "notes":
            raise ValueError("Currently only note layer extraction possible")

        try:
            self.unzip()
        except Exception as e:
            raise Exception("Error during unzipping: {}".format(e.args[-1]))

        xmldoc = self.XMLparse()
        data = xmldoc.getElementsByTagName("model")
        if data.length == 0:
            raise ValueError("No models found, got {}".format(data.length))

        #print "No of Models: " + str(data.length)
        models = []
        for i in range(data.length):
            models.append(SVModel(data[i]))
        datasets = {}
        for m in models:
            d = SVDataSet(m)
            if len(d.getId())>0:
                d.parse(xmldoc)
                datasets[d.getType()] = d
        if len(datasets) != data.length-1:
            raise ValueError("Expected {} datasets, got {}".format(data.length, len(datasets)))

        notetrack = None
        try:
            svn = SVParseTonyNotesLayer(datasets['notes'].parse(xmldoc))
            notetrack = svn.getNoteTrack()
        except Exception as e:
            raise RuntimeError("Error parsing note layer: " + e.args[0])
        return notetrack

    def parse(self, diagnostic=False, duration_threshold=0.):
        """
            Parses the data sets and model and return object for
            further bundling
        """

        xmldoc = self.XMLparse()
        data = xmldoc.getElementsByTagName("model")
        if data.length < 4 or data.length > 6:
            raise ValueError("Expected 4 to 6 models, got {}".format(data.length))

        #print "No of Models: " + str(data.length)
        models = []
        for i in range(data.length):
            models.append(SVModel(data[i]))
        datasets = {}
        for m in models:
            #print str(m.getSampleRate()) + " " + m.getMainType() + "/" + m.getSubtype()+ " " + str(m.getDataId())
            d = SVDataSet(m)
            if len(d.getId())>0:
                d.parse(xmldoc)
                datasets[d.getType()] = d
        if len(datasets) != data.length-1:
            raise ValueError("Expected {} datasets, got {}".format(data.length, len(datasets)))
        #parsing notes
        if diagnostic:
            print("Parsing notes...")
        #out of try
        #svn = SVParseNotes(datasets['notes'].parse(xmldoc))
        #svn.getNoteTrack(duration_threshold)
        try:
            svn = SVParseNotes(datasets['notes'].parse(xmldoc))
            self.__notetrack = svn.getNoteTrack(duration_threshold)
        except Exception as e:
            if not  diagnostic:
                raise RuntimeError(" note layer: " + e.args[0])
            else:
                print(("Error during parsing note layer " + e.args[0]))
        if diagnostic:
            print("...okay")


        #parsing phrases
        if diagnostic:
            print("Parsing phrases...")
        try:
            self.__sectPhrases = SVParsePhrases(datasets['phrases'].getRaw(), self.__notetrack).getPhraseSection()
        except Exception as e:
            if not  diagnostic:
                raise RuntimeError(" phrase layer: " + e.args[0])
            else:
                print(("phrase layer " + e.args[0]))
        if diagnostic:
            print("...okay")

        #parsing ideas
        self.__sectIFA = None
        if "IFA" in datasets:
            if diagnostic:
                print("Parsing ideas...")
            #out of try
            try:
                self.__sectIFA = SVParseIdeas(datasets['IFA'].getRaw(), self.__notetrack).getIFASections()
            except Exception as e:
                if not  diagnostic:
                    raise RuntimeError(" IFA layer: " + e.args[0])
                else:
                    print(("IFA layer: " + e.args[0]))
            if diagnostic:
                print("...okay")

        #parsing modulation
        if diagnostic:
            print("Parsing modulation...")
        try:
            self.__modulations = SVParseModulation(datasets['modulation'].getRaw(), self.__modulations).getModulation()
        except Exception as e:
            if not  diagnostic:
                pass
                #print "WARNING: Parsing Modulation layer: " + e.args[0]
                #raise RuntimeError(" Modulation layer: " + e.args[0])
            else:
                print("Could not find modulation layer.")
        if diagnostic:
            print("...okay")

        #parsing chord/form/signatures
        if diagnostic:
            print("Parsing chord and forms...")
        #OUT OF TRY
        #spf = SVParseChordForm(datasets['beats'].getRaw(), svn.getNoteTrack())
        #self.__beattrack, self.__sectForm, self.__sectChords, self.chord_changes = spf.parse(diagnostic)
        #spf = SVParseChordForm(datasets['beats'].getRaw(), svn.getNoteTrack())
        #self.__beattrack, self.__sectForm, sc1, self.chord_changes = spf.parse()
        #self.__beattrack, self.__sectForm, sc2, self.chord_changes = spf.parse2()
        #print "sc1", sc1
        #print "sc2", sc2

        try:
            spf = SVParseChordForm(datasets['beats'].getRaw(), self.__notetrack)
            self.__beattrack, self.__sectForm, self.__sectChords, self.chord_changes = spf.parse(diagnostic)
        except Exception as e:
            if not  diagnostic:
                raise RuntimeError(" chord form layer: " + e.args[-1])
            else:
                print(("Error during parsing chord form layer: " + e.args[-1]))
        if diagnostic:
            print("...okay")

        if diagnostic:
            print("Done parsing.")
        return self

    def bundle(self, params=None, normalize=None, diagnostic=None, strictly_monophonic=None, duration_threshold=None):
        """
            Evertyhing together: Unzipping, data extraction, parsing,
            bundling
        """

        if params is None:
            params = self.params
        
        if normalize is None:
            normalize = params.getValue("normalize")
        if diagnostic is None:
            diagnostic = params.getValue("diagnostic")
        if strictly_monophonic is None:
            strictly_monophonic = params.getValue("strictly_monophonic")
        if duration_threshold is None:
            duration_threshold = params.getValue("duration_threshold")

        self.__diagnostics = []
        try:
            self.unzip()
        except Exception as e:
            raise Exception("Error during unzipping: {}".format(e.args[-1]))
        #OUT OF TRY
        #self.parse(diagnostic)
        try:
            self.parse(diagnostic, duration_threshold)
        except Exception as e:
            #raise Exception("Error during parsing: {}".format(e.args[0]))
            raise Exception("Error during parsing {}".format(e.args[-1]))
        if diagnostic:
            self._beatDiagnostics(self.beattrack.getOnsets())
            self._noteDiagostics(self.notetrack)
        #print self.beattrack
        #out of try

        if strictly_monophonic:
            if diagnostic or not diagnostic:
                 print("Enforcing monophony...")
            self.notetrack.monophonize()

        ma = MetricalAnnotator(self.notetrack, self.beattrack, params["flexq"])
        mg = ma.annotate()
        if diagnostic:
            print("Calculating metrical annotation with params: {}...".format(params["flexq"]))
        try:
            mg = ma.annotate()
        except Exception as e:
            msg = "Error during metrical annotation: {}".format(e.args[0])
            raise Exception(msg)

        if diagnostic:
            print("Annotating meter...")
        self.__melody = self.notetrack.annotateMeter(mg)
        if diagnostic:
            print("...done.")

        if diagnostic:
            print("Annotating modulation...")
        #out of try
        try:
            self.__melody = self.__melody.annotateModulation(self.__modulations)
        except Exception as e:
            msg = "Error during modulation annotation: {}".format(e.args[0])
            raise Exception(msg)

        if diagnostic:
            print("...done.")

        try:
            formEvents = self.getFormSections().getValues(eventBased=True)
        except Exception as e:
            if diagnostic:
                print("Something wrong with the form section.")
            raise(e)
        try:
            chordEvents = self.getChordsSections().getValues(eventBased=True)
        except Exception as e:
            if diagnostic:
                print("Something wrong with the chord section.")
            raise(e)
        try:
            phraseIDs = self.getPhraseSections().getValues(eventBased=True)
        except Exception as e:
            if diagnostic:
                print("Something wrong with the phrase section.")
            raise(e)

        if self.__sectIFA != None:
            try:
                IFAEvents = self.getIFASections().getValues(eventBased=True)
            except Exception as e:
                if diagnostic:
                    print("Something wrong with the IFA section.")
                raise(e)

        if len(phraseIDs) != len(self.__melody):
            startID = self.getPhraseSections()[0].getStartID()
            endID   = self.getPhraseSections()[-1].getEndID()
            raise RuntimeError("Expected {} phrase ids, got {}. (Start: {}, end:{})".format(len(self.__melody), len(phraseIDs), startID, endID))
        if len(chordEvents) != len(self.__melody):
            startID = self.getChordsSections()[0].getStartID()
            endID   = self.getChordsSections()[-1].getEndID()
            raise RuntimeError("Expected {} chord events, got {}. (Start: {}, end:{})".format(len(self.__melody), len(chordEvents), startID, endID))
        if len(formEvents) != len(self.__melody):
            startID = self.getFormSections()[0].getStartID()
            endID   = self.getFormSections()[-1].getEndID()
            raise RuntimeError("Expected {} form events, got {}. (Start: {}, end:{})".format(len(self.__melody), len(formEvents), startID, endID))
        if self.__sectIFA != None and len(IFAEvents) != len(self.__melody):
            startID = self.getIFASections()[0].getStartID()
            endID   = self.getIFASections()[-1].getEndID()
            raise RuntimeError("Expected {} IFA events, got {}. (Start: {}, end:{})".format(len(self.__melody), len(IFAEvents), startID, endID))

        if normalize:
            if diagnostic:
                print("Normalizing...")
            self.melody.standardize(force=True)
        if diagnostic:
            print("...done.")
        finalevents  = []
        si = SoloInfo(chord_changes=self.chord_changes)

        smd = SoloMetaData(soloInfo=si)
        self.__solo = Solo(melody=self.melody, metadata=smd, beatTrack=self.beattrack, phrases=self.getPhraseSections(), form=self.getFormSections(), chorus=None, chords=self.getChordsSections(), keys=None, ideas=self.getIFASections())

        try:
            self.__solo.setChorusFromForm()
        except Exception as e:
            try:
                self.__solo.setSingleChorus()
            except:
                raise RuntimeError("Non-standard form: {}".format(e.args[0]))
        for i in range(len(self.__melody)):
            e = self.__melody[i]
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
                  'modulation':e.getAnnotatedF0Modulation(),\
                  'phrase':phraseIDs[i],\
                  'chord':str(chordEvents[i]),\
                  'form':str(formEvents[i])
                  }
            finalevents.append(row)
        if diagnostic:
            print("Done bundling.")
        return finalevents

    def _addDiagnostic(self, onset, value):
        if self.__diagnostics== None:
            self.__diagnostics= []
        self.__diagnostics.append([onset, value])
        return self.__diagnostics

    def _noteDiagostics(self, notetrack, thresh = .03):
        onsets= notetrack.getOnsets()
        durs = notetrack.getDurations()
        pitches = notetrack.getPitches()
        iois = diff(onsets)
        suspects = []
        overlaps = []
        doubles  = []
        for i in range(len(iois)):
            if iois[i]<=thresh:
                suspects.append(s_to_hms(onsets[i])+" ("+ str(s_to_ms(iois[i], 1)) + "ms)")
                self._addDiagnostic(onsets[i], "Short")
            if durs[i]>iois[i]:
                rel_diff = (durs[i]-iois[i])/iois[i]
                if rel_diff>.1:
                    overlaps.append(s_to_hms(onsets[i+1])+" (" + str(s_to_ms(durs[i]-iois[i], 1)) + "ms)")
                    #self._addDiagnostic(onsets[i+1], "Overlap")
            if (durs[i]+thresh) >= iois[i] and pitches[i] == pitches[i+1]:
                    doubles.append(s_to_hms(onsets[i+1])+" (" + str(pitches[i]) + ")")
                    self._addDiagnostic(onsets[i+1], "Doublet")

        print("Note diagnostics:")
        print("===============")
        if len(suspects)>0:
            print("Very short events at: {}\n".format("|".join(suspects)))
        print("Overlapping durations at: {}\n".format("|".join(overlaps)))
        print("Doubles at: {}\n".format("|".join(doubles)))

    def _beatDiagnostics(self, beats):
        iois = diff(beats)
        mean_ioi = mean(iois)
        sd_ioi = sd(iois)
        min_ioi = min(iois)
        max_ioi = max(iois)
        range_ioi = max_ioi-min_ioi
        outliers = []
        for i in range(len(iois)):
            if iois[i]<=mean_ioi-1.96*sd_ioi or iois[i]>=mean_ioi+1.96*sd_ioi:
                outliers.append(s_to_hms(beats[i]))
                self._addDiagnostic(beats[i], "Beat outlier")

        print("\nBeat statistics:")
        print("===============")
        print("Mean: {} ms, SD = {} ms".format(s_to_ms(mean_ioi), s_to_ms(sd_ioi)))
        if sd_ioi>.25*mean_ioi:
            print("ATTENTION: Standard deviation suspiciously high!")
        print("Min: {}, max= {}, range: {}".format(s_to_ms(min_ioi), s_to_ms(max_ioi), s_to_ms(range_ioi)))
        print("Two-sig outlier onsets at: {}\n".format("|".join(outliers)))

    def getPath(self):
        """ Get Path Portion of Filename"""
        return os.path.dirname(self.__filename)

    filename        = property(getFilename, setFilename)
    path            = property(getPath)
    lines           = property(getLines, setLines)
    notetrack       = property(getNoteTrack)
    beattrack       = property(getBeatTrack)
    phrasesections  = property(getPhraseSections)
    formsections    = property(getFormSections)
    chordsections   = property(getChordsSections)
    melody          = property(getMelody)
    solo            = property(getSolo)
    diagnostics     = property(getDiagnostics)
