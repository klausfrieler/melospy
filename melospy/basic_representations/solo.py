""" Class for Solos"""
import numpy as np

from melospy.basic_representations.accents import *
from melospy.basic_representations.annotated_beat_track import *
from melospy.basic_representations.chord_scale_theory import *
from melospy.basic_representations.idea_filter import *
from melospy.basic_representations.jm_util import find_first_gt, find_last_lt, try_clone
from melospy.basic_representations.section_list import *
from melospy.basic_representations.solo_event import *
from melospy.basic_representations.solo_meta_data import *
from melospy.basic_representations.song import *


class Solo(Song):
    """ Class representing Solos"""
    exportTypes = {
        'modulation': ['modulation', 'mod'],
        'beats': ['beats', 'beattrack'],
        'ch':  ['ch', 'chords', 'chord-symbols', 'chord-symbols'],
        'che': ['che', 'chord-events'],
        'cp': ['cp', 'chord-pitch', 'chordal-pitch', 'chordal-pitch'],
        'cpc': ['cpc', 'chord-pc', 'chordal-pc', 'chordal-pitch-class'],
        'tpc': ['tpc', 'tonal-pc', 'tonal-pitch-class'],
        'tdpc': ['tdpc', 'tonal-dpc', 'tonal-diatonic-pitch-class'],
        'cdpc':['cdpc', 'chord-dpc', 'chordal-dpc', 'chordal-diatonic-pitch-class'],
        'cdpcx':['cdpcx', 'chord-dpc-ext', 'chordal-dpc-ext', 'chordal-diatonic-pitch-class-ext'],
        'cpt': ['cpt', 'chord-pt', 'chordal-pt',  'chordal-pitch-type'],
        'csc': ['csc', 'chord-scale-comp', 'chordal-scale-comp', 'chordal-scale-compatibility'],
        'bsc': ['bsc', 'best-chord-scale'],
        'phrid': ['phrid', 'phrase-ids', 'phraseids'],
        'phrbd': ['phrbd', 'phrase-boundaries', 'phrasebounds'],
        'chorusid': ['chorusid', 'chorus-ids', 'chorusids'],
        'form': ['form', 'formlabels', 'form-labels', 'formnames', 'form-names', 'formtags', 'form-tags'],
        'ideas': ['ideas'],
        'idea_durs': ['idea_durations', 'idea_durs'],
        'chtype': ['chtype', 'chord-types', 'chordtypes'],
        'accent': ['accent', 'marker'],
        'mcm': ['mcm', 'metrical-circle-map'],
        'swing-shapes': ['swing-shapes'],
        'nom-onsets': ['nom-onsets', "nominal-onsets", "quantized-onsets"],
        'meta': ['meta']
    }

    def __init__(self, melody=None, metadata=None, beatTrack=None, phrases=None, form=None, chorus=None, chords=None, keys=None, ideas=None):
        self.setMelody(melody)
        self.setMetadata(metadata)
        self.setBeatTrack(beatTrack)
        self.setPhraseSections(phrases)
        self.setFormSections(form)
        self.setChorusSections(chorus)
        self.setChordSections(chords)
        self.setKeySections(keys)
        self.setIFASections(ideas)

    def clone(self):
        mel = Melody.clone(self)
        return Solo(mel,\
            try_clone(self.getMetadata()),\
            try_clone(self.getBeatTrack()),\
            try_clone(self.getPhraseSections()),\
            try_clone(self.getFormSections()),\
            try_clone(self.getChorusSections()),\
            try_clone(self.getChordSections()),\
            try_clone(self.getKeySections()),
            try_clone(self.getIFASections())
            )

    def setMelody(self, melody):
        if isinstance(melody, Melody) or melody == None:
            Melody.__init__(self, melody)
        else:
            raise TypeError("Expected 'Melody' object or 'None', got {}".format(type(melody)))
        return self

    def getMetadata(self):
        try:
            smd = self.__metadata
        except:
            smd = None
        if smd == None:
            try:
                smd = self.__dict__["esacinfo"]
            except:
                smd = None
        return smd

    def setMetadata(self, val):
        self.__metadata = try_clone(val)
        return self

    def getBeatTrack(self):
        return self.__beattrack

    def setBeatTrack(self, val):

        if isinstance(val, Rhythm) or val == None:
            self.__beattrack = try_clone(val)
        else:
            raise TypeError("Expected 'Rhythm' object or 'None'!")
        return self

    def getSwingShapes(self, average=False, max_div=4):
        """
            Returns a list of all swing shapes for beats with binary
            division, swing shape is the loudness difference between first
            and second eighth.
        """
        swingShapes= []
        bcfp = BeatChunkFilterPattern(pattern="full_swing")
        if max_div < 2:
            max_div = 2
        bcfd = BeatChunkFilterDivision(divisions=list(range(2, max_div+1)))
        bcfc = BeatChunkFilterCombi([bcfp, bcfd])
        chunks= self.getBeatChunksRaw(chunk_filter=bcfc, as_indices=False)
        for bc in chunks:
            if len(bc) != 2 and len(bc) != 3:
                raise RuntimeError("Beat chunk of invalid length {} found.".format(len(bc)))
            try:
                swingShape =  bc[0].getLoudnessField("median")-bc[len(bc)-1].getLoudnessField("median")
                #print "SwingShape: {}".format(swingShape)
                swingShapes.append(swingShape)
            except:
                continue
        if average and len(swingShapes)>0:
            swingShapes = mean(swingShapes)
        return swingShapes


    def getBarSequence(self, start, end=None):
        """
            Export events with bar numbers from 'start' to 'end' as Solo-object
        """
        idz = []
        if end == None:
            end = start

        if end < start:
            raise ValueError("'End' {} must be greater than 'start' {}".format(start, end))

        for i in range(len(self)):
            if self[i].getBar() >= start and self[i].getBar() <= end:
                idz.append(i)
        if len(idz) == 0:
            return []
        return self.slice(min(idz), max(idz))

    def getBarsAsSectionList(self):
        old_bar = None
        sect_list = SectionList("BAR")
        start = 0
        for i in range(len(self)):
            cur_bar = self[i].getBar()
            if cur_bar != old_bar or i == len(self)-1:
               if old_bar != None:
                   sect = Section("BAR", old_bar, start, i-1)
                   sect_list.append(sect)
                   start = i
               old_bar = cur_bar
        return sect_list

    def copySections(self, s, start=None, end=None):

        if start == None:
            start = 0
        if end == None:
            end = len(s)
        try:
            newPhrases = s.getPhraseSections().clone().truncate(start, end, True)
            self.setPhraseSections(newPhrases)
        except:
            pass
        try:
            newChords = s.getChordSections().clone().truncate(start, end, True)
            self.setChordSections(newChords)
        except:
            pass

        try:
            #print s.getChorusSections()
            newChorus = s.getChorusSections().clone().truncate(start, end, True)
            self.setChorusSections(newChorus)
        except:
            pass

        try:
            newKeys = s.getKeySections().clone().truncate(start, end, True)
            self.setKeySections(newKeys)
        except:
            pass

        try:
            newForms = s.getFormSections().clone().truncate(start, end, True)
            self.setFormSections(newForms)
        except:
            pass
        try:
            newIdeas= s.getIFASections().clone().truncate(start, end, True)
            self.setIFASections(newIdeas)
        except:
            pass

        return self

    def _sliceBeatTrack(self, start, end, to_full_bar=True):
        """slice Beat track between start and end"""
        return self.__beattrack.slice(start, end, to_full_bar)

    def slice(self, start, end, clone=True):
        """
            Slice Solo object between start and end and return clone.
            Adjust sections and beat track accordingly.
        """
        #print "slice"
        s = Solo()

        if end == None:
            end = start

        if end < start:
            raise ValueError("'End' {} must greater than 'start' {}".format(start, end))

        if end >= len(self):
            raise ValueError("'End' {} must smaller than length {}".format(end, len(self)))

        if start < 0:
            raise ValueError("'Start' {} must be positive".format(start))

        for i in range(start, end+1):
            s.append(self[i].clone())
        s.copySections(self, start, end)
        try:
            s.__beattrack = self._sliceBeatTrack(self[start].onsetSec, self[end].onsetSec)
        except:
            s.__beattrack  = None
        #s.__beattrack.calcSignatureChanges(in_form=False)
        s.setMetadata(self.getMetadata())
        return s

    def splitBySections(self, sections):
        s = None
        for sect in sections:
            if s == None:
                s = self.slice(sect.startID, sect.endID)
            else:
                s.concat(self.slice(sect.startID, sect.endID))
        return s

    def concat(self, solo):
        #print "Solo.concat()"
        Melody.concat(self, solo)

        newPhrases = solo.getPhraseSections().clone()
        offset = self.getPhraseSections()[-1].getValue()+1
        for i in range(len(newPhrases)):
            newPhrases[i].setValue(i + offset)

        try:
            newPhrases = self.getPhraseSections().concat(newPhrases)
            self.setPhraseSections(newPhrases)
        except:
            pass

        try:
            newChords = self.getChordSections().concat(solo.getChordSections().clone())
            self.setChordSections(newChords)
        except:
            pass

        try:
            newKeys = self.getKeySections().concat(solo.getKeySections().clone())
            self.setKeySections(newKeys)
        except:
            pass

        #arbitrary slices are very likely to destroy form and chorus integrity
        #so we don't check for them
        try:
            newForms = self.getFormSections().concat(solo.getFormSections().clone(), withCheck=False)
            self.setFormSections(newForms)
        except:
            pass

        try:
            newIdeas = self.getIFASections().concat(solo.getIdeaSections().clone(), withCheck=False)
            self.setIFASections(newIdeas)
        except:
            pass

        try:
            newChoruses= solo.getChorusSections().clone()
            self.getChorusSections().concat(newChoruses, withCheck=False)
        except:
            pass

        return self

    def concatSlices(self, idz):
        """
            Find consecutive slices from a list of indices,
            glue them together to o return a Solo-object
        """
        if len(idz) == 0:
            return None
        #s = Solo()
        slices = []
        slices.append(idz[0])
        for i in range(1, len(idz)-1):
            if idz[i+1] != idz[i] + 1:
                slices.append(idz[i])
                slices.append(idz[i+1])
        slices.append(idz[-1])
        assert len(slices) % 2 == 0
        s = self.slice(slices[0], slices[1])
        for i in range(2, len(slices), 2):
            s.concat(self.slice(slices[i], slices[i+1]))

        return s

    def getPhrase(self, phraseID):
        ret = []
        #if self.__phraseIDs == None:
        #    return None
        for i in range(len(self)):
            if self.__phraseIDs[i] == phraseID:
                ret.append(i)
        if len(ret)>0:
            return self.slice(min(ret), max(ret))
        else:
            return None

    def getPhraseSections(self):
        return self.__phrases

    def setPhraseSections(self, val):
        #self.__phrases = None
        #self.__phraseIDs = None
        if val == None or (isinstance(val, SectionList) and val.getType() == 'PHRASE'):
            if self._checkSectionIntegrity(val):
                self.__phrases   = try_clone(val)
                self._setPhraseIDs(self.__phrases)
            else:
                raise ValueError("Phrase list does not match melody events")
        else:
            raise TypeError("Expected 'SectionList<'PHRASES>' object!")
        return self

    def getPhraseIDs(self):
        return self.__phraseIDs

    def _setPhraseIDs(self, val):
        if val:
            self.__phraseIDs = val.getValues(eventBased=True)
            if len(self.__phraseIDs) != len(self):
                startID = self.__phrases()[0].getStartID()
                endID   = self.__phrases()[-1].getEndID()
                raise RuntimeError("Expected {} phrase ids, got {}. (Start: {}, end:{})".format(len(self.__melody), len(phraseIDs), startID, endID))
        else:
            self.__phraseIDs = None

    def hasIntro(self):
        if self.__formEvents == None or len(self.__formEvents)==0:
            return False
        if self.__formEvents[0].getLetter() == "I":
            return True
        return False

    def _formPartsChorusIDs(self):
        ret = []
        if self.__form == None or len(self.__form) == 0:
            return ret

        c_id = 0
        found_form_start = False
        for fe in self.__form:
            form = fe.getValue()
            if len(ret) == 0 and form.getLetter() == "I":
                ret.append(-1)
                continue
            if form.getLabel() == "A1":
                c_id += 1
                found_form_start = True
            if form.getLetter() != "I" and not found_form_start:
                #dirty hack
                #if another form part except I was found before first A1,
                #assume incomplete form and start form there
                c_id += 1
                found_form_start = True
            ret.append(c_id)
        return ret

    def patchStartTime(self, start_time):
        self.getMetadata().setField("solostart", start_time)

    def getSection(self, sect_type):
        sect_type == sect_type.upper()
        if sect_type == "PHRASE":
            return self.__phrases
        elif sect_type == "FORM":
            return self.__form
        elif sect_type=="CHORUS":
            return self.__chorus
        elif sect_type == "CHORD":
            return self.__chords
        elif sect_type == "IDEA":
            return self.__IFA
        elif sect_type == "BAR":
            return self.getBarsAsSectionList()
        else:
            raise ValueError("Unknown section type:{}".format(sect_type))
        return None

    def getFormPart(self, formID, chorus_id=None, exact=True):
        idz = []
        if self.__formEvents == None or len(self.__formEvents) == 0:
            return None
        if chorus_id != None and (self.__chorusIDs == None or len(self.__chorusIDs) == 0):
                raise ValueError("No chorus annotation available!")

        try:
            formID = str(formID)
        except Exception:
            pass
        for i in range(len(self)):
            chorus_condition =  self.__chorusIDs[i] == chorus_id if chorus_id != None else True
            #print "CC:{}, formID:{}, I:{}, form[i]:{}, ci:{}, chorus[i]:{}".format(chorus_condition, formID, i, self.__formEvents[i].getLabel(), chorus_id, self.__chorusIDs[i])
            if exact:
                if self.__formEvents[i].getLabel() == formID and chorus_condition:
                    idz.append(i)
            else:
                if self.__formEvents[i].getLetter() == formID and chorus_condition:
                    idz.append(i)
        if len(idz) == 0:
            return None
        #s = Solo()
        #print "FormID: {}, chorus_id:{}, #idz:{}, idz_min:{}, idz_max:{}".format(formID, chorus_id, len(idz), idz[0], idz[-1])
        return self.concatSlices(idz)

    def getIdeaSlices(self, idea_type=None, aux_id=None, with_labels=False):
        if self.__IFA == None:
            return []
        ret = []

        if idea_type == None or idea_type == "":
            if with_labels:
                tmp = []
                ids = self.getIFASections()
                for sect in ids:
                    tmp.append((self.slice(sect.startID, sect.endID), sect.value))
            else:
                tmp = self.getSegments("idea")

            return tmp
        #print idea_type
        #IT = Idea(idea_type)
        try:
            IT = Idea(idea_type)
            cond = "idea"
        except:
            IT = str(idea_type)
            cond = "string"
        #print IT, type(IT), cond
        for k, sect in enumerate(self.__IFA):
            #print "{}, {} ({})".format(k, sect.value, aux_id)
            #print "CONDITION", cond, IT, sect.value, sect.value.type_list()
            if aux_id is not None and k != aux_id:
                continue
            if (cond == "idea" and IT.mainly_equal(sect.value)) or str(IT).lower() in sect.value.type_list():
                if with_labels:
                    ret.append((self.slice(sect.startID, sect.endID), sect.value))
                else:
                    ret.append(self.slice(sect.startID, sect.endID))
        #print len(ret)
        return ret

    def getFormSections(self):
        return self.__form

    def setFormSections(self, val):
        #self.__form = None
        #self.__formEvents = None
        if  val == None or (isinstance(val, SectionList) and val.getType() == 'FORM'):
            if self._checkSectionIntegrity(val):
                self.__form = try_clone(val)
                self._setFormEvents(self.__form)
            else:
                raise ValueError("Form list does not match melody events")
        else:
            raise TypeError("Expected 'SectionList<'FORM>' object!")
        return self

    def getFormEvents(self):
        return self.__formEvents

    def _setFormEvents(self, val):
        if val:
            self.__formEvents= val.getValues(eventBased = True)
            #print [str(f) for f in self.__formEvents]
            if len(self.__formEvents) != len(self):
                startID = self.__form()[0].getStartID()
                endID   = self.__form()[-1].getEndID()
                raise RuntimeError("Expected {} form events, got {}. (Start: {}, end:{})".format(len(self.__melody), len(phraseIDs), startID, endID))
        else:
            self.__formEvents = None

    def getChorus(self, chorusID):
        ret = []
        if self.__chorusIDs== None:
            return None
        for i in range(len(self.__chorusIDs)):
            if self.__chorusIDs[i] == chorusID:
                ret.append(i)
        #if (chorusID==6):
            #print "*-"*40
        #    print self.getChorusSections()
        #    print min(ret), max(ret), len(self)
        #    print self.slice(min(ret), max(ret)).getChorusSections()
        if len(ret)>0:
            return self.slice(min(ret), max(ret))
        else:
            return None

    def patchChorusSections(self, val):
        startID = val.getStartID()
        newChorusList = SectionList("CHORUS")
        if startID>0:
            introChorus = Section("CHORUS", val=-1, start=0, end=startID-1)
            newChorusList.append(introChorus)
            #print "Added intro chorus:\n", introChorus
        newChorusList.concat(val)
        endID   = val.getEndID()
        if endID<(len(self)-1):
            outChorus = Section("CHORUS", val=-1, start=endID+1, end=len(self)-1)
            newChorusList.append(outChorus)
            #print "Added outro chorus:\n", introChorus
        #print "Patched: \n", newChorusList
        return newChorusList

    def getChorusSections(self):
        return self.__chorus

    def setChorusSections(self, val):
        #self.__chorus = None
        #self.__chorusIDs= None
        if  val == None or (isinstance(val, SectionList) and val.getType() == 'CHORUS'):
            if not self._checkSectionIntegrity(val):
                val = self.patchChorusSections(val)
            self.__chorus = try_clone(val)
            self._setChorusIDs(self.__chorus)
            #else:
            #    raise ValueError("Section does not match melody events")
        else:
            raise TypeError("Expected 'SectionList<'CHORUS>' object!")
        return self

    def setChorusFromForm(self):
        """Calculates ChorusSection from FormSection"""
        try:
            if self.__form == None or len(self.__form) == 0:
                raise ValueError("No FormSectionList set")
        except AttributeError:
            raise ValueError("No form SectionList set")

        idlist = []
        for f in self.__form:
            if f.getValue().getLabel() == "A1":
                #print "Found: " + str(f.getStartID())
                idlist.append(f.getStartID())

        n = len(idlist)

        chorusList = SectionList("CHORUS")
        for i in range(n-1):
            s = Section("CHORUS", i+1, idlist[i], idlist[i+1]-1)
            chorusList.append(s)

        s = Section("CHORUS", n, idlist[n-1], self.__form.getEndID())
        chorusList.append(s)
        self.setChorusSections(chorusList)
        return self

    def setSingleChorus(self):
        """
            Force one single chorus for whole solo
            to cope with unusual forms or fragmented solos
        """
        chorusList = SectionList("CHORUS")
        s = Section("CHORUS", 1, 0, len(self)-1)
        chorusList.append(s)

        self.setChorusSections(chorusList)
        return self

    def setSingleForm(self, start_position=0):
        """
            Force one form part for whole solo
        """
        if isinstance(start_position, MetricalPosition):
            pos = self.find_first_greater_than(start_position)
            if pos < 0:
                raise ValueError("Could not determine start position for {}".format(start_position))
            else:
                start_position = pos
        formList = SectionList("FORM")
        #print "Setting single form with ", start_position
        if start_position != 0:
            s = Section("FORM", FormName("I1"), 0, start_position-1)
            formList.append(s)
            s = Section("FORM", FormName("A1"), start_position, len(self)-1)
            formList.append(s)
        else:
            s = Section("FORM", FormName("A1"), 0, len(self)-1)
            formList.append(s)
        #print formList
        self.setFormSections(formList)
        return self

    def getChorusIDs(self):
        return self.__chorusIDs

    def _setChorusIDs(self, val):
        if val:
            self.__chorusIDs = val.getValues(eventBased=True)
        else:
            self.__chorusIDs = None

    def getChorusCount(self, threshold=32):
        if self.__chorus == None or len(self.__chorus) == 0:
            return 0
        ids = self.__chorus.getValues()
        count = max(ids)
        #print "Found ", count
        numEventsLastChorus = self.__chorus[-1].eventCount()
        #print "numEventsLastChorus", numEventsLastChorus
        if numEventsLastChorus <= threshold and count > 1:
            count = count -1

        return count

    def _chordSectionIDfromEventId(self, ev_id):
        if self.__chords == None or len(self.__chords) == 0:
            return None

        for i, ch in enumerate(self.__chords):
            #print i, ch.startID
            if ch.startID <= ev_id and ev_id <= ch.endID:
                return i
        return None

    def getEventsByChord(self, chord, aux_id=None):

        idz = []
        if not isinstance(chord, Chord):
            try:
                chord = Chord(chord)
            except:
                raise ValueError("Could not coerce {} to Chord-object".format(chord))

        for i in range(len(self)):
            aux_cond = self._chordSectionIDfromEventId(i) == aux_id if aux_id != None else True
            #print "Aux_cond: {}, aux_id:{}, i:{}, chord_id:{}".format(aux_cond, aux_id, i, self._chordSectionIDfromEventId(i))
            if self.__chordEvents[i] == chord and aux_cond:
                idz.append(i)
        return self.concatSlices(idz)

    def getChordSections(self):
        return self.__chords

    def setChordSections(self, val):
        #self.__chords = None
        #self.__chordEvents = None
        if val == None or (isinstance(val, SectionList) and val.getType() == 'CHORD'):
            if self._checkSectionIntegrity(val):
                self.__chords = val
                self._setChordEvents(val)
            else:
                raise ValueError("Chord list does not match melody events")
        else:
            raise TypeError("Expected 'SectionList<'CHORD>' object!")
        return self


    def getChordEvents(self):
        return self.__chordEvents

    def _setChordEvents(self, val):
        if val:
            self.__chordEvents = val.getValues(eventBased = True)
            if len(self.__chordEvents) != len(self):
                startID = self.__chords()[0].getStartID()
                endID   = self.__chords()[-1].getEndID()
                raise RuntimeError("Expected {} chord events, got {}. (Start: {}, end:{})".format(len(self.__melody), len(phraseIDs), startID, endID))
        else:
            self.__chordEvents = None

    def getEventsByKey(self, key):
        idz = []
        if not isinstance(key, Key):
            try:
                key = Key(key)
            except:
                raise ValueError("Could not coerce {} to Key-object".format(key))

        for i in range(len(self)):
            if self.__keyEvents[i] == key:
                idz.append(i)
        if len(idz) == 0:
            return None
        #s = Solo()
        return self.concatSlices(idz)

    def getKeySections(self):
        return self.__keys

    def setKeySections(self, val):
        #self.__keys = None
        #self.__keyEvents = None
        if val == None or (isinstance(val, SectionList) and val.getType() == 'KEY'):
            if self._checkSectionIntegrity(val):
                self.__keys = val
                self._setKeyEvents(val)
            else:
                raise ValueError("Key list does not match melody events")
        else:
            raise TypeError("Expected 'SectionList<'KEY>' object!")
        return self

    def getKeyEvents(self):
        return self.__keyEvents

    def _setKeyEvents(self, val):
        #print "Called _setKeyEvents with ", val
        if val:
            self.__keyEvents = val.getValues(eventBased = True)
            if len(self.__keyEvents) != len(self):
                startID = self.__keys()[0].getStartID()
                endID   = self.__keys()[-1].getEndID()
                raise RuntimeError("Expected {} key events, got {}. (Start: {}, end:{})".format(len(self.__melody), len(phraseIDs), startID, endID))
        else:
            self.__keyEvents = None

    def getIFASections(self):
        return self.__IFA

    def setIFASections(self, val):
        #self.__IFA = None
        #self.__IFAEvents = None
        if  val == None or (isinstance(val, SectionList) and val.getType() == 'IDEA'):
            if self._checkSectionIntegrity(val):
                self.__IFA = try_clone(val)
                self._setIFAEvents(self.__IFA)
            else:
                raise ValueError("Idea list does not match melody events")
        else:
            raise TypeError("Expected 'SectionList<'IDEA>' object!")
        return self

    def getIFAEvents(self):
        return self.__IFAEvents

    def _setIFAEvents(self, val):
        if val:
            self.__IFAEvents= val.getValues(eventBased=True)
            #print "\n".join([str(f) for f in self.__ideaEvents])
            if len(self.__IFAEvents) != len(self):
                startID = self.__IFA()[0].getStartID()
                endID   = self.__IFA()[-1].getEndID()
                raise RuntimeError("Expected {} IFA events, got {}. (Start: {}, end:{})".format(len(self.__melody), len(phraseIDs), startID, endID))
        else:
            self.__IFAEvents = None

    def _checkSectionIntegrity(self, sect):
        if sect == None:
            #be nice to your user
            return True
        if sect.getStartID() == 0 and sect.getEndID() == (len(self)-1):
            return True
        return False

    def hasIFASections(self):
        try:
            _ = self.getIFASections()
        except:
            return False
        return True

    def _getAnnotationList(self, listSections = ["phrases", "form", "chords", "chorus", "keys", "IFA"]):
        sections = []
        nEvents = len(self.getEvents())
        for sect in listSections:
            try:
                anno = eval("self." + sect + ".getValues(eventBased=True)")
            except:
                continue
                raise ValueError("Invalid section name: " + sect)
            if nEvents  != len(anno):
                raise RuntimeError("Inconsistent solo object. Number of events and of " + sect + " list do not match")
            sections.append(anno)
        rows = []
        for i in range(nEvents):
            rows.append([a[i] for a in sections])
        return rows

    def annotationAsString(self, listSections = ["phrases", "form", "chords", "chorus", "keys", "IFA"], sep = ";"):
        if not isinstance(sep, str):
            sep = ";"
        if self.isEmpty():
            raise RuntimeError("No events to annotate, buddy")
        events = self.getEvents()
        s = ""
        annoList = self._getAnnotationList(listSections)
        vals = []
        for i in range(len(events)):
            row  = [str(v) for v in list(events[i].__dict__.values()) if v != None]
            row += [str(v) for v in annoList[i]]
            vals.append(sep.join(row))
        s = "\n".join(vals)
        return s

    def getSpellingContext(self):
        try:
            key = self.getMetadata().getField("key")
            if not isinstance(key, Key):
                key = Key(key)
        except:
            key = Key("C")

        scale_pcs = key.getPitchClasses()
        key_flat = key.onTheFlatSide()

        # print("Key:{}, PCS:{}, key flat:{}".format(key, scale_pcs, key_flat))

        ret  = []
        if self.__chordEvents == None:
            return [key_flat]*len(self)
        for i in range(len(self)):
            chord_flat = True
            found_in_scale = False
            passing = 0
            e = self.__chordEvents[i]
            # print("*"*60)
            # print("spelling context", i, e)
            if e != None and str(e) != "NC":
                chord_flat = e.onTheFlatSide()
                # print("found chord", e, chord_flat)

            if self.pitches[i] % 12 in scale_pcs:
                # print("Found pc {} in key scale{}".format(self.pitches[i] % 12, scale_pcs))
                found_in_scale = True

            if i < (len(self)-1):
                interval = self[i+1].pitch-self[i].pitch
                if interval == 1 or interval == -1:
                    passing = interval
            if found_in_scale:
                tmp = key_flat
            elif passing != 0:
                tmp = True if passing < 0 else False
            else:
                tmp = chord_flat
            # print("pitch: {}, chord:{}, chord_flat:{}, in_scale:{}, passing:{}".format(self.pitches[i] % 12, e, chord_flat, found_in_scale, passing))
            # print("-> flat:{}".format(tmp))
            ret.append(tmp)
        return ret

    def detect_suspicious_chord_changes(self):
        if not self.beattrack:
            return True
        return self.beattrack.detect_suspicious_chord_changes()

    def signature_check(self):
        if not self.beattrack:
            return True
        md_signature = self.getMetadata().getField("signature")
        if not md_signature:
            return True
        bt_signatures = set(self.beattrack.getSignatureList(as_string=True, simplify=True))
        if str(md_signature) in bt_signatures:
                return True
        print("Found inconsistent signatures metadata: {} Beat track:{}".format(md_signature, bt_signatures))
        return False

    def getChordalPitchClasses(self, filterNC=False, circle_factor=1):
        return self.getChordalPitch(filterNC, mod_factor=12, min_pitch=0, circle_factor=circle_factor)

    def getChordalPitch(self, filterNC=False, mod_factor=1, min_pitch=60, circle_factor=1, symmetric=False):
        if self.__chordEvents == None:
            if filterNC:
                return []
            else:
                return [-1]*len(self)
        events = self.getMelodyEvents()
        ret = []
        for i in range(len(events)):
            p = int(round(events[i].getPitch()))
            c = self.__chordEvents[i]
            try:
                cpc  = p - (c.getRootNote().getMIDIPitch() + min_pitch)
                if mod_factor > 1:
                    cpc = (circle_factor * cpc) % mod_factor
                if symmetric and circle_factor > 1 and cpc > mod_factor/2:
                    cpc = cpc - mod_factor
                ret.append(cpc)
                #print "Pitch: {}, Chord: {}, Root:{}, CPC: {}, mod={}, min={}, circ={}".format(p, c, c.rootnote.getPitchClass(), cpc, mod_factor, min_pitch, circle_factor)
            except Exception:
                if not filterNC:
                    ret.append(-1)

        return ret

    def getTonalPitchClasses(self):
        if self.__keyEvents == None :
            return []
        events = self.getMelodyEvents()
        ret = []
        for i in range(len(events)):
            p = int(round(events[i].getPitch()))
            k = self.__keyEvents[i]
            try:
                tpc = (p-k.rootName.getMIDIPitch()) % 12
                #print "Pitch: {}, Key: {}, TPC: {}".format(p, k, tpc)
                ret.append(tpc)
            except Exception:
                ret.append(-1)

        return ret

    def getTonalDiatonicPitchClasses(self, minmaj_map=True, extended=False, filterNC=False):
        if self.__keyEvents == None:
            return []
        events = self.getMelodyEvents()
        ret = []
        for i in range(len(events)):
            p = int(round(events[i].getPitch()))
            c = self.__keyEvents[i].getChordByScaleStep("I")
            if c == None:
                label = ""
            else:
                #print "key, chord:", self.__keyEvents[i], c
                label = c.getDiatonicPitchClass(p, minmaj_map=minmaj_map, extended=extended, filterNC=filterNC)
                #print "pitch:{} in chord:{} gets  label: {}".format(p, c, label)
                #print p, c, label, self.__keyEvents[i]
            ret.append(label)
        return ret

    def getChordalDiatonicPitchClasses(self, minmaj_map=True, extended=False, filterNC=False):
        if self.__chordEvents == None:
            return []
        events = self.getMelodyEvents()
        ret = []
        for i in range(len(events)):
            p = int(round(events[i].getPitch()))
            c = self.__chordEvents[i]
            label = c.getDiatonicPitchClass(p, minmaj_map=minmaj_map, extended=extended, filterNC=filterNC)
            ret.append(label)
        return ret

    def getChordalPitchTypes(self):
        if self.__chordEvents is None:
            return []
        events = self.getMelodyEvents()
        ret = []
        chord_scale_cache = {}
        for i in range(len(events)):
            p = events[i].getPitch()
            chord = self.__chordEvents[i]
            #print type(chord)
            if str(chord) in chord_scale_cache:
                c = chord_scale_cache[str(chord)]
            else:
                c = ChordScale(chord)
                chord_scale_cache[str(chord)] = c
                #print "c=", type(c), c.rootnote
            try:
                cpc = c.classifyPitch(p)
                #print "Pitch: {}, Chord: {}, CPC: {}".format(p, c, cpc)
                ret.append(cpc)
            except Exception:
                ret.append(p)
                raise
        return ret

    def getChordalScaleCompatibility(self, strategy='most'):
        events = self.getMelodyEvents()
        cs = self.getChordSections()
        ret = []
        for sect in cs:
            pcvec = [int(round(events[i].getPitch())) % 12 for i in range(sect.startID, sect.endID+1)]
            scales = ChordScale(sect.value, strategy=strategy).getBestScales()
            maxVal = 0
            comp = 1.
            for s in scales:
                comp = theScaleManager.calcCompatibility(s[0], sect.value.getRootNote(), pcvec, weighted = True)

                if not comp:
                    if sect.value.getRootNote() == None:
                        comp = 1.
                    else:
                        #print "Section: {}, PCVec: {}, Scale: {}".format(sect, pcvec, scales)
                        #print "Comp: {}".format(comp)
                        comp = 0.
                else:
                    comp = float(comp[0])/len(pcvec)
                    if comp > maxVal:
                        maxVal = comp
                #if comp == 0.0:
                    #print "Section: {}, PCVec: {}, Scale: {}".format(sect, pcvec, scales)
                    #print "Comp: {}".format(comp)
            ret.append(round(comp, 4))
        return ret


    def getBestScale(self):
        events = self.getMelodyEvents()
        cs = self.getChordSections()
        ret = []
        for sect in cs:
            pcvec = [int(round(events[i].getPitch())) % 12 for i in range(sect.startID, sect.endID+1)]
            if sect.value.getRootNote() == None:
                ret.append("N/A")
                continue
            ms = theScaleManager.matchScale(pcvec, sect.value)
            #print type( [ms[0][0], ms[0][1]]), [ms[0][0], ms[0][1]]
            #ret.append(ms[0][1])
            #ret.append("{} {}".format(sect.value, ms[0][1]))
            ret.append("{}".format(ms[0][1]))
            val = "-".join(s[1] for s in ms)
            #ret.append("{}".format(ms[0][1]))
            ret.append(val)
            pcvec_nice = sorted([(p-sect.value.getRootNote().getPitchClass()) % 12 for p in pcvec])
            #print "getBestScale", pcvec_nice, sect.value, ret[-1]
        return ret


    def getSegments(self, segmentType):
        #print "getSegments Solo. Type:{}".format(segmentType)
        ret = []
        if segmentType == "bars":
            for i in self.getBarNumbers():
                ret.append(self.getBarSequence(i, i))
        elif segmentType == "phrases":
            for i in set(self.getPhraseIDs()):
                ret.append(self.getPhrase(i))
        elif segmentType == "chords":
            cs = self.getChordSections()
            for i in cs:
                ret.append(self.slice(i.startID, i.endID))
        elif segmentType == "chorus":
            cs = self.getChorusSections()
            for i in cs:
                ret.append(self.slice(i.startID, i.endID))
        elif segmentType == "keys":
            ks = self.getKeySections()
            for i in ks:
                ret.append(self.slice(i.startID, i.endID))
        elif segmentType == "form":
            ks = self.getFormSections()
            for i in ks:
                ret.append(self.slice(i.startID, i.endID))
        elif segmentType == "idea":
            ids = self.getIFASections()
            for i in ids:
                ret.append(self.slice(i.startID, i.endID))
        #print len(ret)
        #print ret
        return ret

    def getExportType(self, exportType):
        spec = exportType.split(".")
        exportType = spec[0]
        subType = None
        if len(spec)>1:
            subType = spec[1]
        for k in list(self.exportTypes.keys()):
            if exportType in self.exportTypes[k]:
                return k, subType
        return None, None

    def simpleExport(self, what, optParam=None):
        #print "Solo.simpleExport called with what: {}, optParam: {}".format(what, optParam)
        try:
            #print "Try {} in projections".format(what)
            val = np.array(self.projection(what))
            #print "{} found in projections".format(what)
            return val
        except:
            pass
        #val = np.array(Melody.simpleExport(self, what, optParam))
        try:
            #print "Try {} (optParam={})in Melody exports".format(what, optParam)
            val = np.array(Melody.simpleExport(self, what, optParam))
            #print "{} found in Melody exports".format(what)
            #print "Solo: {}".format(np.size(val))
            return val
        except:
            #print "XPORT FAILED"
            pass
        #print "{} not found in projections or Melody exports".format(what)
        exportType, subType = self.getExportType(what)
        #print "Export: {}, subType: {}".format(exportType, subType)

        if exportType == "cpc":
            #print "{} found in other exports".format(what)
            filterNC = True
            if optParam != None and optParam.lower() == "keepnc":
                filterNC = False

            cpc  = self.getChordalPitchClasses(filterNC=filterNC)
            #cpc  = self.getChordalPitch(mod_factor=12, circle_factor=7, filterNC=filterNC)
            return np.array(cpc)

        elif exportType == "cp":
            #print "{} found in other exports".format(what)
            filterNC   = get_safe_value_from_dict(optParam, "keepnc", False)
            mod_factor = get_safe_value_from_dict(optParam, "modulo", 1)
            min_pitch  = get_safe_value_from_dict(optParam, "base-pitch", False)
            circ_factor= get_safe_value_from_dict(optParam, "circle", 1)
            symmetric  = get_safe_value_from_dict(optParam, "symmetric", True)

            return np.array(self.getChordalPitch(filterNC=filterNC, mod_factor=mod_factor, min_pitch=min_pitch, circle_factor=circ_factor, symmetric=symmetric))

        elif exportType == "cdpc":
            #print "{} found in other exports".format(what)
            filterNC = True
            if optParam != None and optParam.lower() == "keepnc":
                filterNC = False

            return np.array(self.getChordalDiatonicPitchClasses(filterNC=filterNC))

        elif exportType == "tpc":
            #print "{} found in other exports".format(what)
            return np.array(self.getTonalPitchClasses())

        elif exportType == "tdpc":
            #print "{} found in other exports".format(what)
            return np.array(self.getTonalDiatonicPitchClasses())

        elif exportType == "cdpcx":
            #print "{} found in other exports".format(what)
            filterNC = True
            if optParam != None and optParam.lower()=="keepnc":
                filterNC = False
            return np.array(self.getChordalDiatonicPitchClasses(extended=True, filterNC=filterNC))

        elif exportType == "cpt":
            #print "{} found in other exports".format(what)
            return np.array(self.getChordalPitchTypes())

        elif exportType == "csc":
            #print "{} found in other exports".format(what)
            return np.array(self.getChordalScaleCompatibility())

        elif exportType == "bsc":
            #print "{} found in other exports".format(what)
            return np.array(self.getBestScale())

        elif exportType == "ch":
            #print "{} found in other exports".format(what)
            try:
                if optParam =="types":
                    vals = [c.value.getChordTypeLabel(reduced=True) for c in self.getChordSections()]
                else:
                    vals = [str(c.value) for c in self.getChordSections()]
            except Exception:
                vals = None
            return np.array(vals)

        elif exportType == "beats":
            #print "{} found in other exports".format(what)
            return np.array(self.__beattrack.getOnsets())

        elif exportType == "che":
            #print "{} found in other exports".format(what)
            try:
                vals = [str(c) for c in self.getChordEvents()]
            except Exception:
                vals = None
            return np.array(vals)

        elif exportType == "phrid":
            #print "{} found in other exports".format(what)
            assert(len(self.getPhraseIDs()) == len(self))
            return np.array(self.getPhraseIDs())

        elif exportType == "phrbd":
            #print "{} found in other exports".format(what)
            boundary_markers = [1]
            boundary_markers.extend(diff(self.getPhraseIDs()))
            assert len(boundary_markers), len(self)
            return np.array(boundary_markers)

        elif exportType == 'chorusid':
            #print "{} found in other exports".format(what)
            try:
                vals = self.getChorusIDs()
            except Exception:
                vals = None
            return np.array(vals)

        elif exportType == 'form':
            #print "{} found in other exports".format(what)
            try:
                vals = [str(k) for k in self.getFormEvents()]
            except Exception:
                vals = None
            return np.array(vals)

        elif exportType == 'chtype':
            #print "{} found in other exports".format(what)
            #to do
            try:
                vals = [k.getChordTypeLabel(reduced=True) for k in self.getChordEvents()]
            except Exception:
                vals = None
            return np.array(vals)

        elif exportType == "ideas":
            event_based = get_safe_value_from_dict(optParam, "events", True)
            filter = get_safe_value_from_dict(optParam, "type", "id")
            iv = get_safe_value_from_dict(optParam, "include_voids", "False")
            IF = IFAFilter(self)
            ret = IF.filter(filter_type=filter, include_voids=iv, event_based=event_based)
            return np.array(ret)

        elif exportType == "idea_durs":
            type = get_safe_value_from_dict(optParam, "type", "IOI")
            unit = get_safe_value_from_dict(optParam, "unit", "sec")
            iv = get_safe_value_from_dict(optParam, "include_voids", "False")
            IF = IFAFilter(self)
            ret = IF.getIdeaDurations(type=type, units=unit, include_voids=iv)
            return np.array(ret)
        elif exportType == "swing-shapes":
            max_div = 2
            if optParam is not None:
                if isinstance(optParam, int):
                    max_div = min(2, optParam)
                if isinstance(optParam, str) and optParam.lower() == "include-ternary":
                    max_div = 3
            return np.array(self.getSwingShapes(max_div=max_div))
        elif exportType == "nom-onsets":
            return np.array(self.getNominalOnsets())

        elif exportType == "meta":
            #print "="*60
            #out of try
            #if subType=="key" or subType=="signature":
            #    print "{}, {} found in other exports".format(what, subType)
            #    vals = self.getMetadata().getField(subType)
            #    print "vals", vals
            try:
                vals = self.getMetadata().getField(subType)
            except Exception:
                #print (self.__dict__["esacinfo"].getField(subType))
                try:
                    vals = self.__dict__["esacinfo"].getField(subType)
                except Exception:
                    vals= ""
            return vals
        else:
            raise ValueError("Solo: Invalid export specified: " +str(what))

    def export(self, what, segmentType=None, optParam=None):
        #print "Solo.export called with {}, {}".format(what, optParam)
        parts = what.split("-")
        if parts[0] == "accent" and optParam == None and len(parts) > 1:
            what = parts[0]
            optParam = parts[1]
        ret = Melody.export(self, what, segmentType, optParam)
        return ret

    def getMeanTempo(self, bpm=False):
        if self.isEmpty():
            raise RuntimeError("No events")
        if self.__beattrack is None:
            raise RuntimeError("No beat track")
        tempo = mean(self.__beattrack.getIOIs())
        #print self.__beattrack.getIOIs()
        if bpm:
            tempo = 60./tempo
        return tempo

    def getMedianTempo(self, bpm=False):
        if self.isEmpty():
            raise RuntimeError("No events")
        if self.__beattrack is None:
            raise RuntimeError("No beat track")
        tempo = median(self.__beattrack.getIOIs())
        if bpm:
            tempo = 60./tempo
        return tempo

    def getStdDevTempo(self, bpm=False):
        if self.isEmpty():
            raise RuntimeError("No events")
        if self.__beattrack is None:
            raise RuntimeError("No beat track")
        if bpm:
            stddev = sd([60./ioi for ioi in self.__beattrack.getIOIs() if ioi != 0.])
        else:
            stddev = sd(self.__beattrack.getIOIs())
        return stddev

    def getNominalOnsets(self):
        abt = self.beattrack
        ret = []
        if abt is None or not isinstance(abt, AnnotatedBeatTrack):
            return ret
        #print abt
        for e in self:
            mp = e.getMetricalPosition()
            abe = abt.findBeat(mp.bar, mp.beat)
            if abe is None:
                raise RuntimeError("Could not find beat {}.{} in annotated beat track".format(mp.bar, mp.beat))
            beat_dur =  abe.metrical_position.getBeatInfo().beatDurationSec
            #print "abe.druation", abe.duration, abe.metrical_position.getBeatInfo()
            nom_onset = abe.onset + (mp.tatum-1)*beat_dur/mp.division
            dp = nom_onset-e.onset
            #if abs(dp)>.5:
            #    print "MP: {}, beat:{}, beat_onset: {}, beat_dur: {}".format(mp, abe.metrical_position, abe.onset, beat_dur)
            #    print "Onset: {}, nom_onset: {}, diff:{}".format(e.onset, nom_onset, nom_onset-e.onset)
            #    #raise RuntimeError("Large difference")
            ret.append(nom_onset)
        #print len(ret), len(self.onsets)
        return ret


    def getLoudnessRange(self):
        try:
            l = self.getLoudnessField("median")
            max_l = max(l)
            min_l = max_l - 25
        except:
            #print "getLoudnessRange: No loudness values present"
            max_l = 80
            min_l = 55
        #print "getLoudnessRange: max, min", max_l, min_l
        return max_l, min_l

    def get_main_id(self):
        main_id = "NA"
        try:
            smd = self.__metadata
        except:
            return main_id
        try:
            main_id = smd.getField("filenamesv")
        except:
            try:
                main_id = smd.getField("esacid")
            except:
                main_id = smd.getField("filename")

        return main_id

    def addBassData(self, bass_pitches, quick_fix=True):
        if bass_pitches == None or len(bass_pitches) ==  0:
            return self
        #out of try
        try:
            self.__beattrack.addBassData(bass_pitches, quick_fix)
        except Exception as e:
            print(e)
            pass
        return self

    def shiftbar(self, bar):
        """ Shift all bar numbers by constant amount """

        MeterGrid.shiftbar(self, bar)
        if self.__beattrack is not None:
            try:
                self.__beattrack.shiftbar(bar)
            except:
                pass

    def _getSectionAsString(self, sect):
        """ internal use only, does not check anything"""
        preamble = "\n" + sect + "\n==============================\n"

        try:
            s = eval("self.get"+ sect + "()")
        except:
            return ""

        if s == None:
            return preamble + "(Not set)"
        else:
            return preamble + str(s)

    def __eq__(self, other):
        if isinstance(other, type(None)):
            return False
        if self.__metadata != other.__metadata:
            #if self.__metadata.soloinfo != other.__metadata.soloinfo:
            #    print "Self SI:\n", self.__metadata.soloinfo.__dict__
            #    print "Comp SI:\n", other.__metadata.soloinfo.__dict__
            #if self.__metadata.transinfo != other.__metadata.transinfo:
            #    print "Self TI:\n", self.__metadata.transinfo.__dict__
            #    print "Comp TI:\n", other.__metadata.transinfo.__dict__
            #print "Different metadata"
            return False
        if Rhythm.__ne__(self, other):
            #print "Different events"
            return False
        if self.__beattrack != other.__beattrack:
            return False
        if self.__phrases != other.__phrases:
            return False
        if self.__form != other.__form:
            return False
        if self.__chords != other.__chords:
            return False
        if self.__chorus != other.__chorus:
            return False
        if self.__keys != other.__keys:
            return False
        if self.__IFA != other.__IFA:
            return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    def toQuarterFormat(self):
        mg = Melody(self).toQuarterFormat()
        ret = self.clone()
        mel = Solo()
        for i, e in enumerate(mg):
            try:
                modulation = self[i].modulation
            except:
                modulation = ""
            se = SoloEvent(e, modulations=modulation)
            mel.append(se)
        ret.setMelody(mel)
        return ret

    def to_dataframe(self,
                     annotations=[],
                     metadata=[],
                     exclude_empty=True,
                     split_metrical_positions=True,
                     ignore_loudness=True,
                     ignore_f0mod=True,
                     ignore_values=True,
                     quote_signatures=False):
        """Convert Solo object into a handy pandas DataFrame"""
        if len(self) == 0:
            return DataFrame()

        df = Melody.to_dataframe(self,
                                 split_metrical_positions,
                                 ignore_loudness,
                                 ignore_f0mod,
                                 ignore_values,
                                 quote_signatures)
        for a in annotations:
            #print("Adding annotation", a)
            if a == "phrase":
                df["phrase_id"] = self.getPhraseIDs()
                boundary_markers = [1]
                boundary_markers.extend(diff(self.getPhraseIDs()))
                df["phrase_begin"] = boundary_markers
            if a == "chorus":
                tmp = self.getChorusIDs()
                if not exclude_empty or (exclude_empty and tmp and any(tmp)):
                    df["chorus_id"] = tmp

            if a == "chord":
                tmp = self.getChordEvents()
                if not exclude_empty or (exclude_empty and tmp and any(tmp)):
                    df["chord"] = tmp
                    #print("Added chords")
            if a == "form":
                tmp = self.getFormEvents()
                if not exclude_empty or (exclude_empty and tmp and any(tmp)):
                    df["form"] = tmp
            if a == "key":
                tmp = self.getKeyEvents()
                if not exclude_empty or (exclude_empty and tmp and any(tmp)):
                    df["key"] = tmp
            if a == "idea":
                tmp = self.getIFAEvents()
                if not exclude_empty or (exclude_empty and tmp and any(tmp)):
                    df["idea"] = tmp
        for m in metadata:
            tmp = self.getMetadata().getField(m)
            if not exclude_empty or (exclude_empty and tmp and any(tmp)):
                df[m] = tmp

        return df

    def beattrack_as_dataframe(self, split_metrical_positions=True, exclude_empty=True, include_tatums=False, quote_signatures=False):
        if isinstance(self.beattrack, AnnotatedBeatTrack):
            df = self.beattrack.to_dataframe(split_metrical_positions, exclude_empty=exclude_empty, include_tatums=include_tatums, quote_signatures=quote_signatures)
        else:
            df = self.beattrack.to_dataframe(ignore_values=False)

        return df

    def __str__(self):
        linesep = "=============================="
        if self.isEmpty(): return "(Empty Song)"
        sections = ["phrases", "form", "chords", "chorus", "keys"]
        if self.hasIFASections():
            sections.append("IFA")
        #print   "AAS", self.annotationAsString(sections, sep="|"),

        s = "\n".join([
            str(self.__metadata),
            #linesep,
            "\nEvents:",
            linesep,
            Melody.__str__(self),
            #self.annotationAsString(sections, sep="|"),
            self._getSectionAsString("PhraseSections"),
            self._getSectionAsString("FormSections"),
            self._getSectionAsString("ChordSections"),
            self._getSectionAsString("ChorusSections"),
            self._getSectionAsString("KeysSections"),
            self._getSectionAsString("IFASections"),
            ])
        return s


    metadata            = property(getMetadata, setMetadata)
    beattrack           = property(getBeatTrack, setBeatTrack)
    phrases             = property(getPhraseSections, setPhraseSections)
    form                = property(getFormSections, setFormSections)
    chords              = property(getChordSections, setChordSections)
    chorus              = property(getChorusSections, setChorusSections)
    keys                = property(getKeySections, setKeySections)
    IFA                 = property(getIFASections, setIFASections)
    phraseIDs           = property(getPhraseIDs)
    formEvents          = property(getFormEvents)
    chordEvents         = property(getChordEvents)
    chorusIDs           = property(getChorusIDs)
    keyEvents           = property(getKeyEvents)
