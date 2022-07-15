""" Class for chord types """

import re

import melospy.basic_representations.jm_util as util


class ChordType(object):
    """ Class for chord types """

    triadTypeLabel  = {"min":["min", "m", "-"], "dim":["o", "dim"], "aug":["aug", "+"], "sus":["sus"], "maj":["maj", ""], "nc":["nc"]}
    triadTypeStandardLabels  = {"min":"-", "dim":"o", "aug":"+", "sus":"sus", "maj":"", "nc":"NC"}
    seventhLabel    = { -1:"6",   0:"7",  1:"j7", "N/A":"" }
    ninthLabel      = { -1:"9b",  0:"9",  1:"9#" , "N/A":""}
    eleventhLabel   = {  0:"11",  1:"11#", "N/A":"" }
    thirteenthLabel = { -1:"13b", 0:"13",  "N/A":"" }

    lily_seventhLabel    = { -1:"6",   0:"7",  1:"maj", "N/A":"" }
    lily_ninthLabel      = { -1:"9-",  0:"9",  1:"9+" , "N/A":""}
    lily_eleventhLabel   = {  0:"11",  1:"11+", "N/A":"" }
    lily_thirteenthLabel = { -1:"13-", 0:"13",  "N/A":"" }

    def __init__(self, chordTypeLabel = None):
        self.__triadType = None
        self.__seventh = None
        self.__ninth = None
        self.__second_ninth = None
        self.__eleventh = None
        self.__thirteenth = None
        self.is_alt = False
        """ Initialize chord type """
        if chordTypeLabel != None:
            try:
                self.setChordTypeByLabel(chordTypeLabel)
            except:
                raise ValueError("Invalid chord label: {}".format(chordTypeLabel))
    def key_from_value(self, d, v):
        """ check if v is in given dictionary d,
            if v is a key, return the v,
            iv v is a value or part of a value list, return the corresponding key
        """
        if v in list(d.keys()):
            return v
        for key, val in list(d.items()):
            if ( isinstance( val, list)):
                if v in val:
                    return key
            else:
                if val == v:
                    return key
        else:
            raise Exception("{} can not be found in dictionary!".format(v))

    def getTriadType(self):
        """ Get chord triad type """
        return self.__triadType

    def getSeventh(self):
        """ Get chord seventh """
        return self.__seventh

    def getNinth(self):
        """ Get chord ninth """
        return self.__ninth

    def getSecondNinth(self):
        """ Get chord second ninth """
        return self.__second_ninth

    def getEleventh(self):
        """ Get chord eleventh """
        return self.__eleventh

    def getThirteenth(self):
        """ Get chord thirteenth """
        return self.__thirteenth

    def getOriginalLabel(self):
        """ Get chord thirteenth """
        return self.__originalLabel

    def setTriadType(self, val):
        """ Set chord triad type """
        val = val.lower()
        self.__triadType = self.key_from_value(self.triadTypeLabel, val);

    def setSeventh(self, val):
        """ Set chord seventh """
        self.__seventh = self.key_from_value(self.seventhLabel, val);

    def setNinth(self, val):
        """ Set chord ninth """
        self.__ninth = self.key_from_value(self.ninthLabel, val);

    def setSecondNinth(self, val):
        """ Set chord second ninth """
        self.__second_ninth = self.key_from_value(self.ninthLabel, val);

    def setEleventh(self, val):
        """ Set chord eleventh """
        self.__eleventh = self.key_from_value(self.eleventhLabel, val);

    def setThirteenth(self, val):
        """ Set chord thirteenth """
        self.__thirteenth = self.key_from_value(self.thirteenthLabel, val);

    def getChordTypeLabel(self, reduced=False):
        """ Return text label to represent chord type """
        triadType = self.triadTypeStandardLabels[self.__triadType]
        seventhLabel = self.seventhLabel[self.__seventh]
        if self.__triadType == "dim" and self.__seventh == 0:
            triadType = "m7b5"
            seventhLabel = ""
        if self.__triadType == "dim" and self.__seventh == -1:
            triadType = "o7"
            seventhLabel = ""

        if self.is_alt:
            ret = "7alt"
            return ret

        if reduced:
            if self.__triadType == "maj" and seventhLabel == "":
                triadType = "maj"
            ret = triadType + seventhLabel
        else:
            ret = triadType + \
                  seventhLabel + \
                  self.ninthLabel[self.__ninth] + \
                  self.eleventhLabel[self.__eleventh] + \
                  self.thirteenthLabel[self.__thirteenth]
        return ret

    def getLilypondLabel(self):
        """ Return text label to represent chord type """
        triadType = self.__triadType

        label7 = self.lily_seventhLabel[self.__seventh]
        label9 = self.lily_ninthLabel[self.__ninth]
        label11 = self.lily_eleventhLabel[self.__eleventh]
        label13 = self.lily_thirteenthLabel[self.__thirteenth]
        #print "triadType ", triadType , self.__seventh

        if triadType == "maj":
            triadType = ""

        add_sus4 = False

        if triadType == "sus":
            triadType = ""
            add_sus4 = True

        if triadType == "dim":
            if label7 == "7":
                triadType= "min5-"
            if label7 == "6":
                label7 = "7"

        if triadType == "min":
            if label7 == "maj":
                triadType  = "min7+"
        extensions = ""


        ret = triadType
        #print "inpout:{}, triad: {}, l7:{}, l9:{}, l11:{}, l13:{}".format(self, ret, label7, label9, label11, label13)
        raisedFifth = False
        if triadType == "aug":
            triadType  = ""
            #extensions = "5+"
            raisedFifth = True

        if label7 == "maj" and triadType != "min7+":
            highest = "maj"
        else:
            highest = ""

        if label13:
            highest += label13
            extensions = label9 + label11
        elif label11:
                highest += label11
                extensions = label9
        elif label9:
                highest += label9
                extensions = ""
        elif label7:
            extensions = ""
            highest = label7
            if raisedFifth:
                highest = label7 + "7"

        else:
            if extensions:
                highest = extensions
                extensions = ""
        #if raisedFifth:
        #    print "highest: '{}'".format(highest)
        #    print "ext: '{}'".format(extensions)
        ret = triadType + highest

        if add_sus4:
            ret += "sus4"

        if raisedFifth:
            extensions += "5+"

        if extensions:
            if extensions == "5+":
                ret += extensions
            else:
                ret += "."  + extensions
        #if raisedFifth:
        #    print ret
        return ret

    def setChordTypeByLabel(self, label):
        """
        Set chord type by label,
        function looks for 13th, 11th, 9th, 7th, and the triad type
        and iteratively removes found chord parts from the chord label
        """
        self.__originalLabel = label
        # look for 13th & remove it from label
        val = util.find_after_sort(label, list(self.thirteenthLabel.values()))
        self.setThirteenth(val)
        label = label.replace(val, "")

        # look for 11th & remove it from label
        val = util.find_after_sort(label, list(self.eleventhLabel.values()))
        self.setEleventh(val)
        label = label.replace(val, "")

        # look for 9th & remove it from label
        val = util.find_after_sort(label, list(self.ninthLabel.values()))
        self.setNinth(val)
        label = label.replace(val, "")

        val = util.find_after_sort(label, list(self.ninthLabel.values()))
        #print self.__originalLabel , label, val
        self.setSecondNinth(val)
        label = label.replace(val, "")
        # find halfdim special notation
        halfdim = False
        if label.find("min7b5") > -1 or label.find("m7b5") > -1 or label.find("-7b5") > -1:
            halfdim = True
        # find dominant7b5 and substitute it with "alt"
        #(workaround, maybe not fully justified)
        if (label.find("7b5") > -1 or label.find("7b5") > -1) and not halfdim:
            label = label.replace("b5", "alt")
        # look for 7th & remove it from label
        val = util.find_after_sort(label, list(self.seventhLabel.values()))
        self.setSeventh(val)
        label = label.replace(val, "")

        # special treatment for "dim", "halfdim" and "alt" chords
        if label.find("dim") > -1 or label.find("o") > -1:
            self.setTriadType("dim")
            if self.getSeventh() != "N/A":
                self.setSeventh(-1)
            val = "dim"
        elif halfdim :
            self.setTriadType("dim")
            val = "dim"
        elif label.find("alt") > -1:#
            self.setTriadType("maj")
            val = "maj"
            self.setNinth("9#")
            self.setSecondNinth("9b")
            self.setEleventh("11#")
            self.setThirteenth("13b")
            self.is_alt= True
        else:
            # look for triad type
            val = util.find_after_sort(label, list(self.triadTypeLabel.values()))
            self.setTriadType(val)
        #higher tensions usually imply lower ones as well, only a thirteenth does not imply an eleventh (but ninth and seventg)
        if self.getThirteenth() != "N/A" :
            if self.getNinth() == "N/A":
                self.setNinth("9")
            if self.getSeventh() == "N/A":
                self.setSeventh("7")
        if self.getEleventh() != "N/A" :
            if self.getNinth() == "N/A":
                self.setNinth("9")
            if self.getSeventh() == "N/A":
                self.setSeventh("7")
        if self.getNinth() != "N/A":
            if self.getSeventh() == "N/A":
                self.setSeventh("7")
        # Give warning
        #if len(label.replace(val,"")) > 0:
            #print "Warning! '" + label + "' of the chord type label could not be processed!"

    def __str__(self):
        return "{}|7:{}|9:{}|11:{}|13:{}".format(self.getTriadType(), self.getSeventh(), self.getNinth(), self.getEleventh(), self.getThirteenth())

    # define attributes
    triadType           = property(getTriadType, setTriadType)
    seventh             = property(getSeventh, setSeventh)
    ninth               = property(getNinth, setNinth)
    second_ninth        = property(getSecondNinth, setSecondNinth)
    eleventh            = property(getEleventh, setEleventh)
    thirteenth          = property(getThirteenth, setThirteenth)
    originalLabel       = property(getOriginalLabel)
