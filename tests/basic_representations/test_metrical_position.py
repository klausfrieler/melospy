#!/usr/bin/env python

""" Unit test for class BeatInfo """

import unittest
from decimal import Decimal

from melospy.basic_representations.metrical_position import *


class TestMetricalPosition( unittest.TestCase ):

    def testHelper(self):
        """ Test assures that period and division can be easily retrieved"""
        mi = MeterInfo(8, 8, (3, 3, 2))
        bi = BeatInfo(4, .5)
        beatFrac = mi.fractions(True)

        pos, dur = find_position(beatFrac, .5)
        self.assertEqual(pos, 1)
        self.assertEqual(dur, .375)

        pos, dur = find_position(beatFrac, .25)
        self.assertEqual(pos, 0)
        self.assertEqual(dur, .375)

        pos, dur = find_position(beatFrac, 1.75)
        self.assertEqual(pos, None)
        self.assertEqual(dur, None)


    def testGetPeriodAndDivision(self):
        """ Test assures that period and division can be easily retrieved"""

    def testConstruction(self):
        """ Test assures that construction and setting members works fine"""
        mi = MeterInfo(7, 8, (3, 2, 2))
        bi = BeatInfo(4, .5)
        mc = MetricalContext(bi, mi)
        #self.assertRaises(Exception, MetricalPosition, 1.1,2,3,0, mc)
        #self.assertRaises(Exception, MetricalPosition, 1,2.1,3,0, mc)
        #self.assertRaises(Exception, MetricalPosition, 1,2,3.1,0, mc)
        #self.assertRaises(Exception, MetricalPosition, 1,2,3.1,0, mc)
        #self.assertRaises(Exception, MetricalPosition, 1,2,3,0.1, mc)
        #self.assertRaises(Exception, MetricalPosition, 1,2,3,0.0, mi)

        #default hell: BeatInfo: 120 bpm, 2 tatums, MeterInfo: 4/4 with equal proportions
        mc = MetricalContext(BeatInfo(), MeterInfo())
        #self.assertRaises(Exception, MetricalPosition, 1,0,3,0,   mc)
        #self.assertRaises(Exception, MetricalPosition, 1,1,3,0,   mc)

        mp = MetricalPosition(1, 2, 3, 0, MetricalContext(bi, mi))
        self.assertEqual((mp.toString()), "(3+2+2).4.1.2.3")
        self.assertEqual(mp.getPeriod(), 3)
        self.assertEqual(mp.getDivision(), 4)
        self.assertEqual(mp.toDict(), {'division': 4, 'bar': 1, 'beat': 2, 'meter': 3, 'subtatum': 0, 'tatum': 3})
        self.assertEqual(mp.getBeatDuration(), bi.beatDurationSec)
        self.assertEqual(mp.getSignature(), mi.getSignature())
        mp = mp.change(1, 3, 1, 0)
        self.assertEqual((mp.toString()), "(3+2+2).4.1.3.1")

        mp1 = mp.clone()
        self.assertEqual((mp.__eq__(mp1)), True)

        #print mp.toString()
        mp1 = mp.clone(4)
        self.assertEqual((mp1.toString()), "(3+2+2).4.1.3.4")
        mp1 = mp.clone(3, 2)
        self.assertEqual((mp1.toString()), "(3+2+2).4.1.2.3")
        mp1 = mp.clone(1, 3, 4)
        #print mp1.toString()
        self.assertEqual((mp1.toString()), "(3+2+2).4.4.3.1")

        mc1 = MetricalContext(BeatInfo(2, .5), MeterInfo(8, 8, (3, 3, 2)))
        mp1 = MetricalPosition(6, 2, 1, 0, mc1)
        self.assertEqual(str(mp1.getMeterInfo()), "3+3+2/8|3|(3, 3, 2)")
        self.assertEqual(str(mp1.getSignature()), "3+3+2/8")
        self.assertEqual(mp1.toDecimal(), 6 + .375)
        self.assertEqual(mp1.toFraction(), 6 + .375)
        mp2 = MetricalPosition(6, 3, 2, 0, mc1)
        self.assertEqual(mp2.toDecimal(), 6 + .75 + .125)
        self.assertEqual(mp2.toFraction(), 6 + .75 + .125)
        mc2 = MetricalContext(BeatInfo(2, .5), MeterInfo(10, 8, (2, 2, 2, 2, 2)))
        mp3 = MetricalPosition(1, 5, 2, 0, mc2)
        #print mp3.toFraction()
        #print mp3.toDecimal()
        self.assertEqual(mp3.quarterPositionFractional(), 4.5)
        self.assertEqual(mp3.quarterPositionDecimal(), 4.5)
        mc2 = MetricalContext(BeatInfo(3, .5), MeterInfo(6, 8))
        for beat in range(2):
            for tatum in range(3):
                #print "Beat: {}, tatum: {}".format(beat, tatum)
                mp3 = MetricalPosition(0, beat+1, tatum+1, 0, mc2)
                self.assertEqual(mp3.toFraction(), Fraction(3*beat+tatum, 6))
                #print mp3.toDecimal()
                self.assertEqual(mp3.quarterPositionFractional(), Fraction(3*beat+tatum, 2))
                #self.assertEqual(mp3.quarterPositionDecimal(), 2)

        self.assertEqual(mp2.fromDecimal(1.187, mc1).toString(), "(3+3+2).2.1.1.1")
        self.assertEqual(mp2.fromDecimal(1.188, mc1).toString(), "(3+3+2).2.1.1.2")
        self.assertEqual(mp2.fromDecimal(1.374, mc1).toString(), "(3+3+2).2.1.1.2")
        self.assertEqual(mp2.fromDecimal(1.375, mc1).toString(), "(3+3+2).2.1.2.1")
        self.assertEqual(mp2.fromDecimal(1.74,  mc1).toString(), "(3+3+2).2.1.2.2")
        self.assertEqual(mp2.fromDecimal(1.75,  mc1).toString(), "(3+3+2).2.1.3.1")
        self.assertEqual(mp2.fromDecimal(mp1.toDecimal(), mp1.getMetricalContext()).toDecimal(), mp1.toDecimal())
        self.assertEqual(mp2.getQuarterPeriod(), 4.0)
        self.assertEqual(mp3.getQuarterPeriod(), 3.0)


        MCM_div = 12
        mc_n = MetricalContext(BeatInfo(MCM_div/4, .25), MeterInfo(4, 4))
        for i in range(MCM_div):
            self.assertEqual(mp2.fromDecimal(1 + i/float(MCM_div), mc_n).getMCM(MCM_div), i)
            #print "="*10
            #print "Vals: ", i, i/float(MCM_div), (i/float(MCM_div)) % 1
            #print mp2.fromDecimal(1 + i/float(MCM_div), mc_n).getMCM(MCM_div)

        self.assertEqual(mp1 != mp2, True)
        self.assertEqual(mp1 == mp2, False)

        self.assertEqual(mp1<mp2, True)
        self.assertEqual(mp1>mp2, False)

        self.assertEqual(mp1<=mp2, True)
        self.assertEqual(mp1>=mp2, False)
        mp2 = mp1.clone().incSubtatum()

        self.assertEqual(mp1<=mp2, True)
        self.assertEqual(mp1>=mp2, False)

        self.assertEqual(mp1.hasConsistentMeterInfo(mp2), True)
        self.assertEqual(mp1.hasConsistentBeatInfo(mp2), True)
        self.assertEqual(mp1.consistent(mp2), True)

        mp3 = MetricalPosition(6, 2, 2, 0, MetricalContext(BeatInfo(2, .6), MeterInfo(8, 8, (3, 3, 2))))
        self.assertEqual(mp1.hasConsistentBeatInfo(mp3), False)

        mp3 = MetricalPosition(6, 2, 2, 0, MetricalContext(BeatInfo(2, .5), MeterInfo(8, 8, (3, 2, 3))))
        self.assertEqual(mp1.hasConsistentMeterInfo(mp3), False)

        self.assertEqual(mp1.consistent(mp3), False)

        mp = mp.incSubtatum()
        self.assertEqual((mp.toString()), "(3+2+2).4.1.3.1.1")
        mp = mp.change(1, 3, 2, 0)
        mp.rescale(24)
        self.assertEqual((mp.toString()), "(3+2+2).24.1.3.7")

        mp.rescale(4, True)
        #print mp
        self.assertEqual((mp.toString()), "(3+2+2).4.1.3.2")

        mp.addBar(24)
        self.assertEqual((mp.toString()), "(3+2+2).4.25.3.2")

        mp.addBeat(2)
        self.assertEqual(mp.toString(), "(3+2+2).4.26.2.2")

        mp.addBeat(6)
        self.assertEqual(mp.toString(), "(3+2+2).4.28.2.2")

        mp.addTatum(7)
        self.assertEqual(mp.toString(), "(3+2+2).4.29.1.1")
        mp.addTatum(4)
        self.assertEqual(mp.toString(), "(3+2+2).4.29.2.1")
        mp.addTatum(-5)
        #print "="*25
        mc1 = MetricalContext(BeatInfo(2, .5), MeterInfo(4, 4))
        test_vals = [(1, 2), (1.125, 0), (1.25, 1), (1.5, 2)]

        for t in test_vals:
            #print "val:{}, pos: {}, w: {}".format(t[0], mp3.fromDecimal(t[0], mc1).toString(), mp3.fromDecimal(t[0], mc1).getMetricalWeight())
            self.assertEqual(mp3.fromDecimal(t[0], mc1).getMetricalWeight(), t[1])

        #print "="*25

        mc1 = MetricalContext(BeatInfo(2, .5), MeterInfo(5, 4))
        test_vals = [(1, 2), (1.3, 0), (1.4, 1), (1.6, 2)]
        for t in test_vals:
            #print "-"*25
            #print "val:{}, pos: {}, w: {}".format(t[0], mp3.fromDecimal(t[0], mc1).toString(), mp3.fromDecimal(t[0], mc1).getMetricalWeight())
            self.assertEqual(mp3.fromDecimal(t[0], mc1).getMetricalWeight(), t[1])

        #print "="*25

        mc1 = MetricalContext(BeatInfo(3, .75), MeterInfo(5, 8))
        mc2 = MetricalContext(BeatInfo(2, .5), MeterInfo(5, 8))
        test_vals = [(1, 2, mc1), (1.2, 0, mc1), (1.4, 0, mc1), (1.6, 1, mc2)]
        for t in test_vals:
            #print "val:{}, pos: {}, w: {}".format(t[0], mp3.fromDecimal(t[0], t[2]).toString(), mp3.fromDecimal(t[0], t[2]).getMetricalWeight())
            self.assertEqual(mp3.fromDecimal(t[0], t[2]).getMetricalWeight(), t[1])

        mc1 = MetricalContext(BeatInfo(), MeterInfo(4, 4))
        mc2 = MetricalContext(BeatInfo(), MeterInfo(6, 8))
        test_vals = [(1, mc1, 0.), (2.25, mc1, 1.), (3.5,  mc1, 2.), (4.75, mc1, 3.)]
        test_vals.extend([(1, mc2, 0.), (2.25, mc2, 0.75), (3.5,  mc2, 1.5), (4.75, mc2, 2.25)])
        for t in test_vals:
            mp = mp3.fromDecimal(t[0], t[1])
            #print "val:{}, pos: {}, qpos: {}".format(t[0], mp, mp.quarterPositionDecimal())
            self.assertEqual(mp.quarterPositionDecimal(), t[2])

        test_vals = [(1, mc1, 0.), (2.25, mc1, 1.), (3.5,  mc1, 2.), (4.75, mc1, 3.)]
        test_vals.extend([(1, mc2, 0.), (2.25, mc2, 0.5), (3.5,  mc2, 1), (4.75, mc2, 1.5)])
        for t in test_vals:
            mp = mp3.fromDecimal(t[0], t[1])
            #print "val:{}, pos: {}, qpos: {}".format(t[0], mp, mp.quarterPositionDecimal())
            self.assertEqual(mp.beatPositionFractional(), Fraction.from_decimal(Decimal(t[2])))

if __name__ == "__main__":
    unittest.main()
