# coding: latin-1
'''
Created on 08.12.2013

@author: kf
'''

import os

#import xlrd
from xlrd import XL_CELL_DATE, XL_CELL_NUMBER, XL_CELL_TEXT, open_workbook, xldate_as_tuple

from melospy.basic_representations.jm_util import chomp
from melospy.basic_representations.solo_meta_data import *


class MasterTableReader(object):
    '''
    Class to parse the JAZZOMAT Excel master table
    '''
    data_start_row = 2
    column_names = ['ID',
                        'PerformerLastName',
                        'PerformerFirstName',
                        'Title',
                        'TitleAddOn',
                        'SoloPart',
                        'Style',
                        'Instrument',
                        'AvgTempo',
                        'TempoClass',
                        'RhythmFeel',
                        'Genre',
                        'Meter',
                        'TonalityType',
                        'OriginalForm',
                        'HarmonyTemplate',
                        'Key',
                        'Type',
                        'SoloTime',
                        'ThemeTime',
                        'Comment',
                        'Artist',
                        'RecordTitle',
                        'Label',
                        'RecordBib',
                        'MusicBrainzID',
                        'TrackNo',
                        'LineUp',
                        'ReleaseDate',
                        'RecordingDate',
                        'Recording Year',
                        'Composer',
                        'Source',
                        'SourceType',
                        'ErrorRate',
                        'Transcriber',
                        'Tapper',
                        'Coder',
                        'FilenameOriginalAudio',
                        'FilenameSolo',
                        'SourceChanges',
                        'Status',
                        'MidlevelAnalysisStatus']
    def __init__(self, filename, exact_find=False):
        try:
            wb = open_workbook(filename)
        except:
            raise ValueError("Could not open {}".format(filename))
        self.book = wb
        self.sheet = wb.sheets()[0]
        #print "Found sheet with {} rows and {} columns".format(self.sheet.nrows, self.sheet.ncols)
        self.read_header()
        self.nrows = self.sheet.nrows-self.data_start_row
        self.ncols = self.sheet.ncols
        self.exact = exact_find
        self.row_cache = {}
        self.filename_cache = {}
        self.counter = 0

    def cell(self, row, col):
        cell = self.sheet.cell(self.data_start_row + row, col)
        if cell.ctype == XL_CELL_NUMBER:
            #cell = str(floor(cell.value))
            cell = str(cell.value).split(".")[0]
        elif cell.ctype == XL_CELL_DATE:
            cell = xldate_as_tuple(cell.value, self.book.datemode)
            cell = str(date(*cell[:3]))
        else:
            cell = chomp(cell.value)
        return cell

    def colidx_from_header(self, header):
        return self.column_map[header]

    def read_header(self):
        header = []
        s = self.sheet
        for col in range(s.ncols):
            h = self.cell(-1, col)
            #simply ignore columns with empty header
            if h:
                header.append(h)
        #print "Header: ", "\":\"".join(header)
        count = 0
        for head in header:
            if head in self.column_names:
                count += 1
            else:
                if head:
                    print("'{}' not found in column name constants".format(head))
        #print "Matched: {}, Total: {}, Columns: {}".format(count, len(header), len(self.column_names))
        if count != len(self.column_names):
            raise RuntimeError("Headers do not match column header. Check version of mastertable")
        self.header = header
        self.column_map = {}
        for h in self.header:
            self.column_map[h] = self.column_names.index(h)
        #print self.column_map
        return self

    def read_column(self, header):
        col = self.column_map[header]
        ret = [""]*self.nrows
        for row in range(0, self.nrows):
            ret[row] = self.cell(row, col)
            #print "Reading row",ret[row]
        return ret

    def capitalize_in_brackets(self, s):
        i = 0
        if len(s)==0:
            return s
        if s.find("(") == -1:
            return s.capitalize()
        while s[i] == "(" or s[i] == "{" or s[i] == "[":
            i += 1
        #print "s: {}, i:{}, s[0:i]:{}, s[i_len(s)]:{}".format(s, i, s[0:i], s[i:len(s)].capitalize())
        return s[0:i]+ s[i:len(s)].capitalize()

    def capitalize(self, s):
        s = self.capitalize_in_brackets(s)
        dummy = s.split(".")
        return ".".join([_.capitalize() for _ in dummy])

    def camelize(self, s):
        return "".join([self.capitalize(_) for _ in s.split(" ")])

    def remove_char(self,s, chars=["\"", "'"]):
        for c in chars:
            s = s.replace(c, "")
        return s

    def read_cell(self, row, header):
        #print self.find_row(row)
        #self.counter +=1
        #if self.counter>1:
        #    sys.exit(0)
        try:
            row = self.find_row(row)
        except:
            pass
        if row == -1:
            print("Warning row:{} not found".format(row))
            return ""

        #print "Row:{}, header:{}".format(row, header)
        return self.cell(row, self.column_map[header])

    def _status_from_filename_sv(self, filename_sv):
        tmp = os.path.splitext(filename_sv)[0]
        tmp = tmp.split("_")[-1]
        return tmp

    def read_transcription_info(self, item):
        ti = TranscriptionInfo()
        ti.setCoder(self.read_cell(item, "Coder"))
        ti.setTranscriber(self.read_cell(item, "Transcriber"))
        ti.setFileNameSolo(self.read_cell(item, "FilenameSolo"))
        ti.setFileNameSV(item)
        ti.setFileNameTrack(self.read_cell(item, "FilenameOriginalAudio"))
        ti.setSourceType(self.read_cell(item, "SourceType"))
        ti.setSource(self.read_cell(item, "Source"))
        ti.setCoder(self.read_cell(item, "Coder"))
        ti.setSoloTime(self.read_cell(item, "SoloTime"))
        try:
            alt_status = self._status_from_filename_sv(ti.getFileNameSV())
            ti.status = alt_status
        except:
            ti.setStatus(self.read_cell(item, "Status"))

        #print "alt_stat", alt_stat
        #if ti.status =="PREFINAL":
        #    print "item: {}, filenamesv:{}".format(item, ti.filenamesv)
        #print ti
        return ti

    def read_solo_info(self, item):
        si = SoloInfo()
        #print(item)
        first   = self.read_cell(item, "PerformerFirstName")
        last    = self.read_cell(item, "PerformerLastName")
        #print("First {}". format(first))
        #print("Last: {}".format(last))
   
        si.setPerformer(first + " " + last)
        si.setTitle(self.read_cell(item, "Title"))
        si.setTitleAddOn(self.read_cell(item, "TitleAddOn"))
        si.setInstrument(self.read_cell(item, "Instrument"))
        si.setSoloPart(self.read_cell(item, "SoloPart"))
        si.setStyle(self.read_cell(item, "Style"))
        si.setRhythmFeel(self.read_cell(item, "RhythmFeel").replace(" ", ""))
        si.setTempoClass(self.read_cell(item, "TempoClass"))
        try:
            si.setSignature(self.read_cell(item, "Meter"))
        except:
            pass
        si.setKey(self.read_cell(item, "Key"))
        #print si
        return si

    def read_record_info(self, item):
        ri = RecordInfo()
        ri.setArtist(self.read_cell(item, "Artist"))
        ri.setLabel(self.read_cell(item, "Label"))
        ri.setRecordTitle(self.read_cell(item, "RecordTitle"))
        ri.setRecordBib(self.read_cell(item, "RecordBib"))
        #print "Raw RecDate1", self.read_cell(item, "RecordingDate")
        ri.setRecordingDate(self.read_cell(item, "RecordingDate"))
        #print "Raw RecDate2", self.read_cell(item, "RecordingDate")
        ri.setReleaseDate(self.read_cell(item, "ReleaseDate"))
        ri.setLineUp(self.read_cell(item, "LineUp"))
        ri.setTrackNumber(self.read_cell(item, "TrackNo"))
        ri.setMusicBrainzID(self.read_cell(item, "MusicBrainzID"))
        #print "Raw RecDate", self.read_cell(item, "RecordingDate")

        #print(ri)
        return ri

    def read_composition_info(self, item):
        ci = CompositionInfo()
        ci.setComposer(self.read_cell(item, "Composer"))
        ci.setTitle(self.read_cell(item, "Title"))
        ci.setForm(self.read_cell(item, "OriginalForm"))
        ci.setHarmonyTemplate(self.read_cell(item, "HarmonyTemplate"))
        ci.setTonalityType(self.read_cell(item, "TonalityType"))
        ci.setGenre(self.read_cell(item, "Genre"))

        #print(ci)
        return ci

    def guess_filename_sv_base(self, item):
        if item in self.row_cache:
            return self.row_cache[item]

        last_name = self.cell(item, 1)
        first_names = self.cell(item, 2).split(" ")
        if len(first_names)>1:
            first_names = first_names[1]
        else:
            first_names = first_names[0]
        #first_names = self.remove_char(first_names, chars=["."])
        #if first_names=="J.J.":
        #    print self.camelize(first_names+ " " + last_name)
        performer = self.camelize(first_names+ " " + last_name)
        performer = self.remove_char(performer, chars=["."])
        title     = self.cell(item, 3)
        #print "Raw title: {} (by {})".format(title, performer)
        #title = title.replace("\xe1", "a")
        #title = title.replace("\xe0", "a")
        #title = self.remove_char(title, chars=["."])
        title_addon = self.cell(item, 4)
        #title_addon = self.remove_char(title_addon, chars=["."])
        solo_part   = self.cell(item, 5)

        #if last_name=="Coltrane":
        #    print "=" * 60
        #    print "Performer: {}, title: {}, item:{}".format(performer, title, item)
        #    print "Title add on: {}, solo part: {}".format(title_addon, solo_part)

        title = self.remove_char(title, chars=["\""])
        title = self.camelize(title)
        #print "Makeup title: ", title

        filename_sv = performer + "_" + title

        if len(title_addon)>0:
            filename_sv += "_" + self.camelize(title_addon)

        if len(solo_part)>0 and solo_part != " ":
            filename_sv += "-" + solo_part

        filename_sv += "_FINAL.sv"

        #if last_name=="Coltrane":
        #    print "File_SV:", filename_sv

        if item not in self.row_cache:
            self.row_cache[item] = filename_sv
        #print "guess_filename_sv_base", filename_sv
        return filename_sv

    def getBasename(self, fsv):
        return "_".join(_ for _ in fsv.split("_")[0:2])

    def getTitleAddon(self, fsv,):
        parts = fsv.split("_")
        if len(parts) > 3:
            return parts[2].split("-")[0]
        return ""

    def find_row(self, filename):
        ext = os.path.splitext(filename)[1][1:]
        if ext == "krn":
            return self.find_row_krn(filename)
        if ext == "sv":
            return self.find_row_sv(filename)
        print("Unknown extension {} for {}".format(ext, filename))
        return -1

    def find_row_krn(self, filename_krn):
        #print "find_row_krn"
        if filename_krn in self.filename_cache:
            #print "Found {} in cache row: {}".format(filename_sv, self.filename_cache[filename_sv])
            return self.filename_cache[filename_krn]
        for i in range(self.nrows):
            ID = self.cell(i, 0)
            #print "ID:", ID, i
            if ID.lower() == filename_krn.lower():
                #print "Found {} in row {}".format(filename_krn, i)
                return i
        return -1

    def find_value_by_column(self, key_column, key_value, target_column):
        key_col = self.column_map[key_column]
        target_col = self.column_map[target_column]
        for row in range(self.nrows):
            value = self.cell(row, key_col)
            if value == key_value:
                ret = self.cell(row, target_col)
                return ret
        return None

    def find_row_sv(self, filename_sv):
        debug = False

        if filename_sv in self.filename_cache:
            return self.filename_cache[filename_sv]

        fsv = filename_sv.split("_")
        base_name  = self.getBasename(filename_sv)
        ta = self.getTitleAddon(filename_sv)

        if debug:
            print("Searching for: ", filename_sv, " Base: ", base_name, " ", base_name.lower())

        for i in range(self.nrows):
            tmp = self.getBasename(self.guess_filename_sv_base(i))
            if debug:
                print("tmp: {}".format(tmp))
                pass
            if tmp == base_name or tmp == base_name + "-1":
                tmp_ta = self.getTitleAddon(self.guess_filename_sv_base(i))
                #print("tmp == basename. ta:'{}', tmp_ta:'{}'".format(ta, tmp_ta))
                if tmp_ta == ta:
                    self.filename_cache[filename_sv] = i
                    return i
            if not self.exact:
                if tmp.lower() == base_name.lower() or tmp.lower() == base_name.lower() + "-1":
                    tmp_ta = self.getTitleAddon(self.guess_filename_sv_base(i))
                    if tmp_ta == ta:
                        self.filename_cache[filename_sv] = i
                        return i
        return -1

    def read(self, filename_sv):
        ''' Read entry according to filename_sv
        '''
        pass
