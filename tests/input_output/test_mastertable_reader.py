#!/usr/bin/env python

""" Class implementation of TestMasterTableReader"""

import csv
import os
import unittest

import pytest

from melospy.input_output.mastertable_reader import *

from tests.rootpath import *

class TestMasterTableReader( unittest.TestCase ):

    def read_filenames_sv(self, filename):
        test_names = []
        with open(filename, "r") as fp:
            content = csv.reader(fp, delimiter=";")
            test_names = [row[0] for row in content]
        return test_names

    def getMTPath(self):
        mt_path = add_data_path("Solodatenbank_MASTERTABELLE.xlsx")
        #mt_path = "e:/projects/science/jazzomat/projects/weimar_bass_database/sv/Bass-MASTERTABELLE_END_MP.xlsx"
        return mt_path

    #@pytest.mark.skip(reason="Path mismatch")
    def testReadColumn(self):
        mt_path = self.getMTPath()
        mt_reader = MasterTableReader(mt_path)

        col = mt_reader.read_column("FilenameSolo")
        #print "Read {} elements for {}".format(len(col), "FilenameSolo")
        self.assertEqual(len(col), 456)
        col = mt_reader.read_column("FilenameOriginalAudio")
        #print "Read {} elements for {}".format(len(col), "FilenameOriginalAudio")
        self.assertEqual(len(col), 456)
        
    #@pytest.mark.skip(reason="Path mismatch")
    def testMasterTableReader(self):
        """ Initialize module """
        mt_path = self.getMTPath()
        #mt_path = os.path.join(root_path(), "analysis/data/METADATA/omnibook_meta_final.xlsx")
        mt_reader = MasterTableReader(mt_path)
        #fsv = mt_reader.guess_filename_sv_base(63)
        #print mt_reader.find_value_by_column("FilenameSolo", "ArtPepper_Anthropology_Solo", "PerformerLastName")
        #for i in range(mt_reader.nrows):
        #    fsv = mt_reader.guess_filename_sv_base(i)
        #    print "fsv row {}: {}".format(i, fsv)
        #dirlist_path = os.path.join(root_path(), "analysis/data/PREFINAL/dir.txt")
        #dirlist_path = os.path.join(root_path(), "analysis/data/MIDLEVEL/RELEASE1.2/FINAL/dir.txt")
        dirlist_path = add_data_path("sv_dir.txt")
        #dirlist_path = "e:/projects/science/jazzomat/projects/weimar_bass_database/sv/bass_sv_dir.txt"

        test_names = self.read_filenames_sv(dirlist_path)
        #print "Read:\n", "\n".join(test_names)
        found = 0
        invalid = []
        row = mt_reader.find_row(test_names[0])
        # print test_names

        for fsv in test_names:
            row = mt_reader.find_row(fsv)
            if row > -1:
                print("Found {} in row {}".format(fsv, row))
                found += 1
            else:
                invalid.append(fsv)
                print("***Could not find {} in master table".format(fsv))
        print("Found {} out of {}, {} missing".format(found, len(test_names), len(test_names)-found))
        empty = 0

        for i in range(0, len(test_names)):
            #print "="*60
            ti = mt_reader.read_transcription_info(test_names[i])
            #print "Transcriber: '{}'".format(ti.transcriber)
            si = mt_reader.read_solo_info(test_names[i])
            ri = mt_reader.read_record_info(test_names[i])
            ci = mt_reader.read_composition_info(test_names[i])
            #print "Tonality Type: '{}'".format(ci.tonalitytype)
            mbzid = ri.getMusicBrainzID()
            if mbzid == "":
                empty += 1
                print("File: ", test_names[i])
                print("MBZID: '{}'".format(ri.getMusicBrainzID()))
                #print ci
                print("Title '{}' for {}".format(mt_reader.read_cell(test_names[i], "Title"), test_names[i]))
                print("Performer '{}' for {}".format(mt_reader.read_cell(test_names[i], "PerformerLastName"), test_names[i]))
        print("Found {} tracks without mbzid".format(empty))
""" Function calls all unit tests """
if __name__ == '__main__':
    alltests = unittest.TestSuite([unittest.TestLoader().loadTestsFromTestCase(TestMasterTableReader)])
    unittest.main()
