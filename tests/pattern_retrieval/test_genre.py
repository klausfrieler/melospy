#!/usr/bin/env python

""" Unit test for GenRegexp class"""

import unittest

import pytest

from melospy.input_output.melody_importer import *
from melospy.pattern_retrieval.genre import *
from melospy.tools.commandline_tools.dbinfo import *

from tests.rootpath import *

def prepareTestData(performer, title, titleaddon=None, solopart=None, v1=True):
    dbpath = add_data_path('wjazzd.db')    
    dbinfo = DBInfo.fromDict({'path': dbpath, "use": True, "type":"sqlite3"})
    query = MelodyImporter.queryFromSoloInfo(performer, title, titleaddon, solopart)
    mi = MelodyImporter(tunes=query, path=dbpath, dbinfo=dbinfo )
    mel = next(mi.fetcher())
    return mel

class TestGenRegexpClass( unittest.TestCase ):
    """ Unit test for GenRegexp and helper classes """

    def testIntervalsToUnicode(self):
        pass

    def testEncoderFactory(self):
        ef= EncoderFactory()
        test = ef.create("int")
        self.assertEqual(isinstance(test, IntegerToUnicode), True)
        ef.debug = True
        test = ef.create("int")
        self.assertEqual(isinstance(test, IntegerToString), True)

    #@pytest.mark.skip(reason="Signature mismatch")
    def testConstructorAndMethods(self):
        """ Test functionality """
        genre = GenRegExp("int", debug=True)
        self.assertEqual(isinstance(genre.encoder, IntegerToString), True)
        self.assertEqual(isinstance(genre.encoder, IntegerToUnicode), False)
        solo = prepareTestData("Bob Berg", "Angles", v1 = False)

        pattern = [2, u'+(.){1,2}', -4, '+']
        genre.compile(pattern)
        #print(genre.pattern)
        self.assertEqual(genre.pattern, "".join([str(_) for _ in pattern]))
        genre = GenRegExp("int", debug=False)
        self.assertEqual(isinstance(genre.encoder, IntegerToUnicode), True)
        genre.compile(pattern)

        spans =[(46, 49), (67, 71), (78, 81), (94, 97), (146, 149), (181, 185), (213, 216), (245, 249), (263, 266), (365, 369), (417, 420), (488, 493), (634, 637), (673, 676)]
        intervals = solo.intervals()
        for i, m in enumerate(genre.finditer(intervals)):
            self.assertEqual(m.span(), spans[i])
            
        cpc = list(solo.export("cpc"))
        genre2 = GenRegExp("int", debug=False)
        pattern = [7, 9, 11]
        genre2.compile(pattern)
        spans = [(78, 81), (258, 261)]
        for i, m in enumerate(genre2.finditer(cpc)):
            self.assertEqual(m.span(), spans[i])

if __name__ == "__main__":
    unittest.main()
