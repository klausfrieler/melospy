# coding: latin-1
'''
Created on 21.01.2017

@author: kf
'''

import os
import re
#import xlrd
from xlrd import open_workbook, XL_CELL_NUMBER, XL_CELL_TEXT, XL_CELL_DATE, xldate_as_tuple
#from transcription_info import *
from melospy.basic_representations.chord import *
from melospy.basic_representations.key import *
from melospy.basic_representations.jm_util import chomp, Timer
from melospy.similarity.similarity_edit_distance import *

DATA_START_ROW = 1
CHORUS_START_COL = 43
PERFORMER_COL = 1
TITLE_COL = 2
FORM_COL = 3
VERSE_START_COL = 3
MAX_COL = 74

def chord_sub_cost(chord1, chord2):
    if chord1 == chord2:
        return 0
    return 1

def chord_sub_cost_with_minor_parallels(chord1, chord2):
    if chord1 == chord2 or chord1.isMinorParallel(chord2) or chord2.isMinorParallel(chord1):
        return 0
    return 1
    
class TillessenChordSequence(object):
    def __init__(self, chords={}):
        if not isinstance(chords, dict):
            raise TypeError("Chords must be dictionary" )
        self.chords = chords

    def get_downbeat_sequence(self, downbeats="1+3"):
        ret = {}
        if downbeats not in ["1", "1+3"]:
            raise ValueError("Invalid downbeat spec:{}".format(downbeats))
        for bar_num in self.chords:
            chords = self.chords[bar_num]
            #print bar_num, chords, self.chords
            bar = []
            bar.append(chords[0])
            if downbeats == "1+3":
                if len(chords) == 1:
                    bar.append(chords[0])
                elif len(chords) == 2:
                    bar.append(chords[1])
                elif len(chords) >= 3:
                    bar.append(chords[2])
            ret[bar_num] = bar
        return TillessenChordSequence(ret)
    
    def normalize(self):
        ret = {}
        for bar_num in self.chords:
            chords = self.chords[bar_num]
            bar = []*4
            if len(chords) == 1:
                bar = [chords[0]]*4
            elif len(chords) == 2:
                bar = [chords[0]]*2 + [chords[1]]*2
            elif len(chords) == 3:
                bar = [chords[0]] + [chords[1]] + [chords[2]]*2
            elif len(chords) == 4:
                bar = [chords[0]] + [chords[1]] + [chords[2]] + [chords[4]]
            else:
                raise ValueError("Too many ({}) chords in bar".format(len(chords)))
            ret[bar_num] = bar
        return TillessenChordSequence(ret)

    def flatten(self):
        ret = []
        for bar in self.chords.values():
            ret.extend(bar)
        return ret

    def clone(self):
        cs = {}
        for c in self.chords:
            cs[c] = self.chords[c]
        return TillessenChordSequence(cs)

    def match(self, cs1, cs2, identity_func=chord_sub_cost):
        if len(cs1) != len(cs2):
            raise ValueError("Chord sequences do not match in length {} vs. {}".format(len(cs1), len(cs2)))
        match = 0.
        for i in range(len(cs1)):
            match += 1. - identity_func(cs1[i], cs2[i])
        return match/len(cs1)
        
    def similarity(self, chord_sequence, sim_type="edit_distance", minor_parallels=True):
        cs1 = self.clone()
        cs2 = chord_sequence.clone()
        l1 = len(cs1)        
        l2 = len(cs2)
        nc1 = cs1.num_chords()
        nc2 = cs2.num_chords()
        sim = 0
        transformation = ""
        if l1 != l2:
            if l1 == 2*l2:
                cs1 = cs1.get_downbeat_sequence("1").flatten()
                cs2 = cs2.get_downbeat_sequence("1+3").flatten()
                transformation = "Double/half time"
            elif l2 == 2*l1:
                cs1 = cs1.get_downbeat_sequence("1+3").flatten()
                cs2 = cs2.get_downbeat_sequence("1").flatten()
                transformation = "Double/half time"
            else:
                return 0, ""
        else:
            if nc1 != nc2:
                cs1 = cs1.get_downbeat_sequence("1+3").flatten()
                cs2 = cs2.get_downbeat_sequence("1+3").flatten()
                transformation = "Downbeat reduction"
            else:
                cs1 = cs1.flatten()
                cs2 = cs2.flatten()
        sub_cost = chord_sub_cost_with_minor_parallels if minor_parallels else chord_sub_cost
        #print "Calculating similarity '{}' with parallels:{}".format(sim_type, minor_parallels)
        if sim_type == "edit_distance":
            sed = SimilarityEditDistance(sub_cost=sub_cost)
            sim = sed.process(cs1, cs2)
        elif sim_type == "match":
            sim = self.match(cs1, cs2, identity_func=sub_cost)
        else:
            raise ValueError("Invalid similarity type: {}".format(sim_type))
        #if sim >.75:
        #    print "CS1", "".join(str(c) for c in cs1)                
        #    print "CS2", "".join(str(c) for c in cs2)
        #if transformation:
        #    print "transformation", transformation
        return sim, transformation

    def num_chords(self):
        n = sum(len(c) for c in self.chords.values())
        return n
        
    def _bar_string(self, bar_chords):
        return "".join([str(c) for c in bar_chords])
    def _form_string(self, form_bars):
        return "|".join([self._bar_string(bar) for bar in form_bars])
    def __len__(self):
        return len(self.chords)
    def __str__(self):
        return self._form_string(self.chords.values())
        
    def __repr__(self):
        return self.__str__()

