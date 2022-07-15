#!/usr/bin/env python

""" Unit test for class MetricalAnnotator"""

import unittest

from melospy.basic_representations.metrical_annotator import *


class TestMetricalAnnotator( unittest.TestCase ):

    def testConstructor(self):
        cma = FlexQParams()

        e  = RhythmEvent(0,   0, Signature(4, 4) )
        e1 = RhythmEvent(0.5, 0)
        e2 = RhythmEvent(1.0, 0)
        e3 = RhythmEvent(1.5, 0)
        e4 = RhythmEvent(2.0, 0)
        e5 = RhythmEvent(2.5, 0)
        r = Rhythm()
        r.append(e).append(e1).append(e2).append(e3).append(e4).append(e5)

        #print "\nBeattrack\n================"
        #print r

        C4 = 60
        C5 = C4 + 12
        e  = NoteEvent(C4,   0.0,  0.125)
        e1 = NoteEvent(C4+2, 0.25, 0.1)
        e2 = NoteEvent(C4+3, 0.57, 0.21)
        e3 = NoteEvent(C4+5, 0.78, 1.0)
        e4 = NoteEvent(C4+5, 1.78, 0.01)
        e5 = NoteEvent(C4+5, 1.85, 50)
        n = NoteTrack()
        n.append(e).append(e1).append(e2).append(e3).append(e4).append(e5)

        #print "\nNotetrack\n================"
        #print n

        ma = MetricalAnnotator(n, r, cma)
        grid4 = constant_grid(4)
        grid2 = constant_grid(2)
        grid1 = constant_grid(1)
        x = [0.1, .3, .79]
        #idz = ma.closestGridPoints(x, grid4)
        #self.assertRaises(TypeError, ma.closestGridPoints, ["t", "t"], constant_grid(4))

        x = [-0.1, .3, .79]
        #idz = ma.closestGridPoints(x, constant_grid(4))

        x = [0.1, .3, 1.79]
        #idz = ma.closestGridPoints(x, constant_grid(4))

        x = [0.24, .25, .26, .27, .74]


        x = [0.42342]
        #print ma.quantize(x, 0.04, debug=False)
        #cma.setValue("scaleFactor", 0.5, float)
        cma.setValue("mismatchPenalty", 1.8, float)
        cma.setValue("distPenalty", 12.0, float)
        cma.setValue("oddDivisionPenalty", 0.2, float)
        for i in range(0, 100):
            x = [i*0.01]
            #print "="*40
            #print "Testing: ", round(x[0], 2)
            y = ma.quantize(x, 0.04, debug=False)
            #print  "Result:", round(x[0], 2), y

        for i in range(0, 20):
            for j in range(i+1, 20):
                x = [(i-1)*0.05, (j-1)*0.05]
                #print "="*40
                #print "Testing: ", round(x[0], 2), round(x[1], 2)
                y = ma.quantize(x, 0.04, debug=False)
                #print  "Result:", y

        #idz1 = ma.closestGridPoints(x, grid1, spread=True, scale=1, debug=False)
        #idz2 = ma.closestGridPoints(x, grid2, spread=True, scale=1, debug=False)
        #print "Idz1: {}, idz2:{}".format(idz1, idz2)
        ma.annotate()
        n = NoteTrack()
        e  = NoteEvent(C4,   26.819,  0.165)
        n.append(e)
        r1  = RhythmEvent(26.678, 0, Signature(4, 4))
        r2  = RhythmEvent(27.011, 0)
        r = Rhythm()
        r.append(r1).append(r2)
        ma = MetricalAnnotator(n, r, cma)
        mg = ma.annotate()

if __name__ == "__main__":
    unittest.main()
