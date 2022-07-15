""" Class for ideas (for Ideational Flow/Midlevel Analysis (IFA/MLA)"""

import re

import melospy.basic_representations.jm_util as util
from melospy.basic_representations.section_list import *
from melospy.basic_representations.solo import *


class IFAFilter(object):
    """ Class for filtering and and manipulating section lists of ideas"""
    filters = ["id", "full-type", "main-type", "backref", "glue", "movement"]
    def __init__(self, solo):
        self.solo = solo
        self.IFA = solo.getIFASections()
        self.NA_str = "NA"

    def filter(self, filter_type="id", include_voids=False, event_based=True):
        if self.IFA == None:
            return None
        vals = self.IFA.getValues(event_based)
        ret = []
        #print "IFA_filter:", filter_type
        for v in vals:
            add_void = not event_based and include_voids and v.void_prefix
            if filter_type == "id":
                if add_void:
                    ret.append("void")
                ret.append(v.label)
            elif filter_type == "full-type":
                if add_void:
                    ret.append("void")
                ret.append(v.type_string())
            elif filter_type == "main-type":
                if add_void:
                    ret.append("void")
                ret.append(v.type)
            elif filter_type == "glue":
                if add_void:
                    ret.append(0)
                glue = 1 if v.glue else 0
                ret.append(glue)
            elif filter_type == "modifier":
                if add_void:
                    ret.append("N")
                mod = v.modifier
                if mod == "":
                    mod = "N"
                ret.append(mod)
            elif filter_type == "modifier-bin":
                if add_void:
                    ret.append(0)
                mod = 1 if len(v.modifier)>0 else 0
                ret.append(mod)
            elif filter_type == "backref":
                if add_void:
                    ret.append(0)
                ret.append(v.backref)
            elif filter_type == "backref-bin":
                if add_void:
                    ret.append(0)
                bf = 1 if v.backref>0 else 0
                ret.append(bf)
            elif filter_type == "main-direction":
                if add_void:
                    ret.append(self.NA_str)
                main_dir = v.getMainDirection(reduced=False).replace("undefined", self.NA_str)
                ret.append(main_dir)
            elif filter_type == "main-direction-reduced":
                if add_void:
                    ret.append(self.NA_str)
                main_dir = v.getMainDirection(reduced=True).replace("undefined", self.NA_str)
                ret.append(main_dir)
            else:
                raise ValueError("Unknown idea filter:{}".format(filter_type))
        return ret


    def getPhrasesFromIFA(self):
        if self.IFA == None:
            return None
        psl = SectionList("PHRASE")
        i = 1
        startID = 1
        endID = -1
        glue_flag = False
        for v in self.IFA:
            if v.getValue().glue:
                endID = v.endID
                glue_flag = True
                #print "GLue: ", endID
                continue
            if endID != -1:
                sect = Section("PHRASE", i, startID, endID)
                psl.append(sect)
                i += 1
                #print "Added: ", startID, endID
            startID = v.startID
            endID = v.endID

        if glue_flag:
            #print "Last: ", startID, endID
            sect = Section("PHRASE", i, startID, endID)
            psl.append(sect)

        return psl

    def _getIdeaDuration(self, startID, endID, type="IOI", units="sec"):
        """
            Get duration or IOI of idea (parameter type) and in different units.
            Types:
                IOI:        Interval between onsets of first event in idea
                             first event in next idea ()
                duration:   Interval between onset of first event and
                            offset of last event in the idea
                notes:      Number of notes ()
            Allowed units:
                sec:    Seconds (default)
                bars:   fractional bars (decimal representation )
        """
        if self.IFA == None:
            return None
        start = end = 0
        if type == "notes":
            end = endID + 1
            start = startID
        elif type == "IOI":
            if units =="bars":
                start = self.solo[startID].mp.toDecimal()
                end   = self.solo[endID].mp.toDecimal()
            else:
                start = self.solo[startID].onset
                end   = self.solo[endID].onset
                #print "IOI_sec", end-start
        elif type == "duration":
            if units == "bars":
                return None
            else:
                start = self.solo[startID].onset
                end   = self.solo[endID].onset + self.solo[endID].duration
                #print startID, endID, start, end
                #print start, self.solo[endID].onset, self.solo[endID].duration, end
                #print "Dur_sec", end-start
        else:
            raise ValueError("Invalid duration type:{}".format(type))
        #print end, start
        return end-start

    def getIdeaDurations(self, type="IOI", units="sec", include_voids=False):
        """
            Get duration or IOI of idea (parameter type) and in different units.
            Types:
                IOI:        Interval between onsets of first event in idea
                             first event in next idea ()
                duration:   Interval between onset of first event and
                            offset of last event in the idea
                notes:      Number of notes ()
            Allowed units:
                sec:    Seconds (default)
                bars:   fractional bars (decimal representation )
        """
        if self.IFA == None:
            return None
        ret = []
        oois = None
        for i, v in enumerate(self.IFA):
            if type == "notes":
                dur = len(v)
                if include_voids and v.getValue().void_prefix:
                    ret.append(0)
            elif type == "count":
                if include_voids and v.getValue().void_prefix:
                    ret.append(1)
                ret.append(1)
            elif type == "IOI":
                correction = 0
                startID = v.startID

                if i == len(self.IFA)-1:
                    endID = v.endID
                else:
                    endID = self.IFA[i+1].startID
                    if self.IFA[i+1].getValue().void_prefix:
                        #endID = v.endID
                        if units == "sec":
                            if oois == None:
                                oois = self.solo.getOOIs()
                            correction = oois[v.endID]
                        else:
                            endID = v.endID

                if include_voids and i > 0 and v.getValue().void_prefix:
                    dur = self._getIdeaDuration(self.IFA[i-1].endID, v.startID, type=type, units=units)
                    ret.append(dur)

                dur = self._getIdeaDuration(startID, endID, type=type, units=units)-correction
            elif type == "duration":
                if units == "bars":
                    raise ValueError("Unit 'bars' not available for type 'duration'")
                startID = v.startID
                endID = v.endID
                if include_voids and v.getValue().void_prefix and startID>0:
                    if oois == None:
                        oois = self.solo.getOOIs()
                    dur = oois[startID-1]
                    ret.append(dur)
                dur = self._getIdeaDuration(startID, endID, type=type, units=units)
            else:
                raise ValueError("Invalid duration type:{}".format(type))
            ret.append(dur)
        if type == "count":
           ret = [sum(ret)]
        return ret

    def getIdeaGaps(self, include_voids= False):
        oois = self.solo.getOOIs()
        if self.IFA == None:
            return None
        ret = []
        for i in range(1, len(self.IFA)):
            ret.append(oois[self.IFA[i].startID-1])
        return ret