class TillessenSong(object):
    def __init__(self, performer="", title="", form="", verse_chords=TillessenChordSequence(), alt_verse_chords=TillessenChordSequence(), chorus_chords=TillessenChordSequence(), alt_chorus_chords=TillessenChordSequence(), diagnostics={"more_than_4": 0, "uneven_number": 0}):
        self.performer = performer
        self.title = title
        self.form = form
        self.verse_chords = self._make_TCS(verse_chords)
        self.alt_verse_chords = self._make_TCS(alt_verse_chords)
        self.chorus_chords = self._make_TCS(chorus_chords)
        self.alt_chorus_chords = self._make_TCS(alt_chorus_chords)
        self.diagnostics = diagnostics
        self.has_issues = sum(diagnostics[v] for v in diagnostics) > 0

    def _sim_helper(self, cs1, cs2, sim_type="edit_distance", minor_parallels=True):
        sim = -1.
        transformation = "" 
        if len(cs1) > 0 and len(cs2) > 0:
            sim, transformation = cs1.similarity(cs2, sim_type, minor_parallels)
        
        return sim, transformation
        
    def similarity(self, song, sim_type="edit_distance", minor_parallels=True):
        ret = {}
        vc1 = [self.verse_chords, self.alt_verse_chords]
        vc2 = [song.verse_chords, song.alt_verse_chords]
        cc1 = [self.chorus_chords, self.alt_chorus_chords]
        cc2 = [song.chorus_chords, song.alt_chorus_chords]
        alt_marker = ["", "a"]
        max_v_sim = -1
        max_c_sim = -1
        max_v_trafo = ""
        max_c_trafo = ""
        for i in range(2):
            for j in range(2):
                sim, v_transformation = self._sim_helper(vc1[i], vc2[j], sim_type=sim_type, minor_parallels=minor_parallels)
                sim_id = "sim_v1{}_v2{}".format(alt_marker[i], alt_marker[j])
                ret[sim_id] = sim
                if sim > max_v_sim:
                    max_v_sim = sim
                    max_v_trafo = v_transformation
                sim, c_transformation = self._sim_helper(cc1[i], cc2[j], sim_type=sim_type, minor_parallels=minor_parallels)
                sim_id = "sim_c1{}_c2{}".format(alt_marker[i], alt_marker[j])
                ret[sim_id] = sim
                if sim > max_c_sim:
                    max_c_sim = sim
                    max_c_trafo = c_transformation
        if max_v_sim >= 0:
            if max_c_sim >= 0:
                ret["sim_tot"] = .5*(max_v_sim+ max_c_sim)
            else:
                ret["sim_tot"] = max_v_sim
        else:
                ret["sim_tot"] = -1
        #print "ret", ret
        ret["v_transformation"] = max_v_trafo
        ret["c_transformation"] = max_c_trafo
        return ret
        
    def _make_TCS(self, chord_dict):
        if not isinstance(chord_dict, TillessenChordSequence):
            chord_dict = TillessenChordSequence(chord_dict) 
        return chord_dict

    def _bar_string(self, bar_chords):
        return "".join([str(c) for c in bar_chords])

    def _form_string(self, form_bars):
        return "|".join([self._bar_string(bar) for bar in form_bars])
        
    def __str__(self):
        verse_str = str(self.verse_chords)
        alt_verse_str = str(self.alt_verse_chords)

        chorus_str = str(self.chorus_chords)
        alt_chorus_str = str(self.alt_chorus_chords)
        ret = u""
        #print self.performer, self.title
        #print u"{}".format(self.title)
        if chorus_str:
            if alt_verse_str:
                if alt_chorus_str:
                    ret = u"{}:{} ({})\nV1({}):{}\nV2({}):{}\nC1({}):{}\nC2({}):{}".format(self.performer, self.title, self.form, len(self.verse_chords), verse_str, len(self.alt_verse_chords), alt_verse_str, len(self.chorus_chords), chorus_str, len(self.alt_chorus_chords), alt_chorus_str)        
                else:
                    ret = u"{}:{} ({})\nV1({}):{}\nV2({}):{}\nC({}):{}\n".format(self.performer, self.title, self.form, len(self.verse_chords), verse_str, len(self.alt_verse_chords), alt_verse_str, len(self.chorus_chords), chorus_str)        
            else:
                if alt_chorus_str:
                    ret = u"{}:{} ({})\nV({}):{}\n\nC1({}):{}\nC2({}):{}\n".format(self.performer, self.title, self.form, len(self.verse_chords), verse_str, len(self.chorus_chords), chorus_str, len(self.alt_chorus_chords), alt_chorus_str)        
                else:
                    ret = u"{}:{} ({})\nV({}):{}\nC({}):{}\n".format(self.performer, self.title, self.form, len(self.verse_chords), verse_str, len(self.chorus_chords), chorus_str)
        else:
            if alt_verse_str:
                ret = u"{}:{} ({})\nV1({}):{}\nV2({}):{}".format(self.performer, self.title, self.form, len(self.verse_chords), verse_str, len(self.alt_verse_chords), alt_verse_str)        
            else:
                ret = u"{}:{} ({})\nV({}):{}\n".format(self.performer, self.title, self.form, len(self.verse_chords), verse_str)        
            
        #print ret, type(ret)
        return ret

    def __repr__(self):
        return self.__str__()

    def __eq__(self, comp):
        if not isinstance(comp, TillessenSong):
            return False
        if self.performer.lower() == comp.performer.lower() and self.title.lower() == comp.title.lower():
            return True
        return False
        
    def __ne__(self, comp):
        return not self.__eq__(comp)
        
