""" Class for reading **kern files"""
import csv
import re
import sys

from melospy.input_output.krn_params import *
from melospy.input_output.krn_spines import *


class KernReader(object):
    """ Class for reading **kern files """

    def __init__(self, filename=None, params=None):
        self.filename   = filename
        self.solo       =  None
        self.spines     = None
        self.metadata   = []
        if params is None:
            params = KernReaderParams()
        self.params = params
        self.debug  = self.params.getValue("diagnostic")
        part_no     = self.params.getValue("part_no")
        if filename:
            self.solo  = self.readKernFile(filename, part_no)

    def debug_msg(self, s):
        if self.debug:
            print("KernReader: {}".format(s))

    def tempo_check(self):
        if len(self.spines) < 2:
            return True
        
        gauge = self.spines[0].tempos_bpm[0]
        for i in range(1, len(self.spines)):
            if not self.spines[i].tempos_bpm:
                continue
            test = self.spines[i].tempos_bpm[0]
            if test != gauge:
                return False
        return True

    def _patch_value(self, d):
        if d[1] == ".":
            if d[0] == "1r":
                d[1] = "1NC"
                #print "inserted NC @L:{}".format(i)
            if d[0][0] == "=":
                d[1] = d[0]
                #print "Copied meaure {} @L:{}".format(d[0], i)
        return d

    def _patch_chord_spines(self, data):
        self.debug_msg("Patching chord spine")
        ret = []
        for i, d in enumerate(data):
            if len(d) == 1:
                ret.append([d[0]])
                continue
            if len(d) == 2:
                ret.append([d[0]+d[1]])
                continue
            chord_spine_element = d[1]
            quality = d[2]
            if quality[0] == ":":
                chord_spine_element = "{}{}".format(chord_spine_element, quality[1:])
                #print "Joined chord", chord_spine_element
            ret.append([d[0], chord_spine_element])
        return ret

    def _extract_spines(self, filename):
        with open(filename, 'r') as csvfile:
            csvreader = csv.reader(csvfile, delimiter='\t', lineterminator="\n")
            data = list(csvreader)

        if len(data) == 0:
            raise RuntimeError("No spines found\n")
        #print data[14]
        total_spine_count = max(len(d) for d in data)
        data_spine_count = len(data[0])

        self.debug_msg("-"*40)
        self.debug_msg("Found {} spines".format(total_spine_count))
        self.debug_msg("Found {} data spines".format(data_spine_count))

        if data_spine_count == total_spine_count and data_spine_count > 2:
            data = self._patch_chord_spines(data)
            total_spine_count = 2
            data_spine_count = 2

        spines = [None] * total_spine_count

        for i in range(total_spine_count):
            spines[i] = KernSpine(id=i)
            spines[i].debug = self.debug
            if i >= data_spine_count:
                spines[i].spine_type = "comment"
        i = 1
        for l, d in enumerate(data):
            for i in range(total_spine_count):
                spines[i].cur_line = l + 1
            #self.debug_msg("Line: {}:{}".format(l, d))
            if d[0][0:2] == "!!":
                self.metadata.append(data[2:])
                continue
            print("D:", d)
            for j in range(total_spine_count):
                #print(len(d), j)
                spines[j].append(d[j])
                try:
                    d = self._patch_value(d)
                    spines[j].append(d[j])
                except IndexError:
                    pass
            i += 1
        #print spines[1].markers["bars"]
        #print spines[1]
        if total_spine_count > 1:
            spines[1]._patch_bar_gaps()
        #print spines[0]
        #print spines[1].bar_qstarts
        #sys.exit(0)
        for sp in spines:
            print(sp.spine_type)
            if sp.spine_type is not None and sp.spine_type != "comment":
                sp.post_process()
        #print spines[1]
        return spines

    def analyseKernFile(self, filename=None):
        """ Method to analyse a **kern file
        """
        #self.debug = True
        if not filename:
            filename = self.filename
        if not filename or filename is None:
            return None
        self.spines = self._extract_spines(filename)
        #print "Analysing: ", filename
        try:
            if not self.tempo_check():
                print("Found unmatching tempos")
        except:
            print("No tempo indication found")
        return self.spines

    def readKernFile(self, filename=None, partNo=None):
        """ Method to read a **krn file
        """
        if not filename:
            filename = self.filename
        if not filename or filename is None:
            raise ValueError("No file name given")

        self.analyseKernFile(filename)

        if len(self.spines) == 0:
            raise RuntimeError("**kern file {} has no valid spines".format(filename))
        #print(self.spines[0])
        if self.spines[0].spine_type != "notes":
            raise RuntimeError("**kern file {} first spine does not contain notes but {}".format(filename, self.spines[0].spine_type))
        #print  "\n".join(["p: {}, v:{}, t:{}".format(e.phrase, e.value, e.tie) for e in self.spines[0].data ])

        melody = self.spines[0].convert_to_melody()
        abt = None
        if self.spines[1].spine_type == "chords":
            abt = self.spines[1].convert_to_annotated_beat_track()

        key        = self.spines[0].get_main_key()
        avg_tempo  = self.spines[0].get_avg_tempo(bpm=True)
        main_meter = self.spines[0].get_main_meter()

        psi = PopSongInfo(filename=filename, avgTempoBPM=avg_tempo, key=key, mainSignature=main_meter)
        md  = PopSongMetaData(psi)
        phrases = self.spines[0].phrases
        if len(phrases) == 0:
            sp = SegmenterParams(method="relative_simple_segmenter", output_format="section_list")
            s = Segmenter(rhythm=melody, params=sp)
            phrases = s.process()
        #print phrases
        #print len(melody)
        choruses = self.spines[0].choruses
        #print choruses
        solo_start = choruses.getStartID()
        solo_end = choruses.getEndID()
        choruses.pad(-1, 0, len(melody)-1)
        #print choruses
        #print solo_start, melody[solo_start]
        solo = Solo(melody=melody, metadata=md, beatTrack=abt, phrases=phrases, form=None, chorus=choruses, chords=None, keys=None, ideas=None)
        #solo.setSingleChorus()
        #form = self,spines[0].form
        #if form is None or len(form) == 0:
        solo.setSingleForm()
        #else:
        #    solo.setFormSections(form)
        if abt is not None:
            sl = solo.rhythmToSectionList(abt.getChords(), sectType="CHORD")
            sl.pad(Chord("NC"), 0, len(solo)-1)
            solo.setChordSections(sl)
            form_start =abt._get_form_start()
            if form_start is not None:
                #print "MP:", abt[form_start].metrical_position
                solo.setSingleForm(abt[form_start].metrical_position)
            #print "\n".join(["{}:{}".format(a.getMetricalPosition(), a.signature_change) for a in abt if a.signature_change] )
        if self.params.getValue("only_solos"):
            #print "Cutting solo!"
            solo = solo.slice(solo_start, solo_end)
            solo.phrases.renumber(start=1)
            bt = solo.getBeatTrack()
            if not bt[0].form:
                bt[0].form = FormName("I1")
            form_start = abt._get_form_start()
            if form_start is not None:
                #print "MP:", abt[form_start].metrical_position
                solo.setSingleForm(abt[form_start].metrical_position)
            #print "\n".join(["{}:{}".format(a.getMetricalPosition(), a.signature_change) for a in abt if a.signature_change] )
            #print "<->".join([a.signature_change for a in solo.getBeatTrack()])
            #print_vector( solo.getMetricalPositions())
        #print solo.getBeatTrack().getSignatureChanges(compact=True)
        #solo.getBeatTrack().setSingleForm()
        chord_changes = solo.getBeatTrack().get_chord_changes_by_form()
        solo.getMetadata().setField("chordchanges", chord_changes)
        #print solo.chorus
        #print "Beattrack "
        #print_vector(solo.getBeatTrack()[0:10])
        return solo
