""" Class implementation of MCSV reader"""
import os
import re
import sys

from melospy.basic_representations.esac_info import *
from melospy.basic_representations.jm_util import bpm_to_s, chomp
from melospy.basic_representations.melody import *
from melospy.basic_representations.note_name import *
from melospy.basic_representations.signature import *
from melospy.input_output.esac_parser import *


class EsacReader(object):
    """Class for reading EsAC files"""
    allowed_units = [1, 2, 4, 8, 16, 32, 64, 128, 256]

    def __init__(self, filename, tempo = bpm_to_s(120)):
        self.setTempo(tempo)
        self.read(filename)

    def getEventList(self):
        return self.__events

    def getEsacMelody(self):
        return self.__melody

    def getMelody(self):
        return self.solo

    def getSolo(self):
        return self.solo

    def getKey(self):
        return self.__key

    def getSignatures(self):
        return self.__signatures

    def getUnit(self):
        return self.__unit

    def getMelID(self):
        return self.__melID

    def getEsacID(self):
        return self.__esacID

    def getChords(self):
        return self.__chords

    def getTempo(self):
        return self.__tempo

    def setTempo(self, tempo):
        self.__tempo = tempo

    def getEsacInfo(self):
        return self.__esacinfo

    def get_bar_lengths(self):
        if self.__signatures == None:
            return None
        lengths = []
        for i in range(len(self.__signatures)):
            num = self.__signatures[i].numerator
            denom = self.__signatures[i].denominator
            unit = self.getUnit()
            lengths.append(num * unit/denom)
        return lengths

    def read_metadata(self, ef):
        collection  = ef.split("\n")[0]
        if collection.find("[") != -1:
            if collection.find("]") == -1:
                collection = collection.split("[")[1]
            else:
                collection = ""
        title       = self.get_field(ef, "CUT")
        #sys,exit(0)
        region      = self.get_field(ef, "REG")
        function    = self.get_field(ef, "FCT")
        text        = self.get_field(ef, "TXT")
        if function == "":
            function    = self.get_field(ef, "FKT")
        source = self.get_field(ef, "TRD")
        if source == "":
            source = self.get_field(ef, "SRC")
        comment  = self.get_field(ef, "CMT")
        if comment == "":
            comment = self.get_field(ef, "BEM")
        cnr = self.get_field(ef, "CNR")
        if self.__signatures != None:
            sig_str = " ".join([str(sig) for sig in self.__signatures])
        else:
            sig_str  = "FREE"
        melstring = self.get_field(ef, "MEL")

        return EsacInfo(collection=collection, title=title,
                        melid=self.__melID, esacid=self.__esacID, region=region,
                        function=function, source=source, cnr=cnr,
                        key=str(self.__key), unit=str(self.__unit),
                        signature=sig_str, text=text,
                        melstring=melstring)

    def read(self, filename):
        """
        Read Esac file. Parse meta data fields, then invoke EsacParser
        on the melody string, and hope for the best
        """
        self.__events = []
        self.__melody = None
        self.__melID = None
        self.__esacID = None
        self.__unit = None
        self.__key = None
        self.__signatures = None
        self.__chords = None

        with open(filename, 'r') as esacfile:
            ef =  esacfile.read()
            try:
                self.parse_KEY(self.get_field(ef, "KEY"))
            except Exception as e:
                raise ValueError("Missing or invalid KEY field ({})".format(e.args[0]))
            try:
                self.__melody = chomp(self.get_field(ef, "MEL").replace("//", ""))
                if self.__melody == "":
                    raise
                #normalize:
                #chop some extra white space at end of line
                self.__melody = re.sub(r"\s+\n+", "\n", self.__melody)

                #use ' as phrase marks,
                #in new style esac no problem with extra white space at begining of line
                # in old style esac use @ for possible bars at beginning of line
                if "|" not in self.__melody:
                    self.__melody = re.sub(r"\n+\s+", "'@", self.__melody)
                else:
                    self.__melody = re.sub(r"\n+\s+", "'", self.__melody)

                self.__melody = re.sub("\n+", "'", self.__melody)

               #| as bar separator, allow whitespace before and after | signs for readabilitys
                self.__melody = re.sub("[ ]*[|]{1}[ ]*", "|", self.__melody)
                self.__melody = re.sub("[ ]+", "|", self.__melody)
                #print self.__melody
            except Exception:
                raise ValueError("No MEL field found")
            try:
                self.__chords = self.get_field(ef, "CHORDS")
            except:
                pass
        self.__esacinfo = self.read_metadata(ef)
        esac_parser = EsacParser(self.__melody, self.unit, self.get_bar_lengths(), self.signatures, self.key, self.tempo)
        esac_parser.solo.__dict__["esacinfo"] = self.__esacinfo
        self.solo = esac_parser.solo
        return True

    def get_field(self, esac_file, fieldname):
        """Retrieves AskSam formatted field from the Esac file/string"""
        #expr = ".*(\s{}\[)(.*?)(\])".format(fieldname.upper())
        expr = r".*(\s{}\[)(.*?)(\])".format(fieldname.upper())
        field = re.compile(expr, re.DOTALL)
        match = field.match(esac_file)
        if match:
            #print "Match: {}".format(chomp(match.group(2)))
            return chomp(match.group(2))
        else:
            expr = r"(\A{}\[)(.*?)(\])".format(fieldname.upper())
            field = re.compile(expr, re.DOTALL)
            match = field.match(esac_file)
            if match:
                return chomp(match.group(2))
            return ""

    def split_raw_sm_file(self, filename):
        path = os.path.dirname(filename)
        #print path
        with open(filename) as smfile:
            ef = smfile.read()
            tunes = ef.split("\n\n")
            for tune in tunes:
                key = self.get_field(tune, "KEY")
                el = [chomp(e) for e in re.compile(r"\s+").split(key)]
                esacID = el[0]
                if len(esacID) == 0:
                    continue
                #print esacID
                tunename = (path +"/" + esacID + ".esa")
                tune = chomp(tune)
                tmp = tune.split("\n")
                if len(tmp[0]) == 0:
                    print(esacID)
                    #tune = "\n".join([_ for _ in tmp[1:])
                if tmp[0] != "KOLBERG":
                    tune = "KOLBERG\n" + tune
                with open(tunename, "w") as tunefile:
                    tunefile.write(tune)

    def is_allowed_unit(self, unit):
        try:
            u = int(unit)
        except:
            return False
        if u not in self.allowed_units:
            return False
        return True

    def reparse_KEY_hack(self, key, el):
        #Hack due to some files in Balladen kollektion where key and unit got
        #glued together by a period. So try read them
        comps = el[0].split(".")
        #print comps, el, len(el)
        if len(el) >= 3 and len(comps) == 2:
            tmp = [comps[0], comps[1]]
            for i in range(1, len(el)):
                tmp.append(el[i])
            #another nasty special case:
            # some files habe EsacIds of the FORM ID.SOMETHING
            #print tmp
            if self.is_allowed_unit(tmp[2]):
                return el
            el = tmp
            #print el
        return el

    def parse_KEY(self, key):
        el = [chomp(e) for e in re.compile(r"\s+").split(key)]
        #print el
        if not self.is_allowed_unit(el[1]):
            el = self.reparse_KEY_hack(key, el)
            if not self.is_allowed_unit(el[1]):
                raise ValueError("Invalid unit:  {}".format(el[1]))
        self.__unit = int(el[1])
        if len(el) < 4:
            raise ValueError("Invalid KEY field:{}".format(key))
        self.__esacID = el[0]

        self.__key = NoteName(el[2])
        if self.__unit == 1:
            self.__unit = 2
            for i in range(3, len(el)):
                el[i] = el[i].replace("/1", "/2")
        try:
            self.__signatures = [Signature.fromString(el[i]) for i in range(3, len(el))]
        except:
            self.__signatures = None
        if self.__signatures:
            for s in self.__signatures:
                if self.__unit < s.denominator:
                    raise ValueError("Unit ({}) invalid for signature ({})".format(self.__unit, str(s)))

    def __str__(self):
        ret = str(self.__esacinfo)
        ret += "\nUnit: {}\nKey: {}\nSignature:{}\nTempo:{} bpm\n".format(self.unit, self.key, self.signatures, round(bpm_to_s(self.tempo), 1))
        ret += "MEL:\n{}\n".format(self.melody)
        if self.__chords and len(self.__chords):
            ret += "CHORDS:\n{}\n".format(self.__chords)

        return ret

    melody      = property(getMelody)
    events      = property(getEventList)
    esacmelody  = property(getEsacMelody)
    key         = property(getKey)
    signatures  = property(getSignatures)
    unit        = property(getUnit)
    melid      =  property(getMelID)
    esacid      = property(getEsacID)
    chords      = property(getChords)
    tempo       = property(getTempo, setTempo)
    esacinfo    = property(getEsacInfo)