class TillessenReader(object):
    '''
    Class to parse chord sequences provided by Peter Tillessen 
    for his Whatever project.
    '''

    def __init__(self, filename):
        try:
            wb = open_workbook(filename)
        except:
            raise ValueError("Could not open {}".format(filename))
        self.book = wb
        self.sheet = wb.sheets()[0]
        print("Found sheet with {} rows and {} columns".format(self.sheet.nrows, self.sheet.ncols))
        #self.read_header()
        self.nrows = self.sheet.nrows-DATA_START_ROW
        self.ncols = self.sheet.ncols

    def _parse_chord(self, chord):
        diatonic_to_chromatic = {1:0, 2:2, 3:4, 4:5, 5:7, 6:9, 7:11}
        note_name_map= ('C','C#','D','Eb','E','F','F#','G', 'Ab', 'A', 'Bb', 'B')
        flat = 0
        if chord[0].lower() == "b":
            flat = 1
            digit = int(chord[1])
        else:
            digit = int(chord[0])
        note_name = note_name_map[diatonic_to_chromatic[digit]-flat]

        ch_type = ""
        chord_type_map = {"": "", "m":"-", "a":"+", "d":"o"}
        if len(chord)> 1 + flat:
            ch_type = chord[1+flat]
        ch_type = chord_type_map[ch_type]
        chord_label = "{}{}".format(note_name, ch_type)
        c = Chord(chord_label)
        return c

    def _parse_bar(self, entry):
        parts = entry.split("0")
        if len(parts) == 0:
            return None
        chord_pattern = re.compile('[b]?[1-7]{1}[mad]?')    
        chords1 = re.findall(chord_pattern, parts[0])
        chords2 = []
        if len(parts)>1:
            chords2 = re.findall(chord_pattern, parts[1])
        chords1 = [self._parse_chord(c) for c in chords1]
        chords2 = [self._parse_chord(c) for c in chords2]
        #print ":".join([str(c) for c in chords1])
        return chords1, chords2

    def _parse_chord_sequence(self, cs):
        cs1 = {}
        cs2 = {}
        warnings = {"more_than_4": 0, "uneven_number": 0}
        for i in range(0, len(cs)):
            ch1, ch2 = self._parse_bar(cs[i])
            if len(ch1) == 0:
                continue
            cs1[i+1] = ch1
            if len(ch1)>4:
                #print "Warning: Found more  {} chords in bar.".format(len(ch1)) 
                warnings["more_than_4"] += 1
            elif len(ch1)> 1 and len(ch1) % 2 != 0:
                #print "Warning: Number of chords ({}) not an even number.".format(len(ch1)) 
                warnings["uneven_number"] += 1
                
            cs2[i+1] = ch2 if ch2 else ch1
        if cs2.values() == cs1.values():
            cs2 = {}
        return cs1, cs2, warnings
        
    def cell(self, row, col):
        cell = self.sheet.cell(DATA_START_ROW+ row, col)
        if cell.ctype == XL_CELL_NUMBER:
            #cell = str(floor(cell.value))
            cell = str(cell.value).split(".")[0]
        elif cell.ctype == XL_CELL_DATE:
            cell = xldate_as_tuple(cell.value, self.book.datemode)
            cell = str(date(*cell[:3]))
        else:
            cell = chomp(cell.value)
        return cell

    def read_column(self, col):
        ret = [""]*self.nrows
        for row in range(0, self.nrows):
            ret[row] = self.cell(row, col)
            #print "Reading row",ret[row]
        return ret
        

    def read_row(self, row):
        #print "Row:{}, header:{}".format(row, header)
        ret = [""]*self.ncols
        for col in range(0, self.ncols):
            ret[col] = self.cell(row, col)
        return ret        

    def read_song(self, row):
        row = self.read_row(row)
        #print u"Reading {}: {}".format(row[0], row[1])
        verse= [c for c in row[VERSE_START_COL:CHORUS_START_COL] if len(c)>0]
        chorus = [c for c in row[CHORUS_START_COL:self.ncols] if len(c)>0]        
        v1, v2, w1 = self._parse_chord_sequence(verse)
        c1, c2, w2 = self._parse_chord_sequence(chorus)
        warnings = {}
        for v in w1:
            warnings[v] = w1[v] + w2[v]
        song = TillessenSong(row[0], row[1], row[2], v1, v2, c1, c2, warnings)
        #if song.has_issues:
        #    print u"{}".format(song)
        return song
    
    def read_all_songs(self, clean=False):
        ''' Read all songs at once
        '''
        ret = [None]*self.nrows
        n_issues = 0
        for i in range(0, self.nrows):
            ret[i] = self.read_song(i)
            if ret[i].has_issues:
                n_issues  += 1
            #print ret[i].__str__()
        print("Read {} songs, {} OK, {} with issues".format(self.nrows, self.nrows-n_issues, n_issues))
        if clean:
            ret = [song for song in ret if not song.has_issues]
        return ret