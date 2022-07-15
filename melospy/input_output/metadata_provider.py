import os
import re

from melospy.basic_representations.composition_info import CompositionInfo
from melospy.basic_representations.popsong_info import PopSongInfo
from melospy.basic_representations.popsong_meta_data import PopSongMetaData
from melospy.basic_representations.record_info import RecordInfo
from melospy.basic_representations.solo_info import SoloInfo
from melospy.basic_representations.solo_meta_data import SoloMetaData
from melospy.basic_representations.transcription_info import TranscriptionInfo
from melospy.input_output.mastertable_reader import MasterTableReader
from melospy.input_output.pop_daniel_meta_reader import PopDanielMetaReader


class MetadataProvider(object):
    """Helper class for meta data. Reads either form Excel sheet
        or tries to guess some rudimentary stuff from filenames.
    """
    def __init__(self, metadata_file="", type="sv"):
        self.mt = None
        self.type = type

        if metadata_file:
            if self.type == "sv" or self.type == "**kern":
                self.mt = MasterTableReader(metadata_file)
            elif self.type == "mcsv1":
                self.mt = PopDanielMetaReader(metadata_file)

    def solo_info_from_filename(self, filename):
        base = os.path.basename(filename)
        comp = base.split("_")
        if len(comp) > 2:
            a = re.compile('((?<=[a-z0-9])[A-Z]|(?!^)[A-Z](?=[a-z]))')
            return SoloInfo(performer=a.sub(r' \1', comp[0]), title=a.sub(r' \1', comp[1]))
        return SoloInfo(title=os.path.splitext(base)[0])

    def transcription_info_from_filename(self, filename):
        status = ""
        fileNameSV = ""
        filename = filename.replace("\\", "/")
        base = os.path.basename(filename)
        comp = base.split("_")
        if len(comp) > 2:
            status = comp[-1].split(".")[0]
            #print "Status:", status
        if os.path.splitext(filename)[1].lower()[1:] == "sv":
            fileNameSV = base
        #print "Filename: {}, Status: {}, fileNameSV: {}".format(filename, status, fileNameSV)
        if len(status) or len(fileNameSV):
            return TranscriptionInfo(fileNameSV=fileNameSV, status=status)
        return TranscriptionInfo(fileNameSV=base)

    def solo_metadata_from_filename(self, filename):
        #print "Called solo_metadata_from_filename for ", filename
        si = self.solo_info_from_filename(filename)
        ti = self.transcription_info_from_filename(filename)
        ci = CompositionInfo()
        ri = RecordInfo()
        return SoloMetaData(si, ri, ti, ci)

    def solo_metadata_from_master_table(self, filename):
        filename = os.path.basename(filename)
        si = self.mt.read_solo_info(filename)
        ti = self.mt.read_transcription_info(filename)
        ri = self.mt.read_record_info(filename)
        ci = self.mt.read_composition_info(filename)
        smd = SoloMetaData(si, ri, ti, ci)

        if ri.musicbrainzid == "":
            print("WARNING: No musicbrainzid for {}".format(filename))

        return smd

    def get_pop_meta_data(self, filename, popsong_info):
        psi = PopSongInfo(filename=os.path.basename(filename))
        if not self.mt:
            return psi
        #psi = self.mt.read_pop_song_info(filename)
        try:
            psi = self.mt.read_pop_song_info(filename)
        except:
            pass
        for k in psi.__dict__:
            v = popsong_info.__dict__[k]
            if not v:
                popsong_info.__dict__[k] = psi.__dict__[k]
        pmd = PopSongMetaData(popsong_info)

        return pmd

    def get_solo_meta_data(self, filename):
        if self.mt:
            #OUT OF TRY
            #smd = self.solo_metadata_from_master_table(filename)
            #print smd
            try:
                smd = self.solo_metadata_from_master_table(filename)
            except:
                smd = self.solo_metadata_from_filename(filename)
        else:
            smd = self.solo_metadata_from_filename(filename)
        return smd
