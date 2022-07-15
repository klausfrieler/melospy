""" Class implementation of SectionList """

from melospy.basic_representations.form_name import *
from melospy.basic_representations.idea import *
from melospy.basic_representations.section import *


class _SectionConsistencyChecker(object):
    """
        Callable class for extra consistency checking of sections list, for internal use only
        NB: At the same time a fancy excercise for callable object. Could be just a method of
        section list, but well: It's more fancy this way!
    """
    def __init__(self, sectionType=None):
        """ Initialize class """
        self.__type = sectionType
        self.__reason = ""

    def getReason(self):
        return self.__reason

    def __call__(self, sect1, sect2):
        if self.__type == 'KEY' or self.__type == 'CHORD' or self.__type == "IDEA":
            return True
        elif self.__type == 'CHORUS' or self.__type == 'PHRASE' or self.__type == 'BAR':

            start = 1 if sect1 == None else sect1.getValue()
            end   = 1 if sect2 == None else sect2.getValue()

            #if (start + 1) == end:
            if start < end:
                return True
            else:
                self.__reason = "ID {} is smaller than {}".format(end, start)
                return False

        elif self.__type == 'FORM':
            try:
                formlist = sect1.getValues()
            except Exception:
                return False

            formitem = sect2.getValue()
            #Start of new Form run-through is always okay.
            #print formitem, formitem.getLetter()
            if formitem.getLabel()=="A1" or formitem.getLetter()=="I" or formitem.hasWildcard():
                return True
            #find last A1
            found = -1
            #print "len(formlist)", len(formlist)
            for i in range(len(formlist)):
                cur = formlist[len(formlist)-i-1]
                #print "Cur: {}, hasWC:{}".format(cur, cur.hasWildcard())
                if cur.getLabel() == "A1" or cur.hasWildcard():
                    found = len(formlist)-i-1
                    break
            #if no start or no element with wildcard was found, that's not good.
            if found == -1:
                self.__reason = "Found neither beginning of form nor wildcard"
                return False
            #now do the hard stuff, try to build a FormDefinition object for
            #consistency checking
            formlist = formlist[found:]
            formlist.append(formitem)
            try:
                fd = FormDefinition(formlist)
                return True
            except Exception as e:
                self.__reason = str(e)
                return False
        raise ValueError("Invalid section type: " + self.__type)


