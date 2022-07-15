#!/usr/bin/env python

""" Unit test for class RecordInfo"""

import unittest

from melospy.basic_representations.record_info import *


class TestRecordInfo( unittest.TestCase ):

    def testConstructor(self):

        ri = RecordInfo("John Coltrane", "Giant Steps", "Impulse", "I2012", 1, "Reggie Workman (b); Elvin Jones (dr, perc); Paul Flanagan (p)", "02.04.1959", "09.1958", "189002e7-3285-4e2e-92a3-7f6c30d407a2")

        # test with valid initialization
        self.assertEqual(ri.getArtist(), "John Coltrane")
        self.assertEqual(ri.getRecordTitle(), "Giant Steps")
        self.assertEqual(ri.getLabel(), "Impulse")
        self.assertEqual(ri.tracknumber, 1)
        self.assertEqual(ri.getLineUp(), "Reggie Workman (b); Elvin Jones (dr, perc); Paul Flanagan (p)")
        self.assertEqual(ri.getReleaseDate(), SloppyDate.fromString("02.04.1959"))
        self.assertEqual(ri.recordingdate, "09.1958")
        self.assertEqual(ri.musicbrainzid, "189002e7-3285-4e2e-92a3-7f6c30d407a2")
        #print ri.parseLineup(ri.getLineUp())
        self.assertDictEqual(ri.parseLineup(ri.getLineUp()), {'Elvin Jones': ['dr', 'perc'], 'Reggie Workman': ['b'], 'Paul Flanagan': ['p']})
        #print ri.parseLineup("Coleman Hawkins (ts); Tommy Lindsay (tp); Joe Guy (tp); Earl Hardy (tb); Jackie Fields (as); Eustis Morre (as,cl); Gene Rodgers (p); William Oscar Smith (b); Arthur Herbert (dr); Thelma Carpenter (voc) + Bigband", player_based=False)
        self.assertDictEqual(ri.parseLineup("Coleman Hawkins (ts); Tommy Lindsay (tp); Joe Guy (tp); Earl Hardy (tb); Jackie Fields (as); Eustis Morre (as,cl); Gene Rodgers (p); William Oscar Smith (b); Arthur Herbert (dr); Thelma Carpenter (voc) + Bigband", player_based=False), {'b': ['William Oscar Smith'], 'cl': ['Eustis Morre'], 'dr': ['Arthur Herbert'], 'voc': ['Thelma Carpenter'], 'ts': ['Coleman Hawkins'], 'tp': ['Tommy Lindsay', 'Joe Guy'], 'p': ['Gene Rodgers'], 'as': ['Jackie Fields', 'Eustis Morre'], 'tb': ['Earl Hardy']})
        #print si
        #si = RecordInfo("John Coltrane")
        #print si
        # test with non-valid initialization
        #self.assertRaises(Exception, si.__init__, 1)
        #self.assertRaises(Exception, si.__init__, "John Coltrane", 2.)
        #self.assertRaises(Exception, si.__init__, "John Coltrane", "Giant Steps", 3., )
        #self.assertRaises(Exception, si.__init__, "John Coltrane", "Giant Steps", "Impulse", SloppyDate(2013, 1,2))
        #self.assertRaises(Exception, si.__init__, "John Coltrane", "Giant Steps", "Impulse", "I2012", "r")
        #self.assertRaises(Exception, si.__init__, "John Coltrane", "Giant Steps", "Impulse", "I2012", 1, .4)
        #self.assertRaises(Exception, si.__init__, "John Coltrane", "Giant Steps", "Impulse", "I2012", 1, "People", 2)
        #self.assertRaises(Exception, si.__init__, "John Coltrane", "Giant Steps", "Impulse", "I2012", 1, "People", "003.23.2012")
        #self.assertRaises(Exception, si.__init__, "John Coltrane", "Giant Steps", "Impulse", "I2012", 1, "People", "02.04.1959", "09.195890")

if __name__ == "__main__":
    unittest.main()
