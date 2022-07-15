#!/usr/bin/env python

""" Unit test for class SectionList """

import unittest

from melospy.basic_representations.chord import *
from melospy.basic_representations.key import *
from melospy.basic_representations.scale import *
from melospy.basic_representations.section_list import *


class TestSectionList( unittest.TestCase ):

    def testConstructor(self):
        n = NoteName("Ab")
        k = Key("Ab", 'maj')
        c = Chord("Caug13b")

        # test with valid initialization
        sl = SectionList("KEY")
        self.assertEqual(sl.getType(), "KEY")

        sl = SectionList()
        self.assertEqual(sl.isEmpty(), True)

        sl.append(Section("KEY", Key("Ab"), 1,  10))
        sl.append(Section("KEY", Key("Db"), 11, 20))
        sl.append(Section("KEY", Key("Db"), 21, 30))
        sl.append(Section("KEY", Key("Eb"), 31, 40))
        self.assertEqual(sl.getValues(), [Key("Ab"), Key("Db"), Key("Db"), Key("Eb")])
        self.assertEqual(len(sl), 4)
        self.assertEqual(sl.eventCount(), 40)
        self.assertEqual(sl.getStartID(), 1)
        self.assertEqual(sl.getEndID(), 40)

        self.assertRaises(Exception, sl.append, Section("FORM", FormName("A1"), 1,  10))
        self.assertRaises(Exception, sl.append, 1)
        sl.clear()
        sl.append(Section("FORM", FormName("A1"), 1, 10))
        sl.append(Section("FORM", FormName("A2"), 11, 20))
        sl.append(Section("FORM", FormName("A3"), 21, 30))
        sl.append(Section("FORM", FormName("A4"), 31, 40))
        self.assertEqual(len(sl), 4)
        self.assertEqual(sl[1] == Section("FORM", FormName("A2"), 11,  20), True )
        self.assertRaises(Exception, sl.append, Section("FORM", FormName("A''5"), 41, 50))

        sl.clear()
        sl.append(Section("FORM", FormName("*B1"), 1, 10))
        sl.append(Section("FORM", FormName("A3"), 11, 20))
        sl.append(Section("FORM", FormName("A1"), 21, 30))
        sl.append(Section("FORM", FormName("A2"), 31, 40))
        sl.append(Section("FORM", FormName("B1"), 41, 50))
        sl.append(Section("FORM", FormName("B2"), 51, 60))
        self.assertEqual(len(sl), 6)
        #sl.append(Section("PHRASE", 1, 41, 34))
        #print Section(None, None, 41, 50)
        #print  "\n".join([str(e) for e in sl.getValues(eventBased = True)])
        self.assertEqual(len(sl.getValues(eventBased = True)), 60)
        sl.clear()
        self.assertEqual(sl.isEmpty(), True)

        sl.append(Section("PHRASE", 1, 1, 10))
        sl.append(Section("PHRASE", 2, 11, 20))
        sl.append(Section("PHRASE", 4, 21, 30))
        self.assertRaises(Exception, sl.append, Section("PHRASE", 2, 31, 40))

        sl.clear()
        sl.append(Section("CHORUS", 1, 1, 10))
        sl.append(Section("CHORUS", 2, 11, 20))
        sl.append(Section("CHORUS", 3, 21, 30))
        self.assertEqual(sl[1] == Section("CHORUS", 1, 11,  20), True )
        self.assertRaises(Exception, sl.append, Section("CHORUS", 2, 31, 40))

        sl.clear()
        sl.append(Section("CHORD", Chord("Ab"), 1,  10))
        sl.append(Section("CHORD", Chord("Db"), 11, 20))
        sl.append(Section("CHORD", Chord("Db"), 21, 30))
        sl.append(Section("CHORD", Chord("Eb"), 31, 40))
        self.assertEqual(sl[1] == Section("CHORD", Chord("Db"), 11,  20), True )

        sl.clear()
        sl.append(Section("IDEA", Idea("lick_blues"), 1,  10))
        sl.append(Section("IDEA", Idea("#*lick_blues"), 11, 20))
        sl.append(Section("IDEA", Idea("line_w_asdl"), 21, 30))
        sl.append(Section("IDEA", Idea("theme:t1"), 31, 40))
        self.assertEqual(sl[3] == Section("IDEA", Idea("theme:t1"), 31,  40), True)
        vals = [1, 1, 1, 2, 2, 3, 3, 4, 4]
        sl = SectionList.fromEventList(vals, "PHRASE")
        self.assertEqual(sl[0] == Section("PHRASE", 1, 0,  2), True)
        vals = [1]
        sl = SectionList.fromEventList(vals, "PHRASE")
        self.assertEqual(sl[0] == Section("PHRASE", 1, 0,  0), True)
        vals = ["Cmaj7"]
        sl = SectionList.fromEventList(vals, "CHORD")
        # print type(sl[0].value)
        self.assertEqual(sl[0] == Section("CHORD", Chord("Cmaj7"), 0,  0), True)

    def testMethods(self):

        sl = SectionList()
        sl.append(Section("CHORD", Chord("Ab"), 1,  10))
        sl.append(Section("CHORD", Chord("Db"), 11, 20))
        sl.append(Section("CHORD", Chord("Db"), 21, 30))
        sl.append(Section("CHORD", Chord("Eb"), 31, 40))
        self.assertEqual(sl.clone().truncate(5, 35).getStartID(), 5)
        self.assertEqual(sl.clone().truncate(5, 35).getEndID(), 35)
        self.assertEqual(sl.clone().truncate(0, 35).getStartID(), 1)
        self.assertEqual(sl.clone().truncate(0, 35).getEndID(), 35)
        self.assertEqual(sl.clone().truncate(5, 45).getStartID(), 5)
        self.assertEqual(sl.clone().truncate(5, 45).getEndID(), 40)
        self.assertEqual(sl.clone().truncate(0, 45).getStartID(), 1)
        self.assertEqual(sl.clone().truncate(0, 45).getEndID(), 40)
        self.assertEqual(sl.clone().truncate(5, 35, True).getStartID(), 0)
        self.assertEqual(sl.clone().truncate(5, 35, True).getEndID(), 30)
        fsl = [x for x in sl if str(x.getValue()) == "Eb"]
        self.assertEqual(fsl[0].getStartID(), 31)
        self.assertEqual(fsl[0].getEndID(), 40)
        self.assertEqual(fsl[0].getValue(), Chord("Eb"))
        #print "\n".join([str(_) for _ in filter(lambda x:  not (x.startID<= 35 and x.endID>=35), sl )])
        #fsl = sl.filter(filter_func=lambda x, y:  x<= 35 and y>=35, filter_type="position")
        #self.assertEqual(fsl[0].getStartID(), 31)
        #self.assertEqual(fsl[0].getEndID(), 40)
        #self.assertEqual(fsl[0].getValue(), Chord("Eb"))

        #print "\n".join([str(s) for s in fsl])
        #print sl.clone().truncate(4, 47, True)
        #print sl.clone().truncate(0, 7).getStartID()
        self.assertEqual(sl.clone().shiftIDs(10).getStartID(), 11)
        self.assertEqual(sl.clone().shiftIDs(10).getEndID(), 50)
        self.assertEqual(sl.clone().shiftIDs(-1).getStartID(), 0)
        self.assertEqual(sl.clone().shiftIDs(-1).getEndID(), 39)
        self.assertEqual(sl.clone().pad(Chord("NC"), 0, 41).eventCount(), 42)
        # test with valid initialization
        #s = Section("KEY", k, 1, 2)
        #self.assertRaises(Exception, s.type, 1, 1.0, 2.0)
        #self.assertRaises(Exception, s.startID, 1.0, 1.0, 2.0)
        #self.assertRaises(Exception, s.endID, 1.0, 1.0, 2.0)
        #self.assertRaises(Exception, s.value, 1.0, 1.0, 2.0)
        self.assertEqual(sl.concat(sl.clone()).eventCount(), 80)
        #print sl.flatten()
        sl = SectionList()
        sl.append(Section("PHRASE", 1, 1,  10))
        sl.append(Section("PHRASE", 2, 11, 20))
        sl.append(Section("PHRASE", 3, 21, 30))
        sl.append(Section("PHRASE", 4, 31, 40))
        # print sl.clone().renumber(5)
        sects = sl.get_sections_by_ids(startID = 23, endID=None)
        # print "\n".join([str(s) for s in sects])
if __name__ == "__main__":
    unittest.main()