class SectionList(object):
    """
    SectionList is a gap-free list of Sections objects
    """

    types = {'KEY':Key, 'FORM':FormName, 'PHRASE':int, 'CHORUS':int, 'CHORD':Chord, 'BAR': int, 'IDEA': Idea}

    def __init__(self, sectionType=None, sectionList=None):
        """ Initialize class """
        #print "SectionList.init {}, {}".format(sectionType, sectionList)
        if sectionList:
            self.__list = sectionList
        else:
            self.__list = []
        self.setType(sectionType)

    def clone(self):
        """ Returns a deep copy"""
        #print "SectionList.clone"
        tmp_list = [__.clone() for __ in self.__list]
        return SectionList(self.getType(), tmp_list)

    def append(self, sect, withCheck=True):
        """
            Use (only) this method to add elements.
            Checks for sections type consistency.
        """
        if not isinstance(sect, Section):
            raise TypeError("Expected Section-type element")
        t = sect.getType()
        if self.getType() is not None:
            if  t != self.getType():
                raise ValueError("Expected section of type {}, got {}".format(self.getType(), t))
        else:
            self.setType(t)
        if self.isEmpty():
            self.__list.append(sect)
        else:
            last = self.__list[-1]
            if sect.getStartID() != last.getEndID() + 1:
                raise ValueError("Section must start with {} instead of {}.".format(last.getEndID()+1, sect.getStartID()))
            else:
                #print "append called {}, last:{}, sect:{}".format(withCheck, last, sect)
                if withCheck:
                    ok = self.__checker(last, sect) if (self.__type != 'FORM' and self.__type != 'IDEA') else self.__checker(self, sect)
                else:
                    ok = True
                if ok:
                    self.__list.append(sect)
                else:
                    raise ValueError("Section value not consistent: " + self.__checker.getReason())
        return self

    @staticmethod
    def _section_value_from_string(val, sect_type):
        if sect_type == "CHORD":
            val = Chord(val)
        elif sect_type == "KEY":
            val = Key(val)
        elif sect_type == "FORM":
            val = FormName(val)
        elif sect_type == "IFA":
            val = Idea(val)
        elif sect_type == "PHRASE" or sect_type == "CHORUS":
            val = int(val)
        return val

    @staticmethod
    def fromEventList(vec, sect_type):
        ret = SectionList()
        if len(vec) == 0:
            print("Got empty value list")
            return ret
        last = vec[0]
        start = 0
        for i, v in enumerate(vec):
            #print "Testing I={} V={}, last={}".format(i,v, last)
            if v != last:
                val = SectionList._section_value_from_string(last, sect_type)
                sect = Section(sect_type, val, start, i-1)
                #print "Added new section ", sect
                ret.append(sect)
                last = v
                start = i
        val = SectionList._section_value_from_string(v, sect_type)
        sect = Section(sect_type, val, start, len(vec)-1)
        ret.append(sect)
        return ret

    def clear(self):
        del self.__list
        self.__list = []
        self.__type = None

    def setType(self, sectionType):
        """ Set type of list"""
        if sectionType is None:
            self.__type = None
            return self

        #if not isinstance(sectionType, basestring):
        #    raise TypeError("Expected string, one of" + ",".join(self.types.keys()))

        if str(sectionType).upper() in list(self.types.keys()):
            self.__type = sectionType.upper()
            self.__checker = _SectionConsistencyChecker(self.__type)
        else:
            raise ValueError("Invalid section type: {}".format(sectionType))
        return self

    def getType(self):
        """ Get type of section"""
        return self.__type

    def getValues(self, eventBased=False):
        """ Get list of section values"""
        if self.isEmpty():
            return []
        if eventBased:
            ret = []
            for s in self.__list:
                for __ in range(len(s)):
                    ret.append(s.getValue())
        else:
          ret = [s.getValue() for s in self.__list]
        return ret

    def getList(self):
        """ Get value of sections in list"""
        return self.__list

    def isEmpty(self):
        return len(self.__list) == 0

    def getStartID(self):
        if not self.isEmpty():
            return self.__list[0].getStartID()
        raise RuntimeError("SectionList empty.")

    def getEndID(self):
        if not self.isEmpty():
            return self.__list[-1].getEndID()
        raise RuntimeError("SectionList empty.")

    def getStartIDs(self):
        return [_.getStartID() for _ in self.__list]

    def getEndIDs(self):
        return [_.getEndID() for _ in self.__list]


    def shiftIDs(self, delta):
        """ shiftIDs of all section in list by delta"""
        for s in self.__list:
            s.shiftIDs(delta)
        return self

    def eventCount(self):
        if not self.isEmpty():
            return self.getEndID()-self.getStartID()+1
        return 0

    def flatten(self, start_value=None):
        if len(self) == 0:
            return None
        events = self.getValues(eventBased=True)
        start_ids = self.getStartIDs()
        end_ids = self.getEndIDs()
        start = start_ids[0]
        end = end_ids[-1]
        ids = list(range(start, end+1))
        ret = {}
        for i in range(len(events)):
            tmp = ids[i]
            if tmp in start_ids:
                if tmp == start and start_value == None:
                    marker = "start-list"
                else:
                    if events[i] == start_value:
                        marker = "start-list"
                    else:
                        marker = "start"
            elif tmp in end_ids:
                if tmp == end:
                    marker = "end-list"
                else:
                    marker = "end"
            else:
                marker = "inner"
            ret[tmp] =  {"#": i, "value": events[i], "marker": marker}
        return ret

    def pad(self, left_pad_val, min_id, max_id, right_pad_val=None):
        s = self.getStartID()
        if min_id < s:
            sect = Section(self[0].type, left_pad_val, min_id, s-1)
            self.__list.insert(0, sect)
        e = self.getEndID()
        if e < max_id:
            if right_pad_val is None:
                sect_type = self[-1].type
                if sect_type == "PHRASE" or sect_type == "CHORUS":
                    right_pad_val = self[-1].value + 1
                elif sect_type == "CHORD":
                    right_pad_val = Chord("NC")
                else:
                    raise ValueError("Need explicit righ pad val for sections of type:{}".format(self[0].type))

            sect = Section(self[0].type, right_pad_val, e+1, max_id)
            self.append(sect)
        return self

    def get_sections_by_value(self, value):
        ret = []
        for sect in self.__list:
            if sect.value == value:
                ret.append(sect)
        return ret

    def get_sections_by_ids(self, startID, endID=None):
        ret = []
        if endID is None:
            endID = startID
        if startID > endID:
            startID, endID = endID, startID
        start_section_idx = -1
        end_section_idx = -1
        for i, sect in enumerate(self.__list):
            if sect.is_inside(startID):
                start_section_idx = i
            if sect.is_inside(endID):
                end_section_idx = i
        if start_section_idx < 0 or end_section_idx <0:
            return ret
        #print start_section_idx, end_section_idx
        for i in range(start_section_idx, end_section_idx+1):
            ret.append(self.__list[i])
        return ret

    def concat(self, sectionList, withCheck=True):
        if sectionList.type != self.type:
            raise ValueError("Expected section list of type '{}', got: '{}' ".format(self.type, sectionList.type))
        offset = self.getEndID()-sectionList.getStartID()+1
        for s in sectionList.__list:
            self.append(s.clone().shiftIDs(offset), withCheck)
        return self

    def truncate(self, startID, endID, normalize=False, renumber=False):
        ret = []
        if startID > endID:
            raise ValueError("StartID '{}' must less than endID '{}' ".format(startID, endID))
        if startID > self.__list[-1].endID:
            raise ValueError("StartID '{}' must less than highest ID in list'{}' ".format(startID, self.__list[-1].endID))
        if endID < self.__list[0].startID:
            raise ValueError("endID '{}' must less than smallest ID in list'{}' ".format(startID, self.__list[0].startID))

        for s in self.__list:
            #print "startID: {}, endID:{}, s.startID:{}, s.endID:{}".format(startID, endID, s.startID, s.endID)
            if s.startID >= startID:
                if s.endID <= endID:
                    ret.append(s)
                elif s.startID<=endID:
                    ret.append(s.snip(s.startID, endID))
            else:
                if s.endID >= startID:
                    if s.endID <= endID:
                        ret.append(s.snip(startID, s.endID))
                    else:
                        ret.append(s.snip(startID, endID))
                else:
                    pass
        if normalize:
            for s in ret:
                s.shiftIDs(-startID)
        if renumber:
            self.renumber

        self.__list = ret
        return self

    def renumber(self, start=1):
        if self.__type == "PHRASE" or  self.__type == "CHORUS":
            for s in self:
                s.value = start
                start += 1
        return self

    def filter(self, filter_func=None, filter_type="value", negate=False):
        """
            Filters sections according to a filter_func
            and return list of Sections (not a SectionList!)
        Parameter:
            filter_func: Boolean function
            filter_type: Type of filter. Allowed types:
                         "value", "position", "enumeration"
            negate: Negate filter condition
        """
        ret = []
        for i, sect in enumerate(self.__list):
            if filter_type == "value":
                cond = filter_func(sect.getValue())
            elif filter_type == "position":
                cond = filter_func(sect.startID(), sect.endID())
            elif filter_type == "enumerate":
                cond = filter_func(i)
            else:
                raise ValueError("Invalid filter_type: '{}'".format(filter_type))
            if negate:
                cond = not cond
            if cond:
                ret.append(sect)
        return ret

    def __getitem__(self, i):
        """ Get element i from section list"""
        try:
            val = self.__list[i]
        except IndexError:
            raise IndexError("Index out of bounds")
        return val

    def toString(self):
        if self.isEmpty():
            return "(Empty List)"
        s = "\n".join([str(sect) for sect in self.__list])
        return(s)

    def __eq__(self, other):
        if not isinstance(other, SectionList):
            return False
        return self.type == other.type and self.list == other.list

    def __ne__(self, other):
        return not self.__eq__(other)


    def __str__(self):  return self.toString()
    def __len__(self):  return len(self.__list)
    #def __repr__(self): return self.toString()

    type        = property(getType, setType)
    list        = property(getList)
