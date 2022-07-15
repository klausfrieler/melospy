import os
import sys
import time

import pandas
import yaml

from melospy.basic_representations.metrical_annotation_param import *
from melospy.basic_representations.popsong_meta_data import *
from melospy.input_output.esac_reader import *
from melospy.input_output.lilypond_writer2 import *
from melospy.input_output.mastertable_reader import *
from melospy.input_output.mcsv_reader import *
from melospy.input_output.mcsv_writer import *
from melospy.input_output.mel_db_adapter_factory import *
from melospy.input_output.melody_importer import *
from melospy.input_output.midi_writer import *
from melospy.input_output.read_sv_project import *
from melospy.tools.commandline_tools.param_helper import ParameterContainer


class PopDanielMetaReader(object):
    """Helper class for reading Geerdes/Pop Daniel meta data.
    """
    def __init__(self, filename=""):
        self.filename = filename
        #self.df.columns.values =
        header = ["id", "title", "artist", "style", "year", "country_code", "country"]
        #self.df = pandas.read_csv(filename, names=header, sep=";", encoding="latin-1")
        try:
            #header = ["id", "title", "artist", "style", "year", "country_code", "country"]
            self.df = pandas.read_csv(filename, names=header, sep=";", encoding="latin-1")
        except:
            print("Could not read {}".format(filename))
            self.df = None

    def read_pop_song_info(self, csv_filename):
        csv_id = os.path.splitext(os.path.basename(csv_filename))[0]
        pi = PopSongInfo(filename=os.path.basename(csv_filename))
        tmp = self.df.query("id == '{}'".format(int(csv_id)))
        if len(tmp) == 0:
            return pi
        try:
            pi.title = str(list(tmp["title"])[0])
            pi.artist = str(list(tmp["artist"])[0])
            pi.style = str(list(tmp["style"])[0])
            pi.country = list(tmp["country_code"])[0]
        except:
           pass
        try:
            pi.year = int(list(tmp["year"])[0])
        except:
            pi.year = None
        return pi
