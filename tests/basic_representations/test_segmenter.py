#!/usr/bin/env python

""" Unit test for class Segmenter"""

import unittest

from melospy.basic_representations.segmenter import *


class TestSegmenter( unittest.TestCase ):
    def getTestRhythm(self):
        r = Rhythm()
        onsets = [0, .5, 1., 1.5, 2, 4.5, 5.5, 7.5, 9.4]
        for on in onsets:
            e  = RhythmEvent(on,   0)
            r.append(e)
        return r

    def testConstructor(self):
        sp = SegmenterParams()
        r = self.getTestRhythm()
        s = Segmenter(rhythm=r, params=sp)
        self.assertEqual(len(s.rhythm), len(r))
        self.assertEqual(s.getParams().getValue("method"), sp.getValue("method"))
        self.assertEqual(s.getParams().getValue("output_format"), "rhythm")

    def testSimpleSegmenter(self):
        r = self.getTestRhythm()
        sp = SegmenterParams()
        s = Segmenter(rhythm=r, params=sp)
        sl = s.process()
        self.assertEqual(len(sl), 3)
        sp = SegmenterParams(output_format="section_list")
        s = Segmenter(rhythm=r, params=sp)
        sl = s.process()
        self.assertEqual(len(sl), 3)
        sp = SegmenterParams(method="relative_simple_segmenter", output_format="section_list")
        s = Segmenter(rhythm=r, params=sp)
        sl = s.process()
        self.assertEqual(len(sl), 4)

if __name__ == "__main__":
    unittest.main()
